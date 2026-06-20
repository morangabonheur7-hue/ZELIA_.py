import streamlit as st
import time
import requests
import urllib.parse
import os

# ==========================================
# CONFIGURATION INTERFACE & ACCÈS SÉCURISÉS
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1d2twcmZvd2diaW10Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDc2MDI0OSwiZXhwIjoyMDk2MzM2MjQ5fQ.zkDmslMSHuPtS2mJgC4qwWca5cq8IZUQMz6p6ecpTNA")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "re_7fidYWed_3hLMv1XeTBQ3urCAr9SQoHCz")
PADDLE_API_KEY = os.environ.get("PADDLE_API_KEY", "pdl_live_apikey_01ktezxq12q0j88mtc9ven94xz_QPM2hzX6pBWRDRarmvTS9W_A0Y") 
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_metier" not in st.session_state: st.session_state.user_metier = "plombier"
if "user_ville" not in st.session_state: st.session_state.user_ville = "global"

lang = {
    "titre_connexion": "🔐 Connexion sécurisée à l'infrastructure Zelia",
    "erreur_champs": "⚠️ Veuillez remplir tous les champs pour vous connecter.",
    "flux_statut": "🟢 Le flux géo-localisé en direct est ouvert. Chargement de vos clients..."
}

def verifier_si_utilisateur_existe(email):
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs?email=eq.{email.lower()}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and len(res.json()) > 0:
            return res.json()[0]
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
        if res.status_code == 200 or res.status_code == 201:
            return True
    except:
        pass
    return False

def extraire_leads_strict(metier, ville):
    url = f"{SUPABASE_URL}/rest/v1/leads?metier=eq.{metier.lower()}&ville=in.({ville.lower()},global)&order=id.desc&limit=10"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return []

st.title("🚀 ZELIA GLOBAL — L'Application des Artisans")
st.write("---")

if not st.session_state.authentifie:
    email_input = st.text_input("🔑 Entrez votre adresse e-mail pour accéder à votre espace :", placeholder="artisan@example.com").strip().lower()
    
    if email_input:
        utilisateur = verifier_si_utilisateur_existe(email_input)
        if utilisateur:
            st.success(f"✅ Compte validé ! Spécialité : {utilisateur['metier'].upper()} | Zone : {utilisateur['ville'].upper()}")
            if st.button("🔓 Ouvrir mon tableau de bord privé", use_container_width=True, type="primary"):
                st.session_state.user_email = utilisateur['email']
                st.session_state.user_metier = utilisateur['metier']
                st.session_state.user_ville = utilisateur['ville']
                st.session_state.authentifie = True
                st.rerun()
        else:
            st.info("🆕 Nouveau sur Zelia Global ? Créez vos identifiants de ciblage :")
            with st.form("form_inscription"):
                choix_metier = st.selectbox("Votre corps de métier :", ["plombier", "electricien", "serrurier", "mecanicien"])
                choix_ville = st.text_input("Votre Ville principale d'intervention :", placeholder="paris, london, montreal...").strip().lower()
                if st.form_submit_button("🚀 Créer mon compte unique et ouvrir le flux"):
                    if choix_ville:
                        if inscrire_nouvel_artisan(email_input, choix_metier, choix_ville):
                            st.session_state.user_email = email_input
                            st.session_state.user_metier = choix_metier
                            st.session_state.user_ville = choix_ville
                            st.session_state.authentifie = True
                            st.success("Inscription validée avec succès !")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erreur technique de communication.")
                    else:
                        st.error("Veuillez remplir le champ de la ville.")
else:
    st.header(f"📬 Vos opportunités en direct à : {st.session_state.user_ville.upper()}")
    st.write(f"🧑‍🔧 Spécialité : **{st.session_state.user_metier.upper()}** | 📧 Connecté : {st.session_state.user_email}")
    st.write("---")
    
    leads = extraire_leads_strict(st.session_state.user_metier, st.session_state.user_ville)
    if leads:
        st.toast(f"🔔 Alerte : Nouveaux clients identifiés à {st.session_state.user_ville.upper()} !")
        for idx, client in enumerate(leads):
            with st.container(border=True):
                st.markdown(f"### 📍 Client Disponible (Source: Google Scraper Engine)")
                st.write(client.get("texte", "Pas de détails disponibles."))
                pitch = f"Bonjour, je vois votre demande pour un {st.session_state.user_metier} à {st.session_state.user_ville.upper()}. Je suis qualifié, disponible immédiatement et je peux intervenir rapidement !"
                st.text_area("💡 Message commercial rédigé automatiquement :", value=pitch, height=70, key=f"pitch_{idx}", disabled=True)
                
                lien_brut = client.get("lien", "https://google.com")
                num_client = client.get("telephone", "")
                if num_client:
                    lien_whatsapp = f"https://wa.me{num_client}?text={urllib.parse.quote(pitch)}"
                    st.link_button("🟢 Contacter ce particulier sur WhatsApp", lien_whatsapp, use_container_width=True)
                else:
                    st.link_button("➡️ Ouvrir le site d'origine du client pour lui répondre", lien_brut, use_container_width=True)
                
                if st.button(f"📧 Recevoir la fiche client par E-mail (Lead #{idx})", key=f"resend_{idx}", use_container_width=True):
                    url_resend = "https://resend.com"
                    headers_resend = {"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"}
                    payload_resend = {
                        "from": "Zelia Global <onboarding@resend.dev>",
                        "to": [st.session_state.user_email],
                        "subject": f"🚨 NOTIFICATION DE CHANTIER : {st.session_state.user_metier.upper()}",
                        "html": f"<h3>🚀 ZELIA GLOBAL</h3><p>Un client cherche un professionnel :</p><p>{client.get('texte')}</p><p><a href='{lien_brut}'>Répondre au client</a></p>"
                    }
                    try:
                        res = requests.post(url_resend, json=payload_resend, headers=headers_resend, timeout=10)
                        if res.status_code == 200 or res.status_code == 201:
                            st.success("🎯 Alerte envoyée ! Regardez la boîte de réception de votre téléphone.")
                        else:
                            st.error(f"Refus du serveur (Code {res.status_code})")
                    except Exception as e:
                        st.error(f"Erreur de connexion : {e}")
    else:
        st.warning(f"🔎 Aucun client trouvé à {st.session_state.user_ville.upper()} pour le métier de {st.session_state.user_metier}. Le robot continue ses recherches.")

    st.write("---")
    if st.button("🚪 Se déconnecter de mon compte ZELIA GLOBAL", use_container_width=True):
        st.session_state.authentifie = False
        st.session_state.user_email = ""
        st.rerun()
