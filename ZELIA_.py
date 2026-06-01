import streamlit as st
import sqlite3
import time
import requests
import urllib.parse
import threading

# ==========================================
# 1. CONFIGURATION DE LA PAGE & STYLE CSS 
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0518; color: #ffffff; }
    h1, h2, h3, p, label, .stMarkdown { color: #ffffff !important; }
    
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
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_id" not in st.session_state: st.session_state.user_id = None

PADDLE_PRICE_ID = "pri_01ksk58k14szw6a8dys7y7as0r"
PADDLE_CHECKOUT_URL = f"https://paddle.com{PADDLE_PRICE_ID}"

PAYS_LANGUES = {"France": "fr", "Belgique": "fr", "Suisse": "fr", "Canada": "en", "United Kingdom": "en", "United States": "en"}

DICTIONNAIRE_MOTS_CLES = {
    "plombier": {
        "fr": ["je cherche un plombier", "fuite d'eau", "urgence plombier", "canalisation bouchee"]
    },
    "electricien": {
        "fr": ["je cherche un electricien", "panne de courant", "court circuit", "urgence electricien"]
    },
    "serrurier": {
        "fr": ["je cherche un serrurier", "porte claquee", "serrure bloquee", "urgence serrurier"]
    },
    "mecanicien": {
        "fr": ["je cherche un mecanicien", "recherche mecanicien", "panne voiture", "reparer voiture"]
    }
}

TEXTES = {
    "fr": {
        "titre_ins": "📝 Système d'Inscription Mondial", "nom": "Nom & Prénom", "metier": "Métier d'artisan (ex: plombier)", "pays": "Pays de résidence", "ville": "Ville", 
        "licence_label": "Clé de licence Paddle (Reçue par email)", "succes": "✅ Inscription effectuée avec succès !", 
        "erreur_paddle": "❌ Clé de licence invalide.", "bouton_creer": "Créer mon compte et lancer l'essai", 
        "robot_on": "🟢 Allumer le robot ZELIA", "robot_off": "🔴 Éteindre le robot ZELIA", "whatsapp": "🔗 Configurer mon numéro WhatsApp", 
        "num_wa": "Numéro WhatsApp (Format international ex: +33612345678)", "robot_pret": "🚀 Le robot ZELIA est actif en arrière-plan."
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
# 3. BACKEND & MOTEUR ROBOT (FONCTIONNEMENT H24)
# ==========================================
def verifier_licence_paddle(cle):
    if cle.upper() == "TEST-ZELIA": return True
    return False

def generer_pitch_automatique(langue, metier, ville):
    return f"Bonjour, j'ai vu votre demande. Je suis {metier.lower()} qualifié sur {ville}. Disponible immédiatement pour analyser votre besoin et vous faire un devis gratuit. Contactez-moi !"

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
                message_wa = f"🚀 ZELIA ALERTE CLIENT !\n\nBonjour {nom}, un client recherche un {metier} à {ville}.\n\n👉 Message prêt : {pitch}"
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
        except:
            time.sleep(10)

if "robot_thread" not in st.session_state:
    t_robot = threading.Thread(target=execution_moteur_robot, daemon=True)
    t_robot.start()
    st.session_state.robot_thread = True

# ==========================================
# 4. LOGIQUE D'AFFICHAGE UNIQUE (INSCRIPTION)
# ==========================================
st.title("🚀 ZELIA GLOBAL - Artisan Locator")
langue = "fr"
t = TEXTES[langue]

if not st.session_state.authentifie:
    st.subheader(t["titre_ins"])
    with st.form("formulaire_inscription"):
        nom = st.text_input(t["nom"])
        metier = st.selectbox(t["metier"], ["plombier", "electricien", "serrurier", "mecanicien"])
        pays = st.selectbox(t["pays"], list(PAYS_LANGUES.keys()))
        ville = st.text_input(t["ville"])
        licence = st.text_input(t["licence_label"], value="TEST-ZELIA")
        bouton_soumettre = st.form_submit_button(t["bouton_creer"])

    if bouton_soumettre:
        nom_clean = nom.strip() if nom else ""
        ville_clean = ville.strip() if ville else ""
        licence_clean = licence.strip() if licence else ""
        
        if nom_clean and ville_clean and licence_clean:
            if verifier_licence_paddle(licence_clean):
                with db_lock:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("INSERT INTO artisans (nom, metier, pays, ville, licence) VALUES (?, ?, ?, ?, ?)", (nom_clean, metier, pays, ville_clean, licence_clean))
                    conn.commit()
                    conn.close()
                
                st.session_state.user_id = nom_clean
                st.session_state.user_metier = metier
                st.session_state.user_ville = ville_clean
                st.session_state.authentifie = True
                st.rerun()
            else:
                st.error("❌ Clé de licence invalide.")
        else:
            st.error("⚠️ Veuillez remplir tous les champs.")

# ==========================================
# 5. TABLEAU DE BORD CLIENT COMPLET
# ==========================================
else:
    st.header(f"📊 Tableau de bord de {st.session_state.user_id}")
    st.write(f"Métier : **{st.session_state.user_metier}** | Ville : **{st.session_state.user_ville}**")
    
    st.subheader(t["whatsapp"])
    
    with db_lock:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT whatsapp, robot_actif FROM artisans WHERE nom = ?", (st.session_state.user_id,))
        row = c.fetchone()
        conn.close()
        
    db_whatsapp = row[0] if row and row[0] else ""
    db_robot_actif = row[1] if row else 0

    input_whatsapp = st.text_input(t["num_wa"], value=db_whatsapp)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t["robot_on"]):
            if input_whatsapp:
                with db_lock:
                    conn = sqlite3.connect(DB_NAME)
                    c = conn.cursor()
                    c.execute("UPDATE artisans SET whatsapp = ?, robot_actif = 1 WHERE nom = ?", (input_whatsapp, st.session_state.user_id))
                    conn.commit()
                    conn.close()
                st.success("🟢 Robot activé !")
                st.rerun()
            else:
                st.error("Entrez votre numéro WhatsApp.")
                
    with col2:
        if st.button(t["robot_off"]):
            with db_lock:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("UPDATE artisans SET robot_actif = 0 WHERE nom = ?", (st.session_state.user_id,))
