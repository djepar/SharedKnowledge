#!/usr/bin/env python3
"""
French Learning Database Creation Script
Creates a complete SQLite database for the French learning Flask app
Database file: database.db
"""

import sqlite3
import os
from datetime import datetime

def create_database():
    """Create the French learning database with all tables, indexes, triggers, and sample data"""
    
    # Remove existing database if it exists
    if os.path.exists('database.db'):
        os.remove('database.db')
        print("Removed existing database.db")
    
    # Create new database connection
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("Creating French Learning Database...")
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    try:
        # ========================================
        # LEARNING STRUCTURE TABLES
        # ========================================
        
        print("Creating learning structure tables...")
        
        # Learning tracks (course levels)
        cursor.execute('''
        CREATE TABLE learning_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_name VARCHAR(100) NOT NULL UNIQUE,
            track_code VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')) NOT NULL,
            estimated_duration_hours INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # Modules within tracks
        cursor.execute('''
        CREATE TABLE modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER NOT NULL,
            module_name VARCHAR(100) NOT NULL,
            module_code VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            order_sequence INTEGER NOT NULL,
            estimated_duration_hours INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (track_id) REFERENCES learning_tracks(id) ON DELETE CASCADE
        );
        ''')
        
        # Individual lessons
        cursor.execute('''
        CREATE TABLE lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id INTEGER NOT NULL,
            lesson_title VARCHAR(200) NOT NULL,
            lesson_content TEXT NOT NULL,
            lesson_type VARCHAR(20) CHECK (lesson_type IN ('theory', 'practice', 'assessment')) NOT NULL,
            difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')) NOT NULL,
            order_sequence INTEGER NOT NULL,
            estimated_duration_minutes INTEGER,
            points_possible INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (module_id) REFERENCES modules(id) ON DELETE CASCADE
        );
        ''')
        
        # Lesson prerequisites (many-to-many relationship)
        cursor.execute('''
        CREATE TABLE prerequisites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            prerequisite_lesson_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
            FOREIGN KEY (prerequisite_lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
            UNIQUE(lesson_id, prerequisite_lesson_id)
        );
        ''')
        
        # Exercises within lessons
        cursor.execute('''
        CREATE TABLE exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER NOT NULL,
            exercise_type VARCHAR(30) CHECK (exercise_type IN ('multiple_choice', 'fill_blank', 'translation', 'audio', 'writing')) NOT NULL,
            exercise_content TEXT NOT NULL,
            correct_answer TEXT,
            points_possible INTEGER DEFAULT 10,
            order_sequence INTEGER NOT NULL,
            instructions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
        );
        ''')
        
        # Multiple choice options for exercises
        cursor.execute('''
        CREATE TABLE exercise_options (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_id INTEGER NOT NULL,
            option_text TEXT NOT NULL,
            is_correct BOOLEAN DEFAULT FALSE,
            explanation TEXT,
            order_sequence INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
        );
        ''')
        
        # ========================================
        # USER MANAGEMENT TABLES
        # ========================================
        
        print("Creating user management tables...")
        
        # User accounts
        cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            proficiency_level VARCHAR(20) CHECK (proficiency_level IN ('beginner', 'intermediate', 'advanced')) DEFAULT 'beginner',
            preferred_language VARCHAR(10) DEFAULT 'en',
            is_active BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
        ''')
        
        # User progress through lessons
        cursor.execute('''
        CREATE TABLE user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            status VARCHAR(20) CHECK (status IN ('not_started', 'in_progress', 'completed')) DEFAULT 'not_started',
            completion_percentage INTEGER DEFAULT 0 CHECK (completion_percentage >= 0 AND completion_percentage <= 100),
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            last_accessed TIMESTAMP,
            attempts_count INTEGER DEFAULT 0,
            best_score INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE CASCADE,
            UNIQUE(user_id, lesson_id)
        );
        ''')
        
        # User exercise attempts
        cursor.execute('''
        CREATE TABLE user_exercise_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            user_answer TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            points_earned INTEGER DEFAULT 0,
            time_taken_seconds INTEGER,
            attempt_number INTEGER NOT NULL,
            feedback TEXT,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
        );
        ''')
        
        # User skill tracking
        cursor.execute('''
        CREATE TABLE user_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_category VARCHAR(30) CHECK (skill_category IN ('grammar', 'vocabulary', 'pronunciation', 'reading', 'writing')) NOT NULL,
            skill_subcategory VARCHAR(50),
            proficiency_score INTEGER DEFAULT 0 CHECK (proficiency_score >= 0 AND proficiency_score <= 100),
            practice_count INTEGER DEFAULT 0,
            last_practiced TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, skill_category, skill_subcategory)
        );
        ''')
        
        # User statistics summary
        cursor.execute('''
        CREATE TABLE user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            total_lessons_completed INTEGER DEFAULT 0,
            total_exercises_completed INTEGER DEFAULT 0,
            total_points_earned INTEGER DEFAULT 0,
            current_streak_days INTEGER DEFAULT 0,
            longest_streak_days INTEGER DEFAULT 0,
            average_lesson_score DECIMAL(5,2) DEFAULT 0.0,
            level_achieved VARCHAR(20) DEFAULT 'beginner',
            last_activity_date DATE,
            total_study_time_minutes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        ''')
        
        # ========================================
        # CONTENT REFERENCE TABLES
        # ========================================
        
        print("Creating content reference tables...")
        
        # French vocabulary words
        cursor.execute('''
        CREATE TABLE french_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            french_word VARCHAR(100) NOT NULL UNIQUE,
            english_translation VARCHAR(200) NOT NULL,
            pronunciation VARCHAR(200),
            word_type VARCHAR(20) CHECK (word_type IN ('noun', 'verb', 'adjective', 'adverb', 'preposition', 'conjunction', 'article', 'pronoun')) NOT NULL,
            gender VARCHAR(10) CHECK (gender IN ('masculine', 'feminine', 'neutral', 'none')) DEFAULT 'none',
            difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')) NOT NULL,
            usage_frequency INTEGER DEFAULT 1 CHECK (usage_frequency >= 1 AND usage_frequency <= 10),
            example_sentence_french TEXT,
            example_sentence_english TEXT,
            audio_file_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # Grammar and syntax topics
        cursor.execute('''
        CREATE TABLE grammar_syntax_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            topic_name VARCHAR(100) NOT NULL,
            key_concepts TEXT NOT NULL,
            examples TEXT,
            difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')) NOT NULL,
            practice_exercises TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL
        );
        ''')
        
        # Speech and oral skills
        cursor.execute('''
        CREATE TABLE speech_oral_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson_id INTEGER,
            skill_area VARCHAR(100) NOT NULL,
            key_elements TEXT NOT NULL,
            example_activities TEXT,
            difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')) NOT NULL,
            audio_resources TEXT,
            pronunciation_tips TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons(id) ON DELETE SET NULL
        );
        ''')
        
        # Literature content
        cursor.execute('''
        CREATE TABLE literature_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movement_period VARCHAR(100) NOT NULL,
            key_authors TEXT NOT NULL,
            major_works TEXT NOT NULL,
            core_ideas_style TEXT NOT NULL,
            time_period_start INTEGER,
            time_period_end INTEGER,
            historical_context TEXT,
            notable_characteristics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        
        # ========================================
        # DATABASE VIEWS
        # ========================================
        
        print("Creating database views...")
        
        # User lesson progress view
        cursor.execute('''
        CREATE VIEW user_lesson_progress AS
        SELECT 
            u.id as user_id,
            u.username,
            u.proficiency_level,
            lt.track_name,
            m.module_name,
            l.lesson_title,
            up.status,
            up.completion_percentage,
            up.best_score,
            up.attempts_count,
            up.started_at,
            up.completed_at,
            up.last_accessed
        FROM users u
        JOIN user_progress up ON u.id = up.user_id
        JOIN lessons l ON up.lesson_id = l.id
        JOIN modules m ON l.module_id = m.id
        JOIN learning_tracks lt ON m.track_id = lt.id;
        ''')
        
        # User performance summary view
        cursor.execute('''
        CREATE VIEW user_performance_summary AS
        SELECT 
            u.id as user_id,
            u.username,
            u.email,
            u.proficiency_level,
            us.total_lessons_completed,
            us.total_exercises_completed,
            us.total_points_earned,
            us.current_streak_days,
            us.longest_streak_days,
            us.average_lesson_score,
            us.level_achieved,
            us.last_activity_date,
            us.total_study_time_minutes,
            COUNT(up.id) as total_enrolled_lessons,
            SUM(CASE WHEN up.status = 'completed' THEN 1 ELSE 0 END) as completed_lessons,
            SUM(CASE WHEN up.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress_lessons
        FROM users u
        JOIN user_stats us ON u.id = us.user_id
        LEFT JOIN user_progress up ON u.id = up.user_id
        GROUP BY u.id, u.username, u.email, u.proficiency_level, us.total_lessons_completed, 
                 us.total_exercises_completed, us.total_points_earned, us.current_streak_days, 
                 us.longest_streak_days, us.average_lesson_score, us.level_achieved, 
                 us.last_activity_date, us.total_study_time_minutes;
        ''')
        
        # ========================================
        # PERFORMANCE INDEXES
        # ========================================
        
        print("Creating performance indexes...")
        
        # User progress indexes
        cursor.execute("CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);")
        cursor.execute("CREATE INDEX idx_user_progress_lesson_id ON user_progress(lesson_id);")
        cursor.execute("CREATE INDEX idx_user_progress_status ON user_progress(status);")
        
        # Exercise attempts indexes
        cursor.execute("CREATE INDEX idx_user_exercise_attempts_user_id ON user_exercise_attempts(user_id);")
        cursor.execute("CREATE INDEX idx_user_exercise_attempts_exercise_id ON user_exercise_attempts(exercise_id);")
        cursor.execute("CREATE INDEX idx_user_exercise_attempts_date ON user_exercise_attempts(attempted_at);")
        
        # Lesson structure indexes
        cursor.execute("CREATE INDEX idx_exercises_lesson_id ON exercises(lesson_id);")
        cursor.execute("CREATE INDEX idx_lessons_module_id ON lessons(module_id);")
        cursor.execute("CREATE INDEX idx_modules_track_id ON modules(track_id);")
        
        # Content indexes
        cursor.execute("CREATE INDEX idx_french_words_difficulty ON french_words(difficulty_level);")
        cursor.execute("CREATE INDEX idx_french_words_type ON french_words(word_type);")
        cursor.execute("CREATE INDEX idx_user_skills_user_id ON user_skills(user_id);")
        cursor.execute("CREATE INDEX idx_user_skills_category ON user_skills(skill_category);")
        
        # ========================================
        # TRIGGERS FOR AUTOMATION
        # ========================================
        
        print("Creating triggers...")
        
        # Trigger to update user stats when lesson is completed
        cursor.execute('''
        CREATE TRIGGER update_user_stats_on_lesson_completion
        AFTER UPDATE OF status ON user_progress
        FOR EACH ROW
        WHEN NEW.status = 'completed' AND OLD.status != 'completed'
        BEGIN
            UPDATE user_stats 
            SET total_lessons_completed = total_lessons_completed + 1,
                last_activity_date = DATE('now'),
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = NEW.user_id;
        END;
        ''')
        
        # Trigger to update user stats when exercise is completed
        cursor.execute('''
        CREATE TRIGGER update_user_stats_on_exercise_completion
        AFTER INSERT ON user_exercise_attempts
        FOR EACH ROW
        BEGIN
            UPDATE user_stats 
            SET total_exercises_completed = total_exercises_completed + 1,
                total_points_earned = total_points_earned + NEW.points_earned,
                last_activity_date = DATE('now'),
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = NEW.user_id;
        END;
        ''')
        
        # Trigger to create user stats record when user is created
        cursor.execute('''
        CREATE TRIGGER create_user_stats_on_user_creation
        AFTER INSERT ON users
        FOR EACH ROW
        BEGIN
            INSERT INTO user_stats (user_id, created_at, updated_at)
            VALUES (NEW.id, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
        END;
        ''')
        
        # Trigger to update timestamps
        cursor.execute('''
        CREATE TRIGGER update_users_timestamp
        AFTER UPDATE ON users
        FOR EACH ROW
        BEGIN
            UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        ''')
        
        cursor.execute('''
        CREATE TRIGGER update_lessons_timestamp
        AFTER UPDATE ON lessons
        FOR EACH ROW
        BEGIN
            UPDATE lessons SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        ''')
        
        cursor.execute('''
        CREATE TRIGGER update_user_progress_timestamp
        AFTER UPDATE ON user_progress
        FOR EACH ROW
        BEGIN
            UPDATE user_progress SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END;
        ''')
        
        # ========================================
        # SAMPLE DATA INSERTION
        # ========================================
        
        print("Inserting sample data...")
        
        # Insert sample learning tracks
        learning_tracks = [
            ('French Fundamentals', 'french_fundamentals', 'Complete beginner course covering basic French language skills', 'beginner', 40),
            ('Intermediate French', 'intermediate_french', 'Build upon basic skills with more complex grammar and vocabulary', 'intermediate', 60),
            ('Advanced French Mastery', 'advanced_french', 'Master advanced French concepts and achieve fluency', 'advanced', 80)
        ]
        
        cursor.executemany('''
        INSERT INTO learning_tracks (track_name, track_code, description, difficulty_level, estimated_duration_hours) 
        VALUES (?, ?, ?, ?, ?)
        ''', learning_tracks)
        
        # Insert sample modules
        modules = [
            (1, 'French Grammar and Syntax', 'french_grammar_syntax', 'Learn fundamental French grammar rules and sentence structure', 1, 15),
            (1, 'French Speech and Oral Skills', 'french_speech_oral', 'Develop pronunciation and speaking abilities', 2, 12),
            (1, 'French Literature Introduction', 'french_literature_intro', 'Introduction to French literary works and culture', 3, 13),
            (2, 'Advanced Grammar and Syntax', 'advanced_grammar_syntax', 'Complex grammar structures and advanced syntax', 1, 20),
            (2, 'Conversation and Communication', 'conversation_communication', 'Advanced speaking and listening skills', 2, 20),
            (2, 'French Literature Analysis', 'french_literature_analysis', 'In-depth study of French literary movements', 3, 20),
            (3, 'Mastery Grammar and Style', 'mastery_grammar_style', 'Perfect your grammar and develop sophisticated style', 1, 25),
            (3, 'Professional French Communication', 'professional_french', 'Business and academic French communication', 2, 25),
            (3, 'French Literature Mastery', 'french_literature_mastery', 'Comprehensive study of French literature', 3, 30)
        ]
        
        cursor.executemany('''
        INSERT INTO modules (track_id, module_name, module_code, description, order_sequence, estimated_duration_hours) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', modules)
        
        # Insert sample lessons for the first module
        lessons = [
            (1, 'French Articles: Le, La, Les', 'Learn about definite articles in French and their proper usage with masculine, feminine, and plural nouns.', 'theory', 'beginner', 1, 30, 100),
            (1, 'Basic French Verbs: Être and Avoir', 'Master the two most important French verbs - to be (être) and to have (avoir) - including conjugations.', 'theory', 'beginner', 2, 45, 100),
            (1, 'French Noun Gender', 'Understanding masculine and feminine nouns in French and rules for determining gender.', 'theory', 'beginner', 3, 35, 100),
            (1, 'Present Tense Conjugation Practice', 'Practice conjugating regular and irregular verbs in the present tense.', 'practice', 'beginner', 4, 40, 150),
            (1, 'Grammar Assessment 1', 'Test your knowledge of articles, basic verbs, and noun gender.', 'assessment', 'beginner', 5, 25, 200)
        ]
        
        cursor.executemany('''
        INSERT INTO lessons (module_id, lesson_title, lesson_content, lesson_type, difficulty_level, order_sequence, estimated_duration_minutes, points_possible) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', lessons)
        
        # Insert sample exercises
        exercises = [
            (1, 'multiple_choice', 'Choose the correct article for "maison" (house):', 'la', 10, 1, 'Select the appropriate definite article'),
            (1, 'fill_blank', 'Complete: ___ chat est noir (The cat is black)', 'le', 10, 2, 'Fill in the blank with the correct article'),
            (2, 'multiple_choice', 'How do you say "I am" in French?', 'je suis', 10, 1, 'Choose the correct conjugation of être'),
            (2, 'translation', 'Translate: "You have a book"', 'Tu as un livre', 15, 2, 'Translate the English sentence to French')
        ]
        
        cursor.executemany('''
        INSERT INTO exercises (lesson_id, exercise_type, exercise_content, correct_answer, points_possible, order_sequence, instructions) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', exercises)
        
        # Insert sample exercise options
        exercise_options = [
            (1, 'le', 0, 'Incorrect - "maison" is feminine', 1),
            (1, 'la', 1, 'Correct - "maison" is a feminine noun', 2),
            (1, 'les', 0, 'Incorrect - this is plural, but "maison" is singular', 3),
            (3, 'je suis', 1, 'Correct - "je suis" means "I am"', 1),
            (3, 'tu es', 0, 'Incorrect - this means "you are"', 2),
            (3, 'il est', 0, 'Incorrect - this means "he is"', 3)
        ]
        
        cursor.executemany('''
        INSERT INTO exercise_options (exercise_id, option_text, is_correct, explanation, order_sequence) 
        VALUES (?, ?, ?, ?, ?)
        ''', exercise_options)
        
        # Insert sample French words
        french_words = [
            ('bonjour', 'hello', 'bon-ZHOOR', 'noun', 'masculine', 'beginner', 10, 'Bonjour, comment allez-vous?', 'Hello, how are you?'),
            ('maison', 'house', 'may-ZOHN', 'noun', 'feminine', 'beginner', 9, 'Ma maison est grande.', 'My house is big.'),
            ('être', 'to be', 'EH-truh', 'verb', 'none', 'beginner', 10, 'Je suis étudiant.', 'I am a student.'),
            ('avoir', 'to have', 'ah-VWAR', 'verb', 'none', 'beginner', 10, 'J\'ai un chien.', 'I have a dog.'),
            ('chat', 'cat', 'shah', 'noun', 'masculine', 'beginner', 7, 'Le chat est mignon.', 'The cat is cute.')
        ]
        
        cursor.executemany('''
        INSERT INTO french_words (french_word, english_translation, pronunciation, word_type, gender, difficulty_level, usage_frequency, example_sentence_french, example_sentence_english) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', french_words)
        
        # Insert sample literature content
        literature_content = [
            ('Classicism', 'Pierre Corneille, Jean Racine, Molière', 'Le Cid, Phèdre, Le Misanthrope', 'Order, reason, and adherence to classical unities', 1600, 1700, 'Era of Louis XIV and absolute monarchy', 'Emphasis on noble subjects, moral lessons, and formal structure'),
            ('Romanticism', 'Victor Hugo, Alexandre Dumas, George Sand', 'Les Misérables, The Count of Monte Cristo, Indiana', 'Emotion, individualism, and nature worship', 1800, 1850, 'Post-revolutionary France and industrial change', 'Focus on passion, exotic settings, and social issues'),
            ('Realism', 'Gustave Flaubert, Émile Zola, Guy de Maupassant', 'Madame Bovary, Germinal, Boule de Suif', 'Objective portrayal of contemporary life', 1850, 1900, 'Industrial revolution and social transformation', 'Detailed observation, social criticism, and psychological depth'),
            ('Symbolism', 'Charles Baudelaire, Paul Verlaine, Stéphane Mallarmé', 'Les Fleurs du mal, Romances sans paroles, L\'Après-midi d\'un faune', 'Suggestion over description, musicality', 1870, 1900, 'Reaction against realism and positivism', 'Use of symbols, synesthesia, and musical effects'),
            ('Existentialism', 'Jean-Paul Sartre, Albert Camus, Simone de Beauvoir', 'La Nausée, L\'Étranger, Le Deuxième Sexe', 'Individual existence, freedom, and authenticity', 1940, 1960, 'World War II and post-war disillusionment', 'Themes of absurdity, responsibility, and human condition')
        ]
        
        cursor.executemany('''
        INSERT INTO literature_content (movement_period, key_authors, major_works, core_ideas_style, time_period_start, time_period_end, historical_context, notable_characteristics) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', literature_content)
        
        # Insert sample grammar topics
        grammar_topics = [
            (1, 'Definite Articles', 'Le (masculine), La (feminine), Les (plural)', 'le chat, la maison, les enfants', 'beginner', 'Match articles with nouns, identify gender'),
            (2, 'Verb Être Conjugation', 'je suis, tu es, il/elle est, nous sommes, vous êtes, ils/elles sont', 'Je suis étudiant, Tu es français', 'beginner', 'Complete conjugation tables, fill-in-the-blank exercises'),
            (3, 'Noun Gender Rules', 'Masculine/feminine endings, exceptions', 'Words ending in -tion are feminine, -ment are masculine', 'beginner', 'Categorize nouns by gender, identify patterns')
        ]
        
        cursor.executemany('''
        INSERT INTO grammar_syntax_topics (lesson_id, topic_name, key_concepts, examples, difficulty_level, practice_exercises) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', grammar_topics)
        
        # Insert sample speech/oral skills
        speech_skills = [
            (1, 'French Pronunciation Basics', 'Vowel sounds, silent letters, liaison', 'Repeat after audio, tongue twisters', 'beginner', 'audio/pronunciation_basics.mp3', 'French vowels are more precise than English'),
            (2, 'Basic Conversation', 'Greetings, introductions, simple questions', 'Role-play dialogues, Q&A practice', 'beginner', 'audio/basic_conversations.mp3', 'Practice intonation patterns for questions')
        ]
        
        cursor.executemany('''
        INSERT INTO speech_oral_skills (lesson_id, skill_area, key_elements, example_activities, difficulty_level, audio_resources, pronunciation_tips) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', speech_skills)
        
        # Sample user for testing (password should be hashed in real application)
        cursor.execute('''
        INSERT INTO users (username, email, password_hash, proficiency_level, preferred_language) 
        VALUES (?, ?, ?, ?, ?)
        ''', ('test_user', 'test@example.com', 'hashed_password_here', 'beginner', 'en'))
        
        # Create initial progress entries for the test user
        progress_entries = [(1, i, 'not_started') for i in range(1, 6)]
        cursor.executemany('''
        INSERT INTO user_progress (user_id, lesson_id, status) 
        VALUES (?, ?, ?)
        ''', progress_entries)
        
        # Initialize skill categories for test user
        skill_entries = [
            (1, 'grammar', 'articles', 0),
            (1, 'grammar', 'verbs', 0),
            (1, 'vocabulary', 'basic_words', 0),
            (1, 'pronunciation', 'vowels', 0),
            (1, 'reading', 'comprehension', 0)
        ]
        
        cursor.executemany('''
        INSERT INTO user_skills (user_id, skill_category, skill_subcategory, proficiency_score) 
        VALUES (?, ?, ?, ?)
        ''', skill_entries)
        
        # Create some sample exercise attempts
        attempt_entries = [
            (1, 1, 'la', 1, 10, 1),
            (1, 2, 'le', 1, 10, 1)
        ]
        
        cursor.executemany('''
        INSERT INTO user_exercise_attempts (user_id, exercise_id, user_answer, is_correct, points_earned, attempt_number) 
        VALUES (?, ?, ?, ?, ?, ?)
        ''', attempt_entries)
        
        # Commit all changes
        conn.commit()
        
        print("✅ Database created successfully!")
        print(f"📊 Database file: database.db")
        print(f"📈 Tables created: {get_table_count(cursor)}")
        print(f"👤 Sample users: 1")
        print(f"📚 Sample lessons: 5")
        print(f"💪 Sample exercises: 4")
        print(f"📖 Sample vocabulary: 5 words")
        print(f"📜 Literature periods: 5")
        
    except sqlite3.Error as e:
        print(f"❌ Error creating database: {e}")
        conn.rollback()
        raise
    
    finally:
        cursor.close()
        conn.close()

def get_table_count(cursor):
    """Get the number of tables created"""
    cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
    return cursor.fetchone()[0]

def verify_database():
    """Verify the database was created correctly"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        print("\n🔍 Verifying database structure...")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        print(f"📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Check views
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;")
        views = cursor.fetchall()
        print(f"👁️  Views found: {len(views)}")
        for view in views:
            print(f"   - {view[0]}")
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        indexes = cursor.fetchall()
        print(f"🔗 Indexes found: {len(indexes)}")
        
        # Check triggers
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger' ORDER BY name;")
        triggers = cursor.fetchall()
        print(f"⚡ Triggers found: {len(triggers)}")
        
        # Sample data verification
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"👤 Users: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM learning_tracks;")
        track_count = cursor.fetchone()[0]
        print(f"📚 Learning tracks: {track_count}")
        
        cursor.execute("SELECT COUNT(*) FROM lessons;")
        lesson_count = cursor.fetchone()[0]
        print(f"📖 Lessons: {lesson_count}")
        
        cursor.execute("SELECT COUNT(*) FROM french_words;")
        word_count = cursor.fetchone()[0]
        print(f"🔤 French words: {word_count}")
        
        print("✅ Database verification complete!")
        
    except sqlite3.Error as e:
        print(f"❌ Error verifying database: {e}")
    
    finally:
        cursor.close()
        conn.close()

def show_sample_queries():
    """Show some sample queries to test the database"""
    print("\n📝 Sample queries to test your database:")
    print("=" * 50)
    
    sample_queries = [
        ("Get all learning tracks:", "SELECT * FROM learning_tracks;"),
        ("Get user progress:", "SELECT * FROM user_lesson_progress WHERE username = 'test_user';"),
        ("Get user stats:", "SELECT * FROM user_performance_summary WHERE username = 'test_user';"),
        ("Get French words for beginners:", "SELECT french_word, english_translation FROM french_words WHERE difficulty_level = 'beginner';"),
        ("Get literature by period:", "SELECT movement_period, key_authors FROM literature_content ORDER BY time_period_start;"),
        ("Get exercises for a lesson:", "SELECT exercise_content, exercise_type FROM exercises WHERE lesson_id = 1;"),
        ("Check user exercise attempts:", "SELECT * FROM user_exercise_attempts WHERE user_id = 1;")
    ]
    
    for description, query in sample_queries:
        print(f"\n{description}")
        print(f"  {query}")

def flask_integration_example():
    """Show Flask integration example"""
    print("\n🐍 Flask Integration Example:")
    print("=" * 50)
    
    flask_code = """
# app.py - Flask integration example

from flask import Flask, g, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    # Get database connection
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # This enables column access by name
    return g.db

def close_db(e=None):
    # Close database connection
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def close_db(error):
    close_db()

@app.route('/api/tracks')
def get_learning_tracks():
    # Get all learning tracks
    db = get_db()
    tracks = db.execute('SELECT * FROM learning_tracks ORDER BY difficulty_level').fetchall()
    return jsonify([dict(track) for track in tracks])

@app.route('/api/user/<int:user_id>/progress')
def get_user_progress(user_id):
    # Get user progress
    db = get_db()
    query = '''SELECT * FROM user_lesson_progress 
               WHERE user_id = ? 
               ORDER BY track_name, module_name'''
    progress = db.execute(query, (user_id,)).fetchall()
    return jsonify([dict(row) for row in progress])

@app.route('/api/lessons/<int:lesson_id>/exercises')
def get_lesson_exercises(lesson_id):
    # Get exercises for a lesson
    db = get_db()
    query = '''SELECT e.*, eo.option_text, eo.is_correct, eo.explanation
               FROM exercises e
               LEFT JOIN exercise_options eo ON e.id = eo.exercise_id
               WHERE e.lesson_id = ?
               ORDER BY e.order_sequence, eo.order_sequence'''
    exercises = db.execute(query, (lesson_id,)).fetchall()
    return jsonify([dict(row) for row in exercises])

if __name__ == '__main__':
    app.run(debug=True)
"""
    
    print(flask_code)

if __name__ == "__main__":
    print("🚀 French Learning Database Creator")
    print("=" * 50)
    
    try:
        # Create the database
        create_database()
        
        # Verify it was created correctly
        verify_database()
        
        # Show sample queries
        show_sample_queries()
        
        # Show Flask integration example
        flask_integration_example()
        
        print("\n🎉 Setup complete! Your database.db file is ready to use with your Flask app.")
        print("💡 Run this script anytime to recreate a fresh database with sample data.")
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        print("Please check the error message above and try again.")
