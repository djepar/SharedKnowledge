import sqlite3
import os
from datetime import datetime

DB_FILE = 'database.db'

def migrate_database():
    """
    Migrate the existing database to the new schema
    """
    print("🔄 Starting database migration...")
    
    # Create backup
    backup_file = f'database_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    if os.path.exists(DB_FILE):
        import shutil
        shutil.copy2(DB_FILE, backup_file)
        print(f"✅ Backup created: {backup_file}")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        # Check current users table structure
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        print(f"📋 Current users table columns: {columns}")
        
        # If the table doesn't have the expected columns, recreate it
        if 'name' not in columns:
            print("�� Migrating users table...")
            
            # Get existing data
            c.execute("SELECT * FROM users")
            existing_users = c.fetchall()
            print(f"📊 Found {len(existing_users)} existing users")
            
            # Drop old table and create new one
            c.execute("DROP TABLE IF EXISTS users_old")
            c.execute("ALTER TABLE users RENAME TO users_old")
            
            # Create new users table with correct schema
            c.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'teacher',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Migrate data - adapt based on your old schema
            # Assuming old table had id, username, password (adjust as needed)
            for user in existing_users:
                try:
                    if len(user) >= 3:  # id, username, password
                        old_id, username, password = user[0], user[1], user[2]
                        c.execute(
                            "INSERT INTO users (name, password, role) VALUES (?, ?, ?)",
                            (username, password, 'teacher')
                        )
                        print(f"✅ Migrated user: {username}")
                    else:
                        print(f"⚠️  Skipping malformed user record: {user}")
                except Exception as e:
                    print(f"❌ Error migrating user {user}: {e}")
            
            # Drop old table
            c.execute("DROP TABLE users_old")
            print("✅ Users table migration completed")
        
        else:
            print("✅ Users table already has correct schema")
        
        # Create other tables if they don't exist
        print("🔧 Creating additional tables...")
        
        # Lessons table
        c.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_number INTEGER NOT NULL,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Student progress tracking
        c.execute('''
            CREATE TABLE IF NOT EXISTS student_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lesson_id INTEGER,
                completed BOOLEAN DEFAULT FALSE,
                notes TEXT,
                completion_date TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons (id)
            )
        ''')
        
        # Reading log for students
        c.execute('''
            CREATE TABLE IF NOT EXISTS reading_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                book_title TEXT NOT NULL,
                author TEXT,
                pages_read INTEGER DEFAULT 0,
                total_pages INTEGER,
                reading_date DATE,
                notes TEXT,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Evaluations table
        c.execute('''
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                evaluation_type TEXT NOT NULL,
                title TEXT NOT NULL,
                score REAL,
                max_score REAL,
                percentage REAL,
                date_evaluated DATE,
                comments TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        print("✅ All tables created successfully")
        
        # Insert sample lesson data if lessons table is empty
        c.execute("SELECT COUNT(*) FROM lessons")
        if c.fetchone()[0] == 0:
            print("📚 Inserting sample lesson data...")
            sample_lessons = [
                (1, "septembre", 1, 1, "🎯 Accueil et présentation du programme", 
                 "Amorce (10 min) : Jeu brise-glace \"Qui suis-je littéraire ?\"\nDéveloppement (50 min) :\n• Présentation des 3 compétences PFEQ (15 min)\n• Survol des œuvres à lire cette année + extraits (20 min)\n• Explication système d'évaluation et portfolios (15 min)\nIntégration (15 min) : Questions-réponses et anticipations",
                 75, "Oral", "Extraits d'œuvres, grille d'évaluation, cahiers", "Créer un climat de confiance et présenter les attentes", "oral"),
                (2, "septembre", 1, 2, "📖 Évaluation diagnostique - Lecture",
                 "Amorce (5 min) : Rappel des stratégies de lecture\nDéveloppement (60 min) :\n• Test de compréhension de lecture - 2 textes variés (45 min)\n• Questionnaire métacognitif sur les stratégies utilisées (15 min)\nIntégration (10 min) : Autoévaluation de la performance",
                 75, "Lecture", "Cahier de textes diagnostiques, grille d'observation", "Évaluer les forces/défis en compréhension de lecture", "lecture,evaluation"),
                (3, "septembre", 1, 3, "✍️ Évaluation diagnostique - Écriture",
                 "Amorce (10 min) : Remue-méninges sur les caractéristiques du texte descriptif\nDéveloppement (55 min) :\n• Rédaction d'un texte descriptif de 150 mots : \"Mon lieu préféré\" (40 min)\n• Relecture et révision autonome (15 min)\nIntégration (10 min) : Remise et réflexion sur le processus d'écriture",
                 75, "Écriture", "Feuilles mobiles, aide-mémoire descriptif", "Évaluer les compétences de base en écriture descriptive", "ecriture,evaluation"),
                (4, "septembre", 1, 4, "📚 Introduction au carnet de lecture",
                 "Amorce (15 min) : Discussion sur les habitudes de lecture des élèves\nDéveloppement (50 min) :\n• Présentation du carnet de lecture et de ses composantes (15 min)\n• Création et personnalisation du carnet (20 min)\n• Première entrée : \"Mes goûts littéraires\" (15 min)\nIntégration (10 min) : Choix du premier roman + planification lecture",
                 75, "Lecture", "Cahiers, liste romans disponibles, exemples carnets", "Établir l'outil de suivi des lectures personnelles", "lecture"),
                (5, "septembre", 1, 5, "🦊 Bilan de la semaine + Introduction aux fables",
                 "Amorce (20 min) : Retour sur la semaine, partage des impressions\nDéveloppement (45 min) :\n• Lecture expressive de \"Le Corbeau et le Renard\" (10 min)\n• Compréhension globale et première analyse (15 min)\n• Introduction au concept de fable et de morale (20 min)\nIntégration (10 min) : Anticipation de la suite du programme",
                 75, "Lecture", "Recueil de fables, tableau des caractéristiques", "Clôturer positivement la première semaine", "lecture,oral"),
            ]
            
            c.executemany('''
                INSERT INTO lessons (lesson_number, month, week_number, day_number, title, content, duration, competences, materials, objectives, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_lessons)
            conn.commit()
            print(f"✅ Inserted {len(sample_lessons)} sample lessons")
        
        print("🎉 Database migration completed successfully!")
        print(f"📁 Backup available at: {backup_file}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
