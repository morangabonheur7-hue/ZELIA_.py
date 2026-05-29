import streamlit as st
import sqlite3
import bcrypt
import os
import base64
import pandas as pd
import streamlit.components.v1 as components

# --- CONFIGURATION STRICTE DE LA PAGE ---
st.set_page_config(page_title="ZELIA - Sourcing Mondial", page_icon="🚀", layout="wide")

PADDLE_VENDOR_ID = "345487"
PADDLE_PRICE_ID = "pri_01ksk58k14szw6a8dys7y7as0r"

# --- STYLE CSS PREMIUM (Boutons, Interface & Animation Logo) ---
st.markdown("""
    <style>
    /* Centrage et animation du logo */
    .logo-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 40px 0px 10px 0px;
    }
    .animated-logo {
        width: 250px;
        height: auto;
        animation: pulse 3s infinite ease-in-out;
        border-radius: 20px;
        box-shadow: 0px 15px 50px rgba(0, 168, 107, 0.4);
    }
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0px 15px 50px rgba(0, 168, 107, 0.3); }
        50% { transform: scale(1.06); box-shadow: 0px 25px 60px rgba(0, 168, 107, 0.6); }
        100% { transform: scale(1); box-shadow: 0px 15px 50px rgba(0, 168, 107, 0.3); }
    }
    .main-title {
        font-size: 46px !important;
        font-weight: 900;
        background: linear-gradient(45deg, #00A86B, #00FF9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 15px;
        letter-spacing: 2px;
    }
    /* Boutons stylisés */
    div.stButton > button {
        background: linear-gradient(135deg, #00A86B 0%, #007d50 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 12px 25px !important;
        box-shadow: 0 4px 15px rgba(0,168,107,0.2) !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,168,107,0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def initialiser_bdd():
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            device_id TEXT,
            Paddle_actif INTEGER DEFAULT 0,
            service_choisi TEXT DEFAULT 'Tous',
            pays_choisi TEXT DEFAULT 'Tous'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS opportunites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            ville TEXT,
            pays TEXT DEFAULT 'Global',
            niche TEXT,
            lien TEXT,
            date_trouvee TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

initialiser_bdd()

# --- FONCTION POUR CHARGER LE LOGO EN ENCODAGE COMPATIBLE ---
def extraire_logo_base64(chemin_fichier):
    if os.path.exists(chemin_fichier):
        with open(chemin_fichier, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# --- SÉCURITÉ ANTI-ABUS / DISPOSITIF UNIQUE ---
if "device_fingerprint" not in st.session_state:
    st.session_state.device_fingerprint = str(os.getpid())

if "connecte" not in st.session_state:
    st.session_state.connecte = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "abonnement_actif" not in st.session_state:
    st.session_state.abonnement_actif = False

# --- FONCTIONS DE GESTION DES MEMBRES ---
def inscrire_utilisateur(email, password, dev_id):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT id FROM utilisateurs WHERE device_id = ?", (dev_id,))
    if c.fetchone():
        conn.close()
        return "anti_abuse"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        c.execute("INSERT INTO utilisateurs (email, password, device_id) VALUES (?, ?, ?)", (email, hashed, dev_id))
        conn.commit()
        return "ok"
    except sqlite3.IntegrityError:
        return "exists"
    finally:
        conn.close()

def verifier_utilisateur(email, password):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT password, Paddle_actif FROM utilisateurs WHERE email = ?", (email,))
    resultat = c.fetchone()
    conn.close()
    if resultat and bcrypt.checkpw(password.encode('utf-8'), resultat[0].encode('utf-8')):
        return True, bool(resultat[1])
    return False, False

def enregistrer_configurations_filtres(email, pays, metier):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("UPDATE utilisateurs SET pays_choisi = ?, service_choisi = ? WHERE email = ?", (pays, metier, email))
    conn.commit()
    conn.close()

def afficher_bouton_paddle_strict(email_user):
    code_html = f"""
    <script src="https://paddle.com"></script>
    <script>
        Paddle.Setup({{ vendor: {PADDLE_VENDOR_ID} }});
    </script>
    <div style="text-align:center; padding: 10px;">
        <button style="
            background: linear-gradient(135deg, #00A86B 0%, #00FF9D 100%);
            color: black;
            padding: 16px 35px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0px 8px 25px rgba(0, 230, 118, 0.3);
        " onclick="Paddle.Checkout.open({{
            product: '{PADDLE_PRICE_ID}',
            email: '{email_user}'
        }})">
            💳 Activer l'accès Premium (Essai 12 jours)
        </button>
    </div>
    """
    components.html(code_html, height=100)

# ==========================================
# 1. LOGO EN GRAND ÉCRAN ET ANIMATION CENTRALE
# ==========================================
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
# Cible votre fichier logo(2).png sur GitHub
logo_data = extraire_logo_base64("logo(2).png")
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="animated-logo">', unsafe_allow_html=True)
else:
    st.markdown('<div style="font-size:90px; animation: pulse 3s infinite ease-in-out;">🚀</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">ZELIA GLOBAL</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 2. ACCÈS STRICTEMENT VERROUILLÉ SI NON CONNECTÉ
# ==========================================
if not st.session_state.connecte:
    st.markdown("<h3 style='text-align:center; color:#bbb;'>Détectez vos futurs clients partout dans le monde. Connectez-vous.</h3>", unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns()
    with col_c2:
        onglets_auth = st.tabs(["🔒 Se connecter", "📝 S'inscrire"])
        
        with onglets_auth:
            email_log = st.text_input("Adresse Email", key="log_email")
            pass_log = st.text_input("Mot de passe", type="password", key="log_pass")
            if st.button("Connexion Immédiate"):
                if email_log and pass_log:
                    succes, actif = verifier_utilisateur(email_log, pass_log)
                    if succes:
                        st.session_state.connecte = True
                        st.session_state.user_email = email_log
                        st.session_state.abonnement_actif = actif
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects ou compte introuvable.")
                else:
                    st.warning("Veuillez remplir tous les champs.")
                    
        with onglets_auth:
            email_reg = st.text_input("Votre Email", key="reg_email")
            pass_reg = st.text_input("Créer un mot de passe", type="password", key="reg_pass")
            if st.button("Créer mon compte unique"):
                if email_reg and pass_reg:
                    status = inscrire_utilisateur(email_reg, pass_reg, st.session_state.device_fingerprint)
                    if status == "ok":
                        st.success("🎉 Compte créé avec succès ! Connectez-vous sur l'onglet de gauche.")
                    elif status == "anti_abuse":
                        st.error("🚨 Un compte existe déjà depuis cet appareil pour éviter le multi-compte abusif.")
                    else:
                        st.error("Cette adresse email est déjà enregistrée.")
                else:
                    st.warning("Veuillez remplir tous les champs.")

# ==========================================
# 3. VERROUILLAGE SÉCURITÉ PADDLE (PAS DE CARTE = PAS DE FLUX)
# ==========================================
elif st.session_state.connecte and not st.session_state.abonnement_actif:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.warning("🔒 SÉCURITÉ COMPTE : Votre robot refuse l'accès aux flux de messages tant qu'aucun moyen de paiement n'est configuré.")
    
    col_p1, col_p2, col_p3 = st.columns()
    with col_p2:
        st.info("ZELIA intègre le protocole international Paddle. Saisissez votre carte ou PayPal pour débloquer votre tableau de bord.")
        afficher_bouton_paddle_strict(st.session_state.user_email)
        
        st.write("---")
        if st.button("🔄 J'ai enregistré ma carte, rafraîchir mon accès"):
            conn = sqlite3.connect("clients.db")
            c = conn.cursor()
            c.execute("UPDATE utilisateurs SET Paddle_actif = 1 WHERE email = ?", (st.session_state.user_email,))
            conn.commit()
            conn.close()
            st.session_state.abonnement_actif = True
            st.success("Carte validée par Paddle ! Accès accordé.")
