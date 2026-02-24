"""
SMART EXCHANGE - Application de Facturation Pro
Streamlit Cloud Ready - v2.0
"""
import streamlit as st
import pandas as pd
import base64
import io
import os
import re
import json
import requests
from datetime import datetime, date
from fpdf import FPDF

# ═══════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════
st.set_page_config(
    page_title="SMART EXCHANGE · Facturation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COMPANY = {
    "name": "SMART EXCHANGE",
    "siren": "982 412 132",
    "siret": "982 412 132 00010",
    "tva": "FR48982412132",
    "email": "Smartexchange673@gmail.com",
}

# ═══════════════════════════════════════
# IMAGES - Load and encode
# ═══════════════════════════════════════
def load_image_b64(filename):
    """Load an image from the app directory and return base64."""
    # Try multiple paths for compatibility
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        os.path.join(os.getcwd(), filename),
        filename,
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    return ""

BANNER_B64 = load_image_b64("banner.png")
BG_B64 = load_image_b64("bg.png")

# ═══════════════════════════════════════
# CSS
# ═══════════════════════════════════════
st.markdown(f"""
<style>
    /* Theme */
    .stApp {{
        background: #0a0a14 !important;
        color: #FFFFFF !important;
    }}
    .stApp > div, .stApp > div > div {{
        color: #FFFFFF !important;
    }}
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown div,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: #FFFFFF !important;
    }}
    /* Force all text elements */
    p, span, div, label, h1, h2, h3, h4, h5, h6 {{
        color: inherit;
    }}
    .element-container {{
        color: #FFFFFF !important;
    }}
    .stApp::before {{
        content: '';
        position: fixed;
        inset: 0;
        background-image: url("data:image/png;base64,{BG_B64}");
        background-size: cover;
        background-position: center;
        opacity: 0.05;
        pointer-events: none;
        z-index: 0;
    }}
    #MainMenu {{visibility: hidden}}
    footer {{visibility: hidden}}
    header {{visibility: hidden}}
    .block-container {{
        padding-top: 0.5rem !important;
        max-width: 1100px;
    }}

    /* Banner */
    .banner {{
        width: 100%;
        border-radius: 20px;
        overflow: hidden;
        position: relative;
        margin-bottom: 1rem;
        box-shadow: 0 8px 40px rgba(255,140,50,0.12);
        border: 1px solid rgba(255,160,50,0.3);
    }}
    .banner img {{
        width: 100%;
        height: 180px;
        object-fit: cover;
        object-position: center 30%;
        display: block;
    }}
    .banner-ov {{
        position: absolute;
        inset: 0;
        background: linear-gradient(180deg, rgba(10,10,20,0.1) 0%, rgba(10,10,20,0.85) 100%);
        display: flex;
        align-items: flex-end;
        padding: 1.2rem 1.5rem;
    }}
    .b-title {{
        font-family: Impact, 'Arial Black', sans-serif;
        font-size: 2.2rem;
        color: white;
        letter-spacing: 4px;
        line-height: 1;
        text-shadow: 0 2px 20px rgba(255,140,50,0.3);
    }}
    .b-title span {{ color: #FF8C32; }}
    .b-sub {{
        font-size: 0.72rem;
        color: #FFB347;
        letter-spacing: 3px;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 2px;
    }}
    .b-line {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #FF8C32, #FFB347, transparent);
    }}

    /* Cards */
    .sec {{
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 16px;
        padding: 1.3rem;
        margin: 0.7rem 0;
        backdrop-filter: blur(16px);
    }}
    .sec:hover {{ border-color: rgba(255,160,50,0.3); }}
    .sec-h {{
        color: #FF8C32;
        font-size: 0.95rem;
        font-weight: 700;
        margin-bottom: 0.9rem;
        padding-bottom: 0.6rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* Totals */
    .tot-box {{
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }}
    .tot-box .lbl {{
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 4px;
    }}
    .tot-box .val {{
        font-size: 1.6rem;
        font-weight: 900;
        font-family: 'Courier New', monospace;
    }}
    .tot-ht {{
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
    }}
    .tot-ht .lbl {{ color: rgba(255,255,255,0.4); }}
    .tot-ht .val {{ color: #eaeaf2; }}
    .tot-tva {{
        background: rgba(255,140,50,0.06);
        border: 1px solid rgba(255,160,50,0.3);
    }}
    .tot-tva .lbl {{ color: rgba(255,140,50,0.7); }}
    .tot-tva .val {{ color: #FF8C32; }}
    .tot-ttc {{
        background: linear-gradient(135deg, #FF6B1A, #FF8C32, #FFB347);
        box-shadow: 0 6px 30px rgba(255,140,50,0.25);
    }}
    .tot-ttc .lbl {{ color: rgba(10,10,20,0.5); }}
    .tot-ttc .val {{ color: #0a0a14; font-size: 1.8rem; }}

    /* Widgets */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea {{
        background: rgba(26,26,46,0.95) !important;
        border: 1px solid rgba(255,140,50,0.2) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }}
    .stTextInput > div > div > input::placeholder {{
        color: rgba(255,255,255,0.4) !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: #FF8C32 !important;
        box-shadow: 0 0 0 2px rgba(255,140,50,0.15) !important;
    }}
    /* Labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label, 
    .stDateInput label, .stTextArea label {{
        color: #FFFFFF !important;
    }}
    /* Date input */
    .stDateInput > div > div > input {{
        background: rgba(26,26,46,0.95) !important;
        border: 1px solid rgba(255,140,50,0.2) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
    }}
    .stButton > button {{
        background: linear-gradient(135deg, #FF6B1A, #FF8C32, #FFB347) !important;
        color: #0a0a14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 15px rgba(255,140,50,0.35) !important;
    }}
    .stDownloadButton > button {{
        background: linear-gradient(135deg, #FF6B1A, #FF8C32, #FFB347) !important;
        color: #0a0a14 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        width: 100%;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 3px; }}
    .stTabs [data-baseweb="tab"] {{
        background: rgba(255,255,255,0.03);
        border-radius: 10px 10px 0 0;
        border: 1px solid rgba(255,255,255,0.06);
        color: white;
        padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background: rgba(255,140,50,0.12) !important;
        border-bottom: 2px solid #FF8C32 !important;
    }}
    .sep {{
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,160,50,0.3), transparent);
        margin: 0.4rem 0;
    }}
    .foot {{
        text-align: center;
        padding: 1rem;
        color: rgba(255,255,255,0.25);
        font-size: 0.7rem;
    }}
    .badge {{
        display: inline-block;
        background: rgba(255,140,50,0.12);
        color: #FF8C32;
        border: 1px solid rgba(255,160,50,0.3);
        border-radius: 20px;
        padding: 3px 13px;
        font-size: 0.7rem;
        font-weight: 700;
    }}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════
if "lines" not in st.session_state:
    st.session_state.lines = []
if "lid" not in st.session_state:
    st.session_state.lid = 0
if "clients" not in st.session_state:
    st.session_state.clients = {}

# ── Clients par defaut (toujours disponibles) ──
DEFAULT_CLIENTS = {
    "RAF MARKET": {
        "addr": "196 avenue du Maine 75014",
        "siret": "99031400700016",
        "tva": "FR37990314007",
    },
}

# ── Persistent client storage ──
CLIENTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clients.json")

def load_clients():
    """Load clients from JSON file on disk"""
    clients = dict(DEFAULT_CLIENTS)  # Start with defaults
    try:
        if os.path.exists(CLIENTS_FILE):
            with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                clients.update(saved)  # Merge saved clients (overrides defaults if same name)
    except:
        pass
    return clients

def save_clients(clients_dict):
    """Save clients to JSON file on disk"""
    try:
        with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(clients_dict, f, ensure_ascii=False, indent=2)
    except:
        pass

# Load saved clients on startup (always includes defaults)
if not st.session_state.clients:
    st.session_state.clients = load_clients()
# Ensure defaults are always present even if session already loaded
for k, v in DEFAULT_CLIENTS.items():
    if k not in st.session_state.clients:
        st.session_state.clients[k] = v

# ═══════════════════════════════════════
# SIDEBAR - Config OCR / IA
# ═══════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    st.markdown("---")
    st.markdown("**📋 Infos entreprise**")
    st.markdown(f"""
    <div style='font-size:.75rem;color:rgba(255,255,255,0.5);line-height:1.6'>
    {COMPANY['name']}<br>
    SIREN: {COMPANY['siren']}<br>
    TVA: {COMPANY['tva']}<br>
    {COMPANY['email']}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════
def ht_from_ttc(ttc, tva):
    if tva <= 0:
        return ttc
    return round(ttc / (1 + tva / 100), 2)

def ttc_from_ht(ht, tva):
    return round(ht * (1 + tva / 100), 2)

def fmt(val):
    return f"{val:,.2f} €".replace(",", " ").replace(".", ",")

def add_line(desc="", qty=1, pu_ht=0.0, tva=20.0, tot_ttc_override=None):
    st.session_state.lid += 1
    st.session_state.lines.append({
        "id": st.session_state.lid,
        "desc": desc, "qty": qty, "pu_ht": pu_ht, "tva": tva,
        "tot_ttc_override": tot_ttc_override,  # Exact TTC from scan (no rounding)
    })

# ═══════════════════════════════════════
# SCAN - Claude Vision reads invoice directly
# ═══════════════════════════════════════

def scan_invoice_with_vision(image_bytes, mime_type="image/jpeg"):
    """
    Send invoice image or PDF DIRECTLY to Claude Vision API.
    Claude sees the image, reads every line, and returns structured JSON.
    No OCR middleman, no regex — Claude reads the invoice like a human.
    Supports: JPEG, PNG, PDF (converted to images via pdf2image or fitz).
    """
    # Key lookup chain: Streamlit secrets > session state > env var
    api_key = ""
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
    except Exception:
        pass
    if not api_key:
        api_key = st.session_state.get("anthropic_key", "")
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        return None, "Cle API non trouvee. Ajoutez ANTHROPIC_API_KEY dans les Secrets Streamlit Cloud (Settings → Secrets)."

    # Validate key format
    api_key = api_key.strip()
    if not api_key.startswith("sk-"):
        return None, f"Format de cle invalide (doit commencer par sk-). Verifiez dans Settings → Secrets."

    # ── Convert PDF pages to images + extract text ──
    images_b64 = []
    pdf_text = ""
    if mime_type == "application/pdf":
        try:
            import fitz  # PyMuPDF
            pdf_doc = fitz.open(stream=image_bytes, filetype="pdf")
            for page_num in range(min(len(pdf_doc), 10)):  # Max 10 pages
                page = pdf_doc[page_num]
                # Extract text (much more reliable for column data)
                page_text = page.get_text("text")
                if page_text.strip():
                    pdf_text += f"\n--- PAGE {page_num+1} ---\n{page_text}"
                # Also render image as backup
                mat = fitz.Matrix(2.0, 2.0)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                images_b64.append({
                    "b64": base64.b64encode(img_data).decode("ascii"),
                    "media": "image/png",
                })
            pdf_doc.close()
        except ImportError:
            return None, "Installez PyMuPDF: ajoutez 'PyMuPDF>=1.23.0' dans requirements.txt"
        except Exception as e:
            return None, f"Erreur lecture PDF: {str(e)}"
    else:
        # Regular image
        media = "image/jpeg"
        if mime_type == "image/png":
            media = "image/png"
        elif mime_type == "image/webp":
            media = "image/webp"
        images_b64.append({
            "b64": base64.b64encode(image_bytes).decode("ascii"),
            "media": media,
        })

    if not images_b64:
        return None, "Aucune image extraite du fichier"

    prompt = """Tu es un comptable expert qui sait lire TOUTES les factures fournisseur, quel que soit leur format.
Si un TEXTE EXTRAIT DU PDF est fourni au-dessus des images, UTILISE-LE EN PRIORITE pour les valeurs numeriques (quantites, prix, montants). Le texte extrait est PLUS FIABLE que la lecture des images pour les chiffres.

OBJECTIF: Extraire chaque article produit de cette facture avec description, quantite et prix unitaire TTC en euros.

METHODE D'ANALYSE (suis ces etapes dans l'ordre):

ETAPE 1 - IDENTIFIER LE FOURNISSEUR ET LE FORMAT:
- Lis le nom de l'entreprise emettrice (en-tete, logo, SIRET)
- Repere la devise (EUR, €) et si les montants ont des decimales ou non
- SI les montants n'ont PAS de decimales (ex: 1807, 5454, 301) et sont des entiers → les prix sont probablement en CENTIMES → tu devras diviser par 100
- SI les montants ONT des decimales (ex: 18.07, 54.54, 3.01) → les prix sont en EUROS directement

ETAPE 2 - COMPRENDRE LA STRUCTURE DES COLONNES:
- Cherche la ligne d'en-tete du tableau (souvent en gras ou en haut)
- Identifie CHAQUE colonne: designation/description, quantite (QTE/Qte/Nbre), prix unitaire HT, prix unitaire TTC, total HT, total TTC, taux TVA, etc.
- Certaines factures ont BEAUCOUP de colonnes (poids, volume, alcool pur, marge, prix conseille...) → ignore tout sauf description, qte, prix et TVA
- S'il y a "Nbre Colis" ET "QTE", prends QTE (c'est le nombre total d'unites)
- DESCRIPTIONS MULTI-LIGNES: certains articles ont leur nom sur 2 lignes (ex: "BTE 50CL BIERE LA CHOUFFE 8°" puis "BLONDE" sur la ligne suivante). Regroupe-les en UN seul article.
- COMPTE BIEN: verifie que tu as extrait EXACTEMENT autant d'articles qu'il y a de lignes avec un montant sur la facture

ATTENTION PIEGE - CONFUSION DE COLONNES:
Sur certaines factures (Codifrance notamment), il y a beaucoup de colonnes numeriques cote a cote:
Code | Nbre Colis | QTE | Description | PU HT | MONTANT HT | TVA | PU TTC | PRIX CONSEILLE | MARGE | MONTANT TTC

EXEMPLE CONCRET D'UNE LIGNE CODIFRANCE:
"1407    24   BTE 4X50CL HEINEKEN 5°    426   10224   2   511   286   10,51   12269"
- 1407 = code article (IGNORER)
- 24 = QTE (nombre d'unites) ← C'EST CA LA QUANTITE (c'est AVANT la description!)
- BTE 4X50CL HEINEKEN 5° = description
- 426 = PU HT en CENTIMES (4.26€) ← CE N'EST PAS LA QUANTITE ! C'est APRES la description
- 10224 = MONTANT HT en centimes
- 2 = code TVA (2 = 20%)
- 511 = PU TTC en centimes (5.11€)
- 286 = prix conseille (IGNORER)
- 10,51 = marge % (IGNORER)
- 12269 = MONTANT TTC en centimes (122.69€) ← C'EST CA LE TOTAL TTC

REGLE QTE: la quantite est le nombre AVANT la description du produit, PAS le nombre juste APRES.
Exemples de QTE correctes: 6, 12, 24, 36 (rarement plus de 50)
Si tu trouves des QTE comme 87, 115, 139, 251, 304, 426, 702 → C'EST FAUX, c'est le PU HT en centimes!

REGLES POUR NE PAS CONFONDRE:
- La QTE pour des bieres/alcools est generalement entre 1 et 50 (rarement plus)
- Si tu trouves des QTE de 100, 200, 400+ pour des bieres → tu lis la MAUVAISE colonne (probablement le PU HT en centimes)
- Le PU HT est en centimes sur Codifrance (ex: 251 = 2.51€), NE LE CONFONDS PAS avec la QTE
- La QTE est le PREMIER chiffre avant la description du produit
- Verifie: QTE × PU TTC (en euros) doit ≈ MONTANT TTC (en euros). Si ca ne colle pas, tu as les mauvaises colonnes
- IMPORTANT: 6 × 3.01 = 18.06 ≈ 18.07 ✓ (correct) vs 251 × 0.07 = 17.57 ✗ (faux = tu confonds PU HT et QTE)

ETAPE 3 - DISTINGUER PRODUITS vs NON-PRODUITS:
Un PRODUIT a vendre en epicerie, c'est:
- De la nourriture, des boissons, de l'alcool, des snacks, des produits menagers, etc.
- Ca a un nom reconnaissable (marque, contenance, description)

=== GUIDE SPECIFIQUE FACTURES SUPERMARCHES (Carrefour, Auchan, Leclerc, etc.) ===

Si la facture vient d'un supermarche (ticket de caisse ou facture avec "Remise immediate"):

REMISES IMMEDIATES: SOUSTRAIRE DU PRODUIT QUI PRECEDE !
- Chaque ligne "Remise immediate -X.XX" s'applique au produit JUSTE AU-DESSUS
- Soustrais la remise du montant du produit precedent
- Exemple: DOVE ORIG ZERO 2X1 = 7.79, Remise immediate -13.24 → montant net = 7.79 - 13.24 = NEGATIF?
  Non! La remise s'applique a l'ENSEMBLE des lignes du meme produit au-dessus.
  Si DOVE apparait avec 7.79 puis remise -13.24 puis DOVE 31.16: la remise porte sur le groupe.
  Total DOVE = 7.79 + 31.16 - 13.24 = 25.71€ pour 5 unites
- Le total final = "Total a payer" (APRES remises)

PRODUITS EN DOUBLE AVEC REMISE:
- Quand un produit apparait sur plusieurs lignes, avec une remise au milieu:
  PRODUIT ligne1: montant1
  Remise immediate: -R
  PRODUIT ligne2: montant2
  → Fusionne: total = montant1 + montant2 - R, qty = qty1 + qty2

MONTANTS TTC:
- Les montants sur un ticket Carrefour sont DEJA en TTC
- Le taux TVA est indique devant chaque produit (5.5% ou 20.0%)
- Utilise le "Total a payer" comme net_a_payer (PAS le "Total avant remises")

=== FIN GUIDE SUPERMARCHES ===

PAS un produit (A IGNORER COMPLETEMENT - NE PAS INCLURE DANS LE JSON):
- *** PALETTES ***: PAL 80X120, PAL.80X120, CHEP, LPR, LOGIPAL = JAMAIS dans le JSON !
- Emballages: consigne, caisse plastique, bac
- Avoirs/retours: lignes avec "AVOIR", montants negatifs, credits
- "Remise immediate" → NE PAS inclure comme article, mais SOUSTRAIRE du produit precedent
- En-tetes de section: "*** SPIRITUEUX Total:", "*** CAVE Total:", "*** BRASSERIE Total:", etc.
- Totaux: sous-total, total HT, total TTC, net a payer, montant TVA
- Frais: transport, port (ex: "FRAIS DE PORT")
- MAIS garder "LIVRAISON AC STANDARD" → c'est un frais facturable, l'inclure comme article avec sa TVA
- Texte legal: mentions, SIRET, IBAN, BIO*, MSC, ASC
- "PRIX AU KG OU AU LITRE:" → IGNORER (info complementaire)
- Lignes commencant par ⑨:NC... → IGNORER (codes regie)
- "N° GTIN et LOT" → IGNORER (tracabilite)
- "_BEST_BEFORE_DATE" → IGNORER (date peremption)

LIGNES SPECIALES A INTEGRER DANS LE PRODUIT (NE PAS CREER DE LIGNE SEPAREE):
- "Plus : COTIS. SECURITE SOCIALE" suivi d'un montant → AJOUTER ce montant au montant HT du produit PRECEDENT
  Exemple: WHISKY montant=57.09, puis COTIS=8.94 → montant final du WHISKY = 57.09 + 8.94 = 66.03
- "Offre Achetez Plus Payez Moins" suivi d'un montant negatif (ex: 13,68-) → SOUSTRAIRE du produit PRECEDENT
  Exemple: VODKA montant=137.52, puis Offre=-13.68 → montant final = 137.52 - 13.68 = 123.84

=== GUIDE SPECIFIQUE FACTURES METRO ===

Si la facture vient de METRO (reconnaissable a "METRO France", "METRO VITRY", etc.):

STRUCTURE METRO:
- Colonnes: EAN | N°article | Designation | Regie | Vol% | VAP | Poids | Prix unitaire | Qte Colisage | Montant | TVA
- La colonne "Montant" est en **HT** (PAS TTC !)
- Pour obtenir le TTC: Montant HT × 1.055 (si TVA B) ou × 1.20 (si TVA D ou C)

QUANTITE METRO:
- La colonne "Qte Colisage" contient DEUX nombres: ex "6  3" ou "24  1" ou "12  2"
- Le 1er nombre = unites par colis, le 2eme = nombre de colis commandes
- La QUANTITE TOTALE pour la facture = 1er nombre × 2eme nombre
- Exemples: "6 3" → 6×3=18 unites, "24 1" → 24×1=24 unites, "12 2" → 12×2=24 unites, "1 1" → 1 unite
- Le MONTANT = Prix unitaire × 2eme nombre (colisage)

TVA METRO:
- Code B = 5.50% (boissons sans alcool, alimentaire, eaux, oeufs, biscuits)
- Code C = 20.00% (services, livraison)
- Code D = 20.00% (alcool, bieres, vins, spiritueux)
- Le code TVA est la LETTRE dans la colonne "TVA" a droite du montant

ARTICLES DUPLIQUES METRO:
- Un MEME produit peut apparaitre PLUSIEURS FOIS (ex: HEINEKEN 3 fois)
- Ce sont des ACHATS SEPARES → garde-les TOUS, ne fusionne PAS
- Verifie que tu as bien CHAQUE ligne avec un montant

SECTIONS METRO A SCANNER (ne saute aucune section!):
- SPIRITUEUX (alcools forts: whisky, vodka, gin, rhum, tequila, liqueurs, pastis) → TVA D (20%)
- CAVE (vins rouges, blancs, roses: Bordeaux, Bourgogne, Cotes du Rhone, IGP, etc.) → TVA D (20%)
- CHAMPAGNES (champagne, prosecco, mousseux, cremant) → TVA D (20%)
- BRASSERIE (bieres + softs + eaux + energy drinks) → bieres TVA D (20%), softs/eaux/energy TVA B (5.5%)
- EPICERIE SUCREE (biscuits, chocolat, snacks) → TVA B (5.5%) sauf exceptions
- BEURRE OEUF (oeufs, produits frais, lait, Alpro, Candy Up, yaourts, cremes, jus, fruits) → TVA B (5.5%)
- FROMAGE (beurre, fromages) → TVA B (5.5%)
- TRAITEUR (sandwiches, pastabox, plats prepares) → TVA B (5.5%)
- CHARCUTERIE (saucisson, chorizo, mortadelle, pave, berger) → TVA B (5.5%)
- DROGUERIE (gobelets, accessoires) → TVA D (20%)
- Articles divers (livraison) → TVA C (20%)

ATTENTION: Certaines sections ont BEAUCOUP de produits (ex: BEURRE OEUF peut avoir 25+ articles).
Ne saute AUCUN article, meme les petits montants (Alpro 2.40, Alpro 2.65, etc.).

ATTENTION PAGES: Cette facture peut avoir 5, 8, 10 ou 11 pages !
- SCANNE TOUTES LES PAGES de la premiere a la derniere
- Ne t'arrete PAS a la page 5 ou 6 !
- Continue JUSQU'A ce que tu voies "Total H.T." dans le recapitulatif TVA
- CHAQUE page peut contenir des produits importants
- Les VINS (CAVE) sont souvent en milieu de facture (pages 6-7)
- Les CHAMPAGNES sont souvent juste apres la CAVE
- Les BIERES (BRASSERIE) sont souvent pages 8-9
- L'EPICERIE est souvent en fin de facture

REGLE TVA METRO ABSOLUE:
Chaque article Metro a un code TVA dans la derniere colonne (B, C, ou D).
- B = 5.5% → UNIQUEMENT pour les boissons sans alcool, alimentaire, snacks
- D = 20% → Alcools (spiritueux, vins, champagnes, bieres), droguerie
- C = 20% → Livraison, services
UTILISE TOUJOURS le code de la facture. NE CHANGE JAMAIS un D en B ou inversement.
Les BIERES sont TOUJOURS en D (20%) sur Metro, JAMAIS en B.

VERIFICATION METRO:
- Nombre total d'articles: generalement 60-90+ pour une grosse facture (peut aller jusqu'a 100+)
- Total HT page finale: compare ta somme de montants HT avec le "Total H.T." de la facture
- Si tu as beaucoup moins d'articles que prevu, tu as saute des sections ou des pages
- COMPTE tes articles a la fin et verifie que la somme HT colle avec le Total H.T. de la facture

VERIFICATION FINALE OBLIGATOIRE (fais-la avant de repondre):
1. Lis le "Total H.T." en fin de facture
2. Additionne tous tes montants "total_ht" dans ton JSON
3. Si l'ecart > 5€, tu as OUBLIE des articles ou des COTIS → relis la facture
4. Verifie que tu as toutes les sections: SPIRITUEUX + CAVE + CHAMPAGNES + BRASSERIE + EPICERIE + etc.
5. Verifie que chaque spiritueux a sa COTIS ajoutee

COTIS ET REMISES METRO (TRES IMPORTANT - NE RATE AUCUNE COTIS):
Sur les factures Metro, presque CHAQUE produit alcool (spiritueux, bieres) est suivi d'une ou plusieurs lignes supplementaires:

1) "Plus : COTIS. SECURITE SOCIALE" avec un montant positif
   → AJOUTER ce montant au montant HT du produit qui PRECEDE
   → CHAQUE alcool a une COTIS, ne l'oublie pas !
   
2) "Offre Achetez Plus Payez Moins" avec un montant negatif (ex: 13,68-)
   → SOUSTRAIRE du produit qui PRECEDE
   ATTENTION REMISES DUPLIQUEES: si le MEME produit apparait plusieurs fois avec chacun une ligne "Offre" du MEME montant,
   c'est UNE SEULE remise globale ! Ne la soustrait qu'UNE SEULE FOIS au total.
   Methode: soustrait la remise UNIQUEMENT de la PREMIERE occurrence du produit. La deuxieme garde son montant SANS remise.
   Exemple: 2× VODKA POLIAKOV 70CL, chacune avec "Offre 13,68-"
   → Premiere POLIAKOV: 137.52 - 13.68 + 29.31 = 153.15
   → Deuxieme POLIAKOV: 137.52 + 29.31 = 166.83 (PAS de remise !)

METHODE: Pour chaque produit alcool, regarde la ou les lignes qui suivent AVANT le produit suivant.
Si tu vois "COTIS" → ajoute le montant
Si tu vois "Offre" → soustrais le montant SEULEMENT si c'est la premiere fois que tu vois cette remise pour ce produit

Exemples concrets:
  VODKA POLIAKOV 37.5D 70CL (1er)  montant=137,52  TVA=D
  Offre Achetez Plus Payez Moins         13,68-
  Plus : COTIS. SECURITE SOCIALE         29,31
  → Montant HT final = 137.52 - 13.68 + 29.31 = 153.15
  → total_ttc = 153.15 × 1.20 = 183.78

  VODKA POLIAKOV 37.5D 70CL (2eme)  montant=137,52  TVA=D
  Offre Achetez Plus Payez Moins         13,68-   ← IGNORER (deja comptee!)
  Plus : COTIS. SECURITE SOCIALE         29,31
  → Montant HT final = 137.52 + 29.31 = 166.83
  → total_ttc = 166.83 × 1.20 = 200.20

  WHISKY LABEL 5 40D 20CL X6  montant=57,09  TVA=D
  Plus : COTIS. SECURITE SOCIALE         8,94
  → Montant HT final = 57.09 + 8.94 = 66.03
  → total_ttc = 66.03 × 1.20 = 79.24

  VODKA POLIAKOV 37,5D 20CL X6  montant=163,50  TVA=D
  Plus : COTIS. SECURITE SOCIALE         27,90
  → Montant HT final = 163.50 + 27.90 = 191.40
  → total_ttc = 191.40 × 1.20 = 229.68

VERIFICATION COTIS: les COTIS sur spiritueux sont souvent entre 3€ et 30€.
Liste des produits qui ont TOUJOURS une ligne COTIS juste apres sur Metro:
- WHISKY, VODKA, GIN, COGNAC, RHUM, RICARD, PASTIS, COCKORICO, tout produit avec un degre > 10°
- Les BIERES n'ont PAS de ligne COTIS separee (deja incluse dans le prix)
- Les VINS n'ont PAS de ligne COTIS separee

ATTENTION: tu dois verifier que tu as bien ajoute la COTIS de CHAQUE spiritueux.
Compte le nombre de lignes "COTIS. SECURITE SOCIALE" dans le texte et verifie que tu en as autant que de spiritueux.

ETAPE 4 - EXTRAIRE LE PRIX:
Pour chaque produit, tu dois trouver le MONTANT HT DE LA LIGNE (le montant tel qu'il apparait sur la facture).
- Sur les factures Metro: la colonne "Montant" est DEJA en HT → prends ce montant directement
- Sur les factures Codifrance: le montant TTC est indique → convertis en HT: HT = TTC / (1 + TVA/100)
- Sur les autres factures: prends le montant de la ligne (HT ou TTC selon ce qui est indique)
- CONVERSION CENTIMES: si la valeur est un entier sans decimale et semble trop elevee (ex: 1807, 12269), divise par 100
- Pour Metro: AJOUTE les COTIS et SOUSTRAIT les remises au montant HT (cf. instructions COTIS plus haut)

IMPORTANT: retourne TOUJOURS le montant HT final (apres COTIS et remises) dans le champ "total_ht".

ETAPE 5 - DETERMINER LA TVA (REGLEMENTATION FRANCAISE):

REGLE METRO PRIORITAIRE: Sur les factures Metro, chaque ligne a un code TVA (B, C, D) dans la colonne "TVA".
UTILISE TOUJOURS LE CODE TVA DE LA FACTURE METRO, NE LE CHANGE JAMAIS:
- B = 5.5% (même pour Red Bull, Monster, Crazy Tiger, energy drinks — Metro les classe en B)
- C = 20%
- D = 20%
Ne remplace JAMAIS un B par 20% même si tu penses que le produit devrait être à 20%.
La facture Metro fait foi, pas ta connaissance des taux TVA.

Pour les AUTRES factures (pas Metro), applique ces regles:

TAUX 20% (taux normal) - ALCOOL et produits non-alimentaires:
- Bieres, vins, spiritueux, cocktails, cidres, liqueurs
- Tous produits avec un degre d'alcool (°, %vol)
- Produits non-alimentaires (emballages, accessoires)

TAUX 5.5% (taux reduit) - ALIMENTATION et boissons sans alcool:
- Snacks: chips, Doritos, Benenuts, Twinuts, cacahuetes, bretzel, melanges aperitifs
- Biscuits, madeleines, gateaux, cookies, cereales, bonbons, chocolat, Kinder, barres chocolatees
- Boissons sans alcool: Coca-Cola, Fanta, Orangina, Oasis, Lipton, Red Bull, Schweppes, Caraibos, Powerade, Hawai, Ginger Beer
- Eaux: Evian, Volvic, Cristalline, San Pellegrino, Perrier, Badoit
- Jus de fruits, nectars, sirops
- Oeufs, beurre, lait, fromage, yaourt, creme
- Fruits, legumes, viande, poisson, pain, farine
- Conserves, plats prepares, condiments

TAUX 10% (taux intermediaire):
- Repas servis sur place (restauration)
- Produits alimentaires non directement consommables

TAUX 2.1%:
- Medicaments rembourses, presse

REGLES:
1) Si la facture indique le taux directement (20%, 5.5%, 10%) → utilise-le
2) Si c'est un code (1, 2, 3, 4) → regarde la legende de la facture
3) Si AUCUNE indication → applique les regles ci-dessus selon le type de produit
4) NE METS PAS TOUT A 20% PAR DEFAUT ! Analyse chaque produit individuellement.

FORMAT DE REPONSE:
Reponds UNIQUEMENT avec un JSON object. RIEN d'autre avant ou apres. Pas de ```.

Exemple EXACT de format attendu:
{"net_a_payer":2253.01,"articles":[{"desc":"VODKA POLIAKOV 37.5D 70CL","qty":18,"total_ht":153.15,"tva":20},{"desc":"COCA COLA PET 50CL","qty":24,"total_ht":23.64,"tva":5.5}]}

Champs obligatoires pour chaque article:
- "desc" = nom du produit
- "qty" = quantite TOTALE (unites × colis pour Metro). Ex: "6 3" → qty=18, "24 1" → qty=24, "12 2" → qty=24
- "total_ht" = MONTANT HT total de la ligne en euros (apres ajout COTIS et soustraction remises si applicable)
  Pour Metro: c'est le montant de la colonne "Montant" + COTIS - remise
  Pour les factures en TTC: convertis en HT = montant_TTC / (1 + tva/100)
- "tva" = taux TVA (20, 5.5, 10, ou 2.1)

Champ global:
- "net_a_payer" = le TOTAL A PAYER TTC de la facture (cherche "Total a payer", "Net a payer", "Total TTC")

VERIFICATIONS:
1) Somme de tous total_ht doit ≈ le "Total H.T." ou "Montant hors T.V.A." de la facture
2) Nombre d'articles: verifie que tu n'as pas saute de produits

Si aucun produit: {"net_a_payer":0,"articles":[]}

VERIFICATION FINALE OBLIGATOIRE:
Avant de repondre, additionne tous tes "total_ttc". Ce total doit etre EGAL au "net_a_payer".
Si ton total est loin du net_a_payer, tu as mal lu certains montants → relis-les attentivement.
Exemple: si net_a_payer=1197.85 et ta somme=1130, il te manque ~68€ → un ou plusieurs montants sont faux."""

    # Build message content with all page images
    content_blocks = []
    # Build content blocks: text first (if PDF), then images, then prompt
    content_blocks = []
    
    # If we have extracted text from PDF, send it first
    if pdf_text.strip():
        content_blocks.append({
            "type": "text",
            "text": f"TEXTE EXTRAIT DU PDF (utilise ces donnees pour les colonnes exactes, noms, quantites et montants):\n{pdf_text[:30000]}",
        })
    
    for img in images_b64:
        content_blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": img["media"],
                "data": img["b64"],
            },
        })
    content_blocks.append({
        "type": "text",
        "text": prompt,
    })

    try:
        # Try with Claude Sonnet 4 first, fallback to 3.5 Sonnet
        models_to_try = [
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-haiku-20240307",
        ]

        resp = None
        used_model = models_to_try[0]
        for model in models_to_try:
            used_model = model
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "max_tokens": 32000,
                    "messages": [{
                        "role": "user",
                        "content": content_blocks,
                    }],
                },
                timeout=240,
            )
            if resp.status_code == 200:
                break  # Success, stop trying
            # If model not found (404) or not available, try next
            if resp.status_code in (404, 400) and "model" in resp.text.lower():
                continue
            # For other errors (401 auth, 429 rate limit), don't retry
            break

        if resp.status_code == 401:
            # Show the actual error to help debug
            err_detail = ""
            try:
                err_detail = resp.json().get("error", {}).get("message", "")
            except:
                err_detail = resp.text[:300]
            return None, f"Erreur authentification API (401). Verifiez que votre cle est correcte dans Settings → Secrets.\nDetail: {err_detail}"
        if resp.status_code == 429:
            return None, "Limite API atteinte. Reessayez dans quelques secondes."
        if resp.status_code != 200:
            err_detail = ""
            try:
                err_detail = resp.json().get("error", {}).get("message", "")
            except:
                err_detail = resp.text[:300]
            return None, f"Erreur API ({resp.status_code}): {err_detail}"

        data = resp.json()
        content = data.get("content", [{}])[0].get("text", "").strip()

        # ── Robust JSON extraction ──
        # Claude might return text before/after the JSON, markdown fences, etc.
        # We need to find the JSON array in the response no matter what.
        
        # Store raw response for debug
        raw_response = content
        
        # Step 1: Remove markdown code fences
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        content = content.strip()
        
        # Step 2: Try direct parse
        parsed = None
        net_a_payer = None
        montants_ht = False
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Handle new format: {"net_a_payer": X, "montants_ht": bool, "articles": [...]}
        if isinstance(parsed, dict) and "articles" in parsed:
            net_a_payer = parsed.get("net_a_payer", None)
            montants_ht = parsed.get("montants_ht", False)
            parsed = parsed["articles"]
        
        # Step 3: If that failed, find the first [ ... ] block in the text
        if parsed is None:
            match = re.search(r'\[[\s\S]*\]', content)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        
        # Step 3b: Try to find {"net_a_payer":..., "articles":[...]} in text
        if parsed is None:
            match = re.search(r'\{[\s\S]*"articles"[\s\S]*\}', content)
            if match:
                try:
                    wrapper = json.loads(match.group(0))
                    if "articles" in wrapper:
                        net_a_payer = wrapper.get("net_a_payer", None)
                        montants_ht = wrapper.get("montants_ht", False)
                        parsed = wrapper["articles"]
                except json.JSONDecodeError:
                    pass
        
        # Step 4: If still failed, try to find individual JSON objects
        if parsed is None:
            objects = re.findall(r'\{[^{}]+\}', content)
            if objects:
                parsed = []
                for obj_str in objects:
                    try:
                        obj = json.loads(obj_str)
                        if "desc" in obj:
                            parsed.append(obj)
                    except:
                        pass
        
        # Step 5: If nothing worked, show what Claude actually returned
        if parsed is None or (isinstance(parsed, list) and len(parsed) == 0):
            # Show first 500 chars of response for debugging
            preview = raw_response[:500].replace('\n', ' ')
            return None, f"L'IA a repondu mais pas en JSON valide. Reessayez.\n\nDebut de la reponse: {preview}"
        
        if not isinstance(parsed, list):
            parsed = [parsed] if isinstance(parsed, dict) else []

        results = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            desc = str(item.get("desc", "")).strip()
            if not desc:
                continue
            try:
                qty = max(1, int(float(item.get("qty", 1))))
            except:
                qty = 1
            
            # Read total_ht (preferred new format) or fallback to total_ttc (old format)
            line_total_ht = 0.0
            line_total_ttc = 0.0
            has_ht = False
            try:
                if "total_ht" in item:
                    line_total_ht = round(float(item["total_ht"]), 2)
                    has_ht = True
                elif "total_ttc" in item:
                    line_total_ttc = round(float(item["total_ttc"]), 2)
                elif "price_ttc" in item:
                    line_total_ttc = round(float(item["price_ttc"]) * qty, 2)
            except:
                pass
            
            try:
                tva = float(item.get("tva", 20))
                if tva not in [0, 2.1, 5.5, 10, 20]:
                    tva = 20.0
            except:
                tva = 20.0

            # Compute TTC from HT (exact, done in code) or use TTC directly
            if has_ht and line_total_ht > 0:
                # Auto-correct centimes
                if line_total_ht > 500 and line_total_ht == int(line_total_ht):
                    line_total_ht = round(line_total_ht / 100, 2)
                line_total_ttc = round(line_total_ht * (1 + tva / 100), 2)
                results.append({
                    "desc": desc[:80],
                    "qty": qty,
                    "line_total_ht": line_total_ht,
                    "line_total_ttc": line_total_ttc,
                    "tva": tva,
                })
            elif line_total_ttc > 0:
                # Auto-correct centimes
                if line_total_ttc > 500 and line_total_ttc == int(line_total_ttc):
                    line_total_ttc = round(line_total_ttc / 100, 2)
                results.append({
                    "desc": desc[:80],
                    "qty": qty,
                    "line_total_ttc": line_total_ttc,
                    "tva": tva,
                })

        if not results:
            preview = raw_response[:500].replace('\n', ' ')
            return None, f"L'IA n'a detecte aucun article.\n\nReponse: {preview}"

        # ── Post-processing: filter and fix ──
        filtered = []
        for r in results:
            desc_upper = r["desc"].upper()
            # Skip palettes, emballages, consignes - broad matching
            skip_words = ["PAL.", "PAL ", "PALETTE", "CHEP", "LOGIPAL", "LPR", 
                         "CONSIGN", "80X120", "80 X 120", "80×120"]
            if any(x in desc_upper for x in skip_words):
                continue
            # Skip avoirs
            if "AVOIR" in desc_upper:
                continue
            # Skip remise lines (should not be in results but just in case)
            if "REMISE" in desc_upper:
                continue
            # Skip delivery/service fees only if explicitly requested
            # Note: LIVRAISON is a real invoiced cost, keep it
            if any(x in desc_upper for x in ["TRANSPORT", "FRAIS DE PORT"]):
                continue
            
            # Auto-correct TVA: food/snack items should be 5.5%, not 20%
            # BUT: skip auto-correction if article has line_total_ht (means TVA was explicit from invoice like Metro)
            # Metro invoices ALWAYS have line_total_ht, so this protects Metro beer/wine from being changed
            has_explicit_ht = "line_total_ht" in r
            if not has_explicit_ht and r["tva"] == 20.0:
                food_keywords = ["DORITOS", "BENENUTS", "TWINUTS", "CHIPS", "SNACK", 
                               "GRILL", "MELANGE", "CACAHUETE", "BRETZEL", "BISCUIT",
                               "MADELEINE", "PALET", "GALETTE", "ROCHAMBEAU", "KINDER",
                               "GATEAUX", "COOKIE", "CEREALE", "BONBON", "CHOCOLAT",
                               "JUS", "NECTAR", "SIROP", "EAU ", "EVIAN", "VOLVIC", 
                               "CRISTAL", "SAN PELL", "LIPTON", "OASIS", "COCA",
                               "FANTA", "ORANGINA", "SCHWEPPE", "RED BULL", "POWERADE",
                               "MONSTER", "CRAZY TIGER", "SPRITE", "ALPRO",
                               "OEUF", "BEURRE", "LAIT", "FROMAGE", "YAOURT",
                               "FRUIT", "LEGUME", "PAIN", "FARINE",
                               "CARAIBOS", "HAWAI", "GINGER", "CANDY"]
                if any(kw in desc_upper for kw in food_keywords):
                    r["tva"] = 5.5
            
            filtered.append(r)
        results = filtered

        if not results:
            return None, "Aucun article produit detecte (que des emballages/consignes)"

        # ── Fallback: extract net_a_payer from PDF text if Claude didn't find it ──
        if not net_a_payer and pdf_text:
            # Try various patterns for total TTC / net a payer
            nap_patterns = [
                r'Total\s*[àa]\s*payer\s*[:\s]*(\d[\d\s]*[.,]\d{2})',
                r'NET\s*A\s*PAYER\s*[:\s]*(\d[\d\s]*[.,]\d{2})',
                r'TOTAL\s*TTC\s*[:\s]*(\d[\d\s]*[.,]\d{2})',
                r'Montant\s*TTC\s*[:\s]*(\d[\d\s]*[.,]\d{2})',
            ]
            for pat in nap_patterns:
                m = re.search(pat, pdf_text, re.IGNORECASE)
                if m:
                    val_str = m.group(1).replace(' ', '').replace(',', '.')
                    try:
                        net_a_payer = float(val_str)
                        break
                    except ValueError:
                        pass
            # Metro specific: look for the last big TTC amount on the summary page
            if not net_a_payer:
                m = re.search(r'(\d[\d\s]*[.,]\d{2})\s*\n.*Total\s*[àa]\s*payer', pdf_text, re.IGNORECASE)
                if not m:
                    # Metro format: "2253,01" appears near end with "Total à payer"
                    amounts = re.findall(r'(\d{3,}[.,]\d{2})', pdf_text[-2000:] if len(pdf_text) > 2000 else pdf_text)
                    if amounts:
                        # Take the largest amount as likely TTC total
                        candidates = []
                        for a in amounts:
                            try:
                                candidates.append(float(a.replace(',', '.')))
                            except:
                                pass
                        if candidates:
                            max_val = max(candidates)
                            # Only use if it's significantly larger than scan total
                            if max_val > total_scan * 1.1:
                                net_a_payer = max_val

        # ── No more HT→TTC auto-detection needed ──
        # The code now converts HT→TTC directly when Claude returns total_ht
        # If Claude returned total_ttc (old format), it's used as-is
        
        total_scan = sum(r["line_total_ttc"] for r in results)
        needs_ttc_conversion = False  # Conversion already done in parsing above

        # Attach net_a_payer and conversion info to results for display
        return (results, net_a_payer, needs_ttc_conversion), None

    except requests.exceptions.Timeout:
        return None, "Timeout — l'image est peut-etre trop lourde. Reduisez la taille ou photographiez une seule page."
    except requests.exceptions.ConnectionError:
        return None, "Pas de connexion internet"
    except Exception as e:
        return None, f"Erreur: {str(e)}"

