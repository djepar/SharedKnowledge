#!/usr/bin/env python3
"""
CSS Build Script for Classroom Management Platform
Combines and optionally minifies CSS files for production
"""

import os
import re
from pathlib import Path
from datetime import datetime

def create_css_structure():
    """Create the CSS directory structure"""
    css_dirs = [
        'static/css/base',
        'static/css/components',
        'static/css/layouts',
        'static/css/pages',
        'static/css/dist'
    ]
    
    for dir_path in css_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")

def build_css(minify=False):
    """Build CSS by combining all component files"""
    
    # Define CSS files in order of dependency
    css_files = [
        'static/css/base/variables.css',
        'static/css/base/reset.css',
        'static/css/base/typography.css',
        'static/css/components/navigation.css',
        'static/css/components/buttons.css',
        'static/css/components/cards.css',
        'static/css/components/forms.css',
        'static/css/components/alerts.css',
        'static/css/layouts/dashboard.css',
        'static/css/layouts/calendar.css',
        'static/css/layouts/auth.css',
    ]
    
    combined_css = f"""/*
 * Classroom Management Platform CSS
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * Auto-generated file - DO NOT EDIT DIRECTLY
 */

"""
    
    for file_path in css_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_css += f"\n/* === {file_path} === */\n"
                combined_css += content + "\n"
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Simple minification if requested
    if minify:
        combined_css = minify_css(combined_css)
        output_file = 'static/css/dist/main.min.css'
    else:
        output_file = 'static/css/dist/main.css'
    
    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_css)
    
    print(f"✅ CSS built successfully: {output_file}")
    print(f"📊 File size: {len(combined_css):,} characters")
    
    return output_file

def minify_css(css_content):
    """Simple CSS minification"""
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    # Remove extra whitespace
    css_content = re.sub(r'\s+', ' ', css_content)
    # Remove whitespace around specific characters
    css_content = re.sub(r'\s*([{}:;,])\s*', r'\1', css_content)
    # Remove trailing semicolons before }
    css_content = re.sub(r';\s*}', '}', css_content)
    
    return css_content.strip()

def extract_css_from_template(template_path, output_path):
    """Extract inline CSS from a template file"""
    if not os.path.exists(template_path):
        print(f"⚠️  Template not found: {template_path}")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find CSS between <style> tags
    css_match = re.search(r'<style[^>]*>(.*?)</style>', content, re.DOTALL)
    if css_match:
        css_content = css_match.group(1).strip()
        
        # Clean up the CSS
        css_content = '\n'.join(line.strip() for line in css_content.split('\n') if line.strip())
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ Extracted CSS from {template_path} to {output_path}")
        return css_content
    else:
        print(f"⚠️  No CSS found in {template_path}")
        return None

def update_template_to_use_external_css(template_path, css_files):
    """Update a template to use external CSS instead of inline"""
    if not os.path.exists(template_path):
        print(f"⚠️  Template not found: {template_path}")
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove existing <style> blocks
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    
    # Add CSS links in the head
    css_links = '\n'.join([
        f'    <link rel="stylesheet" href="{{{{ url_for(\'static\', filename=\'{css_file}\') }}}}">'
        for css_file in css_files
    ])
    
    # Insert CSS links before </head>
    if '</head>' in content:
        content = content.replace('</head>', f'{css_links}\n</head>')
    
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Updated {template_path} to use external CSS")

def migration_helper():
    """Help migrate from inline CSS to external CSS"""
    templates = [
        ('templates/home.html', 'static/css/pages/home.css'),
        ('templates/dashboard.html', 'static/css/layouts/dashboard.css'),
        ('templates/calendar.html', 'static/css/layouts/calendar.css'),
        ('templates/login.html', 'static/css/layouts/auth.css'),
        ('templates/register.html', 'static/css/layouts/auth.css'),
        ('templates/reading_log.html', 'static/css/pages/reading_log.css'),
        ('templates/add_book.html', 'static/css/pages/add_book.css'),
        ('templates/lesson_detail.html', 'static/css/pages/lesson_detail.css'),
    ]
    
    print("�� Starting CSS migration...")
    
    for template_path, css_output in templates:
        if os.path.exists(template_path):
            extract_css_from_template(template_path, css_output)
    
    print("✅ CSS extraction completed!")

def watch_css_files():
    """Watch CSS files for changes and rebuild automatically"""
    import time
    
    css_dir = Path('static/css')
    last_modified = {}
    
    print("👀 Watching CSS files for changes... (Press Ctrl+C to stop)")
    
    try:
        while True:
            changed = False
            
            for css_file in css_dir.rglob('*.css'):
                if css_file.name.startswith('main'):
                    continue  # Skip generated files
                
                try:
                    current_modified = css_file.stat().st_mtime
                    if css_file not in last_modified or last_modified[css_file] != current_modified:
                        last_modified[css_file] = current_modified
                        changed = True
                        print(f"📝 Change detected: {css_file}")
                except FileNotFoundError:
                    pass
            
            if changed:
                build_css()
                print("🔄 CSS rebuilt successfully!")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n👋 Stopped watching CSS files")

def main():
    """Main function with CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
🎨 CSS Build Tool for Classroom Management Platform

Usage:
    python build_css.py setup       - Create CSS directory structure
    python build_css.py build       - Build CSS (development)
    python build_css.py build-prod  - Build and minify CSS (production)
    python build_css.py extract     - Extract CSS from templates
    python build_css.py watch       - Watch files and rebuild automatically
    python build_css.py help        - Show this help message
        """)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'setup':
        create_css_structure()
        print("\n✅ CSS structure created! You can now:")
        print("   1. Move your existing CSS into the component files")
        print("   2. Run 'python build_css.py build' to combine them")
        print("   3. Update your templates to use the combined CSS")
    
    elif command == 'build':
        build_css(minify=False)
    
    elif command == 'build-prod':
        build_css(minify=True)
    
    elif command == 'extract':
        migration_helper()
    
    elif command == 'watch':
        watch_css_files()
    
    elif command == 'help':
        main()  # Show help
    
    else:
        print(f"❌ Unknown command: {command}")
        main()

if __name__ == "__main__":
    main()
