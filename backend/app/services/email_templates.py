from html import escape

from app.core.config import settings
from app.core.utils import TZ


def _layout(title: str, body: str) -> str:
    brand = escape(settings.EMAIL_FROM_NAME)
    return (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#0C0D10;padding:32px 0">'
        '<tr><td align="center">'
        '<table role="presentation" width="600" cellpadding="0" cellspacing="0" '
        'style="max-width:600px;background:#14161C;border:1px solid #3a2f1a;border-radius:16px;font-family:Arial,sans-serif;color:#F4F4F6">'
        f'<tr><td style="padding:28px 36px;border-bottom:1px solid #3a2f1a">'
        f'<p style="margin:0;font-size:12px;letter-spacing:3px;color:#D4A03C;text-transform:uppercase">{brand}</p>'
        f'<h1 style="margin:10px 0 0;font-family:Georgia,serif;font-size:26px;color:#F3E5AB;font-weight:normal">{escape(title)}</h1>'
        '</td></tr>'
        f'<tr><td style="padding:28px 36px;font-size:15px;line-height:1.65;color:#D4D4D8">{body}</td></tr>'
        '<tr><td style="padding:20px 36px;border-top:1px solid #3a2f1a;font-size:12px;color:#71717A">'
        f'Email inviata da {brand} – Corso Casale 97, Torino · info@giguiya.it · 320 155 0017.<br>'
        'Non ti chiederemo mai la password o dati di pagamento via email.'
        '</td></tr></table></td></tr></table>'
    )


def _button(url: str, label: str) -> str:
    return (
        f'<p style="margin:28px 0"><a href="{escape(url)}" '
        'style="background:#D4A03C;color:#0C0D10;padding:14px 26px;border-radius:999px;text-decoration:none;font-weight:bold">'
        f'{escape(label)}</a></p>'
    )


def booking_confirmation(first_name: str, event) -> tuple[str, str]:
    when = event.start_at.astimezone(TZ).strftime("%d/%m/%Y alle %H:%M")
    url = f"{settings.FRONTEND_URL}/eventi/{event.slug}"
    body = (
        f"<p>Ciao {escape(first_name)},</p>"
        f"<p>la tua iscrizione all'evento <strong style=\"color:#F3E5AB\">{escape(event.title)}</strong> è confermata.</p>"
        '<table role="presentation" style="margin:18px 0;border-left:3px solid #D4A03C;padding-left:14px">'
        f"<tr><td style=\"padding:4px 14px\"><strong>Quando:</strong> {escape(when)}</td></tr>"
        f"<tr><td style=\"padding:4px 14px\"><strong>Dove:</strong> {escape(event.location or 'Da definire')}</td></tr>"
        "</table>"
        f"{_button(url, 'Vedi dettagli evento')}"
        "<p>Ti aspettiamo!</p>"
    )
    return f"Iscrizione confermata: {event.title}", _layout("Iscrizione confermata", body)


def member_welcome(first_name: str, membership_number: str, token: str) -> tuple[str, str]:
    url = f"{settings.FRONTEND_URL}/accesso/imposta-password?token={token}"
    body = (
        f"<p>Ciao {escape(first_name)},</p>"
        "<p>grazie per aver richiesto di diventare socio dell'Associazione Giguiya. "
        "Abbiamo ricevuto correttamente la tua domanda di iscrizione.</p>"
        f"<p>Il tuo numero di pratica è <strong style=\"color:#F3E5AB\">{escape(membership_number)}</strong>.</p>"
        '<table role="presentation" style="margin:18px 0;border-left:3px solid #D4A03C">'
        f"<tr><td style=\"padding:4px 14px\">Quota di iscrizione: <strong>{settings.ENROLLMENT_FEE} €</strong> (una tantum)</td></tr>"
        f"<tr><td style=\"padding:4px 14px\">Quota associativa annuale: <strong>{settings.ANNUAL_FEE} €</strong></td></tr>"
        "</table>"
        "<p>Nei prossimi giorni potrai essere contattato dalla nostra segreteria per il rilascio "
        "della tessera associativa.</p>"
        "<p>Per accedere al sito e controllare la tua situazione associativa (tessera e pagamenti), "
        "crea la tua password personale con il pulsante qui sotto. Il link è valido 7 giorni. "
        "Dopo averla impostata potrai accedere dalla pagina Accesso usando questa email.</p>"
        f"{_button(url, 'Crea la tua password')}"
    )
    return "Benvenuto in Giguiya – domanda di iscrizione ricevuta", _layout("Domanda di iscrizione ricevuta", body)


def admin_verification(first_name: str, token: str) -> tuple[str, str]:
    url = f"{settings.FRONTEND_URL}/accesso/verifica-email?token={token}"
    body = (
        f"<p>Ciao {escape(first_name)},</p>"
        "<p>è stato creato un account amministratore per il sito dell'Associazione Giguiya con questo indirizzo.</p>"
        "<p>Conferma il tuo indirizzo email per attivare l'accesso all'area di gestione. Il link è valido 48 ore.</p>"
        f"{_button(url, 'Conferma email')}"
        "<p>Se non hai richiesto tu questo account, ignora questa email.</p>"
    )
    return "Conferma il tuo account amministratore Giguiya", _layout("Conferma il tuo account", body)


def password_reset(first_name: str, token: str) -> tuple[str, str]:
    url = f"{settings.FRONTEND_URL}/accesso/imposta-password?token={token}"
    body = (
        f"<p>Ciao {escape(first_name)},</p>"
        "<p>abbiamo ricevuto una richiesta di reimpostazione della password per il tuo account.</p>"
        "<p>Usa il pulsante qui sotto per sceglierne una nuova. Il link è valido 1 ora.</p>"
        f"{_button(url, 'Reimposta password')}"
        "<p>Se non hai fatto tu la richiesta, ignora questa email: la password resterà invariata.</p>"
    )
    return "Reimposta la tua password Giguiya", _layout("Reimposta password", body)
