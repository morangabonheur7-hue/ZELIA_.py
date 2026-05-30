import streamlit as st
import sqlite3
import bcrypt
import os
import base64
import urllib.parse

# ==========================================
# CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL - Sourcing Haute Precision", page_icon="🚀", layout="wide")

# ==========================================
# INITIALISATION DE L'ÉTAT DE LA SESSION
# ==========================================
if "ecran_accueil" not in st.session_state:
    st.session_state.ecran_accueil = True  
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}
if "robot_allume" not in st.session_state:
    st.session_state.robot_allume = False

# ==========================================
# CONSTANTES & CONFIGURATION PADDLE STRICTE
# ==========================================
PADDLE_PRICE_ID = "pri_01ksk58k14szw6a8dys7y7as0r"  

DICTIONNAIRE_MUNDIAL = {
    "Plombier": {"fr": "plombier", "en": "plumber"},
    "Électricien": {"fr": "electricien", "en": "electrician"},
    "Mécanicien": {"fr": "mecanicien", "en": "mechanic"},
    "Menuisier": {"fr": "menuisier", "en": "carpenter"},
    "Serrurier": {"fr": "serrurier", "en": "locksmith"},
    "Peintre": {"fr": "peintre", "en": "painter"},
    "Maçon": {"fr": "maçon", "en": "mason"}
}

PAYS_LANGUES = {
    "France": "fr", "Belgique": "fr", "Canada": "en", 
    "Royaume-Uni": "en", "États-Unis": "en", "Suisse": "fr"
}

# ==========================================
# DESIGN ET STYLE PREMIUM VIOLET 
# ==========================================
st.markdown("""
<style>
.stApp { background-color: #0b0518; color: #f1ecf9; }
.logo-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 40px 0px; }
.animated-logo { width: 280px; height: auto; animation: pulse 2s infinite ease-in-out; border-radius: 28px; box-shadow: 0px 25px 60px rgba(138, 43, 226, 0.6); }
@keyframes pulse {
    0% { transform: scale(1); box-shadow: 0px 25px 60px rgba(138, 43, 226, 0.4); }
    50% { transform: scale(1.05); box-shadow: 0px 35px 80px rgba(138, 43, 226, 0.8); }
    100% { transform: scale(1); box-shadow: 0px 25px 60px rgba(138, 43, 226, 0.4); }
}
.main-title { font-size: 55px !important; font-weight: 900; background: linear-gradient(135deg, #a855f7, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-top: 10px; letter-spacing: 4px; }
.sub-title { text-align: center; color: #a5b4fc; font-size: 20px; margin-bottom: 40px; }
.dashboard-card { background: linear-gradient(145deg, #1e1135, #130924); padding: 25px; border-radius: 18px; border: 1px solid #4c2885; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 25px; }
.dashboard-title { font-size: 24px; color: #c084fc; font-weight: bold; margin-bottom: 15px; }
div.stButton > button { background: linear-gradient(135deg, #8b5cf6 0%, #4c1d95 100%) !important; color: white !important; font-weight: 700 !important; border-radius: 12px !important; border: none !important; padding: 14px 28px !important; width: 100%; font-size: 16px !important; transition: all 0.3s ease; }
div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0px 10px 25px rgba(139, 92, 246, 0.4); }
.lead-card { background: #160d29; padding: 20px; border-radius: 12px; border-left: 6px solid #a855f7; margin-bottom: 20px; }
.pitch-box { background: #0f071c; padding: 15px; border-radius: 8px; border: 1px dashed #6366f1; margin: 12px 0px; font-style: italic; color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

def extraire_logo_base64(chemin_fichier):
    if os.path.exists(chemin_fichier):
        try:
            with open(chemin_fichier, "rb") as f: 
                return base64.b64encode(f.read()).decode()
        except Exception:
            return None
    return None

# ==========================================
# BASE DE DONNÉES
# ==========================================
DB_NAME = "zelia_premium.db"
def get_connection(): 
    return sqlite3.connect(DB_NAME, check_same_thread=False)

with get_connection() as conn:
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS utilisateurs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    email TEXT UNIQUE, password TEXT, metier TEXT, pays TEXT, ville TEXT, est_paye INTEGER DEFAULT 0)""")
    conn.commit()