def del_line(lid):
    st.session_state.lines = [l for l in st.session_state.lines if l["id"] != lid]

def compute(line):
    pu_ttc = ttc_from_ht(line["pu_ht"], line["tva"])
    tot_ht = round(line["qty"] * line["pu_ht"], 2)
    # Use exact TTC from scan if available (avoids rounding errors)
    if line.get("tot_ttc_override") is not None:
        tot_ttc = line["tot_ttc_override"]
        # Recalculate tot_ht from exact TTC to be consistent
        tot_ht = round(tot_ttc / (1 + line["tva"] / 100), 2)
    else:
        tot_ttc = round(tot_ht * (1 + line["tva"] / 100), 2)
    return {**line, "pu_ttc": pu_ttc, "tot_ht": tot_ht, "tot_ttc": tot_ttc}


# ═══════════════════════════════════════
# PDF GENERATOR (fpdf2) - NO FLASH SYMBOL
# ═══════════════════════════════════════
class InvoicePDF(FPDF):
    def __init__(self, client_name, client_addr, inv_num, inv_date):
        super().__init__()
        self.c_name = client_name
        self.c_addr = client_addr
        self.inv_num = inv_num
        self.inv_date = inv_date

    def header(self):
        # Dark header bar
        self.set_fill_color(26, 26, 46)
        self.rect(0, 0, 210, 48, "F")
        # Orange accent
        self.set_fill_color(255, 140, 50)
        self.rect(0, 48, 210, 2.5, "F")
        # Company name
        self.set_font("Helvetica", "B", 26)
        self.set_text_color(255, 255, 255)
        self.set_xy(15, 10)
        self.cell(0, 12, "SMART EXCHANGE", 0, 0, "L")
        # Subtitle
        self.set_font("Helvetica", "", 9)
        self.set_text_color(255, 179, 71)
        self.set_xy(15, 23)
        self.cell(0, 6, "FACTURATION", 0, 0, "L")
        # Invoice info right
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 255, 255)
        self.set_xy(120, 18)
        self.cell(0, 6, f"Facture : {self.inv_num}", 0, 0, "R")
        self.set_font("Helvetica", "", 9)
        self.set_xy(120, 25)
        self.cell(0, 6, f"Date : {self.inv_date}", 0, 0, "R")
        self.ln(55)

    def footer(self):
        self.set_y(-25)
        self.set_draw_color(255, 140, 50)
        self.set_line_width(0.4)
        self.line(15, self.get_y(), 195, self.get_y())
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(140, 140, 160)
        self.ln(3)
        self.cell(0, 3.5, f"{COMPANY['name']} | SIREN : {COMPANY['siren']} | SIRET : {COMPANY['siret']}", 0, 1, "C")
        self.cell(0, 3.5, f"TVA Intracommunautaire : {COMPANY['tva']} | Email : {COMPANY['email']}", 0, 1, "C")
        self.cell(0, 3.5, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")


def gen_pdf(client_name, client_addr, computed_lines, inv_num, inv_date_str, client_siret="", client_tva=""):
    pdf = InvoicePDF(client_name, client_addr, inv_num, inv_date_str)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=30)

    y = pdf.get_y()

    # Emitter
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 140, 50)
    pdf.cell(90, 5, "EMETTEUR", 0, 1)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(70, 70, 90)
    pdf.cell(90, 4.5, COMPANY["name"], 0, 1)
    pdf.cell(90, 4.5, f"SIREN : {COMPANY['siren']}", 0, 1)
    pdf.cell(90, 4.5, f"SIRET : {COMPANY['siret']}", 0, 1)
    pdf.cell(90, 4.5, f"TVA : {COMPANY['tva']}", 0, 1)
    pdf.cell(90, 4.5, f"Email : {COMPANY['email']}", 0, 1)
    y_after = pdf.get_y()

    # Client
    pdf.set_xy(120, y)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(255, 140, 50)
    pdf.cell(75, 5, "CLIENT", 0, 1)
    pdf.set_x(120)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(75, 5, client_name, 0, 1)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(70, 70, 90)
    for al in client_addr.split("\n"):
        pdf.set_x(120)
        pdf.cell(75, 4.5, al.strip(), 0, 1)
    if client_siret.strip():
        pdf.set_x(120)
        pdf.cell(75, 4.5, f"SIRET : {client_siret.strip()}", 0, 1)
    if client_tva.strip():
        pdf.set_x(120)
        pdf.cell(75, 4.5, f"TVA : {client_tva.strip()}", 0, 1)

    pdf.set_y(max(y_after, pdf.get_y()) + 8)

    # Table
    cw = [58, 14, 24, 16, 24, 22, 24]  # = 182
    headers = ["Description", "Qte", "PU HT", "TVA", "PU TTC", "Total HT", "Total TTC"]

    pdf.set_fill_color(26, 26, 46)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 7.5)
    for i, h in enumerate(headers):
        pdf.cell(cw[i], 7.5, h, 1, 0, "C", True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 7.5)
    fill = False
    for ln in computed_lines:
        if fill:
            pdf.set_fill_color(248, 248, 253)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.set_text_color(50, 50, 70)

        pdf.cell(cw[0], 6.5, str(ln["desc"])[:38], 1, 0, "L", True)
        pdf.cell(cw[1], 6.5, str(ln["qty"]), 1, 0, "C", True)
        pdf.cell(cw[2], 6.5, f'{ln["pu_ht"]:.2f}', 1, 0, "R", True)
        pdf.cell(cw[3], 6.5, f'{ln["tva"]:.1f}%', 1, 0, "C", True)
        pdf.cell(cw[4], 6.5, f'{ln["pu_ttc"]:.2f}', 1, 0, "R", True)
        pdf.cell(cw[5], 6.5, f'{ln["tot_ht"]:.2f}', 1, 0, "R", True)
        # TTC in orange bold
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.set_text_color(255, 107, 26)
        pdf.cell(cw[6], 6.5, f'{ln["tot_ttc"]:.2f}', 1, 0, "R", True)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.ln()
        fill = not fill

    pdf.ln(5)

    # Ensure totals fit on current page (need ~45mm for totals + payment terms)
    if pdf.get_y() > 240:
        pdf.add_page()
        pdf.ln(10)

    # Totals using GROUP TVA method (exact match with supplier invoices)
    from collections import defaultdict
    tva_groups_pdf = defaultdict(float)
    for l in computed_lines:
        tva_groups_pdf[l["tva"]] += l["tot_ht"]
    
    total_ht = round(sum(tva_groups_pdf.values()), 2)
    total_tva = 0.0
    total_ttc = 0.0
    for tva_rate, group_ht in tva_groups_pdf.items():
        group_ht_r = round(group_ht, 2)
        group_tva = round(group_ht_r * tva_rate / 100, 2)
        total_tva += group_tva
        total_ttc += group_ht_r + group_tva
    total_tva = round(total_tva, 2)
    total_ttc = round(total_ttc, 2)

    xL, xV = 133, 178

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(70, 70, 90)
    pdf.set_x(xL)
    pdf.cell(30, 6, "Total HT :", 0, 0, "R")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 6, f"{total_ht:.2f} EUR", 0, 1, "R")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_x(xL)
    pdf.cell(30, 6, "Total TVA :", 0, 0, "R")
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(30, 6, f"{total_tva:.2f} EUR", 0, 1, "R")

    # TTC orange box
    pdf.ln(2)
    y_ttc = pdf.get_y()
    pdf.set_fill_color(255, 140, 50)
    pdf.set_draw_color(255, 140, 50)
    pdf.rect(xL - 3, y_ttc - 1, 70, 11, "F")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(xL, y_ttc)
    pdf.cell(30, 9, "TOTAL TTC :", 0, 0, "R")
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(35, 9, f"{total_ttc:.2f} EUR", 0, 1, "R")

    # Payment terms
    pdf.ln(14)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(120, 120, 140)
    pdf.cell(0, 4.5, "Conditions de paiement : Paiement comptant.", 0, 1, "L")
    pdf.cell(0, 4.5, "En cas de retard, une indemnite forfaitaire de 40 EUR sera appliquee.", 0, 1, "L")

    return bytes(pdf.output())


