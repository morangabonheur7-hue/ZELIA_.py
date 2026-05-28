[NICHE]
mots_cles = plombier, fuite, urgence, tuyau, robinet,technicien,electricien par DEFAULT...

[VILLES]
liste = Paris, Lyon, Marseille, Bordeaux
,lodon ect...

import streamlit as st
import sqlite3
import bcrypt
import os
import requests
import streamlit.components.v1 as components

PADDLE_VENDOR_ID = "TON_VENDOR_ID"
PADDLE_PRICE_ID = "TON_PRICE_ID"

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="ZELIA - Sourcing Clients", page_icon="🚀", layout="wide")

# --- INITIALISATION DE LA BASE DE DONNÉES ---
def initialiser_bdd():
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    # Table des utilisateurs
    c.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            Paddle_actif INTEGER DEFAULT 0
        )
    ''')
    # Table des opportunités clients trouvées par le bot
    c.execute('''
        CREATE TABLE IF NOT EXISTS opportunites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            ville TEXT,
            lien TEXT,
            date_trouvee TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

initialiser_bdd()

# --- SESSIONS UTILISATEURS (Streamlit State) ---
if "connecte" not in st.session_state:
    st.session_state.connecte = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "abonnement_actif" not in st.session_state:
    st.session_state.abonnement_actif = False
# --- FONCTIONS UTILES (Gestion des utilisateurs) ---

def inscrire_utilisateur(email, password,):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        c.execute("INSERT INTO utilisateurs (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verifier_utilisateur(email, password,):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT password, PADDLE_actif FROM utilisateurs WHERE email = ?", (email,))
    resultat = c.fetchone()
    conn.close()
    
    if resultat and bcrypt.checkpw(password.encode('utf-8'), resultat[0].encode('utf-8')):
        return True, bool(resultat[1])
    return False, False

def activer_abonnement_bdd(email):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("UPDATE utilisateurs SET stripe_actif = 1 WHERE email = ?", (email,))
    conn.commit()
    conn.close()
def afficher_bouton_paddle(email_user):
    code_html = f"""
    <script src="https://cdn.paddle.com/paddle/paddle.js"></script>

    <script>
        Paddle.Setup({{
            vendor: {PADDLE_VENDOR_ID}
        }});
    </script>

    <button style="
        background:#00A86B;
        color:white;
        padding:15px 25px;
        border:none;
        border-radius:8px;
        font-weight:bold;
    " onclick="Paddle.Checkout.open({{
        product: {PADDLE_PRICE_ID},
        email: '{email_user}'
    }})">
        ⚡ Activer l'essai 12 jours
    </button>
    """

    components.html(code_html, height=200)
    
# --- INTERFACE GRAPHIQUE (UI) ---

# Barre latérale : Connexion / Déconnexion
st.sidebar.title("🔑 Espace Membre")
if not st.session_state.connecte:
    action = st.sidebar.radio("Action", ["Se connecter", "S'inscrire"])
    email_saisi = st.sidebar.text_input("Adresse Email")
    password_saisi = st.sidebar.text_input("Mot de passe", type="password")
    
    if action == "S'inscrire":
        if st.sidebar.button("Créer mon compte"):
            if email_saisi and password_saisi:
                if inscrire_utilisateur(email_saisi, password_saisi):
                    st.sidebar.success("Compte créé ! Connectez-vous maintenant.")
                else:
                    st.sidebar.error("Cet email est déjà utilisé.")
            else:
                st.sidebar.warning("Veuillez remplir tous les champs.")
                
    elif action == "Se connecter":
        if st.sidebar.button("Connexion"):
            succes, actif = verifier_utilisateur(email_saisi, password_saisi)
            if "%" in email_saisi: # Sécurité basique
                st.sidebar.error("Caractères invalides.")
            elif succes:
                st.session_state.connecte = True
                st.session_state.user_email = email_saisi
                st.session_state.abonnement_actif = actif
                st.rerun()
            else:
                st.sidebar.error("Identifiants incorrects.")
else:
    st.sidebar.write(f"Connecté en tant que : **{st.session_state.user_email}**")
    if st.sidebar.button("Se déconnecter"):
        st.session_state.connecte = False
        st.session_state.user_email = ""
        st.session_state.abonnement_actif = False
        st.rerun()

# PAGE PRINCIPALE
st.title("🚀 ZELIA - Chasseur d'Opportunités SaaS")

