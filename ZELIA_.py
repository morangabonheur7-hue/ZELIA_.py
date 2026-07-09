import streamlit as st
import time, requests, urllib.parse, os, datetime

# ==========================================
# 1. CONFIGURATION INTERFACE & ACCÈS SÉCURISÉS
# ==========================================
st.set_page_config(page_title="ZELIA GLOBAL", page_icon="🚀", layout="wide")

# Modification ici : On s'assure d'avoir l'URL officielle chiffrée
SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1d2twcmZvd2diaW10Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA3NjAyNDksImV4cCI6MjA5NjMzNjI0OX0.rA17-omiRtXuECi0b7RW8wNe583Qa8swoV1HrgcQ9wM")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "re_7fidYWed_3hLMv1XeTBQ3urCAr9SQoHCz")

if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_metier" not in st.session_state: st.session_state.user_metier = "plombier"
if "user_ville" not in st.session_state: st.session_state.user_ville = "global"
if "user_statut" not in st.session_state: st.session_state.user_statut = "inactif"
if "user_date_creation" not in st.session_state: st.session_state.user_date_creation = ""

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
        "statut_abonnement": "inactif",
        "date_activation": None
    }]
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        if res.status_code == 201 or res.status_code == 200: return True
        else: st.error(f"⚠️ Code Erreur Supabase (Artisan) : {res.status_code} - {res.text}")
    except Exception as e: st.error(f"❌ Erreur Technique Inscription : {e}")
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
        "lien": "https://tinyurl.com",
        "plateforme": "Zelia Public Direct"
    }]
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=5)
        if res.status_code == 201 or res.status_code == 200: return True
        else: st.error(f"⚠️ Code Erreur Supabase (Chantier) : {res.status_code} - {res.text}")
    except Exception as e: st.error(f"❌ Erreur Technique Chantier : {e}")
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
        if res.status_code == 200 or res.status_code == 201: st.success("🎯 Envoyé ! Vérifiez vos e-mails.")
        else: st.error("Erreur d'envoi de l'e-mail.")
    except: st.error("Échec de connexion au service d'e-mail.")

# ==========================================
# 3. ARCHITECTURE DE L'ÉCRAN D'ACCUEIL GLOBAL
# ==========================================
# 💎 TITRE PROFESSIONNEL ET LOGO STYLISÉ
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🚀 ZELIA GLOBAL</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #4B5563;'>Radar International d'Interception d'Urgences pour Artisans</h4>", unsafe_allow_html=True)
st.write("---")

