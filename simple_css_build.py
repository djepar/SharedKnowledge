#!/usr/bin/env python3
"""
Simple CSS build script - Clean component-based approach
"""

import os
from pathlib import Path
from datetime import datetime

def build_css():
    """Build CSS by combining component files in logical order"""
    
    # Create dist directory if it doesn't exist
    Path('static/css/dist').mkdir(parents=True, exist_ok=True)
    
    # Clean, logical order
    css_files = [
        'static/css/base/variables.css',         # Variables first (colors, spacing)
        'static/css/base/reset.css',             # Reset browser defaults
        'static/css/components/navigation.css',  # Navigation (used everywhere)
        'static/css/components/buttons.css',     # Buttons (used everywhere)
        'static/css/components/forms.css',       # Forms (used in multiple pages)
        'static/css/components/home.css',        # Home page specific
        'static/css/components/dashboard.css',   # Dashboard page specific
        'static/css/components/auth.css',        # Authentication pages
        'static/css/components/calendar.css',    # Calendar page
        'static/css/components/reading-log.css', # Reading log page
        'static/css/components/add-book.css',    # Add book page
        'static/css/components/lesson-detail.css', # Lesson detail page
    ]
    
    combined_css = f"""/*
 * Classroom Management Platform CSS - Clean Component Architecture
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 
 * Structure:
 * 1. Variables (colors, spacing, fonts)
 * 2. Reset (browser normalization)
 * 3. Navigation (reusable across all pages)
 * 4. Buttons & Forms (reusable components)
 * 5. Page-specific styles (home, dashboard, auth, etc.)
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
    print(f"📁 Clean component-based architecture!")
    
    return output_file

if __name__ == "__main__":
    print("🧹 Building clean CSS architecture...")
    build_css()
    print("🎉 Clean CSS build complete!")
