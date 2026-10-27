from datetime import timedelta

from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_password, verify_password
from app.core.utils import TZ, new_id, utcnow

PROJECTS = [
    {
        "slug": "sport-squadra-maschile", "title": "Sport – Squadra Maschile", "category": "Sport",
        "subtitle": "La nostra squadra maschile nel campionato italiano",
        "summary": "Lo sport come linguaggio universale: la squadra maschile di Giguiya partecipa al campionato italiano "
                   "portando in campo passione, disciplina e spirito di comunità.",
        "description": "La squadra maschile dell'Associazione Giguiya gioca nel campionato italiano – categoria "
                       "[CATEGORIA DA DEFINIRE]. Allenamenti, partite e trasferte sono occasioni di crescita personale, "
                       "di amicizia e di incontro tra ragazzi della comunità maliana e la città di Torino.",
        "image_url": "/images/sport.jpg", "partners": "", "year_label": "Stagione in corso",
        "highlights": ["Campionato italiano – categoria [DA DEFINIRE]", "Allenamenti settimanali",
                       "Inclusione attraverso lo sport", "Tifosi e famiglie sempre benvenuti"],
        "sort_order": 1,
    },
    {
        "slug": "intrecci-di-comunita", "title": "Intrecci di Comunità", "category": "Comunità",
        "subtitle": "Realizzato grazie al contributo della Città di Torino",
        "summary": "Laboratori di treccine maliane e di cucina maliana, gite ed eventi musicali aperti alla "
                   "cittadinanza: un ponte tra culture nel cuore di Torino.",
        "description": "Intrecci di Comunità è un progetto dell'Associazione Giguiya realizzato grazie al contributo "
                       "della Città di Torino. Attraverso laboratori, gite ed eventi musicali aperti a tutta la "
                       "cittadinanza, valorizziamo la cultura maliana e creiamo spazi di incontro, scambio e amicizia.",
        "image_url": "/images/treccine.jpg", "partners": "Città di Torino", "year_label": "In corso",
        "highlights": ["Laboratorio di treccine maliane", "Laboratorio di cucina maliana", "Gite sul territorio",
                       "Eventi musicali aperti alla cittadinanza"],
        "sort_order": 2,
    },
    {
        "slug": "progetto-baliba", "title": "Progetto Baliba", "category": "Inclusione",
        "subtitle": "Con INTERSOS e UNHCR – 2023",
        "summary": "Uno sportello di ascolto aperto alla comunità maliana per facilitare il percorso di inclusione "
                   "e di cittadinanza.",
        "description": "Il Progetto Baliba è stato realizzato nel 2023 insieme a INTERSOS e UNHCR. Ha dato vita a "
                       "uno sportello di ascolto aperto alla comunità maliana, pensato per orientare, accompagnare "
                       "e facilitare il percorso di inclusione sociale e di accesso alla cittadinanza.",
        "image_url": "/images/baliba.jpg", "partners": "INTERSOS · UNHCR", "year_label": "2023",
        "highlights": ["Sportello di ascolto", "Orientamento ai servizi", "Accompagnamento all'inclusione",
                       "Percorsi verso la cittadinanza"],
        "sort_order": 3,
    },
]


def _sample_events() -> list[dict]:
    base = utcnow().astimezone(TZ).replace(hour=15, minute=0, second=0, microsecond=0)
    return [
        {"slug": "laboratorio-treccine-maliane", "title": "Laboratorio di Treccine Maliane", "category": "Laboratorio",
         "summary": "Un pomeriggio dedicato all'arte delle treccine maliane, tra tecnica, storia e racconti.",
         "description": "Nell'ambito del progetto Intrecci di Comunità, un laboratorio aperto a tutte e tutti per "
                        "scoprire l'arte delle treccine maliane. [Dettagli da completare dall'amministrazione]",
         "location": "[Luogo da definire], Torino", "start_at": base + timedelta(days=14),
         "end_at": base + timedelta(days=14, hours=3), "image_url": "/images/treccine.jpg", "capacity": 20,
         "price_label": "Gratuito"},
        {"slug": "laboratorio-cucina-maliana", "title": "Laboratorio di Cucina Maliana", "category": "Laboratorio",
         "summary": "Cuciniamo insieme i sapori del Mali e condividiamo la tavola.",
         "description": "Un laboratorio di cucina maliana aperto alla cittadinanza, parte del progetto Intrecci di "
                        "Comunità. [Dettagli da completare dall'amministrazione]",
         "location": "[Luogo da definire], Torino", "start_at": base + timedelta(days=28, hours=2),
         "end_at": base + timedelta(days=28, hours=5), "image_url": "/images/cucina.jpg", "capacity": 25,
         "price_label": "Gratuito"},
        {"slug": "serata-musicale-maliana", "title": "Serata di Musica Maliana", "category": "Musica",
         "summary": "Ritmi, voci e strumenti della tradizione maliana: una serata aperta a tutta la città.",
         "description": "Evento musicale aperto alla cittadinanza nell'ambito di Intrecci di Comunità. "
                        "[Dettagli da completare dall'amministrazione]",
         "location": "[Luogo da definire], Torino", "start_at": base + timedelta(days=42, hours=5),
         "end_at": base + timedelta(days=42, hours=9), "image_url": "/images/musica.jpg", "capacity": None,
         "price_label": "Ingresso libero"},
    ]


def _doc(values: dict) -> dict:
    return {"id": new_id(), "created_at": utcnow(), "is_published": True, **values}


EVENT_DEFAULTS = {"end_at": None, "capacity": None, "price_label": None, "image_url": None}


async def seed() -> None:
    db = get_db()
    admin = await db.users.find_one({"email": settings.ADMIN_EMAIL})
    if not admin:
        await db.users.insert_one({
            "id": new_id(), "email": settings.ADMIN_EMAIL, "password_hash": hash_password(settings.ADMIN_PASSWORD),
            "first_name": "Admin", "last_name": "Giguiya", "phone": None, "role": "admin",
            "email_verified": True, "admin_status": "approved", "created_at": utcnow(),
        })
    elif not verify_password(settings.ADMIN_PASSWORD, admin.get("password_hash")):
        await db.users.update_one({"email": settings.ADMIN_EMAIL},
                                  {"$set": {"password_hash": hash_password(settings.ADMIN_PASSWORD)}})
    await db.users.update_many(
        {"role": "admin", "email": {"$ne": settings.ADMIN_EMAIL.lower()}, "admin_status": {"$exists": False}},
        {"$set": {"admin_status": "pending"}})
    if not await db.projects.count_documents({}):
        await db.projects.insert_many([_doc(p) for p in PROJECTS])
    if not await db.events.count_documents({}):
        await db.events.insert_many([_doc({**EVENT_DEFAULTS, **e}) for e in _sample_events()])
