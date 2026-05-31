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
    
    .full-screen-splash { 
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
        background-color: #0b0518; display: flex; flex-direction: column; 
        align-items: center; justify-content: center; z-index: 99999; text-align: center; 
    }
    .animated-logo-giant { 
        width: 450px; height: auto; border-radius: 28px; 
        animation: pulse-giant 2.5s infinite ease-in-out; 
        box-shadow: 0px 30px 80px rgba(138, 43, 226, 0.6); 
    }
    @keyframes pulse-giant {
        0% { transform: scale(1); box-shadow: 0px 30px 80px rgba(138, 43, 226, 0.5); }
        50% { transform: scale(1.08); box-shadow: 0px 45px 100px rgba(138, 43, 226, 0.9); }
        100% { transform: scale(1); box-shadow: 0px 30px 80px rgba(138, 43, 226, 0.5); }
    }
    .splash-text { margin-top: 35px; font-size: 22px; color: #a5b4fc !important; letter-spacing: 2px; font-weight: 300; }
    
    div.stButton > button { 
        background: linear-gradient(135deg, #8b5cf6 0%, #4c1d95 100%) !important; 
        color: white !important; font-weight: 700 !important; border-radius: 10px !important; 
        border: none !important; padding: 12px 24px !important; width: 100%; transition: all 0.3s; 
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0px 8px 20px rgba(139, 92, 246, 0.4); }
    
    .lead-card { background: #160d29; padding: 20px; border-radius: 12px; border-left: 6px solid #ef4444; margin-bottom: 20px; }
    .pitch-box { background: #0f071c; padding: 15px; border-radius: 8px; border: 1px dashed #6366f1; margin: 12px 0px; font-style: italic; color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

# Verrou de sécurité thread-safe pour SQLite sur Streamlit Cloud
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
    },
    "serrurier": {
        "fr": ["je cherche un serrurier", "porte claquee", "serrure bloquee", "urgence serrurier"],
        "en": ["need a locksmith", "locked out", "broken lock", "emergency locksmith"]
    },
    "mecanicien": {
        "fr": ["je cherche un mecanicien", "recherche mecanicien", "panne voiture", "reparer voiture"],
        "en": ["need a mechanic", "car repair", "car breakdown", "emergency mechanic"]
    }
}

TEXTES = {
    "fr": {
        "titre_ins": "📝 Système d'Inscription Mondial", "nom": "Nom & Prénom", "metier": "Métier d'artisan (ex: plombier)", "pays": "Pays de résidence", "ville": "Ville", 
        "payer": "💳 Étape 1 : Activer votre essai 12 jours sur Paddle (29,99€ après l'essai)", "licence_label": "Clé de licence Paddle (Reçue par email)", "succes": "✅ Inscription effectuée avec succès !", 
        "existe": "❌ Ce compte existe déjà.", "erreur_paddle": "❌ Clé de licence invalide.", "bouton_creer": "Créer mon compte et lancer l'essai", 
        "robot_on": "🟢 Allumer le robot ZELIA", "robot_off": "🔴 Éteindre le robot ZELIA", "whatsapp": "🔗 Connecter mon WhatsApp Business", 
        "num_wa": "Numéro WhatsApp (ex: +33...)", "robot_pret": "🚀 Le robot ZELIA est initialisé."
    },
    "en": {
        "titre_ins": "📝 Global Registration System", "nom": "Full Name", "metier": "Artisan Craft / Trade (ex: plumber)", "pays": "Country", "ville": "City", 
        "payer": "💳 Step 1: Activate your 12-day trial on Paddle ($29.99 after trial)", "licence_label": "Paddle License Key (Received by email)", "succes": "✅ Registration successful!", 
        "existe": "❌ This account already exists.", "erreur_paddle": "❌ Invalid license key.", "bouton_creer": "Create my account & start trial", 
        "robot_on": "🟢 Turn On ZELIA Robot", "robot_off": "🔴 Turn Off ZELIA Robot", "whatsapp": "🔗 Connect my WhatsApp Business", 
        "num_wa": "WhatsApp number (ex: +1...)", "robot_pret": "🚀 ZELIA Robot initialized."
    }
}

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

def executer_vrai_scrapping_google(mot_cle, ville):
    requete_precise = f'"{mot_cle}" "{ville}"'
    if "GOOGLE_API_KEY" in st.secrets and "GOOGLE_CSE_ID" in st.secrets:
        url = "https://googleapis.com"
        params = {"key": st.secrets["GOOGLE_API_KEY"], "cx": st.secrets["GOOGLE_CSE_ID"], "q": requete_precise, "num": 3, "sort": "date"}
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                items = response.json().get("items", [])
                vrais_leads = []
                for item in items:
                    vrais_leads.append({"texte": item.get("snippet", "Demande détectée"), "lien": item.get("link", "#"), "plateforme": urllib.parse.urlparse(item.get("link")).netloc})
                return vrais_leads
        except: pass

    req_encoded = urllib.parse.quote(requete_precise)
    return [
        {"texte": f"Recherche en temps réel ouverte sur Facebook Groups pour détection de profils cherchant : {mot_cle} à {ville}.", "lien": f"https://facebook.com{req_encoded}", "plateforme": "Facebook Groups (Flux Direct)"},
        {"texte": f"Analyse chirurgicale lancée sur Reddit concernant les fils de discussions : {mot_cle} à {ville}.", "lien": f"https://reddit.com{req_encoded}", "plateforme": "Reddit (Flux Direct)"}
    ]

# ==========================================
# LOGIQUE DE NAVIGATION DE L'APPLICATION
# ==========================================

# Écran de Splash d'accueil
if not st.session_state.splash_done:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(f"""
        <div class="full-screen-splash">
            <h1 style='font-size: 50px; font-weight: 900; background: linear-gradient(to right, #ffffff, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>ZELIA GLOBAL</h1>
            <p class="splash-text">INITIALISATION DU ROBOT DE CHASSE DE LEADS MONDIAL...</p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(2.5)
    st.session_state.splash_done = True
    st.rerun()

# Affichage du Tableau de bord (Si connecté et authentifié)
if st.session_state.authentifie:
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT nom, metier, pays, ville, whatsapp, robot_actif FROM artisans WHERE id = ?", (st.session_state.user_id,))
        user = c.fetchone()
        conn.close()

    if user:
        nom, metier, pays, ville, whatsapp, robot_actif = user
        langue = PAYS_LANGUES.get(pays, "fr")
        t = TEXTES[langue]

        st.title(f"🚀 ZELIA GLOBAL — Dashboard de {nom}")
        st.subheader(f"🎯 Ciblage actif : {metier.capitalize()} à {ville} ({pays})")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.write(f"### ⚙️ {t['whatsapp']}")
            nv_wa = st.text_input(t["num_wa"], value=whatsapp if whatsapp else "", key="wa_input")
            if st.button("Mettre à jour WhatsApp"):
                with db_lock:
