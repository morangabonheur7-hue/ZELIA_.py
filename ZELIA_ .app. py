import streamlit as st
import sqlite3
import bcrypt
import os
import pandas as pd
import streamlit.components.v1 as components

# --- CONFIGURATION INITIALE DE ZELIA ---
# [NICHE]
# mots_cles = "plombier", "fuite", "urgence", "tuyau", "robinet", "technicien", "electricien" par DEFAULT...
# [VILLES]
# liste = "Paris", "Lyon", "Marseille", "Bordeaux", "London" ect...

PADDLE_VENDOR_ID = "345487"
PADDLE_PRICE_ID = "pri_01ksk58k14szw6a8dys7y7as0r"

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
def inscrire_utilisateur(email, password):
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

def verifier_utilisateur(email, password):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT password, Paddle_actif FROM utilisateurs WHERE email = ?", (email,))
    resultat = c.fetchone()
    conn.close()
    
    if resultat and bcrypt.checkpw(password.encode('utf-8'), resultat[0].encode('utf-8')):
        return True, bool(resultat[1])
    return False, False

def activer_abonnement_bdd(email):
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("UPDATE utilisateurs SET Paddle_actif = 1 WHERE email = ?", (email,))
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
        cursor:pointer;
    " onclick="Paddle.Checkout.open({{
        product: '{PADDLE_PRICE_ID}',
        email: '{email_user}'
    }})">
        ⚡ Activer l'essai 12 jours avec Paddle
    </button>
    """
    components.html(code_html, height=100)
    
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
            if "%" in email_saisi:
                st.sidebar.error("Caractères invalides.")
            else:
                succes, actif = verifier_utilisateur(email_saisi, password_saisi)
                if succes:
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

# Affichage du logo
if os.path.exists("logo.png"):
    st.image("logo.png", width=150)
else:
    st.info("💡 Astuce : Ajoutez une image 'logo.png' dans votre dossier pour afficher votre logo ici.")

# Logique d'affichage selon le statut de connexion et de paiement
if not st.session_state.connecte:
    st.markdown("""
    ### Trouvez des chantiers et des clients sans lever le petit doigt.
    ZELIA est un robot intelligent qui scanne le web 24h/24 pour extraire les demandes de prospects (plombiers, électriciens, artisans, techniciens, et autres...).
    
    **Comment ça marche ?**
    1. Créez un compte en quelques secondes dans la barre latérale.
    2. Activez votre abonnement avec **12 jours d'essai gratuit**.
    3. Accédez instantanément à votre tableau de bord de leads qualifiés.
    """)

elif st.session_state.connecte and not st.session_state.abonnement_actif:
    st.warning("⚠️ Accès requis")
    st.subheader("🚀 ZELIA Pro - Essai 12 jours")
    
    st.write("Cliquez ci-dessous pour finaliser votre abonnement d'essai sécurisé via notre partenaire Paddle :")
    afficher_bouton_paddle(st.session_state.user_email)
  
    st.write("---")
    st.write("🔄 *Une fois le paiement effectué via le bouton Paddle ci-dessus, cliquez sur le bouton ci-dessous pour activer votre tableau de bord.*")
    if st.button("Valider et Activer mon accès"):
        activer_abonnement_bdd(st.session_state.user_email)
        st.session_state.abonnement_actif = True
        st.success("Accès activé ! Bienvenue chez ZELIA.")
        st.rerun()

else:
    # TABLEAU DE BORD PRIVÉ (Abonnement OK)
    st.success("✅ Votre abonnement est actif (Période d'essai en cours).")
    st.subheader("🎯 Vos opportunités clients en temps réel")
    
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    c.execute("SELECT titre, ville, lien, date_trouvee FROM opportunites ORDER BY date_trouvee DESC")
    donnees = c.fetchall()
    conn.close()
    
    if donnees:
        df = pd.DataFrame(donnees, columns=["Mission demandée", "Ville", "Lien de l'annonce", "Découvert le"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Le robot est en cours d'analyse. Les premiers clients apparaîtront ici d'ici une heure.")
        
        if st.button("Simulation : Ajouter un client test"):
            conn = sqlite3.connect("clients.db")
            c = conn.cursor()
            c.execute("INSERT INTO opportunites (titre, ville, lien) VALUES (?, ?, ?)", 
                      ("Recherche plombier en urgence pour fuite WC", "Paris", "https://exemple.com"))
            conn.commit()
            conn.close()
            st.rerun()

