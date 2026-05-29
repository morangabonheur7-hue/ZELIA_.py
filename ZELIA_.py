import streamlit as st
import sqlite3
import bcrypt
import os
import base64
import pandas as pd
import httpx
import urllib.parse
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

# ==========================================
# CONFIGURATION PAGE & PADDLE
# ==========================================
st.set_page_config(page_title="ZELIA - Sourcing Mondial", page_icon="🚀", layout="wide")
PADDLE_VENDOR_ID = "345487"
PADDLE_PRICE_ID = "pri_01ksk58k14szw6a8dys7y7as0r"

# --- CONFIGURATION DU ROBOT INTÉGRÉ ---
DICTIONNAIRE_MUNDIAL = {
    "Plombier": {"fr": "plombier", "en": "plumber"},
    "Électricien": {"fr": "electricien", "en": "electrician"},
    "Mécanicien": {"fr": "mecanicien", "en": "mechanic"},
    "Menuisier": {"fr": "menuisier", "en": "carpenter"},
    "Serrurier": {"fr": "serrurier", "en": "locksmith"}
}
EMPREINTES_LANGUES = {
    "fr": ["cherche", "besoin", "recommande", "urgence"],
    "en": ["looking for", "need a", "recommend", "urgent"]
}
PAYS_LANGUES = {"France": "fr", "Belgique": "fr", "Canada": "en", "Royaume-Uni": "en", "États-Unis": "en"}
VILLES_MONDE = {
    "France": ["Paris", "Lyon", "Marseille"],
    "Royaume-Uni": ["London", "Manchester"],
    "Canada": ["Toronto", "Montréal"]
}

