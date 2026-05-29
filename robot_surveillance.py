 import sqlite3
import asyncio
import httpx
import urllib.parse
import re
import time
from bs4 import BeautifulSoup

# --- CONFIGURATION INITIALE ---
DB_NAME = "clients.db"

# --- SYSTEME DE TRADUCTION ET DE SOURCING MONDIAL ---
# Permet au robot de comprendre toutes les langues selon le pays demandé par l'application
DICTIONNAIRE_MUNDIAL = {
    "Plombier": {"fr": "plombier", "en": "plumber", "es": "fontanero", "de": "klempner", "it": "idraulico"},
    "Électricien": {"fr": "electricien", "en": "electrician", "es": "electricista", "de": "elektriker", "it": "elettricista"},
    "Mécanicien": {"fr": "mecanicien", "en": "mechanic", "es": "mecanico", "de": "mechaniker", "it": "meccanico"},
    "Menuisier": {"fr": "menuisier", "en": "carpenter", "es": "carpintero", "de": "tischler", "it": "falegname"},
    "Peintre en bâtiment": {"fr": "peintre", "en": "painter", "es": "pintor", "de": "maler", "it": "pittore"},
    "Serrurier": {"fr": "serrurier", "en": "locksmith", "es": "cerrajero", "de": "schlosser", "it": "fabbro"},
    "Maçon": {"fr": "macon", "en": "mason", "es": "albañil", "de": "maurer", "it": "muratore"},
    "Couvreur": {"fr": "couvreur", "en": "roofer", "es": "techador", "de": "dachdecker", "it": "tettoia"},
    "Chauffagiste": {"fr": "chauffagiste", "en": "heating", "es": "calefactor", "de": "heizungsbauer", "it": "riscaldamento"},
    "Climatisation": {"fr": "climatisation", "en": "ac repair", "es": "aire acondicionado", "de": "klimaanlage", "it": "condizionamento"},
    "Jardinier / Paysagiste": {"fr": "jardinier", "en": "gardener", "es": "jardinero", "de": "gärtner", "it": "giardiniere"}
}

# Empreintes sémantiques de recherche selon la langue du pays cible
EMPREINTES_LANGUES = {
    "fr": ["cherche", "besoin", "recommande", "urgence", "depannage"],
    "en": ["looking for", "need a", "recommend", "urgent", "emergency"],
    "es": ["busco", "necesito", "recomendar", "urgente", "emergencia"],
    "de": ["suche", "brauche", "empfehlen", "dringend", "notdienst"],
    "it": ["cerco", "bisogno", "consigliare", "urgente", "emergenza"]
}

# Correspondance entre le pays sélectionné et la langue à utiliser pour la recherche
PAYS_LANGUES = {
    "France": "fr", "Belgique": "fr", "Suisse": "fr",
    "Canada": "en", "Royaume-Uni": "en", "États-Unis": "en",
    "Allemagne": "de", "Espagne": "es", "Italie": "it"
}

# Villes majeures par défaut par pays pour alimenter le scan global
VILLES_MONDE = {
    "France": ["Paris", "Lyon", "Marseille", "Bordeaux", "Lille", "Nantes"],
    "Belgique": ["Bruxelles", "Anvers", "Liège"],
    "Suisse": ["Genève", "Zurich", "Lausanne"],
    "Canada": ["Toronto", "Montréal", "Vancouver"],
    "Royaume-Uni": ["London", "Manchester", "Birmingham"],
    "États-Unis": ["New York", "Los Angeles", "Miami"],
    "Allemagne": ["Berlin", "Munich", "Frankfurt"],
    "Espagne": ["Madrid", "Barcelona", "Valencia"],
    "Italie": ["Roma", "Milano", "Napoli"]
}

COOKIE_FB_TEST = "c_user=XXXXXX; xs=XXXXXX;"
GROUPES_FB_TEST = ["1234567890", "9876543210"]

