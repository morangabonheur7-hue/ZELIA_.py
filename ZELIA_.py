import streamlit as st
import time, requests, urllib.parse, os, datetime

# ==========================================
# 1. CONFIGURATION INTERFACE & ACCÈS SÉCURISÉS
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

# Modification ici : On s'assure d'avoir l'URL officielle chiffrée
SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1w2twcmZvd2diaW10Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MDc2MDI0OSwiZXhwIjoyMDk2MzM2MjQ5fQ.zkDmslMSHuPtS2mJgC4qwWca5cq8IZUQMz6p6ecpTNA")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "re_7fidYWed_3hLMv1XeTBQ3urCAr9SQoHCz")

if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_metier" not in st.session_state: st.session_state.user_metier = "plombier"
if "user_ville" not in st.session_state: st.session_state.user_ville = "global"
if "user_statut" not in st.session_state: st.session_state.user_statut = "inactif"

# ==========================================
# 2. FONCTIONS DE PROGRAMMATION INTERNE (DATABASE)
# ==========================================
def verifier_si_utilisateur_existe(email):
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs?email=eq.{email.lower()}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            donnees = res.json()
            if len(donnees) > 0:
                u = donnees[0]
                if "statut_abonnement" not in u or u["statut_abonnement"] is None: 
                    u["statut_abonnement"] = "inactif"
                return u
    except: pass
    return None

def inscrire_nouvel_artisan(email, metier, ville):
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}
    payload = [{
        "email": email.lower(), 
        "metier": metier.lower(), 
        "ville": ville.lower(), 
        "statut_abonnement": "inactif"
    }]
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        if res.status_code == 201:
        
            return True
        else:
            st.error(f"⚠️ Code Erreur Supabase (Artisan) : {res.status_code} - {res.text}")
    except Exception as e: 
        st.error(f"❌ Erreur Technique Inscription : {e}")
    return False

def particulier_deposer_chantier(metier, ville, description, telephone):
    url = f"{SUPABASE_URL}/rest/v1/leads"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}
    texte_final = f"🚨 URGENCE PARTICULIER DIRECT :\n📢 {description}"
    payload = [{
        "metier": metier.lower(),
        "ville": ville.lower(),
        "texte": texte_final,
        "telephone": telephone.strip(),
        "lien": "https://streamlit.app",
        "plateforme": "Zelia Public Direct"
    }]
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        if res.status_code in: 
            return True
        else:
            st.error(f"⚠️ Code Erreur Supabase (Chantier) : {res.status_code} - {res.text}")
    except Exception as e: 
        st.error(f"❌ Erreur Technique Chantier : {e}")
    return False

def extraire_leads_strict(metier, ville):
    il_y_a_3_jours = (datetime.datetime.utcnow() - datetime.timedelta(hours=72)).isoformat()
    url = f"{SUPABASE_URL}/rest/v1/leads?metier=eq.{metier.lower()}&ville=in.({ville.lower()},global)&created_at=gte.{il_y_a_3_jours}&order=id.desc&limit=100"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200: return res.json()
    except: pass
    return []

def envoyer_fiche_email(destinataire, texte, lien):
    headers = {"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"}
    payload = {"from": "Zelia Global <onboarding@resend.dev>", "to": [destinataire], "subject": "🚨 FICHE CHANTIER ZELIA", "html": f"<p>{texte}</p><br><a href='{lien}'>Ouvrir l'application</a>"}
    try:
        res = requests.post("https://resend.com", json=payload, headers=headers, timeout=10)
        if res.status_code in: st.success("🎯 Envoyé ! Vérifiez vos e-mails.")
        else: st.error("Erreur d'envoi de l'e-mail.")
    except: st.error("Échec de connexion au service d'e-mail.")

# ==========================================
# 3. ARCHITECTURE DE L'ÉCRAN D'ACCUEIL GLOBAL
# ==========================================
st.title("🚀 ZELIA GLOBAL — Plateforme Mondiale des Artisans")
st.write("L'écosystème international de mise en relation directe pour les dépannages urgents.")
st.write("---")

