# PRD – Sito Associazione Giguiya (ASPCMT – Giguiya)

## Original problem statement
Ho bisogno di vostro aiuto a realizzare un sito angular per la nostra associazione. Giguiya. Vorrei che il sito si presenta moderno bellissimo. E inoltre vorrei che abbiamo un navbar: home, event: contente lista dei eventi per utente, premete le persone a registrarsi per prenotare eventi. con nome, cognome, email obbligatorio, numero opzionale, ogni prenotazione gli venga inviato inviate email di comferma di iscrizione. se vuoi fare il backned: predefinito in nestjs, va bene oppure python_fastapi. con database postgres. inoltre navbar deve avere anche Accesso: continente login, registrazione: solo per colore che vogliono essere nuovo socio, inoltre dopo le registrazionen gli vengonon inviate unn email di conferma e insieme a email di conferma gli vengono dette che fra qualche giorni possono essere contatto per il rilascio della carta della associazione e il passwordi come accedere il sito per controllare la loro situazione associativa se sono in regala al pagamento associativa; iscrizione e' 5 euro, e ogni la quota associativa e' 60 euro. login da la possibilita di utenti admin a gestire il sito es email con dominio xx@giguiya.it, possono a crearsi da soli password per gestire tutto quello che riguarda i contenuti del sito, nel caso questi email vengono confermato il link di confermazione.. inoltre sempre nel navbar: deve avere progetti: con al suo interno i nostri progetti; e che premette di registrare nuovi progetti, La parte login admin: ci permette a gestire utenti sia soci e sia le persone che si interessano i nostri eventi. Raccolta di chi siamo: poi ti fornisco il nostro status, qui dobbiamo riuscire a vedere lista di utenti e a verificare chi socio e se sono in regola con pagamenti e inoltre eventi la visualizzazione dipende: ogni singolo evento. Nella sessione dei progetti: inserisci: Sport: noi abbiamo una squadra maschile che gioca al campionato italiano poi ti fornisco la categoria. poi Intracci di comunita: che un progetto nostro realizzato grazie il contributoi della citta di Torino dove stiamo realizzando laboratorio di Treccine maliane, e il laboratorio della cucina maliana, delle gite, e eventi musicale aperti alla citadinanza. il Porgetto Baliba: realizzato insieme intersos e UNHCR nel 2023 per realizzazione dello sportello di ascolto aperto alla comunita maliana per facilitarli percorso di incluzione e alla cittadinanza. E raccolta di 5 X mille, Tutto resto senti libero di renderlo piu bello e stop. il sito deve essere scalabile ogni cosa al suo posto separate. e vorrei che sia angular versione standalone=true.

Follow-up: logo dell'associazione in alto; indirizzo Corso Casale 97 Torino, info@giguiya.it, 320 155 0017.

User choices: PostgreSQL, Python FastAPI, Resend gestito da Emergent, pagamenti segnati manualmente dall'admin, stile "Elegante scuro con accenti dorati".

