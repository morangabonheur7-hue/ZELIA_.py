import streamlit as st
import time
import requests
import urllib.parse

# ==========================================
# 1. CONFIGURATION INTERFACE & ACCÈS SAAS
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1d2twcmZvd2diaW10Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDc2MDI0OSwiZXhwIjoyMDk2MzM2MjQ5fQ.zkDmslMSHuPtS2mJgC4qwWca5cq8IZUQMz6p6ecpTNA"
RESEND_API_KEY = "re_7fidYWed_3hLMv1XeTBQ3urCAr9SQoHCz"

# Initialisation de la mémoire d'état (Anti-bug de rechargement)
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_metier" not in st.session_state: st.session_state.user_metier = "plombier"
if "user_ville" not in st.session_state: st.session_state.user_ville = "global"

# ==========================================
# 2. FONCTIONS DE PROGRAMMATION DATABASE
# ==========================================
def verifier_si_utilisateur_existe(email):
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs?email=eq.{email.lower()}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and len(res.json()) > 0:
            return res.json()[0] # Renvoie le premier utilisateur trouvé
    except:
        pass
    return None

def inscrire_nouvel_artisan(email, metier, ville):
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    payload = [{"email": email.lower(), "metier": metier.lower(), "ville": ville.lower()}]
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        return res.status_code == 200 or res.status_code == 201
    except:
        return False

def extraire_leads_strict(metier, ville):
    # Filtre strict : Même métier ET (Même ville OU étiquette globale)
    url = f"{SUPABASE_URL}/rest/v1/leads?metier=eq.{metier.lower()}&ville=in.({ville.lower()},global)&order=id.desc&limit=10"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

# ==========================================
# 3. INTERFACE DE CONNEXION INTELLIGENTE
# ==========================================
st.title("🚀 ZELIA GLOBAL — L'Application des Artisans")
st.write("---")

if not st.session_state.authentifie:
    # Formulaire de vérification initiale de l'adresse e-mail
    email_input = st.text_input("🔑 Entrez votre adresse e-mail pour accéder à votre espace :", placeholder="artisan@example.com").strip().lower()
    
    if email_input:
        utilisateur = verifier_si_utilisateur_existe(email_input)
        
        if utilisateur:
            # L'utilisateur existe -> BOUTON DE CONNEXION AUTOMATIQUE SIMPLE
            st.success(f"✅ Compte trouvé ! Métier : {utilisateur['metier'].upper()} | Ville : {utilisateur['ville'].upper()}")
            if st.button("🔓 Se connecter à mon espace privé", use_container_width=True, type="primary"):
                st.session_state.user_email = utilisateur['email']
                st.session_state.user_metier = utilisateur['metier']
                st.session_state.user_ville = utilisateur['ville']
                st.session_state.authentifie = True
                st.rerun()
        else:
            # L'utilisateur n'existe pas -> FORMULAIRE D'INSCRIPTION UNIQUE
            st.info("🆕 Nouveau sur Zelia Global ? Remplissez vos informations de ciblage :")
            with st.form("form_inscription"):
                choix_metier = st.selectbox("Votre corps de métier :", ["plombier", "electricien", "serrurier", "mecanicien"])
                choix_ville = st.text_input("Votre Ville principale d'intervention :", placeholder="paris, london, montreal...").strip().lower()
                
                if st.form_submit_button("🚀 Créer mon compte et ouvrir le flux"):
                    if choix_ville:
                        if inscrire_nouvel_artisan(email_input, choix_metier, choix_ville):
                            st.session_state.user_email = email_input
                            st.session_state.user_metier = choix_metier
                            st.session_state.user_ville = choix_ville
                            st.session_state.authentifie = True
                            st.success("Compte créé avec succès !")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erreur technique lors de la création du compte.")
                    else:
                        st.error("Veuillez indiquer votre ville pour le ciblage Google.")

# ==========================================
# 4. LE TABLEAU DE BORD PRIVÉ GÉO-LOCALISÉ
# ==========================================
else:
    st.header(f"📬 Chantiers en direct à : {st.session_state.user_ville.upper()}")
    st.write(f"🧑‍🔧 Profil : **{st.session_state.user_metier.upper()}** | 📧 {st.session_state.user_email}")
    st.write("---")
    
    # Récupération des leads filtrés strictement
    leads = extraire_leads_strict(st.session_state.user_metier, st.session_state.user_ville)
    
    if leads:
        st.toast(f"🔔 Alerte : Clients trouvés pour {st.session_state.user_ville.upper()} !")
        
        for idx, client in enumerate(leads):
            with st.container(border=True):
                st.markdown(f"### 📍 Client Identifié ({client.get('plateforme', 'Google Scraper')})")
                st.write(client.get("texte", "Pas de détails disponibles."))
                
                # Message de vente pré-rédigé automatiquement
                pitch = f"Bonjour, je vois votre demande pour un {st.session_state.user_metier} à {st.session_state.user_ville.upper()}. Je suis qualifié, disponible immédiatement et je peux intervenir rapidement !"
                st.text_area("💡 Message commercial prêt à l'envoi :", value=pitch, height=70, key=f"pitch_{idx}", disabled=True)
                
                # ROUTAGE COMMERCIAL INTELLIGENT
                lien_brut = client.get("lien", "https://google.com")
                num_client = client.get("telephone", "") # Si le robot trouve un numéro
                
                if num_client:
                    lien_whatsapp = f"https://wa.me{num_client}?text={urllib.parse.quote(pitch)}"
                    st.link_button("官方 🟢 Contacter le particulier sur WhatsApp (Message rédigé)", lien_whatsapp, use_container_width=True)
                else:
                    st.link_button("➡️ Ouvrir le site d'origine du client pour lui répondre", lien_brut, use_container_width=True)
                
                # ALERTE EMAIL VIA RESEND
                if st.button(f"📧 Recevoir ce chantier par E-mail (Lead #{idx})", key=f"resend_{idx}", use_container_width=True):
                    url_resend = "https://resend.com"
                    headers_resend = {"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"}
                    payload_resend = {
                        "from": "Zelia Global <onboarding@resend.dev>",
                        "to": [st.session_state.user_email],
                        "subject": f"🚨 ALERTE CHANTIER IMMÉDIAT : {st.session_state.user_metier.upper()}",
                        "html": f"<h3>🚀 ZELIA GLOBAL</h3><p>Chantier disponible : {client.get('texte')}</p><p>Lien : {lien_brut}</p>"
                    }
                                        try:
                        res = requests.post(url_resend, json=payload_resend, headers=headers_resend, timeout=10)
                        if res.status_code == 200 or res.status_code == 201: 
                            st.success("🎯 Alerte envoyée dans ta boîte mail !")
                        else: 
                            st.error("Erreur d'envoi Resend.")
                    except Exception as e: 
                        st.error(f"Connexion Resend échouée : {e}")
            
    else:
        st.warning(f"🔎 Aucun client trouvé à {st.session_state.user_ville.upper()} pour le métier de {st.session_state.user_metier} pour le moment. Le robot cherche en continu.")

    st.write("---")
    if st.button("🚪 Se déconnecter de mon compte ZELIA GLOBAL", use_container_width=True):
        st.session_state.authentifie = False
        st.session_state.user_email = ""
        st.rerun()
    
