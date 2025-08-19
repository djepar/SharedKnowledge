# 📚 Classroom Management Platform
*Plateforme de gestion de classe - Éducation québécoise*

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-yellow.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

Une plateforme web moderne pour la gestion de classe et le suivi pédagogique, spécialement conçue pour le système éducatif québécois.

## ✨ Fonctionnalités principales

### 🎯 Gestion de leçons multi-matières (AMÉLIORÉ!)
- **📅 Calendrier interactif** - 160 séances complètes du programme PFEQ
- **📖 Plans de cours détaillés** - Objectifs, matériel, déroulement complet
- **✏️ Édition complète des leçons** - Formulaire avancé avec tous les champs
- **🎯 Filtrage par matière** - Organisation par français, mathématiques, etc.
- **📊 Suivi de progression** - Marquez les leçons terminées, statistiques en temps réel
- **📚 Carnet de lecture personnel** - Portfolio de lecture avec notes et évaluations
- **🔄 Compétences dynamiques** - API pour charger les compétences par discipline

### 🎨 Interface moderne (RÉCEMMENT AMÉLIORÉ!)
- ✅ **Architecture CSS composants** - BEM-like naming et isolation parfaite
- ✅ **Variables CSS complètes** - Design system unifié sans conflits
- ✅ **Zéro !important** - Spécificité CSS propre et maintenable
- ✅ **Layouts flexibles** - `.layout-auth`, `.layout-main`, `.layout-discipline`
- ✅ **Responsive design** - Optimisé pour desktop, tablette et mobile
- ✅ **Build optimisé** - Compilation CSS sans duplication ni erreurs

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

## 🎨 Architecture CSS Component-Based (RÉCEMMENT REFACTORISÉ!)

### Structure modulaire propre
```
static/css/
├── base/
│   ├── variables.css    # Toutes variables dans :root (FIXÉ!)
│   └── reset.css        # Layouts flexibles (.layout-*)
├── components/          # Composants isolés avec BEM-like naming
│   ├── navigation.css   # .nav-logout, .nav-dropdown
│   ├── auth.css         # .auth-header__title, .auth-btn
│   ├── buttons.css      # .btn-primary, .btn-outline-*
│   ├── forms.css        # .form-group, .form-row
│   ├── edit-lesson.css  # .edit-lesson-form, .field-group (NOUVEAU!)
│   ├── progress.css     # .progress-bar, .progress-circle
│   ├── dashboard.css    # .stat-card, .quick-actions
│   └── [autres...]      # Components page-spécifiques
└── dist/
    └── main.css        # Build final optimisé
```

### Build CSS amélioré
```bash
# Compiler avec validation et optimisation
python simple_css_build.py

# ✅ Résout toutes les variables CSS
# ✅ Élimine les duplications
# ✅ Validation des composants
# ✅ Architecture sans !important
```

### Nouveaux layouts composants
```html
<!-- Auth pages -->
<div class="layout-auth">
  <div class="auth-container">
    <h1 class="auth-header__title">Connexion</h1>
    <button class="auth-btn">Se connecter</button>
  </div>
</div>

<!-- Main app -->
<div class="layout-main">
  <nav class="nav-bar">
    <a href="/logout" class="nav-logout">Déconnexion</a>
  </nav>
</div>
```

## 📋 Liste des tâches

### ✅ Terminé
- [x] Système d'inscription des étudiants
- [x] Calendrier complet français secondaire 2 (160 séances)
- [x] Suivi de progression individuelle
- [x] Carnet de lecture personnel
- [x] Dashboard avec statistiques
- [x] **Architecture CSS component-based** - BEM-like naming et isolation
- [x] **Variables CSS complètes** - Toutes dans :root, zéro conflit
- [x] **Build CSS optimisé** - Sans duplication ni !important
- [x] **Layouts flexibles** - .layout-auth, .layout-main, .layout-discipline
- [x] **Templates mis à jour** - login.html avec nouveaux composants
- [x] **Édition complète des leçons** - Formulaire avancé avec tous les champs
- [x] **Filtrage par matière** - Organisation par discipline avec API compétences
- [x] **Composant edit-lesson.css** - Styles dédiés pour l'édition de leçons

### 📅 Court terme  
- [ ] **Mise à jour templates restants** - Appliquer l'architecture aux autres pages
- [ ] **Tests responsiveness** - Validation mobile/tablette/desktop
- [ ] **Documentation composants** - Guide d'utilisation CSS
- [ ] **Optimisation production** - Minification et tree-shaking

### 🔮 Fonctionnalités futures
- [ ] Gestion des notes et évaluations
- [ ] API REST complète
- [ ] Application mobile native

## 🔧 Développement

### Variables CSS disponibles (DESIGN SYSTEM COMPLET)
```css
/* Couleurs */
--primary-color, --primary-dark, --secondary-color
--success-color, --danger-color, --warning-color, --info-color
--gray-100 à --gray-800, --white, --black

/* Gradients */
--gradient-main, --gradient-primary, --gradient-success, etc.

/* Espacement */
--space-xs à --space-5xl (5px à 80px)

/* Bordures et ombres */
--radius-sm à --radius-2xl, --radius-full
--shadow-sm à --shadow-2xl

/* Typography */
--font-size-xs à --font-size-4xl
--font-weight-normal à --font-weight-bold

/* Transitions */
--transition-fast, --transition-normal, --transition-slow

/* Z-index */
--z-index-dropdown, --z-index-overlay, --z-index-modal
```

### Conventions de nommage
- **Composants**: `.component-name` (ex: `.auth-container`)
- **Modificateurs**: `.component__element` (ex: `.auth-header__title`)
- **Variants**: `.component--variant` (ex: `.alert--error`)
- **Layouts**: `.layout-context` (ex: `.layout-auth`)
- **Utilitaires**: `.u-utility` (rare, préférer les composants)

---

*Développé pour l'enseignement libre de droit*