## Architecture
- Frontend: Angular 20 standalone components (/app/frontend), lazy routes, signals, SCSS design tokens (styles/_*.scss), lucide-angular. `scripts/set-env.js` generates src/environments/environment.ts from REACT_APP_BACKEND_URL. Folders: core (config, models, services, guards, interceptors, utils), shared (components, pipes, directives, icons), features (home, events, projects, about, five-per-mille, membership, auth, member, admin).
- Backend: FastAPI modular (/app/backend/app): core (config, database, security, utils), models (SQLAlchemy async), schemas, services (email, templates, tokens, member, event), routers (auth, members, events, projects, admin/*). Tables auto-created on startup + seed.
- DB: PostgreSQL 15 (supervisor program `postgres`, DATABASE_URL in backend/.env).
- Auth: JWT httpOnly cookies (access 60m + refresh 7d), bcrypt, brute-force lockout, single-use hashed tokens for email verification / set-password / reset.
- Email: Emergent managed Resend (from_name "Associazione Giguiya", reply-to info@giguiya.it).

## User personas
- Visitatore: vede eventi/progetti, prenota eventi, dona 5x1000.
- Socio: si registra, crea password via link, vede tessera e stato pagamenti.
- Admin (@giguiya.it): gestisce soci, interessati, eventi, progetti.

## Core requirements (static)
Navbar Home/Eventi/Progetti/Chi siamo/5x1000/Accesso(Login, Registrazione socio); booking events (nome, cognome, email obbligatori, telefono opzionale) + email; member registration + email (tessera, 5€ + 60€, link password); admin self-signup @giguiya.it with verification; admin management; seeded projects; scalable separated structure.

## Implemented (2026-10-24)
- Full public site, booking flow with real confirmation emails, member registration + welcome email with set-password link, member area (tessera digitale, in regola status, fee history, bookings, change password), forgot/reset password.
- Admin: dashboard stats, Soci (toggles iscrizione/quota/tessera, filters, detail modal, quote per anno, note, reinvio email, elimina, CSV), Interessati (aggregated bookers, CSV), Eventi CRUD + prenotazioni per evento (CSV), Progetti CRUD.
- Logo associazione in navbar (emblema) + logo completo in Chi siamo, favicon; contatti reali in footer/chi siamo/email.
- Testing iteration_1: backend 18/18, frontend all flows pass. Minor fixes applied after: email 429 retry + guardrail ValueError caught, membership number collision retry, pending admin re-register no longer overwrites password, dynamic page titles, solid mobile menu.

## Placeholders to fill
- Categoria campionato squadra maschile [CATEGORIA DA DEFINIRE] – editable from admin Progetti
- 3 sample events (date/luogo da definire) – editable from admin Eventi
- Foto reali degli eventi dell'associazione (da fornire dal cliente)

## Update 2026-10-24 (MongoDB + file storage)
- Production has no PostgreSQL: user chose the built-in database. Backend migrated to MongoDB (motor, MONGO_URL/DB_NAME), same API. Postgres supervisor program/script removed.
- Emergent object storage: admin image upload (POST /api/admin/uploads, magic-byte + 8MB checks), public serving GET /api/files/{path}; upload button with preview in admin event/project forms; MediaUrlPipe resolves /api/files URLs.
- Hardening from iteration_3: lockout uses last X-Forwarded-For hop, duplicate booking checked before capacity, stats counts only published upcoming events.
- Testing iteration_3: backend 25/25, frontend 100%.

## Update 2026-10-24 (statuto + immagini Mali)
- Statuto PDF pubblicato in /docs/statuto-aspcmt-giguiya.pdf (frontend/public/docs); C.F. 97886490016; APS; approvato 23/07/2023.
- Contenuti riscritti dallo statuto: Chi siamo (finalità Art.2, attività Art.3, organi, ammissione soci), Home, Diventa socio (Consiglio direttivo, quota entro 31/12), 5x1000, email di benvenuto. Testi centralizzati in src/app/core/content/association.content.ts.
- Immagini reali del Mali (Wikimedia Commons, crediti nel footer): Djenné, Paese Dogon, Timbuctù, Mopti/Niger, Bandiagara come sfondi hero/page header + sezione "Scopri il Mali".
- PostgreSQL data moved to /app/.pgdata via /app/scripts/start-postgres.sh (supervisor program postgres) so it survives container restarts.

## Backlog
- P1: Pubblicare statuto (PDF) e codice fiscale; caricamento immagini da admin (object storage) invece di URL.
- P1: Galleria foto eventi/progetti; pagina squadra con calendario partite.
- P2: Pagamento online quote (Stripe), promemoria rinnovo quota annuale via email, migrazioni Alembic.

## Next tasks
- Ricevere dal cliente: statuto, codice fiscale, categoria campionato.
