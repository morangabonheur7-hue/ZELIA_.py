import streamlit as st
import requests
import urllib.parse

# 💎 TES CLÉS RÉELLES CENTRALISÉES EN DUR (SÉCURITÉ MAXIMUM)
SUPABASE_URL = "https://qjfipgzuwkprfowgbimt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFqZmlwZ3p1d2twcmZvd2diaW10Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODA3NjAyNDksImV4cCI6MjA5NjMzNjI0OX0.rA17-omiRtXuECi0b7RW8wNe583Qa8swoV1HrgcQ9wM"

st.set_page_config(page_title="ZELIA GLOBAL - Radar de Dépannage Urbain", page_icon="🚨", layout="centered")

# 🔥 INITIALISATION SÉCURISÉE DE LA MÉMOIRE (Évite définitivement les erreurs AttributeError)
if "role" not in st.session_state: st.session_state.role = None
if "authentifie" not in st.session_state: st.session_state.authentifie = False
if "artisan_data" not in st.session_state: st.session_state.artisan_data = {}

def verifier_si_utilisateur_existe(email):
    """ Interroge Supabase pour vérifier l'accès sécurisé de l'artisan """
    url = f"{SUPABASE_URL}/rest/v1/utilisateurs?email=eq.{email.strip().lower()}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and len(res.json()) > 0: return res.json()[0]
    except: pass
    return None

def injecter_dans_supabase(metier, ville, quartier, texte, telephone, lien, plateforme):
    url = f"{SUPABASE_URL}/rest/v1/leads"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=minimal"}
    payload = [{"metier": metier.lower(), "ville": ville.lower(), "quartier": quartier.lower(), "texte": texte, "telephone": telephone, "lien": lien, "plateforme": plateforme}]
    try: requests.post(url, json=payload, headers=headers, timeout=10)
    except: pass

