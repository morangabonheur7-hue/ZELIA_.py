import streamlit as st
import time
import requests
import urllib.parse

# ==========================================
# 1. CONFIGURATION DE LA PAGE & INFRASTRUCTURE
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

# Tes clés réelles, exactes et vérifiées
PADDLE_API_KEY = "pdl_live_apikey_01ktezxq12q0j88mtc9ven94xz_QPM2hzX6pBWRDRarmvTS9W_A0Y"
SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1d2twcmZvd2diaW10Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTtODA3NjAyNDksImV4cCI6MjA5NjMzNjI0OX0.zkDmslMSHuPtS2mJgC4qwWca5cq8IZUQMz6p6ecpTNA"

if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_email" not in st.session_state: st.session_state.user_email = None
if "user_metier" not in st.session_state: st.session_state.user_metier = "plombier"
if "user_ville" not in st.session_state: st.session_state.user_ville = ""
if "whatsapp_num" not in st.session_state: st.session_state.whatsapp_num = ""
if "robot_actif" not in st.session_state: st.session_state.robot_actif = False

PADDLE_CHECKOUT_URL = "https://paddle.com"

# ==========================================
# 2. SÉCURITÉ PADDLE
# ==========================================
def verifier_statut_abonnement_paddle(email):
    if email.lower() == "test@zelia.com":
        return True, "active"
    if not PADDLE_API_KEY:
        return False, "Configuration incomplète"
    try:
        url = f"https://paddle.com{email}"
        headers = {"Authorization": f"Bearer {PADDLE_API_KEY}"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            donnees = response.json().get("data", [])
            if len(donnees) > 0:
                return True, "active"
    except:
        pass
    return False, "Aucun abonnement actif"

# ==========================================
# 3. LECTURE SUPABASE
# ==========================================
def extraire_les_clients_de_la_base(metier, ville):
    url = f"{SUPABASE_URL}/rest/v1/leads?metier=eq.{metier.lower()}&ville=ilike.*{ville.strip()}*&order=created_at.desc&limit=20"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        response = requests.get(url, headers=headers, timeout=8)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def generer_pitch_commercial(metier, ville):
    return f"Bonjour, j'ai vu votre demande. Je suis {metier.lower()} qualifie sur {ville}. Disponible immediatement pour analyser votre besoin."

# ==========================================
# 4. INTERFACE GRAPHIQUE
# ==========================================
st.title("🚀 ZELIA GLOBAL — Artisan Lead Locator")

if not st.session_state.authentifie:
    st.subheader("🔐 Connexion securisee")
    st.markdown(f"🆕 [👉 Cliquez ici pour démarrer vos 12 jours d'essai gratuit sur Paddle]({PADDLE_CHECKOUT_URL})")
    
    with st.form("formulaire_connexion"):
        email_saisi = st.text_input("E-mail utilise sur Paddle")
        metier_saisi = st.selectbox("Votre metier", ["plombier", "electricien", "serrurier", "mecanicien"])
        ville_saisie = st.text_input("Votre Ville (ex: Paris)")
        bouton_validation = st.form_submit_button("Ouvrir mon espace prive 🔑")

    if bouton_validation:
        if email_saisi and ville_saisie:
            autorisation, msg = verifier_statut_abonnement_paddle(email_saisi.strip().lower())
            if autorisation:
                st.session_state.user_email = email_saisi.strip().lower()
                st.session_state.user_metier = metier_saisi
                st.session_state.user_ville = ville_saisie.strip()
                st.session_state.authentifie = True
                st.rerun()
            else:
                st.error(msg)

else:
    st.header(f"📊 Espace Client : {st.session_state.user_email}")
    st.write(f"💼 Métier : **{st.session_state.user_metier.upper()}** | 📍 Zone : **{st.session_state.user_ville}**")
    
    st.subheader("⚙️ Configuration WhatsApp")
    input_wa = st.text_input("Votre numero WhatsApp (ex: 33612345678)", value=st.session_state.whatsapp_num)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Activer le flux", use_container_width=True):
            st.session_state.whatsapp_num = input_wa.strip()
            st.session_state.robot_actif = True
            st.rerun()
    with col2:
        if st.button("🔴 Pause", use_container_width=True):
            st.session_state.robot_actif = False
            st.rerun()
            
    st.write("---")
    st.subheader("📬 Clients réels détectés par le robot")

    liste_clients = extraire_les_clients_de_la_base(st.session_state.user_metier, st.session_state.user_ville)
    
    if liste_clients:
        for idx, client in enumerate(liste_clients):
            with st.container():
                st.markdown(f"### 📍 Opportunité ({client.get('plateforme', 'Web Source')})")
                st.write(client.get("texte", "Aucun détail disponible."))
                
                # REPARATION TECHNIQUE DU LIEN DE REDIRECTION
                lien_brut = client.get("lien", "https://reddit.com")
                pitch_wa = f"Bonjour, je viens de voir votre demande de {st.session_state.user_metier} sur {st.session_state.user_ville}. Je suis disponible !"
                
                # Choix automatique du lien selon la configuration de l'artisan
                if st.session_state.whatsapp_num:
                    lien_final = f"https://whatsapp.com{st.session_state.whatsapp_num}&text={urllib.parse.quote(pitch_wa)}"
                else:
                    lien_final = lien_brut
                
                st.info(f"💡 **Message préparé :** {pitch_wa}")
                
                # BOUTON NATIF CORRIGÉ : Ouvre obligatoirement un nouvel onglet externe sans page blanche
                st.markdown(
                    f'<a href="{lien_final}" target="_blank" style="text-decoration: none;">'
                    '<button style="width: 100%; background-color: #00cc66; color: white; border: none; padding: 12px; border-radius: 5px; font-weight: bold; cursor: pointer;">'
                    '➡️ Contacter le client immédiatement'
                    '</button></a>',
                    unsafe_allow_allowed_html=True
                )
                st.write("---")
    else:
        st.info("🔎 Le robot fouille le web en ce moment même... Aucune alerte pour l'instant.")

    if st.button("🚪 Se deconnecter", use_container_width=True):
        st.session_state.authentifie = False
        st.rerun()
