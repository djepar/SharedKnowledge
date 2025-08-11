#!/usr/bin/env python3
"""
Khan Academy Style Learning Platform Database Setup
Creates a complete database structure for an online learning platform
"""

import sqlite3
import os
from datetime import datetime

def create_database():
    """Create the database file and all tables"""
    
    # Remove existing database if it exists
    if os.path.exists('database.db'):
        print("🗑️  Removing existing database...")
        os.remove('database.db')
    
    print("📚 Creating Khan Academy style learning platform database...")
    
    # Connect to database (creates the file)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # Users table (basic user info)
        print("Creating users table...")
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        ''')
        
        # Learning Tracks (like "Web Development", "Data Science", "Mathematics")
        print("Creating learning_tracks table...")
        cursor.execute('''
        CREATE TABLE learning_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            category VARCHAR(50) NOT NULL,
            difficulty_level VARCHAR(20) DEFAULT 'beginner',
            estimated_hours INTEGER,
            cover_image VARCHAR(255),
            is_published BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            sort_order INTEGER DEFAULT 0
        )
        ''')
        
        # Modules (grouped lessons within a track)
        print("Creating modules table...")
        cursor.execute('''
        CREATE TABLE modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER NOT NULL,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            estimated_minutes INTEGER,
            sort_order INTEGER DEFAULT 0,
            is_published BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (track_id) REFERENCES learning_tracks (id) ON DELETE CASCADE
        )
        ''')
        
        # Lessons (individual content pieces)
        print("Creating lessons table...")
        cursor.execute('''
        CREATE TABLE lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            content_type VARCHAR(20) NOT NULL,
            content_url VARCHAR(500),
            content_text TEXT,
            video_duration INTEGER,
            estimated_minutes INTEGER DEFAULT 10,
            sort_order INTEGER DEFAULT 0,
            is_published BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE
        )
        ''')
        
        # Exercises (practice problems, quizzes)
        print("Creating exercises table...")
        cursor.execute('''
        CREATE TABLE exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            exercise_type VARCHAR(30) NOT NULL,
            question TEXT NOT NULL,
            correct_answer TEXT,
            explanation TEXT,
            difficulty VARCHAR(20) DEFAULT 'easy',
            points INTEGER DEFAULT 10,
            hints TEXT,
            is_published BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE SET NULL
        )
        ''')
        
        # Exercise Options (for multiple choice questions)
        print("Creating exercise_options table...")
        cursor.execute('''
        CREATE TABLE exercise_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_id INTEGER NOT NULL,
            option_text TEXT NOT NULL,
            is_correct BOOLEAN DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
        )
        ''')
        
        # User Progress (tracking what users have completed)
        print("Creating user_progress table...")
        cursor.execute('''
        CREATE TABLE user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id INTEGER,
            exercise_id INTEGER,
            status VARCHAR(20) NOT NULL,
            progress_percentage INTEGER DEFAULT 0,
            time_spent INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
        )
        ''')
        
        # User Skills/Badges (achievements)
        print("Creating user_skills table...")
        cursor.execute('''
        CREATE TABLE user_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name VARCHAR(100) NOT NULL,
            skill_type VARCHAR(30) NOT NULL,
            level INTEGER DEFAULT 1,
            points_earned INTEGER DEFAULT 0,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            track_id INTEGER,
            description TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (track_id) REFERENCES learning_tracks (id) ON DELETE SET NULL
        )
        ''')
        
        # Prerequisites (lesson dependencies)
        print("Creating prerequisites table...")
        cursor.execute('''
        CREATE TABLE prerequisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            module_id INTEGER,
            prerequisite_lesson_id INTEGER,
            prerequisite_module_id INTEGER,
            is_required BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id) ON DELETE CASCADE,
            FOREIGN KEY (module_id) REFERENCES modules (id) ON DELETE CASCADE,
            FOREIGN KEY (prerequisite_lesson_id) REFERENCES lessons (id) ON DELETE CASCADE,
            FOREIGN KEY (prerequisite_module_id) REFERENCES modules (id) ON DELETE CASCADE
        )
        ''')
        
        # User Stats (streaks, points, etc.)
        print("Creating user_stats table...")
        cursor.execute('''
        CREATE TABLE user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            total_points INTEGER DEFAULT 0,
            lessons_completed INTEGER DEFAULT 0,
            exercises_completed INTEGER DEFAULT 0,
            time_spent_total INTEGER DEFAULT 0,
            last_activity_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(user_id)
        )
        ''')
        
        # User Exercise Attempts (detailed tracking)
        print("Creating user_exercise_attempts table...")
        cursor.execute('''
        CREATE TABLE user_exercise_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            user_answer TEXT,
            is_correct BOOLEAN,
            points_earned INTEGER DEFAULT 0,
            time_taken INTEGER,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES exercises (id) ON DELETE CASCADE
        )
        ''')
        
        # Create indexes for better performance
        print("Creating database indexes...")
        indexes = [
            'CREATE INDEX idx_modules_track ON modules(track_id)',
            'CREATE INDEX idx_lessons_module ON lessons(module_id)',
            'CREATE INDEX idx_exercises_lesson ON exercises(lesson_id)',
            'CREATE INDEX idx_user_progress_user ON user_progress(user_id)',
            'CREATE INDEX idx_user_progress_lesson ON user_progress(lesson_id)',
            'CREATE INDEX idx_user_skills_user ON user_skills(user_id)',
            'CREATE INDEX idx_prerequisites_lesson ON prerequisites(lesson_id)',
            'CREATE INDEX idx_exercise_options_exercise ON exercise_options(exercise_id)',
            'CREATE INDEX idx_user_attempts_user ON user_exercise_attempts(user_id)'
        ]
        
        for index in indexes:
            cursor.execute(index)
        
        conn.commit()
        print("✅ Database tables created successfully!")
        
        return conn, cursor
        
    except sqlite3.Error as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        return None, None

def add_sample_data(conn, cursor):
    """Add sample learning content to test the database"""
    
    try:
        print("\n📝 Adding sample data...")
        
        # Sample user
        cursor.execute('''
        INSERT INTO users (name, email, password, role) 
        VALUES (?, ?, ?, ?)
        ''', ('John Doe', 'john@example.com', 'password123', 'student'))
        
        cursor.execute('''
        INSERT INTO users (name, email, password, role) 
        VALUES (?, ?, ?, ?)
        ''', ('Jane Teacher', 'teacher@example.com', 'password123', 'teacher'))
        
        # Sample learning track
        cursor.execute('''
        INSERT INTO learning_tracks 
        (title, description, category, difficulty_level, estimated_hours, sort_order) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Web Development Fundamentals', 
              'Master the building blocks of the web: HTML, CSS, and JavaScript', 
              'programming', 'beginner', 40, 1))
        
        track_id = cursor.lastrowid
        
        cursor.execute('''
        INSERT INTO learning_tracks 
        (title, description, category, difficulty_level, estimated_hours, sort_order) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Python Programming', 
              'Learn Python from basics to advanced concepts', 
              'programming', 'beginner', 60, 2))
        
        # Sample modules for Web Development
        cursor.execute('''
        INSERT INTO modules 
        (track_id, title, description, estimated_minutes, sort_order) 
        VALUES (?, ?, ?, ?, ?)
        ''', (track_id, 'HTML Basics', 
              'Learn the structure and elements of HTML', 120, 1))
        
        module_id = cursor.lastrowid
        
        cursor.execute('''
        INSERT INTO modules 
        (track_id, title, description, estimated_minutes, sort_order) 
        VALUES (?, ?, ?, ?, ?)
        ''', (track_id, 'CSS Fundamentals', 
              'Style your web pages with CSS', 180, 2))
        
        # Sample lessons for HTML Basics module
        cursor.execute('''
        INSERT INTO lessons 
        (module_id, title, description, content_type, estimated_minutes, sort_order) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (module_id, 'What is HTML?', 
              'Introduction to HTML and web structure', 'video', 15, 1))
        
        lesson_id = cursor.lastrowid
        
        cursor.execute('''
        INSERT INTO lessons 
        (module_id, title, description, content_type, content_text, estimated_minutes, sort_order) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (module_id, 'HTML Elements and Tags', 
              'Learn about different HTML elements', 'article',
              'HTML elements are the building blocks of web pages. Common elements include <h1>, <p>, <div>, and <span>.',
              20, 2))
        
        cursor.execute('''
        INSERT INTO lessons 
        (module_id, title, description, content_type, estimated_minutes, sort_order) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (module_id, 'Creating Your First HTML Page', 
              'Hands-on practice creating HTML', 'interactive', 25, 3))
        
        # Sample exercise
        cursor.execute('''
        INSERT INTO exercises 
        (lesson_id, title, exercise_type, question, correct_answer, explanation, points) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (lesson_id, 'HTML Basics Quiz', 'multiple_choice', 
              'What does HTML stand for?', 'HyperText Markup Language',
              'HTML stands for HyperText Markup Language, the standard markup language for web pages.', 10))
        
        exercise_id = cursor.lastrowid
        
        # Multiple choice options
        options = [
            ('HyperText Markup Language', True),
            ('High Tech Modern Language', False),
            ('Home Tool Markup Language', False),
            ('Hyperlink and Text Markup Language', False)
        ]
        
        for i, (option_text, is_correct) in enumerate(options):
            cursor.execute('''
            INSERT INTO exercise_options 
            (exercise_id, option_text, is_correct, sort_order) 
            VALUES (?, ?, ?, ?)
            ''', (exercise_id, option_text, is_correct, i + 1))
        
        # Sample user stats
        cursor.execute('''
        INSERT INTO user_stats 
        (user_id, current_streak, total_points, lessons_completed) 
        VALUES (?, ?, ?, ?)
        ''', (1, 5, 150, 3))
        
        conn.commit()
        print("✅ Sample data added successfully!")
        
    except sqlite3.Error as e:
        print(f"❌ Error adding sample data: {e}")
        conn.rollback()

def show_database_info(cursor):
    """Display information about the created database"""
    
    print("\n" + "="*60)
    print("📊 DATABASE STRUCTURE OVERVIEW")
    print("="*60)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"\n📋 Tables created: {len(tables)}")
    for table in tables:
        print(f"   ├── {table}")
    
    print(f"\n🏗️ Database Structure:")
    print("   learning_tracks (Programming, Math, etc.)")
    print("   ├── modules (grouped lessons within tracks)")
    print("   │   ├── lessons (individual content pieces)")
    print("   │   └── exercises (practice problems)")
    print("   └── prerequisites (lesson dependencies)")
    print("")
    print("   users")
    print("   ├── user_progress (completion tracking)")
    print("   ├── user_skills (badges/achievements)")
    print("   ├── user_stats (streaks, points, etc.)")
    print("   └── user_exercise_attempts (detailed tracking)")
    
    # Show sample data counts
    print(f"\n📈 Sample Data Added:")
    sample_tables = ['users', 'learning_tracks', 'modules', 'lessons', 'exercises']
    for table in sample_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {table}: {count} records")

def main():
    """Main function to set up the Khan Academy style learning platform"""
    
    print("🚀 Khan Academy Style Learning Platform Setup")
    print("=" * 50)
    
    # Create database and tables
    conn, cursor = create_database()
    
    if conn and cursor:
        # Ask about sample data
        print("\n" + "="*50)
        add_sample = input("📚 Add sample learning content for testing? (y/n): ").lower().strip()
        
        if add_sample in ['y', 'yes']:
            add_sample_data(conn, cursor)
        
        # Show database info
        show_database_info(cursor)
        
        print("\n" + "="*60)
        print("�� SETUP COMPLETE!")
        print("="*60)
        print("Your Khan Academy style learning platform database is ready!")
        print("\n📝 Next steps:")
        print("   1. View tables: sqlite3 database.db '.tables'")
        print("   2. Check structure: sqlite3 database.db '.schema learning_tracks'")
        print("   3. View sample data: sqlite3 database.db 'SELECT * FROM learning_tracks;'")
        print("   4. Start building your Flask routes and templates!")
        
        conn.close()
    else:
        print("❌ Failed to create database. Please check for errors above.")

if __name__ == "__main__":
    main()
