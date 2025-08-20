#!/usr/bin/env python3
"""
Simple CSS build script to combine all CSS files
Run this script to build your CSS files into a single main.css
"""

import os
from pathlib import Path
from datetime import datetime

def build_css():
    """Build CSS by combining all component files"""
    
    # Create directories if they don't exist
    Path('static/css/dist').mkdir(parents=True, exist_ok=True)
    
    # Define CSS files in order of dependency
    css_files = [
        'static/css/base/variables.css',
        'static/css/base/reset.css',
        'static/css/components/buttons.css',
        'static/css/components/forms.css',
        'static/css/components/navigation.css',
        'static/css/components/auth.css',
        'static/css/components/discipline-selection.css',
        'static/css/components/dashboard.css',
        'static/css/components/home.css',
        'static/css/components/calendar.css',
        'static/css/components/lesson-detail.css',
        'static/css/components/edit-lesson.css',
        'static/css/components/add-book.css',
        'static/css/components/reading-log.css',
        'static/css/components/theory.css',
        'static/css/components/exercises.css',
        'static/css/components/portfolio.css',
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
            print(f"✅ Added: {file_path}")
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Write combined CSS
    output_file = 'static/css/dist/main.css'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined_css)
    
    print(f"\n✅ CSS built successfully: {output_file}")
    print(f"📊 File size: {len(combined_css):,} characters")
    
    return output_file

if __name__ == "__main__":
    print("🎨 Building CSS files...")
    build_css()
    print("🎉 CSS build complete!")

