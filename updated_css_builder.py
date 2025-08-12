#!/usr/bin/env python3
"""
CSS Builder Complet - Version finale avec tous les composants
Compile tous les composants CSS dans un ordre logique
"""

import os
from pathlib import Path
from datetime import datetime

def build_css():
    """Build CSS en combinant tous les fichiers de composants dans l'ordre logique"""
    
    # Créer le répertoire dist s'il n'existe pas
    Path('static/css/dist').mkdir(parents=True, exist_ok=True)
    
    # Ordre logique et complet des fichiers CSS
    css_files = [
        # 1. Variables et reset (base)
        'static/css/base/variables.css',
        'static/css/base/reset.css',
        
        # 2. Composants réutilisables (dans l'ordre de dépendance)
        'static/css/components/navigation.css',
        'static/css/components/buttons.css',
        'static/css/components/forms.css',
        
        # 3. Pages spécifiques (dans l'ordre d'utilisation)
        'static/css/components/home.css',
        'static/css/components/dashboard.css',
        'static/css/components/auth.css',
        'static/css/components/calendar.css',
        'static/css/components/reading-log.css',
        'static/css/components/add-book.css',
        'static/css/components/lesson-detail.css',
    ]
    
    # En-tête du fichier CSS compilé
    combined_css = f"""/*
 * Classroom Management Platform CSS - Architecture Complète
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 
 * Architecture modulaire:
 * 1. Variables CSS (couleurs, espacements, polices)
 * 2. Reset navigateur (normalisation)
 * 3. Navigation (barre de navigation commune)
 * 4. Composants réutilisables (boutons, formulaires)
 * 5. Pages spécifiques (home, dashboard, auth, etc.)
 * 
 * Tous les templates sont maintenant compatibles avec cette architecture.
 */

"""
    
    # Compilation des fichiers
    files_found = 0
    files_missing = 0
    
    for file_path in css_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Ajouter un commentaire de section
                section_name = file_path.split('/')[-1].replace('.css', '').replace('-', ' ').title()
                combined_css += f"\n/* === {section_name} Component === */\n"
                combined_css += content + "\n"
                
            print(f"✅ Ajouté: {file_path}")
            files_found += 1
        else:
            print(f"⚠️  Fichier manquant: {file_path}")
            files_missing += 1
    
    # Écrire le fichier CSS final
    output_file = 'static/css/dist/main.css'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_css)
    
    # Statistiques de compilation
    print(f"\n🎉 CSS compilé avec succès!")
    print(f"�� Fichier de sortie: {output_file}")
    print(f"�� Taille du fichier: {len(combined_css):,} caractères")
    print(f"✅ Fichiers trouvés: {files_found}")
    print(f"⚠️  Fichiers manquants: {files_missing}")
    
    if files_missing == 0:
        print(f"🌟 Architecture CSS complète et prête!")
    else:
        print(f"⚡ Certains composants manquent, mais la compilation a réussi.")
    
    return output_file

def verify_css_structure():
    """Vérifier la structure des répertoires CSS"""
    
    print("\n🔍 Vérification de la structure CSS...")
    
    required_dirs = [
        'static/css/base',
        'static/css/components', 
        'static/css/dist'
    ]
    
    required_files = [
        'static/css/base/variables.css',
        'static/css/base/reset.css',
        'static/css/components/navigation.css',
        'static/css/components/buttons.css',
        'static/css/components/forms.css',
        'static/css/components/home.css',
        'static/css/components/dashboard.css',
        'static/css/components/auth.css',
        'static/css/components/calendar.css',
        'static/css/components/reading-log.css',
        'static/css/components/add-book.css',
    ]
    
    # Vérifier les répertoires
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Répertoire trouvé: {directory}")
        else:
            print(f"❌ Répertoire manquant: {directory}")
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"🆕 Répertoire créé: {directory}")
    
    # Vérifier les fichiers
    existing_files = 0
    for file_path in required_files:
        if os.path.exists(file_path):
            existing_files += 1
            print(f"✅ Fichier trouvé: {file_path}")
        else:
            print(f"❌ Fichier manquant: {file_path}")
    
    print(f"\n📊 Résumé: {existing_files}/{len(required_files)} fichiers trouvés")
    
    if existing_files == len(required_files):
        print("🌟 Structure CSS complète!")
    else:
        print("⚡ Certains fichiers CSS manquent. Consultez la documentation.")

def create_template_examples():
    """Créer des exemples de templates utilisant l'architecture CSS"""
    
    examples_dir = Path('templates/examples')
    examples_dir.mkdir(exist_ok=True)
    
    # Template d'exemple minimal
    example_template = '''<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Exemple - Français Secondaire 2</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dist/main.css') }}">
</head>
<body>
    <!-- Navigation -->
    <div class="nav-bar">
        <div class="nav-links">
            <a href="{{ url_for('index') }}">🏠 Accueil</a>
            <a href="{{ url_for('dashboard') }}">📊 Tableau de bord</a>
            <a href="{{ url_for('calendar') }}">📅 Calendrier</a>
            <a href="{{ url_for('reading_log') }}">📚 Carnet</a>
        </div>
        <div>
            <span style="margin-right: 15px;">👋 {{ session.user or 'Utilisateur' }}</span>
            <a href="{{ url_for('logout') }}" class="btn btn-danger btn-sm">Déconnexion</a>
        </div>
    </div>

    <!-- Contenu principal -->
    <div class="container">
        <div class="header">
            <h1>Page d'exemple</h1>
            <p>Utilise l'architecture CSS modulaire</p>
        </div>
        
        <!-- Contenu de la page -->
        <div class="content">
            <p>Cette page utilise les composants CSS modulaires.</p>
            
            <div class="form-group">
                <label>Exemple de formulaire:</label>
                <input type="text" placeholder="Utilise les styles de forms.css">
            </div>
            
            <button class="btn btn-primary">Bouton principal</button>
            <button class="btn btn-secondary">Bouton secondaire</button>
        </div>
    </div>
</body>
</html>'''
    
    with open(examples_dir / 'example.html', 'w', encoding='utf-8') as f:
        f.write(example_template)
    
    print(f"📝 Template d'exemple créé: {examples_dir / 'example.html'}")

if __name__ == "__main__":
    print("🏗️  CSS Builder - Version Complète")
    print("=" * 50)
    
    # Vérifier la structure
    verify_css_structure()
    
    # Compiler le CSS
    print("\n🎨 Compilation du CSS...")
    build_css()
    
    # Créer des exemples
    print("\n📝 Création d'exemples...")
    create_template_examples()
    
    print("\n" + "=" * 50)
    print("🎉 CSS Builder terminé!")
    print("\n💡 Prochaines étapes:")
    print("   1. Vérifiez que tous vos templates utilisent:")
    print("      <link rel=\"stylesheet\" href=\"{{ url_for('static', filename='css/dist/main.css') }}\">")
    print("   2. Utilisez les classes CSS comme .container, .nav-bar, .btn, etc.")
    print("   3. Testez l'application pour vérifier les styles")
    print("   4. Personalisez les variables dans static/css/base/variables.css")
