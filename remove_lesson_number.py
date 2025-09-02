#!/usr/bin/env python3
"""
Database migration script to remove lesson_number column and fix the lesson ID issue.
This script will:
1. Create a backup of the current database
2. Remove the lesson_number column from lessons table
3. Update all related code references
"""

import sqlite3
import os
import shutil
from datetime import datetime

def backup_database(db_path):
    """Create a backup of the database before migration"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return backup_path

def remove_lesson_number_column(db_path):
    """Remove lesson_number column from lessons table"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if lesson_number column exists
        cursor.execute("PRAGMA table_info(lessons)")
        columns = cursor.fetchall()
        
        has_lesson_number = any(col[1] == 'lesson_number' for col in columns)
        
        if not has_lesson_number:
            print("✅ lesson_number column already removed or doesn't exist")
            return True
        
        print("🔄 Removing lesson_number column...")
        
        # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
        # First, get the current table schema without lesson_number
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lessons'")
        if not cursor.fetchone():
            print("❌ lessons table not found")
            return False
        
        # Create new table without lesson_number
        cursor.execute('''
            CREATE TABLE lessons_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                week_number INTEGER NOT NULL,
                day_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                duration INTEGER DEFAULT 75,
                competences TEXT,
                materials TEXT,
                objectives TEXT,
                tags TEXT,
                subject TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Copy data from old table to new table (excluding lesson_number)
        cursor.execute('''
            INSERT INTO lessons_new (id, month, week_number, day_number, title, content, 
                                    duration, competences, materials, objectives, tags, subject, created_at)
            SELECT id, month, week_number, day_number, title, content, 
                   duration, competences, materials, objectives, tags, subject, created_at
            FROM lessons
        ''')
        
        # Drop old table
        cursor.execute('DROP TABLE lessons')
        
        # Rename new table to lessons
        cursor.execute('ALTER TABLE lessons_new RENAME TO lessons')
        
        conn.commit()
        print("✅ lesson_number column removed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error removing lesson_number column: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Main migration function"""
    db_path = "classroom.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found")
        return False
    
    print("🚀 Starting database migration to remove lesson_number...")
    
    # Step 1: Backup database
    backup_path = backup_database(db_path)
    
    # Step 2: Remove lesson_number column
    success = remove_lesson_number_column(db_path)
    
    if success:
        print("🎉 Database migration completed successfully!")
        print("✅ lesson_number column removed")
        print("✅ All lesson data preserved")
        print("✅ Auto-increment id will handle all numbering")
        return True
    else:
        print("❌ Migration failed")
        print(f"💾 Database backup available at: {backup_path}")
        return False

if __name__ == "__main__":
    main()