# Affichage du logo si présent
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.info("💡 Astuce : Ajoutez une image 'logo.png' dans votre dossier pour afficher votre logo ici.")

# Logique des onglets / affichage selon statut
if not st.session_state.connecte:
    # Page d'accueil publique
    st.markdown("""
    ### Trouvez des chantiers et des clients sans lever le petit doigt.
    ZELIA est un robot intelligent qui scanne le web 24h/24 pour extraire les demandes de prospects (plombiers, électriciens, artisans,technicien,electricien,et autres,...).
    
    **Comment ça marche ?**
    1. Créez un compte en quelques secondes dans la barre latérale.
    2. Activez votre abonnement avec **12 jours d'essai gratuit**.
    3. Accédez instantanément à votre tableau de bord de leads qualifiés.
    """)
    elif st.session_state.connecte and not st.session_state.abonnement_actif:
    st.warning("⚠️ Accès requis")

    st.subheader("🚀 ZELIA Pro - Essai 12 jours")

    afficher_bouton_paddle(st.session_state.user_email)
  
    if st.button("Activer mon essai gratuit de 12 jours"):
        if len(carte) > 10: # Vérification fictive pour l'exemple
            activer_abonnement_bdd(st.session_state.user_email)
            st.session_state.abonnement_actif = True
            st.success("Paiement validé par Paddle! Bienvenue chez ZELIA.")
            st.rerun()
        else:
            st.error("Veuillez saisir un numéro de carte valide.")

