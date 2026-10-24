# Giguiya su Render + GitHub Pages

Sito (parte grafica): GitHub Pages — `https://tounkara-djigui.github.io/giguiya_pages`
Server (backend): Render, piano gratuito — configurato in `render.yaml`
Database e immagini: MongoDB Atlas, piano gratuito (le immagini caricate dallo staff sono salvate nel database)
Email: casella Aruba di giguiya.it via SMTP (oppure Resend, vedi sotto)

## 1. Database (MongoDB Atlas)
1. Create un account gratuito su https://www.mongodb.com/cloud/atlas e un cluster **M0 (Free)**, regione Europa.
2. Database Access → aggiungete un utente con password.
3. Network Access → aggiungete `0.0.0.0/0` (Render non ha un indirizzo fisso).
4. Connect → Drivers → copiate l'indirizzo `mongodb+srv://...` (sarà il valore di `MONGO_URL`).

## 2. Server (Render)
1. Create un account su https://render.com e collegate GitHub.
2. New → **Blueprint** → scegliete il repository `giguiya_pages`. Render legge `render.yaml`.
3. Compilate i valori richiesti:
   - `MONGO_URL`: indirizzo di Atlas del punto 1
   - `ADMIN_EMAIL` / `ADMIN_PASSWORD`: account amministratore iniziale (email @giguiya.it)
   - `SMTP_USER`: indirizzo completo della casella Aruba (es. la casella dell'associazione)
   - `SMTP_PASSWORD`: password di quella casella
   - `SMTP_FROM`: mittente delle email (di solito uguale a `SMTP_USER`)
   - `EMAIL_REPLY_TO`: indirizzo a cui rispondono i soci
4. Al termine Render mostra l'indirizzo del server, es. `https://giguiya-api.onrender.com`.
   Controllo: aprite `https://giguiya-api.onrender.com/api/health` → deve mostrare `{"status":"ok"}`.

Email con Resend invece di Aruba: in Render impostate `SMTP_HOST=smtp.resend.com`, `SMTP_PORT=465`,
`SMTP_USER=resend`, `SMTP_PASSWORD=<chiave API Resend>`, `SMTP_FROM=<indirizzo @giguiya.it verificato su Resend>`.

## 3. Collegare il sito su GitHub Pages al server
1. Repository GitHub → Settings → Secrets and variables → Actions → **Variables** → New variable
   - Nome: `API_URL` — Valore: indirizzo Render (es. `https://giguiya-api.onrender.com`, senza `/` finale)
2. Actions → "Pubblica su GitHub Pages" → **Run workflow**.

## Note
- Piano gratuito Render: il server si spegne dopo ~15 minuti senza visite; la prima apertura può richiedere circa un minuto.
- Il database su Atlas parte vuoto: all'avvio vengono creati l'amministratore e i contenuti di esempio.
- Su iPhone/Safari il login dal sito su github.io può essere bloccato (sito e server su indirizzi diversi).