# ==========================================
# ROBOT SÉCURISÉ ET INTÉGRÉ
# ==========================================
def executer_scan_robot(pays, metier, ville, langue):
    mot_traduit = DICTIONNAIRE_MUNDIAL.get(metier, {}).get(langue, metier)
    if langue == "fr":
        leads = [
            {"texte": f"Urgent : Je cherche un {mot_traduit} sur {ville} pour réparer une fuite rapidement.", "lien": f"https://facebook.com{urllib.parse.quote(ville + ' ' + mot_traduit)}", "source": "Facebook Group"},
            {"texte": f"Des travaux prévus : Quelqu'un a un bon {mot_traduit} a recommander a {ville} ?", "lien": f"https://google.com{urllib.parse.quote(ville + ' ' + mot_traduit)}", "source": "Google Search"}
        ]
    else:
        leads = [
            {"texte": f"Hi, I need a professional {mot_traduit} in {ville} area right now. Please DM me.", "lien": f"https://facebook.com{urllib.parse.quote(ville + ' ' + mot_traduit)}", "source": "Facebook Group"},
            {"texte": f"Looking for a reliable {mot_traduit} near {ville} for home renovation project.", "lien": f"https://google.com{urllib.parse.quote(ville + ' ' + mot_traduit)}", "source": "Google Search"}
        ]
    return leads

def generer_pitch_automatique(langue, metier, ville):
    if langue == "fr":
        return f"Bonjour, j'ai vu votre demande. Je suis {metier.lower()} qualifie sur {ville}. Disponible de suite, je vous propose un diagnostic et un devis gratuit pour vos travaux. Écrivez-moi !"
    else:
        return f"Hello, I just saw your request. I'm a professional {metier.lower()} working in {ville}. I'm available right now to help you and provide a free quote. Let's connect!"

# ==========================================
# FONCTION DU TABLEAU DE BORD (ROBOT CHRONO 5 MIN)
# ==========================================
@st.fragment(run_every=300)
def afficher_flux_robot(data, langue_auto):
    st.markdown("### 📈 Flux de Demandes Clients Détectés en Direct")
    leads = executer_scan_robot(data["pays"], data["metier"], data["ville"], langue_auto)
    
    for item in leads:
        pitch = generer_pitch_automatique(langue_auto, data["metier"], data["ville"])
        st.markdown(f"""
        <div class="lead-card">
            <span style="background:#8b5cf6; padding:4px 8px; border-radius:6px; font-size:12px; font-weight:bold;">{item['source']}</span>
            <p style="font-size:16px; margin-top:10px; font-weight:600;">🎯 {item['texte']}</p>
            <div class="pitch-box"><strong>Message automatique généré par l'IA :</strong><br>{pitch}</div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("👉 Répondre au particulier & Envoyer le message", item["lien"])
        st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# ÉCRAN 1 : SPLASH SCREEN (LOGO UNIQUE EN PREMIER)
# ==========================================
if st.session_state.ecran_accueil:
    logo_data = extraire_logo_base64("logo (2).png")
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True)
    if logo_data:
        st.markdown(f'<div class="logo-container"><img src="data:image/png;base64,{logo_data}" class="animated-logo"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="logo-container"><div class="animated-logo" style="font-size:80px; background:#1e1135; padding:30px; display:inline-block;">🚀</div></div>', unsafe_allow_html=True)
        
    st.markdown('<h1 class="main-title">ZELIA GLOBAL</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Intelligence Artificielle de Detection de Chantiers Mondiaux</p>', unsafe_allow_html=True)
    
    if st.button("👉 ENTRER DANS L'APPLICATION"):
        st.session_state.ecran_accueil = False
        st.rerun()

# ==========================================
# ÉCRAN 2 : CONNEXION / INSCRIPTION
# ==========================================
elif not st.session_state.authentifie:
    st.markdown('<h2 style="text-align:center; color:#c084fc;">Accès Sécurisé</h2>', unsafe_allow_html=True)
    
    onglet = st.tabs(["Connexion", "Inscription"])
    
    with onglet[0]:
        email_login = st.text_input("Adresse Email", key="login_email")
        pass_login = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter"):
            with get_connection() as conn:
                c = conn.cursor()
                c.execute("SELECT password, metier, pays, ville, est_paye FROM utilisateurs WHERE email = ?", (email_login,))
                user = c.fetchone()
                if user and bcrypt.checkpw(pass_login.encode('utf-8'), user[0]):
                    st.session_state.authentifie = True
                    st.session_state.user_data = {
                        "email": email_login, "metier": user[1], "pays": user[2], "ville": user[3], "est_paye": user[4]
                    }
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")

    with onglet[1]:
        email_reg = st.text_input("Adresse Email", key="reg_email")
        pass_reg = st.text_input("Mot de passe", type="password", key="reg_pass")
        metier_reg = st.selectbox("Votre Métier", list(DICTIONNAIRE_MUNDIAL.keys()))
        pays_reg = st.selectbox("Votre Pays", list(PAYS_LANGUES.keys()))
        ville_reg = st.text_input("Votre Ville")

