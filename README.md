# 📚 Classroom Management Platform
*Plateforme de gestion de classe - Éducation québécoise*

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-yellow.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

Une plateforme web moderne pour la gestion de classe et le suivi pédagogique, spécialement conçue pour le système éducatif québécois.

## ✨ Fonctionnalités principales

### 🎯 **Programme de français secondaire 2 (NOUVEAU!)**
- **📅 Calendrier interactif** - 160 séances complètes du programme PFEQ
- **📖 Plans de cours détaillés** - Objectifs, matériel, déroulement complet
- **📊 Suivi de progression** - Marquez les leçons terminées, statistiques en temps réel
- **📚 Carnet de lecture personnel** - Portfolio de lecture avec notes et évaluations
- **🎯 Conformité PFEQ** - Respect complet du programme officiel du Québec

### 👥 **Gestion des utilisateurs**
- ✅ Système d'inscription et connexion sécurisé
- ✅ Rôles enseignant/étudiant
- ✅ Sessions utilisateur persistantes
- ✅ Tableau de bord personnalisé

### 📊 **Suivi pédagogique**
- ✅ Progression individuelle par étudiant
- ✅ Statistiques de lecture et d'apprentissage
- ✅ Historique des activités complétées
- ✅ Visualisation des données d'apprentissage

## 🚀 Installation et démarrage

### Prérequis
- Python 3.12+
- Flask 3.0+
- SQLite 3.0+

### Installation rapide
```bash
# Cloner le repository
git clone https://github.com/yourusername/classroom-app.git
cd classroom-app

# Installer les dépendances
pip install -r requirements.txt

# Migrer la base de données (si mise à jour)
python migrate_db.py

# Lancer l'application
python app.py
```

L'application sera disponible sur `http://localhost:5002`

## 📁 Structure du projet

```
classroom-app/
├── app.py                 # Application Flask principale
├── migrate_db.py         # Script de migration de base de données
├── config.py             # Configuration de l'application
├── requirements.txt      # Dépendances Python
├── database.db          # Base de données SQLite (générée)
├── templates/           # Templates HTML
│   ├── home.html        # Page d'accueil
│   ├── login.html       # Connexion
│   ├── register.html    # Inscription
│   ├── dashboard.html   # Tableau de bord
│   ├── calendar.html    # Calendrier des cours
│   ├── lesson_detail.html # Détails des leçons
│   ├── reading_log.html # Carnet de lecture
│   └── add_book.html    # Ajouter un livre
├── static/              # Fichiers CSS/JS (à venir)
└── README.md           # Ce fichier
```

## 🗄️ Base de données

### Tables principales
- **`users`** - Comptes utilisateurs (enseignants/étudiants)
- **`lessons`** - 160 leçons du programme PFEQ
- **`student_progress`** - Suivi de progression des étudiants
- **`reading_log`** - Carnet de lecture personnel
- **`evaluations`** - Résultats d'évaluations (prêt pour développement futur)

### Migration automatique
Le système détecte et migre automatiquement les anciennes versions de base de données tout en préservant les données existantes.

## 🎓 Programme PFEQ intégré

### Français secondaire 2 - 160 séances
- **📖 Compétence LIRE (40%)** - 64 séances dédiées
- **✍️ Compétence ÉCRIRE (40%)** - 64 séances dédiées  
- **🗣️ Compétence COMMUNIQUER ORALEMENT (20%)** - 32 séances dédiées

### Genres littéraires couverts
- Romans québécois (3 minimum)
- Théâtre québécois (1 pièce)
- Poésie québécoise
- Fables et contes
- Textes informatifs et d'opinion

### Types de textes
- Descriptif (progression 150-300 mots)
- Justificatif 
- Explicatif
- Informatif

## 📱 Interface utilisateur

### Design moderne et responsive
- **🎨 Interface intuitive** - Navigation claire et accessible
- **📱 Compatible mobile** - Fonctionne sur tous les appareils
- **🇫🇷 Interface française** - Conçue pour l'éducation québécoise
- **⚡ Performances optimisées** - Chargement rapide et fluide

