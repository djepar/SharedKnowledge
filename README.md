# 📚 Classroom Management Platform
*Plateforme de gestion de classe - Éducation québécoise*

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-yellow.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

Une plateforme web moderne pour la gestion de classe et le suivi pédagogique, spécialement conçue pour le système éducatif québécois.

## ✨ Fonctionnalités principales

### 🎯 Programme de français secondaire 2 (NOUVEAU!)
- **📅 Calendrier interactif** - 160 séances complètes du programme PFEQ
- **📖 Plans de cours détaillés** - Objectifs, matériel, déroulement complet
- **📊 Suivi de progression** - Marquez les leçons terminées, statistiques en temps réel
- **📚 Carnet de lecture personnel** - Portfolio de lecture avec notes et évaluations
- **🎯 Conformité PFEQ** - Respect complet du programme officiel du Québec

### 🎨 Interface moderne (NOUVEAU!)
- ✅ **Architecture CSS professionnelle** - Composants modulaires et maintenables
- ✅ **Design cohérent** - Variables CSS centralisées et système de couleurs unifié
- ✅ **Responsive design** - Optimisé pour desktop, tablette et mobile
- ✅ **Animations fluides** - Transitions et effets visuels modernes
- ✅ **Accessibilité** - Contraste et navigation optimisés

## 🚀 Installation et démarrage

### Installation rapide
```bash
# Cloner le repository
git clone https://github.com/yourusername/classroom-app.git
cd classroom-app

# Installer les dépendances
pip install -r requirements.txt

# Construire les assets CSS (NOUVEAU!)
python simple_css_build.py

# Lancer l'application
python app.py
```

L'application sera disponible sur `http://localhost:5002`

## 🎨 Architecture CSS (NOUVEAU!)

### Structure modulaire
```
static/css/
├── base/
│   ├── variables.css    # Variables CSS centralisées
│   └── reset.css        # Reset navigateur
├── components/
│   ├── navigation.css   # Barre de navigation
│   ├── buttons.css      # Système de boutons
│   ├── forms.css        # Formulaires
│   ├── dashboard.css    # Tableau de bord
│   ├── auth.css         # Pages d'authentification
│   └── home.css         # Page d'accueil
└── dist/
   └── main.css         # CSS final compilé
```

### Build CSS
```bash
# Compiler tous les composants CSS
python simple_css_build.py
```

## 📋 Liste des tâches

### ✅ Terminé
- [x] Système d'inscription des étudiants
- [x] Calendrier complet français secondaire 2 (160 séances)
- [x] Suivi de progression individuelle
- [x] Carnet de lecture personnel
- [x] Dashboard avec statistiques
- [x] **Architecture CSS modulaire** - Composants CSS organisés
- [x] **Design system cohérent** - Variables CSS centralisées
- [x] **Build automatisé** - Script de compilation CSS

### 📅 Court terme
- [ ] **Finaliser templates CSS** - Compléter calendar.html, reading_log.html, add_book.html
- [ ] **Tests d'interface** - Validation responsive
- [ ] **Optimisation CSS** - Minification pour production

### 🔮 Fonctionnalités futures
- [ ] Gestion des notes et évaluations
- [ ] API REST complète
- [ ] Application mobile native

## 🔧 Développement

### Variables CSS disponibles
- `--primary-color`, `--secondary-color` - Couleurs principales
- `--space-sm`, `--space-md`, `--space-lg` - Espacement
- `--radius-sm`, `--radius-md`, `--radius-lg` - Bordures arrondies
- `--shadow-sm`, `--shadow-md`, `--shadow-lg` - Ombres

---

*Développé pour l'enseignement libre de droit*