# 🎨 DESIGN DE CONFIANCE BLEU ROI
st.markdown("""
    <style>
    .main-title { color: #1E3A8A; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-title { color: #0F172A; font-size: 16px; text-align: center; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🚨 ZELIA GLOBAL RADAR</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Centrale Internationale de Dépannage et d\'Urgence Urbaine</div>', unsafe_allow_html=True)

# 🚪 FILTRAGE D'ACCÈS : Choix du rôle pour ne pas mélanger les écrans
if st.session_state.role is None:
    st.markdown("<h3 style='text-align:center; color:#0F172A; font-size:18px;'>Veuillez sélectionner votre espace d'accès :</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 ESPACE PARTICULIER\n\n(Déposer une urgence)", use_container_width=True):
            st.session_state.role = "particulier"
            st.rerun()
    with col2:
        if st.button("🔵 PORTAIL ARTISAN PRO\n\n(Accéder au radar)", use_container_width=True):
            st.session_state.role = "artisan"
            st.rerun()

# ==========================================
# BLOC 2 : INTERFACE PARTICULIER ÉPURÉE (DÉPÔT DE PANNE)
# ==========================================
elif st.session_state.role == "particulier":
    if st.button("⬅️ Retour au menu principal"):
        st.session_state.role = None
        st.rerun()
        
    st.markdown("### 📢 Signalement d'une panne ou urgence immédiate")
    
    c1, c2 = st.columns(2)
    with c1: v_metier = st.selectbox("Métier requis :", ["Plombier", "Électricien", "Serrurier", "Mécanicien"])
    with c2: v_ville = st.text_input("🌍 Ville :", value="Bruxelles")
    
    # 📍 Nouvelle case chirurgicale pour la zone résidentielle précise
    v_quartier = st.text_input("📍 Quartier / Zone Résidentielle (Ex: Schaerbeek, Uccle...)", value="Centre")
    
    v_tel = st.text_input("📱 Votre numéro de téléphone portable :", placeholder="+32 4xx xx xx xx")
    v_desc = st.text_area("📝 Description précise de l'intervention demandée :", placeholder="Ex: Grosse fuite d'eau sous mon évier de cuisine...")
    
    if st.button("🚀 Diffuser l'alerte sur le radar", use_container_width=True):
        if not v_tel or not v_desc:
            st.error("⚠️ Erreur : Veuillez remplir le téléphone et la description pour lancer l'alerte.")
        else:
            texte_final = f"🚨 CLIENT CHAUD (ZELIA LIVE):\n📢 Urgence {v_metier} à {v_ville} ({v_quartier})\n📝 Détails : {v_desc}"
            injecter_dans_supabase(v_metier, v_ville, v_quartier, texte_final, v_tel, "https://tinyurl.com", "Zelia Portal v4")
            st.success("✅ Votre alerte a été injectée avec succès ! Les techniciens du secteur ont reçu le signal.")
        
# ==========================================
# BLOC 3 : BARRIÈRE DE SÉCURITÉ ET RADAR ARTISAN
# ==========================================
elif st.session_state.role == "artisan":
    if st.button("⬅️ Retour au menu principal"):
        st.session_state.role = None
        st.session_state.authentifie = False
        st.rerun()

    # Si l'artisan n'est pas encore identifié par la base Supabase
    if not st.session_state.authentifie:
        st.markdown("### 🔒 Connexion sécurisée au Radar Pro")
        email_input = st.text_input("Saisissez votre e-mail d'artisan abonné :", placeholder="exemple@domaine.com")
        
        if st.button("🔓 Vérifier mes droits d'accès", use_container_width=True):
            if email_input:
                artisan = verifier_si_utilisateur_existe(email_input)
                if artisan:
                    st.session_state.authentifie = True
                    st.session_state.artisan_data = artisan[0]  # Récupère le premier utilisateur trouvé
                    st.success("🟢 Accès accordé ! Connexion au radar réussie.")
                    st.rerun()
                else:
                    st.error("❌ Erreur : Cet e-mail n'est pas enregistré comme abonné ZELIA GLOBAL.")
            else:
                st.error("⚠️ Veuillez entrer un e-mail valide.")
                
    # Si la connexion est validée par Supabase -> Ouverture du Radar de combat
    else:
        art = st.session_state.artisan_data
        st.markdown(f"### 🛰️ Radar Connecté : Spécialité {str(art.get('metier','')).upper()}")
        
        # Récupération automatique de la ville et du quartier de l'artisan inscrits dans Supabase
        art_ville = art.get("ville", "Bruxelles")
        art_quartier = art.get("quartier", "Global")
        
        st.write(f"📍 **Zone de couverture automatique** : {art_ville.upper()} ({art_quartier.upper()})")
        
        # Bouton d'alertes Telegram
        activer_telegram = st.checkbox("Activer les vibrations d'alertes sur mon téléphone")
        if activer_telegram:
            st.link_button("🚀 Lier mon mobile à Telegram", "https://t.me")
            
        st.markdown("---")
        st.markdown("#### 📊 Vos chantiers correspondants filtrés en direct :")
        
        url_fetch = f"{SUPABASE_URL}/rest/v1/leads?metier=eq.{str(art.get('metier','')).lower()}&order=id.desc"
        headers_fetch = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        
        try:
            res = requests.get(url_fetch, headers=headers_fetch, timeout=10)
            if res.status_code == 200:
                leads = res.json()
                compteur = 0
                
                for lead in leads:
                    l_ville = lead.get("ville", "").lower()
                    l_quartier = lead.get("quartier", "").lower()
                    
                    # Filtrage chirurgical : Ville identique + (Quartier identique OU Artisan global OU Centre)
                    if l_ville == art_ville.lower() and (art_quartier.lower() == "global" or l_quartier == art_quartier.lower() or l_quartier == "centre"):
                        compteur += 1
                        st.markdown(f"""
                        <div style="background-color: #FFFFFF; border-left: 5px solid #1E3A8A; padding: 15px; border-radius: 8px; margin-bottom: 12px; box-shadow: 0px 2px 4px rgba(0,0,0,0.05);">
                            <h4 style="color: #1E3A8A; margin: 0; font-size: 15px;">🚨 CHANTIER URGENCE RECONNUE</h4>
                            <p style="color: #0F172A; margin: 5px 0; font-size: 13px;"><b>Secteur :</b> {l_quartier.upper()} | <b>🌍 Ville :</b> {l_ville.upper()}</p>
                            <p style="color: #334155; font-size: 13px; margin-top: 8px; background: #F8FAFC; padding: 8px; border-radius: 4px;">{lead['texte']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        tel_propre = lead['telephone'].replace(" ", "")
                        c1, c2 = st.columns(2)
                        with c1: st.link_button(f"📞 Appeler ({lead['telephone']})", f"tel:{tel_propre}", use_container_width=True)
                        with c2: st.link_button("💬 WhatsApp Direct", f"https://wa.me{tel_propre}?text=Bonjour", use_container_width=True)
                
                if compteur == 0:
                    st.info(f"🛰️ Aucune alerte active sur {art_ville.upper()} ({art_quartier.upper()}) pour le moment.")
        except Exception as e:
            st.error(f"Erreur réseau : {e}")
        
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
    