else:
    # TABLEAU DE BORD PRIVÉ (Abonnement OK)
    st.success("✅ Votre abonnement est actif (Période d'essai en cours).")
    st.subheader("🎯 Vos opportunités clients en temps réel")
    
    # Lecture des données insérées par le robot
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT titre, ville, lien, date_trouvee FROM opportunites ORDER BY date_trouvee DESC")
    donnees = c.fetchall()
    conn.close()
    
    if donnees:
        # Affichage sous forme de tableau propre
        import pandas as pd
        df = pd.DataFrame(donnees, columns=["Mission demandée", "Ville", "Lien de l'annonce", "Découvert le"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Le robot est en cours d'analyse. Les premiers clients apparaîtront ici d'ici une heure.")
        # Bouton de démonstration pour tester l'interface sans attendre le bot
        if st.button("Simulation : Ajouter un client test"):
            conn = sqlite3.connect("clients.db")
            c = conn.cursor()
            c.execute("INSERT INTO opportunites (titre, ville, lien) VALUES (?, ?, ?)", 
                      ("Recherche plombier en urgence pour fuite WC", "Paris", "https://exemple.com"))
            conn.commit()
            conn.close()
            st.rerun()

import streamlit as st
import sqlite3
import bcrypt
import os
import streamlit.components.v1 as components

# --- CONFIGURATION DU DESIGN PREMIUM ---
st.set_page_config(page_title="ZELIA", page_icon="🚀", layout="wide")

# Personnalisation des couleurs via du code CSS injecté (Boutons verts, thèmes épurés)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        background-color: #00A86B !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: bold !important;
    }
    .stButton>button:hover { background-color: #008f5a !important; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 5px solid #00A86B;
    }
    </style>
""", unsafe_index=True)

# --- CONFIGURATION PADDLE ---
PADDLE_VENDOR_ID = "12345"  
PADDLE_PRICE_ID = "pri_0123456789abcdefgh"  

# --- ENREGISTREMENT ET CONFIGURATION DE LA BDD ---
def initialiser_bdd():
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    # Ajout des colonnes pays et langue pour mémoriser les choix par défaut de l'utilisateur
    c.execute('''
        CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            paddle_actif INTEGER DEFAULT 0,
            pays_defaut TEXT DEFAULT 'FR',
            langue_defaut TEXT DEFAULT 'FR'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS opportunites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            ville TEXT,
            lien TEXT,
            pays TEXT DEFAULT 'FR',
            niche TEXT DEFAULT 'plombier',
            date_trouvee TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

initialiser_bdd()

# --- DICTIONNAIRE DE TRADUCTION ---
TRADUCTIONS = {
    "FR": {
        "titre_sidebar": "🔑 Espace Profil",
        "label_email": "Adresse Email",
        "label_password": "Mot de passe",
        "btn_creer": "Créer mon compte",
        "btn_connexion": "Connexion",
        "btn_deconnexion": "Se déconnecter",
        "pitch_titre": "Trouvez des clients sans lever le petit doigt.",
        "pitch_corps": "ZELIA est un robot intelligent qui scanne le web 24h/24 pour extraire les demandes de prospects.",
        "statut_inactif": "⚠️ Votre abonnement n'est pas actif.",
        "paddle_titre": "💳 Activer mon accès ZELIA Pro (12 jours gratuits)",
        "dashboard_titre": "🎯 Vos opportunités clients en temps réel",
        "filtre_pays": "Sélectionnez votre pays cible",
        "reco_message": "💬 Message de prospection généré par ZELIA :",
        "btn_copier": "Copier le message prêt à l'envoi",
        "script_txt": "Bonjour, je viens de voir votre demande pour '{titre}' à {ville}. Je suis disponible immédiatement pour vous aider. Pouvons-nous échanger ? Cordialement.",
        "bot_attente": "Recherche de nouveaux clients en cours pour votre zone..."
    },
    "EN": {
        "titre_sidebar": "🔑 Profile Area",
        "label_email": "Email Address",
        "label_password": "Password",
        "btn_creer": "Create Account",
        "btn_connexion": "Log In",
        "btn_deconnexion": "Log Out",
        "pitch_titre": "Find clients without lifting a finger.",
        "pitch_corps": "ZELIA is an intelligent bot scanning the web 24/7 to extract prospect requests.",
        "statut_inactif": "⚠️ Your subscription is not active.",
        "paddle_titre": "💳 Activate ZELIA Pro Access (12-day free trial)",
        "dashboard_titre": "🎯 Your real-time client opportunities",
        "filtre_pays": "Select your target country",
        "reco_message": "💬 Outreach message generated by ZELIA:",
        "btn_copier": "Copy ready-to-send message",
        "script_txt": "Hello, I just saw your request for '{titre}' in {ville}. I am available immediately to help you. Can we discuss? Best regards.",
        "bot_attente": "Scanning for new clients in your area..."
    }
}

# --- INITIALISATION DES VARIABLES DE SESSION ---
if "langue" not in st.session_state: st.session_state.langue = "FR"
if "connecte" not in st.session_state: st.session_state.connecte = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "abonnement_actif" not in st.session_state: st.session_state.abonnement_actif = False
if "pays_choisi" not in st.session_state: st.session_state.pays_choisi = "FR"

txt = TRADUCTIONS[st.session_state.langue]

# --- FONCTIONS UTILISATEURS ---
def inscrire_utilisateur(email, password, pays, langue):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        c.execute("INSERT INTO utilisateurs (email, password, pays_defaut, langue_defaut) VALUES (?, ?, ?, ?)", 
                  (email, hashed, pays, langue))
        conn.commit()
        return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()

def verifier_utilisateur(email, password):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT password, paddle_actif, pays_defaut, langue_defaut FROM utilisateurs WHERE email = ?", (email,))
    resultat = c.fetchone()
    conn.close()
    if resultat and bcrypt.checkpw(password.encode('utf-8'), resultat[0].encode('utf-8')):
        return True, bool(resultat[1]), resultat[2], resultat[3]
    return False, False, "FR", "FR"

# --- INTERFACE GRAPHIC / BARRE LATÉRALE ---
st.sidebar.title("🌐 Configuration")
langue_choisie = st.sidebar.selectbox("Language / Langue", ["FR", "EN"], index=0 if st.session_state.langue == "FR" else 1)
if langue_choisie != st.session_state.langue:
    st.session_state.langue = langue_choisie
    st.rerun()

st.sidebar.title(txt["titre_sidebar"])
if not st.session_state.connecte:
    action = st.sidebar.radio("Action", ["Se connecter", "S'inscrire"])
    email_saisi = st.sidebar.text_input(txt["label_email"])
    password_saisi = st.sidebar.text_input(txt["label_password"], type="password")
    
    # Choix des préférences par défaut à l'inscription
    pays_inscription = st.sidebar.selectbox("Votre pays par défaut", ["FR", "BE", "UK", "US"])
    
    if action == "S'inscrire" and st.sidebar.button(txt["btn_creer"]):
        if email_saisi and password_saisi:
            if inscrire_utilisateur(email_saisi, password_saisi, pays_inscription, st.session_state.langue):
                st.sidebar.success("Compte créé avec succès !")
            else: st.sidebar.error("Erreur ou email déjà pris.")
    elif action == "Se connecter" and st.sidebar.button(txt["btn_connexion"]):
        succes, actif, p_defaut, l_defaut = verifier_utilisateur(email_saisi, password_saisi)
        if {}: st.sidebar.error("Champs invalides.")
        elif succes:
            st.session_state.connecte = True
            st.session_state.user_email = email_saisi
            st.session_state.abonnement_actif = actif
            st.session_state.pays_choisi = p_defaut
            st.session_state.langue = l_defaut
            st.rerun()
else:
    st.sidebar.write(f"👤 **{st.session_state.user_email}**")
    st.sidebar.write(f"📍 Pays configuré : **{st.session_state.pays_choisi}**")
    if st.sidebar.button(txt["btn_deconnexion"]):
        st.session_state.connecte = False
        st.rerun()

# --- ZONE PRINCIPALE DU SITE ---
st.title("🚀 ZELIA Pro")

if not st.session_state.connecte:
    st.header(txt["pitch_titre"])
    st.write(txt["pitch_corps"])

elif st.session_state.connecte and not st.session_state.abonnement_actif:
    st.warning(txt["statut_inactif"])
    st.markdown(f"### {txt['paddle_titre']}")
    
    code_html_paddle = f"""
    <script src="https://paddle.com"></script>
    <script>Paddle.Setup({{ vendor: {PADDLE_VENDOR_ID} }});</script>
    <a href="#" class="paddle_button" data-price-id="{PADDLE_PRICE_ID}" data-email="{st.session_state.user_email}"
       style="background-color: #00A86B; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block; font-family: sans-serif;">
       ⚡ Commencer l'essai gratuit Pro
    </a>
    """
    components.html(code_html_paddle, height=100)

else:
    # --- INTERFACE PREMIUM RECONNAISSANT LE PAYS DE L'UTILISATEUR ---
    st.header(txt["dashboard_titre"])
    
    # Sélecteur dynamique si l'utilisateur veut changer de pays à la volée
    pays_filtre = st.selectbox(txt["filtre_pays"], ["FR", "BE", "UK", "US"], index=["FR", "BE", "UK", "US"].index(st.session_state.pays_choisi))
    
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    # Chargement uniquement des opportunités correspondant au pays choisi
    c.execute("SELECT titre, ville, lien, id FROM opportunites WHERE pays = ? ORDER BY date_trouvee DESC", (pays_filtre,))
    donnees = c.fetchall()
    conn.close()
    
    if donnees:
        for titre, ville, lien, id_lead in donnees:
            # Création visuelle sous forme de "Cartes" stylisées en CSS
            st.markdown(f"""
                <div class="card">
                    <h4>🛠️ Demandé : {titre}</h4>
                    <p>📍 <b>Ville :</b> {ville} | 🌍 <b>Zone :</b> {pays_filtre}</p>
                    <a href="{lien}" target="_blank" style="color: #00A86B; font-weight: bold;">➡️ Ouvrir l'annonce originale</a>
                </div>
            """, unsafe_html=True)
            
            # --- BLOC MESSAGE PRÉPARÉ (SCRIPT D'APPROCHE AUTOMATIQUE) ---
            with st.expander(txt["reco_message"]):
                # Personnalisation dynamique du texte selon la mission trouvée

# À COLLER À LA TOUTE FIN DE VOTRE FICHIER PYTHON (ex: app.py)
import streamlit as st

def configurer_version_mobile_et_style():
    st.markdown("""
        <head>
            <!-- Ce code force les téléphones à afficher l'application à la bonne taille -->
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        </head>
        <style>
        /* Design Bleu et Noir adapté aux PC et Mobiles */
        .stApp {
            background-color: #0B0F19 !important;
            color: #FFFFFF !important;
        }
        
        /* Boutons larges et tactiles pour les doigts sur téléphone */
        .stButton>button {
            background-color: #1D4ED8 !important;
            color: #FFFFFF !important;
            border: 2px solid #3B82F6 !important;
            font-weight: bold !important;
            font-size: 18px !important; /* Plus grand pour les mobiles */
            border-radius: 10px !important;
            padding: 14px 28px !important; /* Plus d'espace pour cliquer */
            width: 100% !important; /* Occupe toute la largeur sur mobile */
        }
        
        /* Menus d'options très visibles sur petit écran */
        div[data-baseweb="select"] {
            background-color: #1F2937 !important;
            border: 2px solid #3B82F6 !important;
            border-radius: 8px !important;
            min-height: 48px !important; /* Hauteur confortable pour le tactile */
        }
        
        div[data-baseweb="select"] * {
            color: #FFFFFF !important;
            font-size: 16px !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Activation du code
configurer_version_mobile_et_style()
