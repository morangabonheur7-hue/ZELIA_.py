import streamlit as st
import time
import requests
import urllib.parse
import os
import datetime

# ==========================================
# 1. CONFIGURATION INTERFACE & ACCÈS SÉCURISÉS
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
if "facebook_group" not in st.session_state: st.session_state.facebook_group = ""

# ==========================================
# FONCTION LOGIQUE : FORMATEUR DE TEXTE EN URL FB
# ==========================================
def formater_nom_groupe_en_url(nom_ou_lien):
    texte_propre = nom_ou_lien.strip()
    if not texte_propre:
        return ""
    # Si l'artisan a mis un vrai lien complet, on le garde
    if "facebook.com" in texte_propre.lower():
        return texte_propre
    # S'il a écrit du texte brut (ex: Entraide Paris), on l'encode pour la recherche Facebook
    texte_encode = urllib.parse.quote(texte_propre)
    return f"https://facebook.com{texte_encode}"

# ==========================================
# 2. FONCTIONS DE PROGRAMMATION DATABASE
# ==========================================
def verifier_si_utilisateur_existe(email):
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs?email=eq.{email.lower()}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            donnees = res.json()
            if len(donnees) > 0:
                return donnees[0]
    except:
        pass
    return None
    
def inscrire_nouvel_artisan(email, metier, ville, groupe_fb):
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}
    
    url_groupe_formate = formater_nom_groupe_en_url(groupe_fb)
    
    payload = [{
        "email": email.lower(), 
        "metier": metier.lower(), 
        "ville": ville.lower(),
        "facebook_group_url": url_groupe_formate
    }]
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        if res.status_code in: return True
    except: pass
    return False

def mettre_a_jour_groupe_artisan(email, nouveau_groupe):
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs?email=eq.{email.lower()}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    
    url_groupe_formate = formater_nom_groupe_en_url(nouveau_groupe)
    payload = {"facebook_group_url": url_groupe_formate}
    try:
        res = requests.patch(url, json=payload, headers=headers, timeout=5)
        if res.status_code in: return True
    except: pass
    return False

def extraire_leads_strict(metier, ville):
    il_y_a_3_jours = (datetime.datetime.utcnow() - datetime.timedelta(hours=72)).isoformat()
    # Lit depuis 'chantiers' qui reçoit le flux nettoyé par FastAPI
    url = f"{SUPABASE_URL}/rest/v1/chantiers?metier=eq.{metier.lower()}&ville=in.({ville.lower()},global)&created_at=gte.{il_y_a_3_jours}&order=id.desc&limit=250"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200: return res.json()
    except: pass
    return []

# ==========================================
# 3. INTERFACE DE CONNEXION INTELLIGENTE
# ==========================================
st.title("🚀 ZELIA GLOBAL — L'Application des Artisans")
st.write("---")

if not st.session_state.authentifie:
    email_input = st.text_input("🔑 Entrez votre adresse e-mail :", placeholder="artisan@example.com").strip().lower()
    if email_input:
        utilisateur = verifier_si_utilisateur_existe(email_input)
        if utilisateur:
            st.success(f"✅ Compte trouvé ! {utilisateur['metier'].upper()} à {utilisateur['ville'].upper()}")
            if st.button("🔓 Ouvrir mon tableau de bord", use_container_width=True, type="primary"):
                st.session_state.user_email = utilisateur['email']
                st.session_state.user_metier = utilisateur['metier']
                st.session_state.user_ville = utilisateur['ville']
                st.session_state.facebook_group = utilisateur.get('facebook_group_url', '')
                st.session_state.authentifie = True
                st.rerun()
        else:
            st.info("🆕 Nouveau ? Remplissez vos informations de zone :")
            with st.form("form_inscription"):
                choix_metier = st.selectbox("Métier :", ["plombier", "electricien", "serrurier", "mecanicien"])
                choix_ville = st.text_input("Ville d'intervention :", placeholder="paris, london, marseille...").strip().lower()
                choix_groupe = st.text_input("📢 Groupe Facebook à scanner (Nom ou Lien) :", placeholder="Ex: Entraide Paris ou Voisins Lyon").strip()
                
                if st.form_submit_button("🚀 Créer mon compte"):
                    if choix_ville and choix_groupe:
                        if inscrire_nouvel_artisan(email_input, choix_metier, choix_ville, choix_groupe):
                            st.session_state.user_email = email_input
                            st.session_state.user_metier = choix_metier
                            st.session_state.user_ville = choix_ville
                            st.session_state.facebook_group = formater_nom_groupe_en_url(choix_groupe)
                            st.session_state.authentifie = True
                            st.success("Compte validé !")
                            time.sleep(1)
                            st.rerun()
                        else: st.error("Erreur de connexion base de données.")
                    else: st.error("Veuillez indiquer votre ville et le nom d'un groupe Facebook.")