if not st.session_state.authentifie:
    # 🛡️ LES 3 BADGES DE CONFIANCE ET DE SÉCURITÉ GLOBALE
    badge_col1, badge_col2, badge_col3 = st.columns(3)
    with badge_col1:
        st.success("🔒 SÉCURITÉ TOTALE\nAucune carte bancaire demandée.")
    with badge_col2:
        st.info("⚡ SANS INSCRIPTION\nPour les particuliers en détresse.")
    with badge_col3:
        st.warning("⏳ PLACES LIMITÉES\nMaximum 5 artisans par quartier.")
        
    st.write("") # Petit espace visuel propre

    # 📑 LES ONGLETS DE NAVIGATION (RADAR VS À PROPOS)
    onglet_radar, onglet_apropos = st.tabs(["📡 Radar en Direct", "ℹ️ À propos & Fonctionnement"])
    
    with onglet_radar:
        col_particulier, col_artisan = st.columns(2, gap="large")
        
        with col_particulier:
            st.header("🟢 J'ai une Urgence (Particulier)")
            st.markdown("##### Déposez votre demande gratuitement en 5 secondes.")
            
            with st.form("form_particulier", clear_on_submit=True):
                p_metier = st.selectbox("De quel professionnel avez-vous besoin ?", ["plombier", "electricien", "serrurier", "mecanicien"])
                p_ville = st.text_input("Dans quelle ville vous situez-vous ?", placeholder="Ex: paris, london, bruxelles...").strip().lower()
                p_phone = st.text_input("Votre numéro de téléphone (WhatsApp de préférence) :", placeholder="Ex: +32483600421").strip()
                st.caption("🔒 *Votre numéro reste strictement confidentiel et n'est transmis qu'au dépanneur qui intercepte l'alerte.*")
                
                p_desc = st.text_area("Expliquez votre problème en quelques mots :", placeholder="Ex: Fuite d'eau sous mon évier, l'eau coule partout au secours !")
                
                submit_particulier = st.form_submit_button("📢 Envoyer ma demande immédiatement")
                if submit_particulier:
                    if p_ville and p_desc and p_phone:
                        if particulier_deposer_chantier(p_metier, p_ville, p_desc, p_phone):
                            st.success("✅ Votre urgence a été diffusée ! Les artisans de votre quartier vont vous contacter d'ici quelques minutes.")
                    else: st.error("Veuillez remplir toutes les cases pour être contacté.")
                    
        with col_artisan:
            st.header("🔵 Espace Professionnel (Artisan)")
            st.markdown("##### Connectez-vous ou enregistrez votre zone d'intervention.")
            
            # 🔐 ENTRÉE LIBRE DE L'E-MAIL SANS FORMULAIRE POUR ÉVITER LA BOUCLE INFINIE
            email_input = st.text_input("🔑 Entrez votre adresse e-mail pro :", placeholder="artisan@example.com").strip().lower()
            st.caption("ℹ️ *Si vous possédez déjà un compte d'essai ou premium, entrez votre e-mail pour ouvrir votre tableau de bord.*")
            
            if email_input:
                utilisateur = verifier_si_utilisateur_existe(email_input)
                if utilisateur:
                    st.success(f"✅ Profil identifié ! {utilisateur['metier'].upper()} à {utilisateur['ville'].upper()}")
                    if st.button("🔓 Ouvrir mon tableau de bord", use_container_width=True, type="primary"):
                        st.session_state.user_email = utilisateur['email']
                        st.session_state.user_metier = utilisateur['metier']
                        st.session_state.user_ville = utilisateur['ville']
                        st.session_state.user_statut = str(utilisateur['statut_abonnement'])
                        st.session_state.user_date_creation = str(utilisateur.get('created_at', ''))
                        st.session_state.user_date_activation = str(utilisateur.get('date_activation', ''))
                        st.session_state.authentifie = True
                        st.rerun()
                else:
                    st.info("🆕 Adresse inconnue. Enregistrez votre zone ci-dessous pour activer vos 12 jours gratuits :")
                    
                    with st.form("form_inscription_artisan"):
                        choix_metier = st.selectbox("Votre corps de métier :", ["plombier", "electricien", "serrurier", "mecanicien"])
                        choix_ville = st.text_input("Votre ville exclusive d'intervention :", placeholder="paris, london, bruxelles...").strip().lower()
                        
                        if st.form_submit_button("🚀 Activer mes 12 jours d'essai gratuit", use_container_width=True):
                            if choix_ville:
                                if inscrire_nouvel_artisan(email_input, choix_metier, choix_ville):
                                    double_check = verifier_si_utilisateur_existe(email_input)
                                    if double_check:
                                        st.session_state.user_email = double_check['email']
                                        st.session_state.user_metier = double_check['metier']
                                        st.session_state.user_ville = double_check['ville']
                                        st.session_state.user_statut = "inactif"
                                        st.session_state.user_date_creation = str(double_check.get('created_at', ''))
                                        st.session_state.user_date_activation = str(double_check.get('date_activation', ''))
                                        st.session_state.authentifie = True
                                        st.success("Compte d'essai créé avec succès !")
                                        time.sleep(1)
                                        st.rerun()
                            else: st.error("Veuillez écrire votre ville d'intervention.")

    with onglet_apropos:
        st.header("ℹ️ À propos de ZELIA Global")
        st.markdown("""
        **ZELIA Global** est une infrastructure numérique internationale dédiée à la mise en relation ultra-rapide entre les particuliers en situation d'urgence domestique et les artisans indépendants de secteur. 
        
        ### 🛡️ Notre Charte de Confiance & Sécurité
        * **Pour les Particuliers** : Le dépôt d'urgence est **100% gratuit et sans aucune inscription**. Votre numéro de téléphone n'est transmis qu'au professionnel certifié qui intercepte votre demande afin de vous garantir une intervention rapide et sans intermédiaire surtaxé.
        * **Pour les Artisans** : Nous luttons contre les plateformes de devis abusives. ZELIA fonctionne sous forme d'un abonnement fixe, transparent et sans engagement, avec une période de test initiale de 12 jours offerte. Pour préserver votre volume d'activité, les places sont strictement limitées à **5 professionnels par secteur**.
        
        ### ⚙️ Comment fonctionne le service ?
        1. **Le Signal** : Un particulier déclare un problème (Ex: fuite d'eau) sur notre interface verte.
        2. **L'Interception** : Notre algorithme pousse l'alerte sur le radar de l'artisan connecté dans la même ville.
        3. **Le Contact** : L'artisan clique sur le bouton sécurisé et appelle directement le client sur son WhatsApp ou téléphone pour fixer l'intervention.
        
        ### ✉️ Support International & Assistance
        Notre équipe technique est à votre écoute 7j/7 pour vous accompagner dans la configuration de votre espace :
        * **Assistance Directe WhatsApp** : Cliquez sur le bouton d'aide en bas de page pour ouvrir un chat privé.
        * **Contact Commercial E-mail** : support.zeliao@gmail.com
        """)

