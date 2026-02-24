# SPEED MARKET - Facturation Pro

## Deploiement sur Streamlit Cloud

### Etape 1 : GitHub
1. Cree un compte sur **github.com**
2. Clique **"New repository"** → nom : `speed-market` → **Public** → **Create**
3. Clique **"uploading an existing file"**
4. Glisse les fichiers de ce dossier dedans :
   - `app.py`
   - `requirements.txt`
   - `banner.png`
   - `bg.png`
   - `README.md`
5. Clique **"Commit changes"**

### Etape 2 : Streamlit Cloud
1. Va sur **share.streamlit.io**
2. Connecte-toi avec ton **compte GitHub**
3. Clique **"New app"**
4. Selectionne : `ton-pseudo/speed-market` → branch `main` → fichier `app.py`
5. Clique **"Deploy!"**

### Etape 3 : Configurer la cle API (IMPORTANT pour le scan)
1. Sur Streamlit Cloud, va dans les **Settings** de ton app
2. Clique **"Secrets"**
3. Colle ceci :
```
ANTHROPIC_API_KEY = "sk-ant-api03-TA_CLE_ICI"
```
4. Remplace par ta vraie cle (console.anthropic.com)
5. Clique **"Save"**

### C'est en ligne !
Tu recois un lien du type : `https://ton-pseudo-speed-market.streamlit.app`

Le scan de factures utilisera automatiquement ta cle API sans que personne ne la voie.
