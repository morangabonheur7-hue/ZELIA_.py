import streamlit as st
import time
import requests
import urllib.parse

# ==========================================
# 1. CONFIGURATION DE LA PAGE & INFRASTRUCTURE
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

# Intégration stricte et définitive de tes clés réelles
PADDLE_API_KEY = "pdl_live_apikey_01ktezxq12q0j88mtc9ven94xz_QPM2hzX6pBWRDRarmvTS9W_A0Y"
SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1d2twcmZvd2diaW10Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA3NjAyNDksImV4cCI6MjA5NjMzNjI0OX0.rA17-omiRtXuECi0b7RW8wNe583Qa8swoV1HrgcQ9wM"

# Initialisation de la mémoire de session (Anti-bug si l'artisan actualise sa page)
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_metier" not in st.session_state: st.session_state.user_metier = "plombier"
if "user_ville" not in st.session_state: st.session_state.user_ville = ""
if "whatsapp_num" not in st.session_state: st.session_state.whatsapp_num = ""
if "robot_actif" not in st.session_state: st.session_state.robot_actif = False

# URL générée à partir de ton Price ID Paddle pour encaisser les abonnements
PADDLE_CHECKOUT_URL = "https://paddle.com"

# ==========================================
# 2. SYSTÈME DE SÉCURITÉ PADDLE (ANTI-TRICHE)
# ==========================================
def verifier_statut_abonnement_paddle(email):
    """ Interroge l'API de Paddle pour vérifier si cet email a un abonnement actif """
    # Compte de secours secret pour te permettre de tester toi-même depuis le Congo
    if email.lower() == "test@zelia.com":
        return True, "active"
        
    if not PADDLE_API_KEY:
        return False, "Configuration système incomplète (Clé API Paddle manquante)"
        
    try:
        # Requête officielle Paddle API v3
        url = f"https://paddle.com{email}"
        headers = {"Authorization": f"Bearer {PADDLE_API_KEY}"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            donnees = response.json().get("data", [])
            if len(donnees) > 0:
                return True, "active"
            return False, "Aucun abonnement actif trouvé pour cet e-mail"
    except Exception as e:
        return False, f"Erreur de communication avec le processeur de paiement : {str(e)}"
        
    return False, "Abonnement invalide ou expiré"

# ==========================================
# 3. INTERCONNEXION AVEC LA BASE SUPABASE
# ==========================================
def extraire_les_clients_de_la_base(metier, ville):
    """ Va lire en temps réel les clients injectés par le robot dans Supabase """
    url = f"{SUPABASE_URL}/rest/v1/leads?metier=eq.{metier.lower()}&ville=ilike.*{ville.strip()}*&order=created_at.desc&limit=20"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Erreur de synchronisation avec la base de données : {str(e)}")
        
    return []

def generer_pitch_commercial(metier, ville):
    return f"Bonjour, j'ai vu votre demande. Je suis {metier.lower()} qualifié sur {ville}. Disponible immédiatement pour analyser votre besoin et vous faire un devis gratuit. Contactez-moi !"

# ==========================================
# 4. DESIGN DE L'INTERFACE UTILISATEUR (UI)
# ==========================================
st.title("🚀 ZELIA GLOBAL — Artisan Lead Locator")

# 🖥️ ÉCRAN A : FORMULAIRE DE CONNEXION DU CLIENT ARTISAN
if not st.session_state.authentifie:
    st.subheader("🔐 Connexion sécurisée à l'infrastructure Zelia")
    st.markdown(f"🆕 Pas encore abonné ? [👉 Cliquez ici pour démarrer vos 12 jours d'essai gratuit sur Paddle]({PADDLE_CHECKOUT_URL})")
    st.write("---")
    
    with st.form("formulaire_authentification_artisan"):
        email_saisi = st.text_input("Saisissez l'adresse E-mail utilisée sur Paddle", placeholder="artisan@exemple.fr")
        metier_saisi = st.selectbox("Votre corps de métier", ["plombier", "electricien", "serrurier", "mecanicien"])
        ville_saisie = st.text_input("Votre Ville principale d'intervention (ex: Paris)")
        bouton_validation = st.form_submit_button("Vérifier mes droits et ouvrir mon espace privé 🔑")

    if bouton_validation:
        email_clean = email_saisi.strip().lower() if email_saisi else ""
        ville_clean = ville_saisie.strip() if ville_saisie else ""
        
        if email_clean and ville_clean:
            with st.spinner("Analyse de vos droits d'accès auprès de Paddle..."):
                autorisation_accordee, message_statut = verifier_statut_abonnement_paddle(email_clean)
                
                if autorisation_accordee:
                    st.session_state.user_email = email_clean
                    st.session_state.user_metier = metier_saisi
                    st.session_state.user_ville = ville_clean
                    st.session_state.authentifie = True
                    st.success("✅ Accès autorisé ! Redirection vers votre tableau de bord...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ Accès refusé : {message_statut}")
        else:
            st.error("⚠️ Veuillez remplir tous les champs (Email et Ville) pour vous connecter.")

# 🖥️ ÉCRAN B : LE TABLEAU DE BORD PRIVÉ (UNE FOIS CONNECTÉ)
else:
    st.header(f"📊 Espace Client : {st.session_state.user_email}")
    st.write(f"💼 Métier : **{st.session_state.user_metier.upper()}** | 📍 Zone de veille : **{st.session_state.user_ville}**")
    st.write("---")
    
    st.subheader("⚙️ Automatisation de vos notifications")
    input_wa = st.text_input("Votre numéro WhatsApp International (Optionnel — ex: 33612345678)", value=st.session_state.whatsapp_num, placeholder="Laissez vide pour consulter uniquement sur le site")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Activer le flux en direct", use_container_width=True):
            st.session_state.whatsapp_num = input_wa.strip()
            st.session_state.robot_actif = True
            st.rerun()
    with col2:
        if st.button("🔴 Mettre le flux en pause", use_container_width=True):
            st.session_state.robot_actif = False
            st.rerun()
            
    st.write("---")
    st.subheader("📬 Clients chauds détectés par le robot (Mis à jour toutes les 5 min)")
    
    if st.session_state.robot_actif:
        st.success(f"🔄 Le système écoute le web pour vous. Les demandes urgentes à **{st.session_state.user_ville}** s'affichent ci-dessous.")
    else:
        st.warning("⏸️ Le flux en direct est en pause. Activez-le pour charger les nouveaux chantiers.")

    # Lecture immédiate des données stockées dans Supabase par le robot
    liste_clients = extraire_les_clients_de_la_base(st.session_state.user_metier, st.session_state.user_ville)
    
    if liste_clients:
        # CORRECTIONS COMPLÈTE DE LA LIGNE DE BOUCLE POUR ÉVITER LE NAMEERROR
        for idx, client in enumerate(liste_clients):
            with st.container():
                st.markdown(f"### 📍 Opportunité ({client.get('plateforme', 'Web Source')})")
                st.write(client.get("texte", "Aucun détail disponible."))
                
                # Gestion de la redirection vers le client
                lien_final = client.get("lien", "https://google.com")
                
                # Si l'artisan souhaite utiliser son WhatsApp pour répondre rapidement
                if st.session_state.whatsapp_num and "whatsapp.com" not in lien_final:
                    pitch_wa = f"Bonjour, je vous contacte suite à votre demande urgente de {st.session_state.user_metier} sur {st.session_state.user_ville}..."
                    lien_final = f"https://whatsapp.com{st.session_state.whatsapp_num}&text={urllib.parse.quote(pitch_wa)}"
                
                st.info(f"💡 **Pitch suggéré :** {generer_pitch_commercial(st.session_state.user_metier, st.session_state.user_ville)}")
                
                # UTILISATION DU BOUTON DE LIEN NATIF SANS PAGE BLANCHE
                st.link_button("➡️ Décrocher ce chantier immédiatement", lien_final, key=f"btn_client_saas_{idx}", use_container_width=True)
                st.write("---")
    else:
        st.info("🔎 Le robot fouille le web en ce moment même... Aucune nouvelle alerte pour cette zone géographique pour l'instant.")

    # 🚪 BOUTON DE DÉCONNEXION SÉCURISÉE
    st.write("---")
    if st.button("🚪 Se déconnecter de ZELIA", key="btn_logout_system", use_container_width=True):
        st.session_state.authentifie = False
        st.session_state.user_email = None
        st.session_state.robot_actif = False
        st.rerun()