# ==========================================
# 4. LE TABLEAU DE BORD ARTISAN PRO VERROUILLÉ & DOUBLE CALCULATEUR
# ==========================================
else:
    jours_restants_essai = 0
    jours_restants_premium = 0
    essai_valide = False
    premium_valide = False
    date_aujourdhui = datetime.datetime.utcnow().date()
    
    # 1. CALCULATEUR PREMIUM AUTONOME (30 JOURS MENSUELS)
    if st.session_state.user_statut == "actif" and st.session_state.user_date_activation and st.session_state.user_date_activation != "None":
        try:
            # Nettoyage chirurgical pour ne garder QUE les 10 premiers caractères (AAAA-MM-JJ)
            date_nettoye = st.session_state.user_date_activation.strip()[:10]
            date_activation = datetime.datetime.strptime(date_nettoye, "%Y-%m-%d").date()
            jours_ecoules_premium = (date_aujourdhui - date_activation).days
            jours_restants_premium = 30 - jours_ecoules_premium
            if jours_restants_premium > 0:
                premium_valide = True
        except:
            premium_valide = False
            
    # 2. CALCULATEUR D'ESSAI GRATUIT (12 JOURS AUTOMATIQUES)
    if st.session_state.user_date_creation and not premium_valide:
        try:
            # Nettoyage chirurgical de la date de création Supabase
            date_nettoye_crea = st.session_state.user_date_creation.strip()[:10]
            date_inscription = datetime.datetime.strptime(date_nettoye_crea, "%Y-%m-%d").date()
            jours_ecoules_essai = (date_aujourdhui - date_inscription).days
            jours_restants_essai = 12 - jours_ecoules_essai
            if jours_restants_essai > 0:
                essai_valide = True
        except:
            essai_valide = False

    # ARCHITECTURE VISUELLE DU TABLEAU DE BORD DE L'ARTISAN CONNECTÉ
    st.header(f"📬 Radar de chantiers en direct : {st.session_state.user_ville.upper()}")
    st.write(f"🧑‍🔧 Artisan : **{st.session_state.user_metier.upper()}** | 📧 {st.session_state.user_email}")
    
    # AFFICHAGE DYNAMIQUE DU STATUT ET DU TEMPS RESTANT
    if premium_valide:
        st.success(f"👑 Compte Premium ZELIA PRO — Il vous reste **{jours_restants_premium} jours** d'accès illimité.")
    elif essai_valide:
        st.info(f"⏳ Période d'essai gratuite active : Il vous reste **{jours_restants_essai} jours** d'utilisation.")
    else:
        st.error("🔒 Période d'accès expiré (0 jours restants).")

    st.write("---")

    # LE VERROU ANTI-TRICHEUR INTERNATIONALE (Bloque si Essai FINI et Premium FINI)
    if not premium_valide and not essai_valide:
        st.error("🔒 ACCÈS LIMITÉ — Réabonnement Requis")
        st.write("Votre période d'accès gratuit ou payant est terminée. Pour débloquer à nouveau l'accès instantané aux demandes urgentes de votre secteur, veuillez renouveler votre accès professionnel.")
        
        # Le signal automatique blindé qui t'envoie toute la fiche de l'artisan par WhatsApp
        texte_signal = (
            f"🚨 ALERTE RÉABONNEMENT ZELIA 🚨\n\n"
            f"L'artisan suivant souhaite activer son accès Pro :\n"
            f"📧 E-mail : {st.session_state.user_email}\n"
            f"🧑‍🔧 Métier : {st.session_state.user_metier.upper()}\n"
            f"🌍 Ville : {st.session_state.user_ville.upper()}"
        )
        msg_encode = urllib.parse.quote(texte_signal)
        st.link_button("💳 Activer mon accès Pro Zelia (29,99€ / mois)", f"whatsapp://send?phone=242055967601&text={msg_encode}", use_container_width=True, type="primary")
    else:
        # L'accès s'ouvre si l'un des deux chronomètres est valide
        leads_bruts = extraire_leads_strict(st.session_state.user_metier, st.session_state.user_ville)
        if not leads_bruts:
            st.warning("🔎 Aucun chantier direct disponible pour le moment dans votre ville. Le système est en veille permanente.")
        else:
            st.success(f"🔔 {len(leads_bruts)} demandes d'urgences interceptées !")
            for idx, client in enumerate(leads_bruts):
                with st.container(border=True):
                    st.markdown("### 📍 Alerte Client Direct (Zelia Sniper)")
                    st.write(client.get("texte", "Pas de détails."))
                    
                    pitch = f"Bonjour, je suis le {st.session_state.user_metier} disponible immédiatement à {st.session_state.user_ville.upper()} pour votre urgence. Je peux intervenir tout de suite !"
                    st.text_area("💡 Votre réponse rapide pré-rédigée :", value=pitch, height=70, key=f"pitch_{idx}", disabled=True)
                    
                    # Double option d'appel direct
                    num_client = client.get("telephone", "").strip()
                    if num_client:
                        num_propre = "".join(c for c in num_client if c.isdigit())
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            st.link_button("📞 Appel Normal Direct", f"tel:{num_propre}", use_container_width=True)
                        with btn_col2:
                            st.link_button("🟢 WhatsApp Message", f"whatsapp://send?phone={num_propre}&text={urllib.parse.quote(pitch)}", use_container_width=True)

    st.write("---")
    if st.button("🚪 Se déconnecter de l'Espace Pro", use_container_width=True):
        st.session_state.authentifie = False
        st.session_state.user_email = ""
        st.session_state.user_statut = "inactif"
        st.session_state.user_date_creation = ""
        st.session_state.user_date_activation = ""
        st.rerun()
        
# ==========================================
# 5. ASSISTANCE TECHNIQUE & SUPPORT
# ==========================================
st.write("---")
st.markdown("### 🛠️ Assistance Technique Internationale")
c1, c2 = st.columns(2)
with c1:
    texte_aide = urllib.parse.quote("Bonjour Support Zelia, j'ai besoin d'aide avec mon application.")
    # 🚀 FIXATION DU LIEN DE SUPPORT DIRECT VERS TON WHATSAPP BUSINESS SANS PAGE BLANCHE
    st.link_button("💬 Support Client WhatsApp", f"whatsapp://send?phone=242055967601&text={texte_aide}", use_container_width=True)
with c2: 
    # 🚀 CONFIGURATION DE TA VRAIE ADRESSE E-MAIL AVEC LE "O"
    st.link_button("📧 Support Commercial E-mail", "mailto:support.zeliao@gmail.com", use_container_width=True)
    