# ==========================================
# 4. LE TABLEAU DE BORD ET FILTRES DE TEMPS
# ==========================================
else:
    with st.sidebar:
        st.subheader("⚙️ Configuration Radar")
        nouveau_nom_groupe = st.text_input("Modifier le groupe ciblé :", value=st.session_state.facebook_group, placeholder="Entrez un nom ou un lien").strip()
        if st.button("💾 Mettre à jour mon groupe", use_container_width=True):
            if mettre_a_jour_groupe_artisan(st.session_state.user_email, nouveau_nom_groupe):
                st.session_state.facebook_group = formater_nom_groupe_en_url(nouveau_nom_groupe)
                st.success("Configuration enregistrée !")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Erreur de mise à jour.")

    st.header(f"📬 Opportunités à : {st.session_state.user_ville.upper()}")
    st.write(f"🧑‍🔧 Profil : **{st.session_state.user_metier.upper()}** | 📧 {st.session_state.user_email}")
    st.caption(f"🎯 Cible actuelle du scanneur : `{st.session_state.facebook_group}`")
    st.write("---")
    
    leads_bruts = extraire_leads_strict(st.session_state.user_metier, st.session_state.user_ville)
    if leads_bruts:
        choix_temps = st.radio("⏳ Tranche horaire des urgences :", ["⏱️ Maintenant (<2h)", "🚀 Aujourd'hui (<8h)", "📅 Récent (<24h)", "📜 Tout (3 jours)"], horizontal=True)
        st.write("---")
        
        leads_filtres = []
        maintenant = datetime.datetime.utcnow()
        
        for client in leads_bruts:
            try:
                date_str = client.get("created_at", "").split("+")
                date_client = datetime.datetime.fromisoformat(date_str[0])
                diff_h = (maintenant - date_client).total_seconds() / 3600
                if choix_temps == "⏱️ Maintenant (<2h)" and diff_h <= 2: leads_filtres.append(client)
                elif choix_temps == "🚀 Aujourd'hui (<8h)" and diff_h <= 8: leads_filtres.append(client)
                elif choix_temps == "📅 Récent (<24h)" and diff_h <= 24: leads_filtres.append(client)
                elif choix_temps == "📜 Tout (3 jours)": leads_filtres.append(client)
            except: leads_filtres.append(client)
            
        if leads_filtres:
            st.toast(f"🔔 {len(leads_filtres)} chantiers qualifiés affichés !")
            for idx, client in enumerate(leads_filtres):
                with st.container(border=True):
                    st.markdown("### 📍 Particulier Identifié (Sniper Engine)")
                    st.write(client.get("texte", "Pas de détails."))
                    pitch = f"Bonjour, je vois votre demande pour un {st.session_state.user_metier} à {st.session_state.user_ville.upper()}. Disponible immédiatement !"
                    st.text_area("💡 Message pré-rédigé :", value=pitch, height=70, key=f"pitch_{idx}", disabled=True)
                    
                    lien_brut = client.get("lien", "https://google.com")
                    num_client = client.get("telephone", "")
                    if num_client:
