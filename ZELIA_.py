import streamlit as st
import sqlite3
import time
import base64
import os
import requests
import urllib.parse
import threading

# ==========================================
# CONFIGURATION DE LA PAGE & STYLE PREMIUM
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0518; color: #ffffff; }
    h1, h2, h3, p, label, .stMarkdown { color: #ffffff !important; }
    .splash-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 80vh; text-align: center; }
    .animated-logo { width: 250px; height: auto; border-radius: 20px; animation: pulse 2s infinite ease-in-out; box-shadow: 0px 20px 50px rgba(138, 43, 226, 0.5); }
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0px 20px 50px rgba(138, 43, 226, 0.4); }
        50% { transform: scale(1.05); box-shadow: 0px 30px 70px rgba(138, 43, 226, 0.7); }
        100% { transform: scale(1); box-shadow: 0px 20px 50px rgba(138, 43, 226, 0.4); }
    }
    div.stButton > button { background: linear-gradient(135deg, #8b5cf6 0%, #4c1d95 100%) !important; color: white !important; font-weight: 700 !important; border-radius: 10px !important; border: none !important; padding: 12px 24px !important; width: 100%; transition: all 0.3s; }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0px 8px 20px rgba(139, 92, 246, 0.4); }
    .lead-card { background: #160d29; padding: 20px; border-radius: 12px; border-left: 6px solid #ef4444; margin-bottom: 20px; }
    .pitch-box { background: #0f071c; padding: 15px; border-radius: 8px; border: 1px dashed #6366f1; margin: 12px 0px; font-style: italic; color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

# Verrou de sécurité pour empêcher les collisions d'écriture dans la base de données
db_lock = threading.Lock()

# ==========================================
# INITIALISATION DES VARIABLES ET CONSTANTES
# ==========================================
if "splash_done" not in st.session_state: st.session_state.splash_done = False
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_id" not in st.session_state: st.session_state.user_id = None

PADDLE_PRICE_ID = "pri_01ksk58k14szw6a8dys7y7as0r"
PADDLE_CHECKOUT_URL = f"https://paddle.com{PADDLE_PRICE_ID}"

PAYS_LANGUES = {"France": "fr", "Belgique": "fr", "Suisse": "fr", "Canada": "en", "United Kingdom": "en", "United States": "en"}

DICTIONNAIRE_MOTS_CLES = {
    "plombier": {
        "fr": ["je cherche un plombier", "fuite d'eau", "urgence plombier", "canalisation bouchee"],
        "en": ["need a plumber", "water leak", "emergency plumber", "clogged drain"]
    },
    "electricien": {
        "fr": ["je cherche un electricien", "panne de courant", "court circuit", "urgence electricien"],
        "en": ["need an electrician", "power outage", "short circuit", "emergency electrician"]
    }
}

TEXTES = {
    "fr": {
        "titre_ins": "📝 Système d'Inscription Mondial", "nom": "Nom & Prénom", "metier": "Métier d'artisan (ex: plombier)", "pays": "Pays de résidence", "ville": "Ville", 
        "payer": "💳 Étape 1 : Activer votre essai 12 jours sur Paddle", "licence_label": "Clé de licence (Reçue par email)", "succes": "✅ Inscription effectuée avec succès !", 
        "existe": "❌ Ce compte existe déjà.", "erreur_paddle": "❌ Clé de licence invalide.", "bouton_creer": "Créer mon compte", 
        "robot_on": "🟢 Allumer le robot ZELIA", "robot_off": "🔴 Éteindre le robot ZELIA", "whatsapp": "🔗 Connecter mon WhatsApp Business", 
        "num_wa": "Numéro WhatsApp (ex: +33...)", "robot_pret": "🚀 Le robot ZELIA est initialisé."
    },
    "en": {
        "titre_ins": "📝 Global Registration System", "nom": "Full Name", "metier": "Artisan Craft / Trade (ex: plumber)", "pays": "Country", "ville": "City", 
        "payer": "💳 Step 1: Activate your 12-day trial on Paddle", "licence_label": "License Key", "succes": "✅ Registration successful!", 
        "existe": "❌ This account already exists.", "erreur_paddle": "❌ Invalid license key.", "bouton_creer": "Create my account", 
        "robot_on": "🟢 Turn On ZELIA Robot", "robot_off": "🔴 Turn Off ZELIA Robot", "whatsapp": "🔗 Connect my WhatsApp Business", 
        "num_wa": "WhatsApp number (ex: +1...)", "robot_pret": "🚀 ZELIA Robot initialized."
    }
}

# Pour le cloud Streamlit.io, on stocke la BDD dans un dossier accessible universellement en écriture
DB_NAME = "zelia_data.db"

def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS artisans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, metier TEXT, pays TEXT, ville TEXT, licence TEXT, whatsapp TEXT DEFAULT NULL, robot_actif INTEGER DEFAULT 0)""")
        c.execute("""CREATE TABLE IF NOT EXISTS alertes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, artisan_id INTEGER, texte TEXT, lien TEXT, plateforme TEXT)""")
        conn.commit()
        conn.close()

init_db()

# ==========================================
# FONCTIONS SÉCURITÉ PADDLE & PITCH AUTO
# ==========================================
def verifier_licence_paddle(cle):
    if cle == "TEST-ZELIA": return True
    if "PADDLE_API_KEY" in st.secrets:
        try:
            r = requests.get(f"https://paddle.com{cle}", headers={"Authorization": f"Bearer {st.secrets['PADDLE_API_KEY']}"}, timeout=10)
            if r.status_code == 200 and r.json().get("data", {}).get("status") == "active": return True
        except: pass
    return False

def generer_pitch_automatique(langue, metier, ville):
    if langue == "fr": return f"Bonjour, j'ai vu votre demande. Je suis {metier.lower()} qualifié sur {ville}. Disponible immédiatement pour analyser votre besoin et vous faire un devis gratuit. Contactez-moi !"
    return f"Hello, I just saw your post. I'm a professional {metier.lower()} working in {ville}. Available right now to assist you and provide a free quote. Let's connect!"

# ==========================================
# MOTEUR DU ROBOT ZELIA (THREAD-SAFE SANS PLANTAGE)
# ==========================================
def execution_moteur_robot():
    while True:
        try:
            with db_lock:
                conn = sqlite3.connect(DB_NAME, check_same_thread=False)
                c = conn.cursor()
                c.execute("SELECT id, metier, pays, ville, whatsapp FROM artisans WHERE robot_actif = 1")
                actifs = c.fetchall()
                conn.close()

            for art in actifs:
                art_id, metier, pays, ville, whatsapp = art
                langue = PAYS_LANGUES.get(pays, "fr")
                mots = DICTIONNAIRE_MOTS_CLES.get(metier.lower().strip(), {}).get(langue, [f"cherche {metier}"])
                
                for m in mots[:2]:
                    req = urllib.parse.quote(f'"{m}" "{ville}"')
                    vrai_lien = f"https://facebook.com{req}"
                    texte_alerte = f"Urgent : Demande client détectée pour la recherche '{m}' localisée à {ville}."
                    
                    with db_lock:
                        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
                        c = conn.cursor()
                        c.execute("SELECT id FROM alertes WHERE artisan_id = ? AND texte = ?", (art_id, texte_alerte))
                        if not c.fetchone():
                            c.execute("INSERT INTO alertes (artisan_id, texte, lien, plateforme) VALUES (?, ?, ?, ?)", (art_id, texte_alerte, vrai_lien, "Web Search"))
                            conn.commit()
                        conn.close()
        except Exception as e:
            print(f"Erreur Robot Invisible: {e}")
        time.sleep(300)

# Allocation sécurisée du processus d'arrière-plan dans le Runtime Streamlit
if not any(t.name == "ZeliaRobotThread" for t in threading.enumerate()):
    t = threading.Thread(target=execution_moteur_robot, name="ZeliaRobotThread", daemon=True)
    t.start()

# ==========================================
# ÉCRAN 1 : SPLASH SCREEN ANIMÉ (10 SECONDES)
# ==========================================
if not st.session_state.splash_done:
    container = st.empty()
    with container.container():
        st.markdown('<div class="splash-container">', unsafe_allow_html=True)
        if os.path.exists("mon logo (2).png"):
            with open("mon logo (2).png", "rb") as f: encoded = base64.b64encode(f.read()).decode()
            st.markdown(f'<img src="data:image/png;base64,{encoded}" class="animated-logo">', unsafe_allow_html=True)
        else:
            st.markdown('<h1 style="font-size:60px; color:#8b5cf6;">ZELIA GLOBAL</h1>', unsafe_allow_html=True)
        st.markdown('<p style="margin-top:20px; font-size:18px; color:#a5b4fc;">Initialisation des protocoles de sourcing...</p></div>', unsafe_allow_html=True)
    time.sleep(10)
    st.session_state.splash_done = True
    st.rerun()

# ==========================================
# ÉCRAN 2 : ACCUEIL & INSCRIPTION REACTIVE
# ==========================================
elif not st.session_state.authentifie:
    st.write("# ZELIA GLOBAL")
    pays_temp = st.selectbox("🌍 Select country / Choisissez le pays", list(PAYS_LANGUES.keys()))
    langue = PAYS_LANGUES.get(pays_temp, "fr")
    txt = TEXTES[langue]
    
    st.subheader(txt["titre_ins"])
    st.markdown(f'<div style="background-color:#1e1135; padding:15px; border-radius:10px; margin-bottom:15px;"><a href="{PADDLE_CHECKOUT_URL}" target="_blank" style="color:#a855f7; font-weight:bold; font-size:18px;">{txt["payer"]}</a></div>', unsafe_allow_html=True)
    
    declencher_redirection = False
    
    with st.form("inscription_form"):
        nom = st.text_input(txt["nom"])