# ═══════════════════════════════════════
# UI
# ═══════════════════════════════════════

# Banner
if BANNER_B64:
    st.markdown(f"""
    <div class="banner">
        <img src="data:image/png;base64,{BANNER_B64}" alt="Smart Exchange">
        <div class="banner-ov">
            <div>
                <div class="b-title">SMART <span>EXCHANGE</span></div>
                <div class="b-sub">Systeme de Facturation Pro</div>
            </div>
        </div>
        <div class="b-line"></div>
    </div>
    """, unsafe_allow_html=True)

# ── Client ──
st.markdown('<div class="sec"><div class="sec-h">👤 Client</div>', unsafe_allow_html=True)

# Init client fields in session state
for field in ["client_name", "client_addr", "client_siret", "client_tva"]:
    if field not in st.session_state:
        st.session_state[field] = ""

# Client selector - ALWAYS visible at top
saved_clients = list(st.session_state.clients.keys())
sel_col, btn_col = st.columns([3, 1])
with sel_col:
    selected = st.selectbox(
        "📂 Sélectionner un client enregistré",
        ["— Nouveau client —"] + saved_clients,
        key="client_selector"
    )
with btn_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if selected != "— Nouveau client —":
        if st.button("🗑️ Supprimer", key="del_client"):
            if selected in st.session_state.clients:
                del st.session_state.clients[selected]
                save_clients(st.session_state.clients)
                st.session_state["client_name"] = ""
                st.session_state["client_addr"] = ""
                st.session_state["client_siret"] = ""
                st.session_state["client_tva"] = ""
                st.rerun()