def inserer_opportunite(titre, ville, pays, niche, lien, plateforme):
    """Insère directement le lead au format exact requis par ZELIA GLOBAL."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute("SELECT id FROM opportunites WHERE lien = ?", (lien,))
    if c.fetchone():
        conn.close()
        return

    c.execute(
        "INSERT INTO opportunites (titre, ville, pays, niche, lien) VALUES (?, ?, ?, ?, ?)",
        (f"[{plateforme}] {titre}", ville, pays, niche, lien)
    )
    conn.commit()
    conn.close()
    print(f"🎉 [ZELIA BOT] Lead mondial enregistré : {titre} ({ville}, {pays})")

# --- MODULE 1 : SCANNER DU WEB MONDIAL (Via DuckDuckGo HTML) ---
async def scanner_web_mondial(client, mot_traduit, langue, ville, pays, métier_cle):
    # Génère des expressions comme : "looking for plumber" London ou "je cherche un plombier" Paris
    if langue == "fr":
        phrase_recherche = f'"je cherche un {mot_traduit}" {ville}'
    elif langue == "en":
        phrase_recherche = f'"looking for {mot_traduit}" {ville}'
    elif langue == "es":
        phrase_recherche = f'"busco un {mot_traduit}" {ville}'
    else:
        phrase_recherche = f"{mot_traduit} {ville}"
        
    query_encodee = urllib.parse.quote(phrase_recherche)
    url = f"https://duckduckgo.com{query_encodee}"
    
    try:
        response = await client.get(url, timeout=12.0)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            resultats = soup.find_all("div", class_="result__body")
            
            for res in resultats:
                snippet = res.find("a", class_="result__snippet")
                lien_h = res.find("a", class_="result__url")
                
                if snippet and lien_h:
                    texte_trouve = snippet.text.lower()
                    # Vérification multilingue intelligente des intentions d'achat/recrutement
                    if any(mot_declencheur in texte_trouve for mot_declencheur in EMPREINTES_LANGUES[langue]):
                        extrait_commentaire = snippet.text[:140] + "..."
                        lien_reel = lien_h["href"]
                        
                        inserer_opportunite(extrait_commentaire, ville, pays, métier_cle, lien_reel, "Web")
    except Exception as e:
        print(f"⚠️ Erreur scan Web ({pays}) pour {métier_cle} - {ville} : {e}")

# --- COMPORTEMENT DOUBLE : OBEIR A L'APPLICATION ET SCANNER EN CONTINU ---
def recuperer_ordres_utilisateurs():
    """Lit les choix des abonnés payants dans la BDD pour exécuter des ordres précis."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # On cible uniquement les abonnés actifs pour économiser les serveurs
    c.execute("SELECT pays_choisi, service_choisi FROM utilisateurs WHERE Paddle_actif = 1")
    ordres = c.fetchall()
    conn.close()
    return ordres

async def execution_moteur():
    print("🤖 Activation du moteur international ZELIA...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    ordres_utilisateurs = recuperer_ordres_utilisateurs()
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        # S'il y a des utilisateurs connectés qui ont configuré le robot : ON LEUR OBÉIT
        if ordres_utilisateurs:
            print(f"🎯 Ordres détectés : Traitement de {len(ordres_utilisateurs)} configurations abonnés.")
            for (pays, métier) in ordres_utilisateurs:
                # Gestion du cas "Tous" ou ciblage précis
                pays_a_scanner = [p for p in PAYS_LANGUES.keys()] if pays == "Tous" else [pays]
                metiers_a_scanner = [m for m in DICTIONNAIRE_MUNDIAL.keys() if m != "Tous"] if métier == "Tous" else [métier]
                
                for p_cible in pays_a_scanner:
                    langue_cible = PAYS_LANGUES.get(p_cible, "en")
                    villes_cibles = VILLES_MONDE.get(p_cible, ["London"])
                    
                    for m_cible in metiers_a_scanner:
                        mot_traduit = DICTIONNAIRE_MUNDIAL[m_cible].get(langue_cible, m_cible.lower())
                        
                        for ville in villes_cibles:
                            print(f"📡 [Priorité Abonné] Scan : {m_cible} ({mot_traduit}) à {ville}, {p_cible}...")
                            await scanner_web_mondial(client, mot_traduit, langue_cible, ville, p_cible, m_cible)
                            await asyncio.sleep(2)
        else:
            # Mode surveillance globale automatique par défaut s'il n'y a aucun ordre
            print("🌐 Aucun ordre utilisateur en attente. Lancement de la routine de surveillance globale...")
            for p_cible, langue_cible in PAYS_LANGUES.items():
                villes_cibles = VILLES_MONDE[p_cible][:2] # Prend les 2 villes majeures pour la routine
                for m_cible, traductions in DICTIONNAIRE_MUNDIAL.items():
                    mot_traduit = traductions.get(langue_cible)
                    for ville in villes_cibles:
                        await scanner_web_mondial(client, mot_traduit, langue_cible, ville, p_cible, m_cible)
                        await asyncio.sleep(2)

if __name__ == "__main__":
    # Exécution simple adaptée au Cron Job toutes les 5 minutes de Render
    asyncio.run(execution_moteur())
    print("😴 Routine terminée avec succès.")
