# 🚀 JobPilot AI

JobPilot AI est une API développée avec FastAPI permettant de rechercher, filtrer et classer automatiquement des offres d'emploi.

## 🎯 Objectifs

- Rechercher des offres d'emploi
- Filtrer les résultats
- Calculer un score de pertinence
- Se connecter aux API d'emploi (France Travail, Jooble...)
- Préparer les données pour une future interface Web

---

## 🛠️ Technologies

- Python 3.14
- FastAPI
- Uvicorn
- Git
- GitHub

---

## 📁 Structure actuelle

```
jobpilot-ai/
│
├── app.py
├── data/
├── models/
├── routes/
├── services/
└── README.md
```

---

## ▶️ Lancer le projet

Installer les dépendances :

```bash
pip install fastapi uvicorn
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

## 📈 Roadmap

- ✅ API FastAPI
- ✅ Lecture des offres JSON
- ✅ Git & GitHub
- ✅ Documentation
- ⏳ API France Travail
- ⏳ Score IA
- ⏳ Interface Web
