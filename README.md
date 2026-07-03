# 🚀 JobPilot AI

JobPilot AI est une API développée avec FastAPI permettant de rechercher, filtrer et classer automatiquement des offres d'emploi, en s'appuyant sur l'API France Travail.

## 🎯 Objectifs

- Rechercher des offres d'emploi par mot-clé et localisation
- Calculer un score de pertinence par offre
- Se connecter aux API d'emploi (France Travail intégré, autres sources à venir : Jooble...)
- Exposer une API stable comme base pour une future interface Web et mobile

---

## 🛠️ Technologies

- Python 3.14
- FastAPI
- Uvicorn
- Pydantic Settings (configuration)
- Pytest (tests)
- SonarQube (qualité de code)
- Git / GitHub

---

## 📁 Structure actuelle

```
jobpilot-ai/
│
├── app.py
├── requirements.txt
├── .env
├── README.md
│
└── app/
    ├── main.py
    │
    ├── api/
    │   └── routes/
    │       ├── jobs.py       # GET /jobs, GET /jobs/{job_id}
    │       └── search.py     # GET /search
    │
    ├── core/
    │   └── config.py         # configuration centralisée (pydantic-settings)
    │
    ├── models/
    │   └── job.py
    │
    ├── services/
    │   ├── france_travail.py # accès API France Travail (OAuth2)
    │   └── jobs_service.py   # scoring, lookup par ID
    │
    ├── data/
    │   └── mock_jobs.json
    │
    └── tests/
        ├── test_jobs.py
        ├── test_jobs_service.py
        ├── test_main.py
        └── test_search.py
```

---

## ⚙️ Configuration

Créer un fichier `.env` à la racine du projet avec les identifiants API France Travail (obtenus sur [francetravail.io](https://francetravail.io)) :

```
FRANCE_TRAVAIL_CLIENT_ID=ton_client_id
FRANCE_TRAVAIL_CLIENT_SECRET=ton_client_secret
```

---

## ▶️ Lancer le projet

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Lancer l'API :

```bash
python -m uvicorn app:app --reload
```

Documentation Swagger :

```
http://127.0.0.1:8000/docs
```

---

## ✅ Lancer les tests

```bash
python -m pytest
```

---

## 📡 Endpoints principaux

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/jobs` | Recherche d'offres avec score de pertinence, triées |
| GET | `/jobs/{job_id}` | Détail d'une offre par identifiant |
| GET | `/search` | Recherche brute (liste d'offres, sans scoring) |
| GET | `/health` | Vérification de l'état de l'API |

---

## 🗺️ Roadmap

- [ ] Interface Web
- [ ] Application mobile (iOS / Android, publication sur les stores)
- [ ] Intégration de sources d'offres supplémentaires (Jooble...)
- [ ] Politique de confidentialité et conformité RGPD (prérequis publication store)
- [ ] Gestion du rate limiting côté API France Travail

---