if not st.session_state.authentifie:
    col_particulier, col_artisan = st.columns(2, gap="large")
    
    with col_particulier:
        st.header("🟢 J'ai une Urgence (Particulier)")
        st.markdown("##### Déposez votre demande gratuitement en 5 secondes. Aucun compte requis.")
        
        with st.form("form_particulier", clear_on_submit=True):
            p_metier = st.selectbox("De quel professionnel avez-vous besoin ?", ["plombier", "electricien", "serrurier", "mecanicien"])
            p_ville = st.text_input("Dans quelle ville vous situez-vous ?", placeholder="Ex: paris, london...").strip().lower()
            p_phone = st.text_input("Votre numéro de téléphone :", placeholder="Ex: +33612345678").strip()
            p_desc = st.text_area("Expliquez votre problème en quelques mots :", placeholder="Fuite d'eau sous mon évier...")
            
            submit_particulier = st.form_submit_button("📢 Envoyer ma demande immédiatement")
            if submit_particulier:
                if p_ville and p_desc and p_phone:
                    particulier_deposer_chantier(p_metier, p_ville, p_desc, p_phone)
                else: st.error("Veuillez remplir toutes les cases.")
                
    with col_artisan:
        st.header("🔵 Espace Professionnel (Artisan)")
        st.markdown("##### Connectez-vous pour intercepter les urgences de votre secteur en direct.")
        
        email_input = st.text_input("🔑 Entrez votre adresse e-mail pro :", placeholder="artisan@example.com").strip().lower()
        if email_input:
            utilisateur = verifier_si_utilisateur_existe(email_input)
            if utilisateur:
                st.success(f"✅ Profil identifié ! {utilisateur['metier'].upper()} à {utilisateur['ville'].upper()}")
                if st.button("🔓 Ouvrir mon tableau de bord", use_container_width=True, type="primary"):
                    st.session_state.user_email = utilisateur['email']
                    st.session_state.user_metier = utilisateur['metier']
                    st.session_state.user_ville = utilisateur['ville']
                    st.session_state.user_statut = str(utilisateur['statut_abonnement'])
                    st.session_state.authentifie = True
                    st.rerun()
            else:
                st.info("🆕 Enregistrez votre zone :")
                with st.form("form_inscription_artisan"):
                    choix_metier = st.selectbox("Votre corps de métier :", ["plombier", "electricien", "serrurier", "mecanicien"])
                    choix_ville = st.text_input("Votre ville d'intervention :", placeholder="paris...").strip().lower()
                    
                    if st.form_submit_button("🚀 Activer mes 12 jours d'essai gratuit"):
                        if choix_ville:
                            inscrire_nouvel_artisan(email_input, choix_metier, choix_ville)
                        else: st.error("Veuillez écrire votre ville.")

else:
    st.header(f"📬 Radar de chantiers en direct : {st.session_state.user_ville.upper()}")
    st.write(f"🧑‍🔧 Artisan : **{st.session_state.user_metier.upper()}** | 📧 {st.session_state.user_email}")
    st.write("---")

    if st.session_state.user_statut != "actif":
        st.error("🔒 ACCÈS LIMITÉ")
        lien_paddle_sandbox = "https://paddle.com"
        st.link_button("💳 Activer mon accès Pro Zelia (29,99€ / mois)", lien_paddle_sandbox, use_container_width=True, type="primary")
    else:
        leads_bruts = extraire_leads_strict(st.session_state.user_metier, st.session_state.user_ville)
        if not leads_bruts:
            st.warning("🔎 Aucun chantier disponible pour le moment.")
        else:
            for idx, client in enumerate(leads_bruts):
                with st.container(border=True):
                    st.write(client.get("texte", "Pas de détails."))
                    num_client = client.get("telephone", "")
                    if num_client:
                        st.link_button("🟢 Appeler WhatsApp", f"https://wa.me{num_client.replace('+', '')}")

    if st.button("🚪 Se déconnecter", use_container_width=True):
        st.session_state.authentifie = False
        st.rerun()
        
# ==========================================
# 5. ASSISTANCE TECHNIQUE & SUPPORT
# ==========================================
st.write("---")
st.markdown("### 🛠️ Assistance Technique Internationale")
c1, c2 = st.columns(2)
with c1: st.link_button("💬 Support Client WhatsApp", "https://wa.me242055967601?text=Bonjour%20Support%20Zelia", use_container_width=True)
with c2: st.link_button("📧 Support Commercial E-mail", "mailto:support.zelia@gmail.com", use_container_width=True)
    
