[NICHE]
mots_cles = plombier, fuite,services, urgence, tuyau, robinet,technicien

[VILLES]
liste = Paris, Lyon, Marseille, Bordeaux,london

import streamlit as st
import sqlite3
import bcrypt
import os

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
            stripe_actif INTEGER DEFAULT 0
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
    c.execute("SELECT password, stripe_actif FROM utilisateurs WHERE email = ?", (email,))
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
    ZELIA est un robot intelligent qui scanne le web 24h/24 pour extraire les demandes de prospects (plombiers, électriciens, artisans...).
    
    **Comment ça marche ?**
    1. Créez un compte en quelques secondes dans la barre latérale.
    2. Activez votre abonnement avec **12 jours d'essai gratuit**.
    3. Accédez instantanément à votre tableau de bord de leads qualifiés.
    """)
    
elif st.session_state.connecte and not st.session_state.abonnement_actif:
    # Tunnel de paiement (Simulation API Stripe)
    st.warning("⚠️ Votre abonnement n'est pas actif.")
    st.subheader("Abonnement ZELIA Pro - 29,99€ / mois")
    st.write("Profitez de 12 jours d'essai gratuit. Annulable à tout moment.")
    
    st.markdown("### 💳 Formulaire de paiement sécurisé (Stripe)")
    carte = st.text_input("Numéro de carte bancaire (Simulation)", placeholder="4242 4242 4242 4242")
    
    if st.button("Activer mon essai gratuit de 12 jours"):
        if len(carte) > 10: # Vérification fictive pour l'exemple
            activer_abonnement_bdd(st.session_state.user_email)
            st.session_state.abonnement_actif = True
            st.success("Paiement validé par Stripe ! Bienvenue chez ZELIA.")
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


import time
import sqlite3
import configparser
import requests
from bs4 import BeautifulSoup

def charger_configuration():
    """Lit le fichier config.txt pour récupérer les mots-clés et les villes."""
    config = configparser.ConfigParser()
    config.read("config.txt", encoding="utf-8")
    
    # Récupération et nettoyage des données
    mots_cles = [m.strip().lower() for m in config.get("NICHE", "mots_cles").split(",")]
    villes = [v.strip().lower() for v in config.get("VILLES", "liste").split(",")]
    
    return mots_cles, villes

def enregistrer_opportunite(titre, ville, lien):
    """Insère une nouvelle opportunité dans la base de données si elle n'existe pas déjà."""
    conn = sqlite3.connect("clients.db")
    c = conn.cursor()
    
    # On vérifie si ce lien exact a déjà été enregistré pour éviter les doublons
    c.execute("SELECT id FROM opportunites WHERE lien = ?", (lien,))
    existe = c.fetchone()
    
    if not existe:
        c.execute("INSERT INTO opportunites (titre, ville, lien) VALUES (?, ?, ?)", (titre, ville, lien))
        conn.commit()
        print(f"[BOT] Nouvelle opportunité ajoutée : {titre} ({ville})")
    
    conn.close()

def scanner_le_web():
    """Simule le scan d'un site d'annonces et filtre selon la configuration."""
    mots_cles, villes = charger_configuration()
    print(f"[BOT] Lancement du scan avec les mots-clés {mots_cles} sur les villes {villes}...")
    
    # --- EXEMPLE DE SCRIPT DE SCRAPING DE BASE ---
    # Pour le lancement, nous utilisons une URL d'exemple. 
    # (À remplacer par l'URL réelle du site d'annonces ciblé, ex: Leboncoin, Travaux.com...)
    url_cible = "https://ycombinator.com" 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    try:
        reponse = requests.get(url_cible, headers=headers, timeout=10)
        if reponse.status_code == 200:
            soup = BeautifulSoup(reponse.text, 'html.parser')
            
            # --- LOGIQUE DE SIMULATION DE RECHERCHE ---
            # Le robot extrait les titres et liens d'un site
            annonces = soup.find_all('tr', class_='athing')
            
            # Pour l'exemple technique, on injecte de fausses annonces correspondantes 
            # afin de valider que les filtres de mots-clés et villes fonctionnent à 100%
            annonces_fictives = [
                {"titre": "Urgence fuite de tuyau dans la cuisine", "ville": "Paris", "lien": "https://annonces.com"},
                {"titre": "Cherche électricien pour salon", "ville": "Lyon", "lien": "https://annonces.com"},
                {"titre": "Remplacement de robinet salle de bain", "ville": "Marseille", "lien": "https://annonces.com"}
            ]
            
            # Analyse et filtrage des annonces trouvées
            for annonce in annonces_fictives:
                titre_minuscule = list(annonce.values())[0].lower()
                ville_minuscule = list(annonce.values())[1].lower()
                
                # Le robot vérifie si la ville ET un mot-clé match avec config.txt
                match_mot = any(mot in titre_minuscule for mot in mots_cles)
                match_ville = any(ville in ville_minuscule for ville in villes)
                
                if match_mot and match_ville:
                    enregistrer_opportunite(annonce["titre"], list(annonce.values())[1], list(annonce.values())[2])
                    
        else:
            print(f"[BOT] Erreur serveur : Code {reponse.status_code}")
    except Exception as e:
        print(f"[BOT] Erreur lors du scan : {e}")

# --- BOUCLE PRINCIPALE (While True) ---
if __name__ == "__main__":
    print("[BOT] ZELIA Surveillance est activé et tourne en arrière-plan.")
    while True:
        scanner_le_web()
        
        # Pause de 1 heure (3600 secondes) avant le prochain scan
        print("[BOT] Scan terminé. Prochaine vérification dans 1 heure...")
        time.sleep(3600)