# Load selected client data
if selected != "— Nouveau client —" and selected in st.session_state.clients:
    cdata = st.session_state.clients[selected]
    if isinstance(cdata, dict):
        st.session_state["client_name"] = selected
        st.session_state["client_addr"] = cdata.get("addr", "")
        st.session_state["client_siret"] = cdata.get("siret", "")
        st.session_state["client_tva"] = cdata.get("tva", "")

c1, c2 = st.columns(2)
with c1:
    client_name = st.text_input("Nom / Raison sociale", value=st.session_state["client_name"], placeholder="Ex: Restaurant Le Bon Gout", key="cn_input")
with c2:
    client_addr = st.text_area("Adresse", value=st.session_state["client_addr"], placeholder="12 Rue de la Paix\n75002 Paris", height=75, key="ca_input")

c3, c4 = st.columns(2)
with c3:
    client_siret = st.text_input("SIRET client (optionnel)", value=st.session_state["client_siret"], placeholder="Ex: 123 456 789 00010", key="cs_input")
with c4:
    client_tva = st.text_input("N° TVA client (optionnel)", value=st.session_state["client_tva"], placeholder="Ex: FR12345678901", key="ct_input")

if st.button("💾 Sauvegarder ce client", use_container_width=True):
    if client_name.strip():
        st.session_state.clients[client_name.strip()] = {
            "addr": client_addr,
            "siret": client_siret,
            "tva": client_tva,
        }
        save_clients(st.session_state.clients)
        st.success(f"✅ {client_name} sauvegardé !")
        st.rerun()
    else:
        st.warning("Entrez un nom de client")