### Fonctionnalités interactives
- Calendrier interactif par mois
- Barres de progression animées
- Cartes de leçons avec prévisualisation
- Système de tags par compétences
- Notifications de succès/erreur

## 🔐 Sécurité

### Mesures actuelles
- Sessions utilisateur sécurisées
- Protection CSRF intégrée
- Validation des données d'entrée
- Isolation des bases de données par utilisateur

### Améliorations prévues
- Hachage des mots de passe (bcrypt)
- Exigences de mot de passe renforcées
- Authentification à deux facteurs
- Chiffrement des données sensibles

## 📋 Liste des tâches

### ✅ **Terminé**
- [x] Système d'inscription des étudiants
- [x] Page d'inscription des utilisateurs
- [x] Calendrier complet français secondaire 2 (160 séances)
- [x] Suivi de progression individuelle
- [x] Carnet de lecture personnel
- [x] Dashboard avec statistiques
- [x] Interface responsive
- [x] Migration automatique de base de données

### 🚧 **En cours de développement**
- [ ] Questions générées par base de données
- [ ] Application de gestion des questions
- [ ] Base de données des évaluations

### 📅 **Court terme (priorité haute)**
- [ ] **Séparation CSS** - Extraire les styles CSS dans des fichiers externes
- [ ] **Prototype complet français** - Finaliser toutes les fonctionnalités
- [ ] **Mathématiques** - Adapter le système pour les maths
- [ ] **Culture et citoyenneté québécoise** - Nouveau programme
- [ ] **Géographie et histoire** - Module d'univers social

### 🔮 **Fonctionnalités futures**
- [ ] Gestion des notes et évaluations
- [ ] Gestion avancée des utilisateurs (ajout/suppression)
- [ ] Téléchargement de fichiers
- [ ] Notifications par courriel
- [ ] Sécurité renforcée (exigences de mot de passe)
- [ ] Configuration de déploiement en production
- [ ] Rapports d'apprentissage automatisés
- [ ] Intégration avec systèmes scolaires existants
- [ ] Application mobile native
- [ ] Support multi-langues (anglais/français)

### 🏗️ **Architecture technique future**
- [ ] Migration vers PostgreSQL
- [ ] API REST complète
- [ ] Tests automatisés (pytest)
- [ ] CI/CD avec GitHub Actions
- [ ] Conteneurisation Docker
- [ ] Monitoring et logging avancés

## 🤝 Contribution

Les contributions sont les bienvenues! Voici comment contribuer:

1. **Fork** le projet
2. **Créer** une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Commiter** vos changements (`git commit -m 'Ajouter nouvelle fonctionnalité'`)
4. **Pousser** vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. **Ouvrir** une Pull Request

### Standards de développement
- Code en français pour les commentaires éducatifs
- Respect des standards PEP 8 pour Python
- Documentation claire des nouvelles fonctionnalités
- Tests unitaires pour les nouvelles features

## 📊 Statistiques du projet

- **Lignes de code**: ~2,000+
- **Templates HTML**: 8 fichiers
- **Fonctionnalités**: 15+ complètes
- **Tables de base de données**: 5
- **Compatibilité**: Python 3.12+, Flask 3.0+

## 🎯 Utilisation pédagogique

### Pour les enseignants
- Planification de cours structurée
- Suivi de progression des élèves
- Gestion des portfolios de lecture
- Respect des exigences PFEQ
- Évaluations standardisées

### Pour les étudiants
- Accès au calendrier de cours
- Suivi de leur propre progression
- Carnet de lecture personnel
- Visualisation des objectifs atteints
- Interface adaptée à leur niveau

## 📧 Support et contact

- **Issues GitHub**: [Ouvrir un ticket](https://github.com/yourusername/classroom-app/issues)
- **Documentation**: Consultez le wiki du projet
- **Discussions**: Utilisez les discussions GitHub pour les questions

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 🙏 Remerciements

- **Flask Team** - Pour le framework web excellent
- **Communauté éducative québécoise** - Pour les retours et suggestions

---


*Développé pour l'enseignement libre de droit*

