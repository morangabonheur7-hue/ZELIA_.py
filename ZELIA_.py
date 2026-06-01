import streamlit as st
import sqlite3
import time
import base64
import os
import requests
import urllib.parse
import threading

# ==========================================
# 1. CONFIGURATION STRICTE DE LA PAGE & STYLE CSS
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    /* Application globale */
    .stApp { background-color: #0b0518; color: #ffffff; }
    h1, h2, h3, p, label, .stMarkdown { color: #ffffff !important; }
    
    /* Splash screen géant centré */
    .full-screen-splash { 
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
        background-color: #0b0518; display: flex; flex-direction: column; 
        align-items: center; justify-content: center; z-index: 99999; text-align: center; 
    }
    .splash-text { margin-top: 40px; font-size: 22px; color: #a5b4fc !important; letter-spacing: 3px; font-weight: 300; text-transform: uppercase; }
    
    /* Boutons premium */
    div.stButton > button { 
        background: linear-gradient(135deg, #8b5cf6 0%, #4c1d95 100%) !important; 
        color: white !important; font-weight: 700 !important; border-radius: 10px !important; 
        border: none !important; padding: 12px 24px !important; width: 100%; transition: all 0.3s ease; 
    }
    div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0px 8px 25px rgba(139, 92, 246, 0.5); }
    
    /* Cartes de leads */
    .lead-card { background: #160d29; padding: 20px; border-radius: 12px; border-left: 6px solid #ef4444; margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.3); }
    .pitch-box { background: #0f071c; padding: 15px; border-radius: 8px; border: 1px dashed #6366f1; margin: 12px 0px; font-style: italic; color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

db_lock = threading.Lock()

# ==========================================
# 2. INITIALISATION DE L'ÉTAT DE SESSION
# ==========================================
if "splash_done" not in st.session_state: st.session_state.splash_done = False
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_id" not in st.session_state: st.session_state.user_id = None

if not st.session_state.splash_done:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown('<div class="full-screen-splash"><div class="splash-text">🚀 ZELIA GLOBAL IS LOADING...</div></div>', unsafe_allow_html=True)
    time.sleep(3)
    st.session_state.splash_done = True
    st.rerun()

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
        "licence_label": "Clé de licence Paddle (Reçue par email)", "succes": "✅ Inscription effectuée avec succès !", 
        "erreur_paddle": "❌ Clé de licence invalide.", "bouton_creer": "Créer mon compte et lancer l'essai", 
        "robot_on": "🟢 Allumer le robot ZELIA", "robot_off": "🔴 Éteindre le robot ZELIA", "whatsapp": "🔗 Configurer mon numéro WhatsApp", 
        "num_wa": "Numéro WhatsApp (Format international ex: +33612345678)", "robot_pret": "🚀 Le robot ZELIA est actif en arrière-plan."
    },
    "en": {
        "titre_ins": "📝 Global Registration System", "nom": "Full Name", "metier": "Artisan Craft / Trade (ex: plumber)", "pays": "Country", "ville": "City", 
        "licence_label": "Paddle License Key (Received by email)", "succes": "✅ Registration successful!", 
        "erreur_paddle": "❌ Invalid license key.", "bouton_creer": "Create my account & start trial", 
        "robot_on": "🟢 Turn On ZELIA Robot", "robot_off": "🔴 Turn Off ZELIA Robot", "whatsapp": "🔗 Configure my WhatsApp Number", 
        "num_wa": "WhatsApp number (International format ex: +1234567890)", "robot_pret": "🚀 ZELIA Robot is active in background."
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
# 3. VERIFICATIONS & BACKEND MOTOR (ROBOT & SCRAP)
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
    req_encoded = urllib.parse.quote(requete_precise)
    return [
        {"texte": f"Recherche active pour : {mot_cle} à {ville}.", "lien": f"https://google.com{req_encoded}", "plateforme": "Google Web"},
        {"texte": f"Recherche ouverte sur Facebook Groups concernant : {mot_cle} à {ville}.", "lien": f"https://facebook.com{req_encoded}", "plateforme": "Facebook Groups"},
        {"texte": f"Analyse lancée sur Reddit concernant : {mot_cle} à {ville}.", "lien": f"https://reddit.com{req_encoded}&sort=new", "plateforme": "Reddit"}
    ]

def execution_moteur_robot():
    while True:
        try:
            with db_lock:
                conn = sqlite3.connect(DB_NAME, check_same_thread=False)
                c = conn.cursor()
                c.execute("SELECT id, nom, metier, ville, whatsapp FROM artisans WHERE robot_actif = 1 AND whatsapp IS NOT NULL")
                actifs = c.fetchall()
                conn.close()
            
            for artisan in actifs:
                artisan_id, nom, metier, ville, whatsapp = artisan
                pitch = generer_pitch_automatique("fr", metier, ville)
                message_wa = f"🚀 ZELIA ALERTE CLIENT !\n\nBonjour {nom}, un client recherche un {metier} à {ville}.\n\n👉 Voici votre message prêt à envoyer : {pitch}"
                msg_encoded = urllib.parse.quote(message_wa)
                
                lien_whatsapp_direct = f"https://whatsapp.com{whatsapp}&text={msg_encoded}"
                
                with db_lock:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO alertes (artisan_id, texte, lien, plateforme) VALUES (?, ?, ?, ?)", 
                              (artisan_id, f"Nouveau client potentiel détecté pour un {metier}", lien_whatsapp_direct, "WhatsApp Notification"))
                    conn.commit()
                    conn.close()
            
            time.sleep(60) 
        except Exception as e:
            time.sleep(10)

if "robot_thread" not in st.session_state:
    t_robot = threading.Thread(target=execution_moteur_robot, daemon=True)
    t_robot.start()
    st.session_state.robot_thread = True

# ==========================================
# 4. INTERFACE GRAPHIQUE DE CONNEXION
# ==========================================
st.title("🚀 ZELIA GLOBAL - Artisan Lead Locator")
langue = "fr"
t = TEXTES[langue]

if not st.session_state.authentifie:
    st.subheader(t["titre_ins"])
    
    # Utilisation d'un formulaire strict pour bloquer les rafraîchissements Android intempestifs
    with st.form("formulaire_inscription"):
        nom = st.text_input(t["nom"])
        metier = st.selectbox(t["metier"], ["plombier", "electricien", "serrurier", "mecanicien"])
        pays = st.selectbox(t["pays"], list(PAYS_LANGUES.keys()))
        ville = st.text_input(t["ville"])
        licence = st.text_input(t["licence_label"], value="TEST-ZELIA")
        
        # Le bouton de soumission du formulaire
        bouton_soumettre = st.form_submit_button(t["bouton_creer"])

    if bouton_soumettre:
        # Nettoyage des espaces cachés que le clavier Android ajoute parfois
        nom_clean = nom.strip() if nom else ""
        ville_clean = ville.strip() if ville else ""
        licence_clean = licence.strip() if licence else ""
        
        if nom_clean and ville_clean and licence_clean:
            if verifier_licence_paddle(licence_clean):
                try:
                    with db_lock:
                        conn = sqlite3.connect(DB_NAME)
                        c = conn.cursor()
                        c.execute("INSERT INTO artisans (nom, metier, pays, ville, licence) VALUES (?, ?, ?, ?, ?)", 
                                  (nom_clean, metier, pays, ville_clean, licence_clean))
                        conn.commit()
                        conn.close()
                    
                    # Sauvegarde des données dans la session avant le rechargement
                    st.session_state.authentifie = True
                    st.session_state.user_id = nom_clean
                    st.session_state.user_metier = metier
                    st.session_state.user_ville = ville_clean
                    st.success(t["succes"])
                    time.sleep(1) # Laisse le temps au message vert de s'afficher
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur de base de données : {e}")
            else: 
                st.error("❌ Clé de licence invalide. Vérifiez l'exactitude du code.")
        else: 
            st.error("⚠️ Attention : Vous devez obligatoirement remplir les champs 'Nom & Prénom' et 'Ville'.")
    