st.markdown('</div>', unsafe_allow_html=True)

# ── Facture details ──
st.markdown('<div class="sec"><div class="sec-h">📋 Facture</div>', unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)
with d1:
    inv_num = st.text_input("N° Facture", value=f"SE-{datetime.now().strftime('%Y%m%d')}-001")
with d2:
    inv_date = st.date_input("Date", value=date.today())
with d3:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<span class="badge">TVA : {COMPANY["tva"]}</span>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Lines ──
st.markdown('<div class="sec"><div class="sec-h">⚡ Articles & Prestations</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✏️ Saisie Manuelle", "📷 Scan & Refacturation"])

with tab1:
    if st.button("➕ Ajouter une ligne", key="add"):
        add_line()

    for idx, line in enumerate(st.session_state.lines):
        cols = st.columns([3, 0.8, 1.2, 0.6, 0.6, 0.3])
        with cols[0]:
            line["desc"] = st.text_input("Desc", value=line["desc"], key=f"d{line['id']}", label_visibility="collapsed", placeholder="Description")
        with cols[1]:
            new_qty = st.number_input("Qte", value=line["qty"], min_value=1, step=1, key=f"q{line['id']}", label_visibility="collapsed")
            if new_qty != line["qty"]:
                line["tot_ttc_override"] = None  # Clear override when qty changes
            line["qty"] = new_qty
        with cols[2]:
            new_pu = st.number_input("PU HT", value=line["pu_ht"], min_value=0.0, step=0.01, format="%.2f", key=f"p{line['id']}", label_visibility="collapsed")
            if abs(new_pu - line["pu_ht"]) > 0.001:
                line["tot_ttc_override"] = None  # Clear override when price changes
            line["pu_ht"] = new_pu
        with cols[3]:
            # TVA: display current value and allow cycling through options on click
            current_tva = line.get("tva", 20.0)
            tva_color = "#26de81" if current_tva == 5.5 else "#FF8C32" if current_tva == 20.0 else "#54a0ff"
            st.markdown(f"<div style='text-align:center;font-weight:700;color:{tva_color};padding:6px 0;font-size:.85rem'>{current_tva}%</div>", unsafe_allow_html=True)
        with cols[4]:
            # Button to cycle TVA: 20 → 5.5 → 10 → 2.1 → 0 → 20
            if st.button("TVA", key=f"ctva{line['id']}", help="Changer le taux de TVA"):
                tva_cycle = {20.0: 5.5, 5.5: 10.0, 10.0: 2.1, 2.1: 0.0, 0.0: 20.0}
                line["tva"] = tva_cycle.get(current_tva, 20.0)
                line["tot_ttc_override"] = None  # Clear override when TVA changes
                st.rerun()
        with cols[5]:
            if st.button("🗑️", key=f"x{line['id']}"):
                del_line(line["id"])
                st.rerun()

    if st.session_state.lines:
        computed = [compute(l) for l in st.session_state.lines]
        df = pd.DataFrame([{
            "Description": l["desc"] or "—",
            "Qté": l["qty"],
            "PU HT": f'{l["pu_ht"]:.2f} €',
            "TVA": f'{l["tva"]}%',
            "PU TTC": f'{l["pu_ttc"]:.2f} €',
            "Total HT": f'{l["tot_ht"]:.2f} €',
            "Total TTC": f'{l["tot_ttc"]:.2f} €',
        } for l in computed])
        st.dataframe(df, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("**📎 Scannez votre facture fournisseur (Metro, etc.)**")
    st.caption("L'IA lit directement votre facture et extrait tous les articles automatiquement.")

    # ── API Key input - directly visible here ──
    has_key = False
    # Check secrets first
    try:
        if st.secrets.get("ANTHROPIC_API_KEY", ""):
            has_key = True
    except Exception:
        pass
    if not has_key and os.environ.get("ANTHROPIC_API_KEY", ""):
        has_key = True
    if not has_key and st.session_state.get("anthropic_key", ""):
        has_key = True

    if not has_key:
        st.markdown("""
        <div style="background:rgba(255,140,50,0.08);border:1px solid rgba(255,160,50,0.3);border-radius:12px;padding:12px 16px;margin-bottom:10px">
            <b style="color:#FF8C32">🔑 Cle API non detectee</b><br>
            <span style="font-size:.82rem;color:rgba(255,255,255,0.6)">
                Ta cle doit etre dans <b>Streamlit Cloud → Settings → Secrets</b> :<br>
                <code>ANTHROPIC_API_KEY = "sk-ant-api03-..."</code><br>
                Si tu l'as deja mise, redemarre l'app (Settings → Reboot). Sinon colle-la ici :
            </span>
        </div>
        """, unsafe_allow_html=True)
        api_key_input = st.text_input(
            "🔑 Colle ta cle API ici (temporaire)",
            type="password",
            key="anthropic_key_input",
            placeholder="sk-ant-api03-...",
        )
        if api_key_input:
            st.session_state["anthropic_key"] = api_key_input
            has_key = True
            st.success("✅ Cle acceptee !")
            st.rerun()
    else:
        st.markdown("<span style='color:#26de81;font-size:.8rem;font-weight:700'>✅ Cle API detectee — scan pret</span>", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Glissez votre facture ici",
        type=["png", "jpg", "jpeg", "pdf"],
        key="scan",
        help="Photo, scan ou PDF de votre facture fournisseur"
    )

    if uploaded:
        sc_l, sc_r = st.columns([1.2, 1])

        with sc_l:
            if uploaded.type.startswith("image"):
                st.image(uploaded, caption="📄 Facture fournisseur", use_container_width=True)
            elif uploaded.type == "application/pdf":
                st.info(f"📄 **{uploaded.name}** ({uploaded.size // 1024} Ko) — PDF detecte")
            else:
                st.info(f"📄 {uploaded.name}")

            if has_key:
                if st.button("🤖 SCANNER TOUTE LA FACTURE", type="primary", use_container_width=True, key="scan_btn"):
                    with st.spinner("L'IA lit votre facture..."):
                        uploaded.seek(0)
                        img_bytes = uploaded.read()
                        result_data, err = scan_invoice_with_vision(img_bytes, uploaded.type)
                        if err:
                            st.error(f"❌ {err}")
                        elif result_data:
                            results, net_a_payer, ht_converted = result_data
                            st.session_state["scan_found"] = results
                            total_scan = sum(r["line_total_ttc"] for r in results)
                            st.success(f"✅ {len(results)} article(s) — Total TTC scanné: {total_scan:.2f} €")
                            if ht_converted:
                                st.info("ℹ️ Montants HT détectés et convertis automatiquement en TTC")
                            if net_a_payer:
                                diff = abs(total_scan - net_a_payer)
                                if diff < 0.10:
                                    st.success(f"✅ NET A PAYER facture: {net_a_payer:.2f} € — EXACT !")
                                elif diff < 5:
                                    st.warning(f"⚠️ NET A PAYER facture: {net_a_payer:.2f} € — Ecart: {diff:.2f} €")
                                else:
                                    st.error(f"❌ NET A PAYER facture: {net_a_payer:.2f} € — Ecart: {diff:.2f} € — Verifiez les montants !")
                            else:
                                st.caption("⚠️ Comparez ce total avec le NET A PAYER de votre facture")
                            # Debug: show articles for verification
                            with st.expander("🔍 Detail des articles extraits (debug)", expanded=False):
                                for i, r in enumerate(results):
                                    st.text(f"{i+1:2d}. {r['desc'][:50]:<50} qty={r['qty']:<4} total_ttc={r['line_total_ttc']:>8.2f}€  TVA={r['tva']}%")
                        else:
                            st.warning("Aucun article detecte")
            else:
                st.info("Ajoutez votre cle API dans ⚙️ pour activer le scan automatique")

        with sc_r:
            st.markdown("**🔄 Articles extraits**")

            # Init scan lines
            if "scan_lines" not in st.session_state:
                st.session_state.scan_lines = []
            if "scan_lid" not in st.session_state:
                st.session_state.scan_lid = 0

            # Auto-populate from scan results
            if "scan_found" in st.session_state and st.session_state["scan_found"]:
                found = st.session_state.pop("scan_found")
                st.session_state.scan_lines = []
                st.session_state["scan_added"] = False  # Reset flag for new scan
                for f in found:
                    st.session_state.scan_lid += 1
                    tva_val = f.get("tva", 20.0)
                    if tva_val not in [0.0, 2.1, 5.5, 10.0, 20.0]:
                        tva_val = 20.0
                    st.session_state.scan_lines.append({
                        "id": st.session_state.scan_lid,
                        "desc": f["desc"],
                        "qty": f["qty"],
                        "ttc": f["line_total_ttc"],  # EXACT total TTC from invoice (no rounding)
                        "tva": tva_val,
                    })
                st.rerun()

            if not st.session_state.scan_lines:
                st.info("Cliquez sur 'Scanner toute la facture' pour extraire les articles")
            else:
                st.caption(f"{len(st.session_state.scan_lines)} article(s) — verifiez puis ajoutez a la facture")

                scan_results = []
                for idx, sl in enumerate(st.session_state.scan_lines):
                    sid = sl["id"]
                    st.markdown(f"<div style='background:rgba(255,140,50,0.05);border:1px solid rgba(255,160,50,0.2);border-radius:10px;padding:5px 10px;margin-bottom:3px'><b style='color:#FF8C32;font-size:.74rem'>Article {idx+1}</b></div>", unsafe_allow_html=True)

                    sc_desc = st.text_input("Desc", value=sl.get("desc", ""), key=f"sd{sid}", label_visibility="collapsed")
                    c1, c2, c3, c4 = st.columns([1, 0.6, 0.4, 1])
                    with c1:
                        sc_qty = st.number_input("Qte", value=sl.get("qty", 1), min_value=1, step=1, key=f"sq{sid}")
                    with c2:
                        # Display TVA as text (not selectbox!) - reads directly from scan_line data
                        sc_tva = float(sl.get("tva", 20.0))
                        tva_color = "#26de81" if sc_tva == 5.5 else "#FF8C32" if sc_tva == 20.0 else "#54a0ff"
                        st.markdown(f"<div style='text-align:center;font-weight:700;color:{tva_color};padding:8px 0;font-size:.82rem'>{sc_tva}%</div>", unsafe_allow_html=True)
                    with c3:
                        # Cycle button to change TVA
                        if st.button("↻", key=f"ctva_s{sid}", help="Changer TVA"):
                            tva_cycle = {20.0: 5.5, 5.5: 10.0, 10.0: 2.1, 2.1: 0.0, 0.0: 20.0}
                            sl["tva"] = tva_cycle.get(sc_tva, 20.0)
                            st.rerun()
                    with c4:
                        sc_ttc = st.number_input("Total TTC", value=float(sl.get("ttc", 0.0)), min_value=0.0, step=0.01, format="%.2f", key=f"sp{sid}")

                    if sc_ttc > 0 and sc_qty > 0:
                        # Calculate HT total DIRECTLY from TTC total (no unit price rounding)
                        tot_ht_s = ht_from_ttc(sc_ttc, sc_tva)
                        pu_ht_s = round(tot_ht_s / sc_qty, 2)
                        pu_ttc_s = round(sc_ttc / sc_qty, 2)
                        st.markdown(f"<span style='color:#26de81;font-size:.76rem;font-weight:700'>→ PU TTC: {pu_ttc_s:.2f} € | PU HT: {pu_ht_s:.2f} € | Total HT: {tot_ht_s:.2f} €</span>", unsafe_allow_html=True)
                        scan_results.append({
                            "desc": sc_desc or "Article",
                            "qty": sc_qty,
                            "pu_ht": pu_ht_s,
                            "tot_ht": tot_ht_s,
                            "tot_ttc": sc_ttc,
                            "tva": sc_tva,
                        })

                bc1, bc2 = st.columns(2)
                with bc1:
                    if st.button("➕ Ligne", key="add_scan_ln"):
                        st.session_state.scan_lid += 1
                        st.session_state.scan_lines.append({"id": st.session_state.scan_lid, "desc": "", "qty": 1, "ttc": 0.0, "tva": 20.0})
                        st.rerun()
                with bc2:
                    if st.button("🗑️ Tout effacer", key="clear_scan"):
                        st.session_state.scan_lines = []
                        st.session_state.scan_lid = 0
                        st.rerun()

                st.markdown("---")
                if scan_results:
                    already_added = st.session_state.get("scan_added", False)
                    if already_added:
                        st.success("✅ Articles déjà ajoutés à la facture ! Vérifiez ci-dessous dans l'onglet Lignes.")
                        col_re, col_cl = st.columns(2)
                        with col_re:
                            if st.button("📥 RE-AJOUTER (doublon)", key="readd_scan", use_container_width=True):
                                for sr in scan_results:
                                    add_line(desc=sr["desc"], qty=sr["qty"], pu_ht=sr["pu_ht"], tva=sr["tva"], tot_ttc_override=sr["tot_ttc"])
                                st.rerun()
                        with col_cl:
                            if st.button("🗑️ Effacer le scan", key="clear_after_add", use_container_width=True):
                                st.session_state.scan_lines = []
                                st.session_state.scan_lid = 0
                                st.session_state["scan_added"] = False
                                st.rerun()
                    else:
                        if st.button(f"📥 AJOUTER LES {len(scan_results)} ARTICLES A LA FACTURE", type="primary", key="add_all_scan", use_container_width=True):
                            for sr in scan_results:
                                add_line(desc=sr["desc"], qty=sr["qty"], pu_ht=sr["pu_ht"], tva=sr["tva"], tot_ttc_override=sr["tot_ttc"])
                            st.session_state["scan_added"] = True
                            st.success(f"✅ {len(scan_results)} ligne(s) ajoutee(s) a la facture !")
                            st.rerun()

    else:
        st.markdown("""
        <div style="border:2px dashed rgba(255,160,50,0.3);border-radius:16px;padding:2rem;text-align:center;background:rgba(255,140,50,0.02)">
            <div style="font-size:2.5rem;margin-bottom:0.5rem">📸</div>
            <div style="color:rgba(255,255,255,0.6);font-weight:600;font-size:0.9rem">Uploadez votre facture fournisseur</div>
            <div style="color:rgba(255,255,255,0.3);font-size:0.75rem;margin-top:4px">
                1. Prenez en photo votre facture Metro, Promocash, etc.<br>
                2. Cliquez sur "Scanner toute la facture"<br>
                3. L'IA lit TOUT et remplit TOUTES les cases automatiquement<br>
                4. Verifiez puis ajoutez a votre facture
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🔄 Calculatrice Inversee (saisie manuelle)**")
        calc_desc = st.text_input("Description article", key="cd", placeholder="Ex: Whisky Jack Daniel's 70cl")
        cc1, cc2 = st.columns(2)
        with cc1:
            calc_qty = st.number_input("Quantite", value=1, min_value=1, step=1, key="cq")
        with cc2:
            calc_tva = st.selectbox("Taux TVA", [0.0, 2.1, 5.5, 10.0, 20.0], index=4, key="ct", format_func=lambda x: f"{x}%")
        calc_ttc = st.number_input("💰 Prix Total TTC paye (€)", value=0.0, min_value=0.0, step=0.01, format="%.2f", key="cp")
        if calc_ttc > 0 and calc_qty > 0:
            pu_ttc = round(calc_ttc / calc_qty, 2)
            pu_ht = ht_from_ttc(pu_ttc, calc_tva)
            tot_ht = round(pu_ht * calc_qty, 2)
            m1, m2, m3 = st.columns(3)
            m1.metric("PU HT", f"{pu_ht:.2f} €")
            m2.metric("PU TTC", f"{pu_ttc:.2f} €")
            m3.metric("Total HT", f"{tot_ht:.2f} €")
            if st.button("➕ Ajouter a la facture", key="add_calc"):
                add_line(desc=calc_desc or "Article (refacturation)", qty=calc_qty, pu_ht=pu_ht, tva=calc_tva)
                st.success("✅ Ligne ajoutee !")
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ── Totals ──
all_comp = [compute(l) for l in st.session_state.lines]

# Calculate totals using GROUP TVA method (matches Metro/supplier invoices exactly)
# Instead of summing per-line TTC (which accumulates rounding), 
# we sum HT by TVA group, then compute TVA once per group
from collections import defaultdict
tva_groups = defaultdict(float)
for l in all_comp:
    tva_groups[l["tva"]] += l["tot_ht"]

g_ht = round(sum(tva_groups.values()), 2)
g_tva = 0.0
g_ttc = 0.0
for tva_rate, group_ht in tva_groups.items():
    group_ht_r = round(group_ht, 2)
    group_tva = round(group_ht_r * tva_rate / 100, 2)
    g_tva += group_tva
    g_ttc += group_ht_r + group_tva
g_tva = round(g_tva, 2)
g_ttc = round(g_ttc, 2)

st.markdown('<div class="sec"><div class="sec-h">💰 Totaux</div>', unsafe_allow_html=True)
t1, t2, t3 = st.columns([1, 1, 1.3])
with t1:
    st.markdown(f'<div class="tot-box tot-ht"><div class="lbl">Total HT</div><div class="val">{fmt(g_ht)}</div></div>', unsafe_allow_html=True)
with t2:
    st.markdown(f'<div class="tot-box tot-tva"><div class="lbl">Total TVA</div><div class="val">{fmt(g_tva)}</div></div>', unsafe_allow_html=True)
with t3:
    st.markdown(f'<div class="tot-box tot-ttc"><div class="lbl">Total TTC</div><div class="val">{fmt(g_ttc)}</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── PDF Export ──
st.markdown('<div class="sec"><div class="sec-h">🚀 Export</div>', unsafe_allow_html=True)
can_gen = len(st.session_state.lines) > 0 and client_name.strip() != ""
if not can_gen:
    st.info("Renseignez le client et ajoutez au moins une ligne.")

def reset_after_download():
    """Reset all data after PDF download"""
    st.session_state.lines = []
    st.session_state.lid = 0
    st.session_state.scan_lines = []
    st.session_state.scan_lid = 0
    st.session_state["scan_added"] = False
    st.session_state["pdf_ready"] = None
    st.session_state["pdf_fname"] = None

if st.button("🚀 GENERER LA FACTURE PDF", disabled=not can_gen, type="primary", use_container_width=True):
    with st.spinner("Generation..."):
        pdf_bytes = gen_pdf(
            client_name.strip(),
            client_addr.strip(),
            all_comp,
            inv_num,
            inv_date.strftime("%d/%m/%Y"),
            client_siret=client_siret.strip() if client_siret else "",
            client_tva=client_tva.strip() if client_tva else "",
        )
        safe = client_name.strip().replace(" ", "_")[:20]
        fname = f"Facture_{inv_num}_{safe}.pdf"
        st.session_state["pdf_ready"] = pdf_bytes
        st.session_state["pdf_fname"] = fname
        st.success("✅ Facture generee !")

# Show download button if PDF is ready
if st.session_state.get("pdf_ready"):
    st.download_button(
        "📥 Telecharger le PDF", 
        data=st.session_state["pdf_ready"], 
        file_name=st.session_state.get("pdf_fname", "facture.pdf"), 
        mime="application/pdf", 
        use_container_width=True,
        on_click=reset_after_download
    )

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="foot">{COMPANY["name"]} · SIREN {COMPANY["siren"]} · TVA {COMPANY["tva"]}<br>{COMPANY["email"]} · v2.0</div>', unsafe_allow_html=True)