# ==========================================
# CSS PREMIUM
# ==========================================
st.markdown("""
<style>
.logo-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 40px 0px 10px 0px; }
.animated-logo { width: 250px; height: auto; animation: pulse 3s infinite ease-in-out; border-radius: 20px; box-shadow: 0px 15px 50px rgba(0, 168, 107, 0.4); }
@keyframes pulse {
    0% { transform: scale(1); box-shadow: 0px 15px 50px rgba(0, 168, 107, 0.3); }
    50% { transform: scale(1.06); box-shadow: 0px 25px 60px rgba(0, 168, 107, 0.6); }
    100% { transform: scale(1); box-shadow: 0px 15px 50px rgba(0, 168, 107, 0.3); }
}
.main-title { font-size: 46px !important; font-weight: 900; background: linear-gradient(45deg, #00A86B, #00FF9D); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 15px; letter-spacing: 2px; }
div.stButton > button { background: linear-gradient(135deg, #00A86B 0%, #007d50 100%) !important; color: white !important; font-weight: bold !important; border-radius: 12px !important; border: none !important; padding: 12px 25px !important; width: 100%; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# BASE DE DONNÉES
# ==========================================
DB_NAME = "clients.db"
def get_connection(): return sqlite3.connect(DB_NAME, check_same_thread=False)

def initialiser_bdd():
    conn = get_connection()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS utilisateurs (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, device_id TEXT, Paddle_actif INTEGER DEFAULT 0, service_choisi TEXT DEFAULT 'Tous', pays_choisi TEXT DEFAULT 'Tous')")
    c.execute("CREATE TABLE IF NOT EXISTS opportunites (id INTEGER PRIMARY KEY AUTOINCREMENT, titre TEXT, ville TEXT, pays TEXT DEFAULT 'Global', niche TEXT, lien TEXT, date_trouvee TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()
initialiser_bdd()

def extraire_logo_base64(chemin_fichier):
    if os.path.exists(chemin_fichier):
        with open(chemin_fichier, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

# --- FONCTION DU ROBOT INTEGRÉ DIRECTEMENT ---
def executer_robot_instantane(pays, métier):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    p_cible = "France" if pays == "Tous" else pays
    m_cible = "Plombier" if métier == "Tous" else métier
    langue = PAYS_LANGUES.get(p_cible, "fr")
    villes = VILLES_MONDE.get(p_cible, ["Paris"])
    mot_traduit = DICTIONNAIRE_MUNDIAL.get(m_cible, {}).get(langue, m_cible.lower())
    
    conn = get_connection()
    c = conn.cursor()
    
    with httpx.Client(headers=headers, follow_redirects=True) as client:
        for ville in villes:
            phrase = f'"je cherche un {mot_traduit}" {ville}' if langue == "fr" else f'"looking for {mot_traduit}" {ville}'
            url = f"https://duckduckgo.com{urllib.parse.quote(phrase)}"
            try:
                res = client.get(url, timeout=5.0)
                if res.status_code == 200:
                    soup = BeautifulSoup(res.text, "html.parser")
                    for body in soup.find_all("div", class_="result__body")[:3]:
                        snippet = body.find("a", class_="result__snippet")
                        lien_h = body.find("a", class_="result__url")
                        if snippet and lien_h:
                            if any(m in snippet.text.lower() for m in EMPREINTES_LANGUES[langue]):
                                c.execute("SELECT id FROM opportunites WHERE lien = ?", (lien_h["href"],))
                                if not c.fetchone():
                                    c.execute("INSERT INTO opportunites (titre, ville, pays, niche, lien) VALUES (?, ?, ?, ?, ?)", (snippet.text[:120]+"...", ville, p_cible, m_cible, lien_h["href"]))
                conn.commit()
            except Exception: pass
    conn.close()

# ==========================================
# UTILISATEURS & SESSION
# ==========================================
if "device_fingerprint" not in st.session_state: st.session_state.device_fingerprint = str(os.getpid())
if "connecte" not in st.session_state: st.session_state.connecte = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "abonnement_actif" not in st.session_state: st.session_state.abonnement_actif = False

def inscrire_utilisateur(email, password, dev_id):
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT id FROM utilisateurs WHERE device_id = ?", (dev_id,))
    if c.fetchone(): conn.close(); return "anti_abuse"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    try:
        c.execute("INSERT INTO utilisateurs (email, password, device_id) VALUES (?, ?, ?)", (email, hashed, dev_id))
        conn.commit(); return "ok"
    except sqlite3.IntegrityError: return "exists"
    finally: conn.close()

def verifier_utilisateur(email, password):
    conn = get_connection(); c = conn.cursor()
    c.execute("SELECT password, Paddle_actif FROM utilisateurs WHERE email = ?", (email,))
    res = c.fetchone(); conn.close()
    # Réparation critique du tuple SQL pour éviter le crash .encode()
    if res and bcrypt.checkpw(password.encode("utf-8"), res[0].encode("utf-8")): return True, bool(res[1])
    return False, False

# ==========================================
# INTERFACE GRAPHIQUE
# ==========================================
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
logo_data = extraire_logo_base64("logo (2).png")
if logo_data: st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="animated-logo">', unsafe_allow_html=True)
else: st.markdown('<div style="font-size:90px; animation: pulse 3s infinite ease-in-out;">🚀</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">ZELIA GLOBAL</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.connecte:
    st.markdown("<h3 style='text-align:center; color:#bbb;'>Détectez vos futurs clients partout dans le monde. Connectez-vous.</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c2:
        tab_login, tab_register = st.tabs(["🔒 Se connecter", "📝 S'inscrire"])
        with tab_login:
            em = st.text_input("Adresse Email", key="l_em")
            pw = st.text_input("Mot de passe", type="password", key="l_pw")
            if st.button("Connexion Immédiate"):
                if em and pw:
                    suc, act = verifier_utilisateur(em, pw)
                    if suc: st.session_state.connecte = True; st.session_state.user_email = em; st.session_state.abonnement_actif = act; st.rerun()
                    else: st.error("Identifiants incorrects.")
        with tab_register:
            em_r = st.text_input("Votre Email", key="r_em")
            pw_r = st.text_input("Créer un mot de passe", type="password", key="r_pw")
            if st.button("Créer mon compte unique"):
                if em_r and pw_r:
                    stat = inscrire_utilisateur(em_r, pw_r, st.session_state.device_fingerprint)
                    if stat == "ok": st.success("🎉 Compte créé ! Connectez-vous sur l'onglet d'à côté.")
                    elif stat == "anti_abuse": st.error("🚨 Un compte existe déjà pour cet appareil.")
                    else: st.error("Email déjà enregistré.")

elif st.session_state.connecte and not st.session_state.abonnement_actif:
    st.warning("🔒 SÉCURITÉ COMPTE : Votre moyen de paiement n'est pas configuré.")
    c1, c2, c3 = st.columns(3)
    with c2:
        code_html = f"""<script src="https://paddle.com"></script><script>Paddle.Initialize({{ token: "{PADDLE_VENDOR_ID}" }});</script><div style="text-align:center;"><button style="background: linear-gradient(135deg, #00A86B 0%, #00FF9D 100%); color: black; padding: 16px 35px; border: none; border-radius: 12px; font-size: 16px; font-weight: bold; cursor: pointer;" onclick='Paddle.Checkout.open({{ items: [{{ priceId: "{PADDLE_PRICE_ID}", quantity: 1 }}], customer: {{ email: "{st.session_state.user_email}" }} }})'>💳 Activer l'accès Premium (Essai 12 jours)</button></div>"""
        components.html(code_html, height=120)
        if st.button("🔄 Rafraîchir mon accès après paiement"):
            conn = get_connection(); c = conn.cursor()
            c.execute("UPDATE utilisateurs SET Paddle_actif = 1 WHERE email = ?", (st.session_state.user_email,))
            conn.commit(); conn.close()
            st.session_state.abonnement_actif = True; st.rerun()

else:
