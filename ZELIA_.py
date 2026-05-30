import streamlit as st
import sqlite3
import bcrypt
import os
import base64
import pandas as pd
import httpx
import urllib.parse
import time
from bs4 import BeautifulSoup
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import streamlit.components.v1 as components

# ==========================================
# CONFIGURATION DE LA PAGE
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL - Sourcing Haute Précision", page_icon="🚀", layout="wide")

# ==========================================
# INITIALISATION DE L'ÉTAT DE LA SESSION (SESSION STATE)
# ==========================================
if "authentifie" not in st.session_state:
    st.session_state.authentifie = False
if "email_utilisateur" not in st.session_state:
    st.session_state.email_utilisateur = None
if "est_premium" not in st.session_state:
    st.session_state.est_premium = False
if "langue" not in st.session_state:
    st.session_state.langue = "fr"
if "leads_detectes" not in st.session_state:
    st.session_state.leads_detectes = []

# ==========================================
# CONSTANTES & CONFIGURATION PADDLE
# ==========================================
PRIX_ABONNEMENT = "29.99€ / mois"
PADDLE_VENDOR_ID = "345487"  
PADDLE_PRICE_ID = "pri_01ksk58k14szw6a8dys7y7as0r"  

TRADUCTIONS = {
    "fr": {
        "titre_principal": "ZELIA GLOBAL",
        "sous_titre": "Le robot d'IA qui détecte vos chantiers toutes les 5 minutes.",
        "label_pays": "🌍 Pays cible",
        "label_ville": "🏙️ Ville ou zone exacte (Ex: Paris, Lyon, Marseille)",
        "label_niche": "🛠️ Corps de métier",
        "label_bouton": "⚡ Activer la Surveillance Automatique (Toutes les 5 min)",
        "recherche_en_cours": "🤖 Le robot ZELIA infiltre le web pour vos zones cibles...",
        "scan_termine": "✅ Scan initial réussi ! Surveillance continue activée.",
        "titre_tableau": "📈 Flux de Chantiers Détectés en Temps Réel",
        "aucun_resultat": "💡 En attente du prochain scan de 5 minutes ou modifiez votre zone.",
        "connexion": "🔒 Connexion Membre",
        "inscription": "📝 S'inscrire au Club",
        "email": "Adresse Email Professionnelle",
        "password": "Mot de passe sécurisé",
        "btn_connecter": "Se connecter",
        "btn_inscrire": "Créer mon compte",
        "deconnexion": "🚪 Fermer la session",
        "statut": "Statut : Artisan Premium - ",
        "export": "📥 Exporter les leads au format CSV",
        "payer_bouton": "💳 Activer mon Accès Premium - 29,99€",
        "bloque_paiement": "⚠️ Votre abonnement est expiré ou inactif. Veuillez régulariser ci-dessous.",
        "msg_auto": "📝 Message Automatique Généré"
    },
    "en": {
        "titre_principal": "ZELIA GLOBAL",
        "sous_titre": "The AI bot tracking your next contracts every 5 minutes.",
        "label_pays": "🌍 Target Country",
        "label_ville": "🏙️ Enter exact city or zone (e.g., London, New York)",
        "label_niche": "🛠️ Trade / Niche",
        "label_bouton": "⚡ Activate Automatic Surveillance (Every 5 min)",
        "recherche_en_cours": "🤖 ZELIA bot is crawling the web for your specific areas...",
        "scan_termine": "✅ Initial scan successful! Continuous tracking active.",
        "titre_tableau": "📈 Real-Time Live Lead Stream",
        "aucun_resultat": "💡 Waiting for the next 5-minute automated crawl...",
        "connexion": "🔒 Premium Login",
        "inscription": "📝 Register",
        "email": "Professional Email Address",
        "password": "Password",
        "btn_connecter": "Login",
        "btn_inscrire": "Create Account",
        "deconnexion": "🚪 Logout",
        "statut": "Status: Premium Member - ",
        "export": "📥 Export Leads to CSV",
        "payer_bouton": "💳 Unlock Premium Access - 29.99€",
        "bloque_paiement": "⚠️ Your subscription is inactive. Please complete payment below.",
        "msg_auto": "📝 Generated Pitch Message"
    }
}

DICTIONNAIRE_MUNDIAL = {
    "Plombier": {"fr": "plombier", "en": "plumber"},
    "Électricien": {"fr": "electricien", "en": "electrician"},
    "Mécanicien": {"fr": "mecanicien", "en": "mechanic"},
    "Menuisier": {"fr": "menuisier", "en": "carpenter"},
    "Serrurier": {"fr": "serrurier", "en": "locksmith"},
    "Peintre": {"fr": "peintre", "en": "painter"},
    "Maçon": {"fr": "maçon", "en": "mason"}
}

PAYS_LANGUES = {"France": "fr", "Belgique": "fr", "Canada": "en", "Royaume-Uni": "en", "États-Unis": "en"}

# ==========================================
# DESIGN ET STYLE PREMIUM HAUTE VALEUR
# ==========================================
st.markdown("""
<style>
.logo-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 20px 0px; }
.animated-logo { width: 400px; height: auto; animation: pulse 2.5s infinite ease-in-out; border-radius: 28px; box-shadow: 0px 25px 70px rgba(0, 210, 120, 0.6); }
@keyframes pulse {
    0% { transform: scale(1); box-shadow: 0px 25px 70px rgba(0, 210, 120, 0.4); }
    50% { transform: scale(1.03); box-shadow: 0px 35px 90px rgba(0, 210, 120, 0.8); }
    100% { transform: scale(1); box-shadow: 0px 25px 70px rgba(0, 210, 120, 0.4); }
}
.main-title { font-size: 60px !important; font-weight: 900; background: linear-gradient(135deg, #00FF9D, #00A86B); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 20px; letter-spacing: 4px; }
div.stButton > button { background: linear-gradient(135deg, #00FF9D 0%, #007d50 100%) !important; color: #022013 !important; font-weight: 800 !important; border-radius: 14px !important; border: none !important; padding: 16px 32px !important; width: 100%; font-size: 18px !important; text-transform: uppercase; transition: all 0.3s ease; }
div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0px 12px 30px rgba(0, 255, 157, 0.5); color: white !important; }
.welcome-overlay { padding: 40px; background: radial-gradient(circle, rgba(0,255,157,0.15) 0%, rgba(0,125,80,0.05) 100%); border: 2px dashed #00FF9D; border-radius: 20px; text-align: center; margin-bottom: 30px; }
.lead-card { background: #111; padding: 20px; border-radius: 14px; border-left: 5px solid #00FF9D; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# BASE DE DONNÉES
# ==========================================
DB_NAME = "zelia_premium.db"

def get_connection(): 
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def initialiser_bdd():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS utilisateurs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        email TEXT UNIQUE, 
                        password TEXT, 
                        device_id TEXT, 
                        Paddle_actif INTEGER DEFAULT 0)""")
        c.execute("""CREATE TABLE IF NOT EXISTS opportunites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        titre TEXT, 
                        ville TEXT, 
                        pays TEXT, 
                        niche TEXT, 
                        lien TEXT UNIQUE, 
                        date_trouvee TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()

initialiser_bdd()

def extraire_logo_base64(chemin_fichier):
    if os.path.exists(chemin_fichier):
        with open(chemin_fichier, "rb") as f: 
            return base64.b64encode(f.read()).decode()
    return None

# ==========================================
# ROBOT DE RECHERCHE CHRONO 5 MINUTES
# ==========================================
def executer_scan_moteur(pays, metier, ville_saisie):
    if not ville_saisie:
        return []
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"
    }
    
    langue = PAYS_LANGUES.get(pays, "fr")
    mot_traduit = DICTIONNAIRE_MUNDIAL.get(metier, {}).get(langue, metier.lower())
    
    query_str = f"offre chantier {mot_traduit} {ville_saisie}" if langue == "fr" else f"need {mot_traduit} contract {ville_saisie}"
    url = f"https://duckduckgo.com{urllib.parse.quote(query_str)}"
    
    nouvelles_opportunites = []
    
    try:
        with httpx.Client(headers=headers, follow_redirects=True, timeout=15.0) as client:
            res = client.get(url)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # DuckDuckGo HTML utilise la classe 'result__a' pour les liens de résultats
                liens = soup.find_all("a", class_="result__a")
                
                with get_connection() as conn:
                    c = conn.cursor()
                    for l in liens:
                        titre = l.get_text(strip=True)
                        lien_brut = l.get("href", "")
                        
                        # Nettoyage des redirections DuckDuckGo si nécessaire
                        if "uddg=" in lien_brut:
                            partie = lien_brut.split("uddg=")[1]
                            lien_reel = urllib.parse.unquote(partie.split("&")[0])
                        else:
                            lien_reel = lien_brut

                        if lien_reel and not lien_reel.startswith("/"):
                            try:
                                c.execute("""INSERT INTO opportunites (titre, ville, pays, niche, lien) 
                                             VALUES (?, ?, ?, ?, ?)""", (titre, ville_saisie, pays, metier, lien_reel))
                                conn.commit()
