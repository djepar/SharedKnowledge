from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, jsonify
import sqlite3
import csv
import io
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_FILE = 'database.db'

def get_competences_by_discipline(discipline):
    """Get competences for a specific discipline from the competences table"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT nom FROM competences WHERE discipline = ? ORDER BY ordre", (discipline,))
    competences = [row[0] for row in c.fetchall()]
    conn.close()
    return competences

def check_and_migrate_database():
    """
    Check if database needs migration and perform it if necessary
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        # Check if users table exists and has correct structure
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        
        needs_migration = False
        
        if not columns:
            # Table doesn't exist
            needs_migration = True
            print("🔧 Users table doesn't exist, creating...")
        elif 'name' not in columns:
            # Table exists but has wrong structure
            needs_migration = True
            print("🔧 Users table needs migration...")
        
        if needs_migration:
            # Get existing data if table exists
            existing_users = []
            try:
                c.execute("SELECT * FROM users")
                existing_users = c.fetchall()
                print(f"📊 Found {len(existing_users)} existing users")
            except:
                print("📊 No existing users found")
            
            # Drop and recreate users table
            c.execute("DROP TABLE IF EXISTS users")
            c.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'teacher',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Migrate existing data if any
            for user in existing_users:
                try:
                    # Try different possible old schemas
                    if len(user) >= 2:
                        # Assume first column is ID, second is username/name, third is password
                        user_id, username = user[0], user[1]
                        password = user[2] if len(user) > 2 else 'password123'  # default password
                        
                        c.execute(
                            "INSERT INTO users (name, password, role) VALUES (?, ?, ?)",
                            (str(username), str(password), 'teacher')
                        )
                        print(f"✅ Migrated user: {username}")
                except Exception as e:
                    print(f"⚠️  Error migrating user {user}: {e}")
            
            print("✅ Users table migration completed")
        
        # Create other tables
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
                subject TEXT DEFAULT 'français',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add subject column if it doesn't exist (for existing databases)
        try:
            c.execute("ALTER TABLE lessons ADD COLUMN subject TEXT DEFAULT 'français'")
        except sqlite3.OperationalError:
            # Column already exists
            pass
        
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
        
        # New tables for the three functionalities
        
        # Theory: Theoretical lessons with exercises
        c.execute('''
            CREATE TABLE IF NOT EXISTS theory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                powerpoint_file TEXT,
                exercise_type TEXT,
                discipline TEXT DEFAULT 'français',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id)
            )
        ''')
        
        # Exercises linked to lessons
        c.execute('''
            CREATE TABLE IF NOT EXISTS exercises (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER,
                theory_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                exercise_type TEXT NOT NULL,
                content TEXT NOT NULL,
                answer_key TEXT,
                points INTEGER DEFAULT 10,
                discipline TEXT DEFAULT 'français',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lesson_id) REFERENCES lessons (id),
                FOREIGN KEY (theory_id) REFERENCES theory (id)
            )
        ''')
        
        # Portfolio, Examens et Travaux
        c.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                lesson_id INTEGER,
                item_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                file_path TEXT,
                content TEXT,
                due_date DATE,
                submission_date DATE,
                grade REAL,
                max_grade REAL,
                feedback TEXT,
                status TEXT DEFAULT 'en_cours',
                discipline TEXT DEFAULT 'français',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (lesson_id) REFERENCES lessons (id)
            )
        ''')
        
        # User exercise attempts
        c.execute('''
            CREATE TABLE IF NOT EXISTS exercise_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                exercise_id INTEGER NOT NULL,
                attempt_number INTEGER DEFAULT 1,
                user_answer TEXT,
                is_correct BOOLEAN,
                points_earned INTEGER DEFAULT 0,
                time_taken INTEGER,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (exercise_id) REFERENCES exercises (id)
            )
        ''')
        
        # Grammar gender exercises - Question database
        c.execute('''
            CREATE TABLE IF NOT EXISTS grammar_gender_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sub_question_id TEXT UNIQUE NOT NULL,
                nom TEXT NOT NULL,
                genre_du_nom TEXT NOT NULL CHECK(genre_du_nom IN ('masculin', 'féminin')),
                niveau_difficulte INTEGER CHECK(niveau_difficulte >= 1 AND niveau_difficulte <= 3),
                exemple_usage_courant TEXT,
                exemple_usage_litteraire TEXT,
                exemple_usage_universitaire TEXT,
                terminaisons TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Grammar gender exercise sessions
        c.execute('''
            CREATE TABLE IF NOT EXISTS grammar_gender_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_type TEXT DEFAULT 'practice',
                questions_count INTEGER DEFAULT 10,
                score INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0,
                time_taken INTEGER,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Individual question attempts within sessions
        c.execute('''
            CREATE TABLE IF NOT EXISTS grammar_gender_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                user_answer TEXT,
                is_correct BOOLEAN,
                time_taken INTEGER,
                hints_used INTEGER DEFAULT 0,
                score INTEGER DEFAULT 10,
                attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES grammar_gender_sessions (id),
                FOREIGN KEY (question_id) REFERENCES grammar_gender_questions (id)
            )
        ''')
        
        conn.commit()
        
        # Add new columns for scoring system if they don't exist
        try:
            c.execute("ALTER TABLE grammar_gender_attempts ADD COLUMN hints_used INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        try:
            c.execute("ALTER TABLE grammar_gender_attempts ADD COLUMN score INTEGER DEFAULT 10")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Insert sample grammar gender questions if table is empty
        c.execute("SELECT COUNT(*) FROM grammar_gender_questions")
        if c.fetchone()[0] == 0:
            sample_questions = [
                ("QAG1-1", "soleil", "masculin", 3, "Un soleil radieux brille dans le ciel", 
                 "Le soleil, ce dieu d'or, s'endort dans son royaume pourpre", 
                 "L'imagerie solaire dans la poésie romantique française", 
                 "-eil (exception car mots en -eil peuvent être féminins comme abeille)"),
                ("QAG1-2", "amour", "masculin", 3, "Un grand amour de jeunesse", 
                 "Les amours défuntes hantent ses vers (usage poétique au féminin)", 
                 "L'amour courtois dans la littérature médiévale", 
                 "exception"),
                ("QAG1-3", "mer", "féminin", 3, "La mer est agitée aujourd'hui", 
                 "La mer, la grande mer consolatrice (Baudelaire)", 
                 "La symbolique de la mer dans l'œuvre de Victor Hugo", 
                 "exception"),
                ("QAG1-4", "automne", "masculin", 3, "Un automne pluvieux", 
                 "L'automne languissant berçait leur rêverie", 
                 "L'imaginaire de l'automne dans la poésie symboliste", 
                 "ambigu"),
                ("QAG1-5", "orchidée", "féminin", 1, "Une belle orchidée blanche", 
                 "L'orchidée sauvage parsemait la forêt", 
                 "Taxonomie des orchidées tropicales", 
                 "typiquement féminin"),
                ("QAG1-6", "pétale", "masculin", 3, "Un pétale de rose", 
                 "Les pétales embaumés tombaient en pluie", 
                 "Morphologie du pétale dans les angiospermes", 
                 "ambigu"),
            ]
            
            c.executemany('''
                INSERT INTO grammar_gender_questions 
                (sub_question_id, nom, genre_du_nom, niveau_difficulte, exemple_usage_courant, 
                 exemple_usage_litteraire, exemple_usage_universitaire, terminaisons)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_questions)
            conn.commit()
        
        # Insert sample lesson data if table is empty
        c.execute("SELECT COUNT(*) FROM lessons")
        if c.fetchone()[0] == 0:
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
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database with migration check"""
    check_and_migrate_database()

@app.route('/')
def index():
    if 'user' in session:
        return render_template('home.html', name=session['user'])
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE name=? AND password=?", (name, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = name
            session['user_id'] = user[0]
            session['role'] = user[3] if len(user) > 3 else 'teacher'
            return redirect(url_for('discipline_selection'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect", 'error')
            return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form.get('role', 'teacher')
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (name, password, role) VALUES (?, ?, ?)", (name, password, role))
            conn.commit()
            flash("Compte créé avec succès! Vous pouvez maintenant vous connecter.", 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Ce nom d'utilisateur existe déjà", 'error')
        except Exception as e:
            flash(f"Erreur lors de la création du compte: {e}", 'error')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/discipline-selection')
def discipline_selection():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('discipline_selection.html')

@app.route('/set-discipline/<discipline>')
def set_discipline(discipline):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Store the selected discipline in session
    session['discipline'] = discipline
    # Redirect directly to discipline dashboard instead of index
    return redirect(url_for('discipline_dashboard', discipline=discipline))

@app.route('/calendar')
def calendar():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get filter parameter
    filter_subject = request.args.get('subject', '')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get all available subjects for the filter dropdown
    c.execute("SELECT DISTINCT subject FROM lessons WHERE subject IS NOT NULL ORDER BY subject")
    available_subjects = [row[0] for row in c.fetchall()]
    
    # Build query based on filter
    if filter_subject and filter_subject != 'all':
        c.execute("SELECT * FROM lessons WHERE subject=? ORDER BY lesson_number", (filter_subject,))
    else:
        c.execute("SELECT * FROM lessons ORDER BY subject, lesson_number")
    
    lessons = c.fetchall()
    conn.close()
    
    # Group lessons by month
    lessons_by_month = {}
    for lesson in lessons:
        month = lesson[2]
        if month not in lessons_by_month:
            lessons_by_month[month] = []
        lessons_by_month[month].append(lesson)
    
    return render_template('calendar.html', 
                         lessons_by_month=lessons_by_month,
                         available_subjects=available_subjects,
                         current_filter=filter_subject)

@app.route('/lesson/<int:lesson_id>')
def lesson_detail(lesson_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    lesson = c.fetchone()
    
    # Get user progress for this lesson
    progress = None
    if 'user_id' in session:
        c.execute("SELECT * FROM student_progress WHERE user_id=? AND lesson_id=?", 
                  (session['user_id'], lesson_id))
        progress = c.fetchone()
    
    conn.close()
    
    if not lesson:
        flash("Leçon non trouvée", 'error')
        return redirect(url_for('calendar'))
    
    return render_template('lesson_detail.html', lesson=lesson, progress=progress)

@app.route('/mark_complete/<int:lesson_id>', methods=['POST'])
def mark_complete(lesson_id):
    if 'user' not in session or 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Check if progress entry exists
    c.execute("SELECT id FROM student_progress WHERE user_id=? AND lesson_id=?", 
              (session['user_id'], lesson_id))
    existing = c.fetchone()
    
    if existing:
        c.execute("""UPDATE student_progress 
                     SET completed=?, completion_date=CURRENT_TIMESTAMP 
                     WHERE user_id=? AND lesson_id=?""", 
                  (True, session['user_id'], lesson_id))
    else:
        c.execute("""INSERT INTO student_progress (user_id, lesson_id, completed, completion_date)
                     VALUES (?, ?, ?, CURRENT_TIMESTAMP)""", 
                  (session['user_id'], lesson_id, True))
    
    conn.commit()
    conn.close()
    
    flash("Leçon marquée comme terminée!", 'success')
    return redirect(url_for('lesson_detail', lesson_id=lesson_id))

@app.route('/reading_log')
def reading_log():
    if 'user' not in session or 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM reading_log WHERE user_id=? ORDER BY reading_date DESC", 
              (session['user_id'],))
    books = c.fetchall()
    conn.close()
    
    return render_template('reading_log.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user' not in session or 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        book_data = (
            session['user_id'],
            request.form['title'],
            request.form['author'],
            request.form.get('pages_read', 0),
            request.form.get('total_pages'),
            request.form['reading_date'],
            request.form.get('notes', ''),
            request.form.get('rating') if request.form.get('rating') else None
        )
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""INSERT INTO reading_log 
                     (user_id, book_title, author, pages_read, total_pages, reading_date, notes, rating)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", book_data)
        conn.commit()
        conn.close()
        
        flash("Livre ajouté au carnet de lecture!", 'success')
        return redirect(url_for('reading_log'))
    
    return render_template('add_book.html')

@app.route('/dashboard')
def dashboard():
    """Redirect to discipline-specific dashboard"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get user's selected discipline
    discipline = session.get('discipline', 'francais')
    return redirect(url_for('discipline_dashboard', discipline=discipline))

@app.route('/dashboard/<discipline>')
def discipline_dashboard(discipline):
    """Discipline-specific dashboard"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Validate discipline
    valid_disciplines = ['mathematiques', 'francais', 'histoire', 'culture_citoyennete', 'geographie']
    if discipline not in valid_disciplines:
        flash("Discipline non reconnue", 'error')
        return redirect(url_for('discipline_selection'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get discipline-specific statistics
    user_id = session.get('user_id')
    completed_lessons = 0
    total_lessons = 0
    books_read = 0
    avg_rating = 0
    
    if user_id:
        # Get completed lessons count for this discipline
        if discipline == 'mathematiques':
            c.execute("""SELECT COUNT(*) FROM student_progress sp 
                        JOIN lessons l ON sp.lesson_id = l.id 
                        WHERE sp.user_id=? AND sp.completed=1 AND l.subject='mathématiques'""", 
                     (user_id,))
            completed_lessons = c.fetchone()[0]
            
            # Get total lessons for mathematics
            c.execute("SELECT COUNT(*) FROM lessons WHERE subject='mathématiques'")
            total_lessons = c.fetchone()[0]
        else:
            # For other disciplines, use general lesson count (adjust as needed)
            c.execute("""SELECT COUNT(*) FROM student_progress sp 
                        JOIN lessons l ON sp.lesson_id = l.id 
                        WHERE sp.user_id=? AND sp.completed=1 AND (l.subject=? OR l.subject='français')""", 
                     (user_id, discipline))
            completed_lessons = c.fetchone()[0]
            
            # Get total lessons count
            c.execute("SELECT COUNT(*) FROM lessons WHERE subject=? OR subject='français'", (discipline,))
            total_lessons = c.fetchone()[0]
        
        # Get books read count (common for all disciplines)
        c.execute("SELECT COUNT(*) FROM reading_log WHERE user_id=?", (user_id,))
        books_read = c.fetchone()[0]
        
        # Get average rating
        c.execute("SELECT AVG(rating) FROM reading_log WHERE user_id=? AND rating IS NOT NULL", (user_id,))
        avg_rating_result = c.fetchone()[0]
        avg_rating = round(avg_rating_result, 1) if avg_rating_result else 0
    
    # Calculate progress percentage
    progress_percentage = round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0
    
    # Get discipline-specific competencies and recent activity
    recent_activity = []
    competencies = []
    
    # Get recent activity for the discipline
    if discipline == 'mathematiques':
        c.execute("""SELECT l.title, l.lesson_number, sp.completion_date
                    FROM student_progress sp
                    JOIN lessons l ON l.id = sp.lesson_id
                    WHERE sp.user_id = ? AND sp.completed = 1 AND l.subject = 'mathématiques'
                    ORDER BY sp.completion_date DESC LIMIT 5""", (user_id,))
    else:
        c.execute("""SELECT l.title, l.lesson_number, sp.completion_date
                    FROM student_progress sp
                    JOIN lessons l ON l.id = sp.lesson_id
                    WHERE sp.user_id = ? AND sp.completed = 1
                    ORDER BY sp.completion_date DESC LIMIT 5""", (user_id,))
    
    recent_activity = c.fetchall()
    
    # Set competencies based on discipline with proper descriptions
    if discipline == 'mathematiques':
        competencies = [
            {'code': 'C1', 'title': 'Résoudre une situation-problème mathématique', 'description': 'Mobiliser les savoirs mathématiques appropriés pour analyser et résoudre des situations-problèmes en utilisant une démarche structurée et des stratégies variées.', 'progress': 45},
            {'code': 'C2', 'title': 'Raisonner à l\'aide de concepts et de processus mathématiques', 'description': 'Développer et appliquer un raisonnement mathématique rigoureux en utilisant les concepts et processus appropriés pour justifier ses actions et valider ses résultats.', 'progress': 60},
            {'code': 'C3', 'title': 'Communiquer à l\'aide du langage mathématique', 'description': 'Interpréter et produire des messages en utilisant le langage mathématique pour partager des informations à caractère mathématique et argumenter.', 'progress': 35}
        ]
    elif discipline == 'francais':
        competencies = [
            {'code': 'C1', 'title': 'Lire et apprécier des textes variés', 'description': 'Comprendre et interpréter des textes de genres variés en mobilisant ses connaissances et stratégies de lecture pour construire du sens et développer sa culture.', 'progress': 70},
            {'code': 'C2', 'title': 'Écrire des textes variés', 'description': 'Produire des textes de genres variés en mobilisant ses connaissances langagières et textuelles dans une démarche active de rédaction.', 'progress': 55},
            {'code': 'C3', 'title': 'Communiquer oralement selon des modalités variées', 'description': 'Réaliser des communications orales de genres variés en mobilisant les ressources de la langue orale et en s\'adaptant à la situation de communication.', 'progress': 65}
        ]
    elif discipline == 'culture_citoyennete':
        competencies = [
            {'code': 'C1', 'title': 'Interroger une réalité sociale', 'description': 'Poser des questions pertinentes et formuler des hypothèses à propos de réalités sociales en mobilisant des concepts et des outils d\'analyse appropriés.', 'progress': 50},
            {'code': 'C2', 'title': 'Interpréter une réalité sociale', 'description': 'Construire sa compréhension d\'une réalité sociale en analysant des sources variées et en établissant des liens significatifs entre les éléments étudiés.', 'progress': 45},
            {'code': 'C3', 'title': 'Construire sa conscience citoyenne', 'description': 'Développer sa capacité d\'action citoyenne en s\'appuyant sur l\'analyse de réalités sociales et en considérant diverses perspectives dans une démarche démocratique.', 'progress': 40}
        ]
    elif discipline == 'histoire':
        competencies = [
            {'code': 'C1', 'title': 'Interroger les réalités sociales dans une perspective historique', 'description': 'Formuler des questions et des hypothèses pertinentes à propos de réalités sociales du passé en mobilisant la pensée historique.', 'progress': 55},
            {'code': 'C2', 'title': 'Interpréter les réalités sociales à l\'aide de la méthode historique', 'description': 'Analyser et comprendre des réalités sociales du passé en utilisant la méthode historique et en établissant des liens avec le présent.', 'progress': 50},
            {'code': 'C3', 'title': 'Construire sa conscience citoyenne à l\'aide de l\'histoire', 'description': 'Développer son identité sociale et sa capacité d\'action citoyenne en s\'appuyant sur la connaissance du passé et la compréhension du présent.', 'progress': 45}
        ]
    elif discipline == 'geographie':
        competencies = [
            {'code': 'C1', 'title': 'Lire l\'organisation d\'un territoire', 'description': 'Analyser l\'organisation spatiale d\'un territoire en mobilisant le raisonnement géographique et les outils appropriés pour comprendre les dynamiques territoriales.', 'progress': 48},
            {'code': 'C2', 'title': 'Interpréter un enjeu territorial', 'description': 'Analyser un enjeu territorial en considérant les multiples perspectives des acteurs concernés et en établissant des liens entre les dimensions du développement durable.', 'progress': 42},
            {'code': 'C3', 'title': 'Construire sa conscience citoyenne à l\'échelle planétaire', 'description': 'Développer sa capacité d\'action citoyenne responsable en s\'appuyant sur la compréhension des enjeux territoriaux locaux et mondiaux.', 'progress': 38}
        ]
    
    conn.close()
    
    # Discipline configuration
    discipline_config = {
        'mathematiques': {
            'title': 'Mathématiques',
            'icon': '🔢',
            'theme': 'math',
            'description': 'Algèbre, géométrie, statistiques et résolution de problèmes'
        },
        'francais': {
            'title': 'Français',
            'icon': '📖',
            'theme': 'francais',
            'description': 'Lecture, écriture, grammaire et littérature québécoise'
        },
        'histoire': {
            'title': 'Histoire',
            'icon': '🏛️',
            'theme': 'histoire',
            'description': 'Histoire du Québec, du Canada et civilisations anciennes'
        },
        'culture_citoyennete': {
            'title': 'Culture et citoyenneté',
            'icon': '🏳️',
            'theme': 'culture',
            'description': 'Éthique, culture québécoise et éducation à la citoyenneté'
        },
        'geographie': {
            'title': 'Géographie',
            'icon': '🌍',
            'theme': 'geographie',
            'description': 'Géographie du Québec, environnement et territoires'
        }
    }
    
    # Prepare data for template
    data = {
        'discipline': discipline,
        'discipline_config': discipline_config[discipline],
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'books_read': books_read,
        'avg_rating': avg_rating,
        'progress_percentage': progress_percentage,
        'recent_activity': recent_activity,
        'competencies': competencies,
        'available_disciplines': valid_disciplines
    }
    
    return render_template('discipline_dashboard.html', **data)
@app.route('/lessons')
def lessons_list():
    """Display all lessons with filtering and search"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get filter parameters
    month_filter = request.args.get('month', '')
    competence_filter = request.args.get('competence', '')
    search_query = request.args.get('search', '')
    subject_filter = request.args.get('subject', session.get('discipline', 'français'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Build query with filters - always filter by subject first
    query = "SELECT * FROM lessons WHERE subject = ?"
    params = [subject_filter]
    
    if month_filter:
        query += " AND month = ?"
        params.append(month_filter)
    
    if competence_filter:
        query += " AND competences LIKE ?"
        params.append(f"%{competence_filter}%")
    
    if search_query:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    
    query += " ORDER BY subject, lesson_number"
    
    c.execute(query, params)
    lessons = c.fetchall()
    
    # Get unique months and competences for filters - filtered by subject
    c.execute("SELECT DISTINCT month FROM lessons WHERE subject = ? ORDER BY lesson_number", (subject_filter,))
    months = [row[0] for row in c.fetchall()]
    
    # Get competences from the competences table for the selected subject
    competences = get_competences_by_discipline(subject_filter)
    
    # Get available subjects for filter dropdown
    c.execute("SELECT DISTINCT subject FROM lessons WHERE subject IS NOT NULL ORDER BY subject")
    available_subjects = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    return render_template('lessons_list.html', 
                         lessons=lessons, 
                         months=months, 
                         competences=competences,
                         available_subjects=available_subjects,
                         current_filters={
                             'month': month_filter,
                             'competence': competence_filter,
                             'search': search_query,
                             'subject': subject_filter
                         })

@app.route('/lesson/create', methods=['GET', 'POST'])
def create_lesson():
    """Create a new lesson"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        subject = request.form.get('subject', 'français')
        
        # Get next lesson number for this specific subject
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT MAX(lesson_number) FROM lessons WHERE subject=?", (subject,))
        result = c.fetchone()
        next_lesson_number = (result[0] or 0) + 1
        
        lesson_data = {
            'lesson_number': next_lesson_number,
            'month': request.form['month'],
            'week_number': request.form.get('week_number', type=int),
            'day_number': request.form.get('day_number', type=int),
            'title': request.form['title'],
            'content': request.form['content'],
            'duration': request.form.get('duration', 75, type=int),
            'competences': request.form.get('competences', ''),
            'materials': request.form.get('materials', ''),
            'objectives': request.form.get('objectives', ''),
            'tags': request.form.get('tags', ''),
            'subject': subject
        }
        
        try:
            c.execute('''
                INSERT INTO lessons 
                (lesson_number, month, week_number, day_number, title, content, 
                 duration, competences, materials, objectives, tags, subject)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(lesson_data.values()))
            
            conn.commit()
            flash(f"Leçon '{lesson_data['title']}' créée avec succès!", 'success')
            return redirect(url_for('lessons_list'))
            
        except sqlite3.IntegrityError:
            flash("Erreur: Une leçon avec ce numéro existe déjà", 'error')
        except Exception as e:
            flash(f"Erreur lors de la création: {e}", 'error')
        finally:
            conn.close()
    
    # Get available subjects for the dropdown
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT DISTINCT subject FROM lessons WHERE subject IS NOT NULL ORDER BY subject")
    available_subjects = [row[0] for row in c.fetchall()]
    
    # Add the 5 main subjects if they don't exist yet
    all_subjects = ['français', 'mathématiques', 'histoire', 'geographie', 'culture_citoyennete']
    for subject in all_subjects:
        if subject not in available_subjects:
            available_subjects.append(subject)
    
    conn.close()
    
    return render_template('create_lesson.html', available_subjects=sorted(available_subjects))

@app.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    """Edit an existing lesson"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if request.method == 'POST':
        # Get the current lesson to preserve lesson_number
        c.execute("SELECT lesson_number FROM lessons WHERE id=?", (lesson_id,))
        current_lesson = c.fetchone()
        current_lesson_number = current_lesson[0] if current_lesson else 1
        
        try:
            c.execute('''
                UPDATE lessons SET 
                lesson_number=?, month=?, week_number=?, day_number=?, title=?, 
                content=?, duration=?, competences=?, materials=?, objectives=?, 
                subject=?, evaluation=?, homework=?, adaptations=?, notes=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (
                current_lesson_number,
                request.form['month'],
                request.form.get('week', type=int),
                request.form.get('day', type=int),
                request.form['title'],
                request.form['content'],
                request.form.get('duration', 75, type=int),
                request.form.get('competence', ''),
                request.form.get('materials', ''),
                request.form.get('objectives', ''),
                request.form.get('subject', ''),
                request.form.get('evaluation', ''),
                request.form.get('homework', ''),
                request.form.get('adaptations', ''),
                request.form.get('notes', ''),
                lesson_id
            ))
            
            conn.commit()
            flash("Leçon mise à jour avec succès!", 'success')
            return redirect(url_for('lesson_detail', lesson_id=lesson_id))
            
        except Exception as e:
            flash(f"Erreur lors de la mise à jour: {e}", 'error')
    
    # Get lesson data
    c.execute("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    lesson = c.fetchone()
    
    # Get available subjects for dropdown
    c.execute("SELECT DISTINCT subject FROM lessons WHERE subject IS NOT NULL ORDER BY subject")
    available_subjects = [row[0] for row in c.fetchall()]
    
    conn.close()
    
    if not lesson:
        flash("Leçon non trouvée", 'error')
        return redirect(url_for('lessons_list'))
    
    # Get competences for the lesson's discipline
    lesson_discipline = lesson[14]  # subject column
    competences = get_competences_by_discipline(lesson_discipline) if lesson_discipline else []
    
    return render_template('edit_lesson.html', lesson=lesson, available_subjects=available_subjects, competences=competences)

@app.route('/api/competences/<discipline>')
def get_competences_api(discipline):
    """API endpoint to get competences for a specific discipline"""
    competences = get_competences_by_discipline(discipline)
    return {'competences': competences}

@app.route('/lesson/<int:lesson_id>/duplicate', methods=['POST'])
def duplicate_lesson(lesson_id):
    """Duplicate an existing lesson"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get original lesson
    c.execute("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    original = c.fetchone()
    
    if not original:
        flash("Leçon non trouvée", 'error')
        return redirect(url_for('lessons_list'))
    
    # Get next lesson number for the original lesson's subject
    subject = original[12] if len(original) > 12 else 'français'  # Get subject from original lesson
    c.execute("SELECT MAX(lesson_number) FROM lessons WHERE subject = ?", (subject,))
    result = c.fetchone()
    next_lesson_number = (result[0] or 0) + 1
    
    try:
        # Create duplicate with new lesson number
        c.execute('''
            INSERT INTO lessons 
            (lesson_number, month, week_number, day_number, title, content, 
             duration, competences, materials, objectives, tags, subject)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            next_lesson_number,
            original[2],  # month
            original[3],  # week_number
            original[4],  # day_number
            f"[COPIE] {original[5]}",  # title
            original[6],  # content
            original[7],  # duration
            original[8],  # competences
            original[9],  # materials
            original[10], # objectives
            original[11], # tags
            subject  # subject
        ))
        
        conn.commit()
        new_lesson_id = c.lastrowid
        flash("Leçon dupliquée avec succès!", 'success')
        return redirect(url_for('edit_lesson', lesson_id=new_lesson_id))
        
    except Exception as e:
        flash(f"Erreur lors de la duplication: {e}", 'error')
        return redirect(url_for('lesson_detail', lesson_id=lesson_id))
    finally:
        conn.close()

@app.route('/lesson/<int:lesson_id>/delete', methods=['POST'])
def delete_lesson(lesson_id):
    """Delete a lesson"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        # Get lesson title for confirmation
        c.execute("SELECT title FROM lessons WHERE id=?", (lesson_id,))
        lesson = c.fetchone()
        
        if not lesson:
            flash("Leçon non trouvée", 'error')
            return redirect(url_for('lessons_list'))
        
        # Delete the lesson
        c.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
        
        # Delete related progress entries
        c.execute("DELETE FROM student_progress WHERE lesson_id=?", (lesson_id,))
        
        conn.commit()
        flash(f"Leçon '{lesson[0]}' supprimée avec succès", 'success')
        
    except Exception as e:
        flash(f"Erreur lors de la suppression: {e}", 'error')
    finally:
        conn.close()
    
    return redirect(url_for('lessons_list'))

@app.route('/lessons/import', methods=['GET', 'POST'])
def import_lessons():
    """Import lessons from CSV"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Aucun fichier sélectionné', 'error')
            return redirect(request.url)
        
        try:
            if file.filename.endswith('.csv'):
                # Read CSV content
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                csv_input = csv.DictReader(stream)
                
                lessons_imported = 0
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                for row in csv_input:
                    try:
                        c.execute('''
                            INSERT INTO lessons 
                            (lesson_number, month, week_number, day_number, title, content, 
                             duration, competences, materials, objectives, tags, subject)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            int(row.get('lesson_number', 0)),
                            row.get('month', ''),
                            int(row.get('week_number', 1)),
                            int(row.get('day_number', 1)),
                            row.get('title', ''),
                            row.get('content', ''),
                            int(row.get('duration', 75)),
                            row.get('competences', ''),
                            row.get('materials', ''),
                            row.get('objectives', ''),
                            row.get('tags', ''),
                            row.get('subject', 'français')
                        ))
                        lessons_imported += 1
                    except Exception as e:
                        print(f"Error importing row: {e}")
                        continue
                
                conn.commit()
                conn.close()
                
                flash(f"{lessons_imported} leçons importées avec succès!", 'success')
                return redirect(url_for('lessons_list'))
            
            else:
                flash('Format de fichier non supporté. Utilisez CSV.', 'error')
                
        except Exception as e:
            flash(f"Erreur lors de l'importation: {e}", 'error')
    
    return render_template('import_lessons.html')

@app.route('/lessons/export')
def export_lessons():
    """Export lessons to CSV"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM lessons ORDER BY lesson_number")
    lessons = c.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'id', 'lesson_number', 'month', 'week_number', 'day_number', 
        'title', 'content', 'duration', 'competences', 'materials', 
        'objectives', 'tags', 'created_at', 'updated_at'
    ])
    
    # Write lesson data
    for lesson in lessons:
        writer.writerow(lesson)
    
    output.seek(0)
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=lessons_export_{datetime.now().strftime("%Y%m%d")}.csv'}
    )

@app.route('/lessons/bulk-actions', methods=['POST'])
def bulk_actions():
    """Handle bulk actions on lessons"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    action = request.form.get('action')
    lesson_ids = request.form.getlist('lesson_ids')
    
    if not lesson_ids:
        flash('Aucune leçon sélectionnée', 'error')
        return redirect(url_for('lessons_list'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        if action == 'delete':
            placeholders = ','.join(['?' for _ in lesson_ids])
            c.execute(f"DELETE FROM lessons WHERE id IN ({placeholders})", lesson_ids)
            c.execute(f"DELETE FROM student_progress WHERE lesson_id IN ({placeholders})", lesson_ids)
            flash(f"{len(lesson_ids)} leçons supprimées", 'success')
            
        elif action == 'update_month':
            new_month = request.form.get('new_month')
            if new_month:
                placeholders = ','.join(['?' for _ in lesson_ids])
                c.execute(f"UPDATE lessons SET month=? WHERE id IN ({placeholders})", 
                         [new_month] + lesson_ids)
                flash(f"{len(lesson_ids)} leçons mises à jour (mois: {new_month})", 'success')
            
        elif action == 'update_competence':
            new_competence = request.form.get('new_competence')
            if new_competence:
                placeholders = ','.join(['?' for _ in lesson_ids])
                c.execute(f"UPDATE lessons SET competences=? WHERE id IN ({placeholders})", 
                         [new_competence] + lesson_ids)
                flash(f"{len(lesson_ids)} leçons mises à jour (compétence: {new_competence})", 'success')
        
        conn.commit()
        
    except Exception as e:
        flash(f"Erreur lors de l'action groupée: {e}", 'error')
    finally:
        conn.close()
    
    return redirect(url_for('lessons_list'))

# Math Schedule Routes
# Math import route moved to math_schedule_importer.py to avoid duplication

@app.route('/math/overview')
def math_schedule_overview():
    """Display overview of the mathematics curriculum"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get lessons by cycle with tags
        cursor.execute('''
            SELECT week_number, COUNT(*) as lesson_count,
                   GROUP_CONCAT(DISTINCT tags) as unit_tags
            FROM lessons 
            WHERE subject = 'mathématiques'
            GROUP BY week_number 
            ORDER BY week_number
        ''')
        cycles = cursor.fetchall()
        
        # Get competency distribution
        cursor.execute('''
            SELECT competences, COUNT(*) as count
            FROM lessons
            WHERE competences IS NOT NULL AND subject = 'mathématiques'
            GROUP BY competences
            ORDER BY count DESC
        ''')
        competencies = cursor.fetchall()
        
        # Get total statistics
        cursor.execute('SELECT COUNT(*) FROM lessons WHERE subject = "mathématiques"')
        total_lessons = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT week_number) FROM lessons WHERE subject = "mathématiques"')
        total_cycles = cursor.fetchone()[0]
        
        conn.close()
        
        return render_template('math_schedule_overview.html', 
                             cycles=cycles, 
                             competencies=competencies,
                             total_lessons=total_lessons,
                             total_cycles=total_cycles)
    except Exception as e:
        flash(f'Erreur lors du chargement de l\'aperçu: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/math/units')
def math_units():
    """Redirect to math schedule overview for consolidated view"""
    return redirect(url_for('math_schedule_overview'))

@app.route('/math/competencies')
def competencies_overview():
    """Display overview of PFEQ competencies distribution"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get competency distribution by cycle
        cursor.execute('''
            SELECT week_number, competences, COUNT(*) as count
            FROM lessons
            WHERE competences IS NOT NULL AND subject = 'mathématiques'
            GROUP BY week_number, competences
            ORDER BY week_number
        ''')
        
        competency_data = cursor.fetchall()
        
        # Get overall competency statistics
        cursor.execute('''
            SELECT 
                SUM(CASE WHEN competences LIKE '%C1%' THEN 1 ELSE 0 END) as c1_count,
                SUM(CASE WHEN competences LIKE '%C2%' THEN 1 ELSE 0 END) as c2_count,
                SUM(CASE WHEN competences LIKE '%C3%' THEN 1 ELSE 0 END) as c3_count,
                COUNT(*) as total
            FROM lessons
            WHERE competences IS NOT NULL AND subject = 'mathématiques'
        ''')
        
        overall_stats = cursor.fetchone()
        
        conn.close()
        
        competencies_info = {
            'C1': {
                'title': 'Résoudre une situation-problème mathématique',
                'description': 'Développer des stratégies de résolution et appliquer différents processus mathématiques',
                'color': '#3B82F6',
                'count': overall_stats[0] if overall_stats else 0
            },
            'C2': {
                'title': 'Utiliser un raisonnement mathématique',
                'description': 'Développer et appliquer des stratégies liées aux concepts et processus mathématiques',
                'color': '#10B981',
                'count': overall_stats[1] if overall_stats else 0
            },
            'C3': {
                'title': 'Communiquer à l\'aide du langage mathématique',
                'description': 'Interpréter et produire des messages à caractère mathématique',
                'color': '#F59E0B',
                'count': overall_stats[2] if overall_stats else 0
            }
        }
        
        return render_template('competencies_overview.html',
                             competency_data=competency_data,
                             competencies_info=competencies_info,
                             total_lessons=overall_stats[3] if overall_stats else 0)
    except Exception as e:
        flash(f'Erreur lors du chargement des compétences: {str(e)}', 'error')
        return redirect(url_for('math_schedule_overview'))

@app.route('/math/progress')
def progress_dashboard():
    """Display student progress dashboard"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        user_id = session.get('user_id', 1)
        
        # Get overall progress
        cursor.execute('''
            SELECT 
                COUNT(*) as total_lessons,
                SUM(CASE WHEN sp.completed = 1 THEN 1 ELSE 0 END) as completed_lessons
            FROM lessons l
            LEFT JOIN student_progress sp ON l.id = sp.lesson_id AND sp.user_id = ?
            WHERE l.subject = 'mathématiques'
        ''', (user_id,))
        
        overall_progress = cursor.fetchone()
        
        # Get progress by unit
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN l.week_number BETWEEN 1 AND 4 THEN 'Unité 1: Arithmétique'
                    WHEN l.week_number BETWEEN 5 AND 8 THEN 'Unité 2: Algèbre'
                    WHEN l.week_number BETWEEN 9 AND 13 THEN 'Unité 3: Géométrie'
                    WHEN l.week_number BETWEEN 14 AND 16 THEN 'Unité 4: Statistiques'
                    WHEN l.week_number BETWEEN 17 AND 20 THEN 'Unité 5: Intégration'
                END as unit_name,
                COUNT(*) as total_lessons,
                SUM(CASE WHEN sp.completed = 1 THEN 1 ELSE 0 END) as completed_lessons
            FROM lessons l
            LEFT JOIN student_progress sp ON l.id = sp.lesson_id AND sp.user_id = ?
            WHERE l.subject = 'mathématiques'
            GROUP BY unit_name
            ORDER BY MIN(l.week_number)
        ''', (user_id,))
        
        unit_progress = cursor.fetchall()
        
        # Get recent activity
        cursor.execute('''
            SELECT l.title, l.lesson_number, sp.completion_date
            FROM student_progress sp
            JOIN lessons l ON l.id = sp.lesson_id
            WHERE sp.user_id = ? AND sp.completed = 1 AND l.subject = 'mathématiques'
            ORDER BY sp.completion_date DESC
            LIMIT 5
        ''', (user_id,))
        
        recent_activity = cursor.fetchall()
        
        conn.close()
        
        return render_template('progress_dashboard.html',
                             overall_progress=overall_progress,
                             unit_progress=unit_progress,
                             recent_activity=recent_activity)
    except Exception as e:
        flash(f'Erreur lors du chargement du tableau de bord: {str(e)}', 'error')
        return redirect(url_for('math_schedule_overview'))

# Theory routes
@app.route('/theory')
def theory():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    discipline = session.get('discipline', 'français')
    
    c.execute('''
        SELECT t.*, l.title as lesson_title 
        FROM theory t
        LEFT JOIN lessons l ON t.lesson_id = l.id
        WHERE t.discipline = ?
        ORDER BY t.created_at DESC
    ''', (discipline,))
    
    theory_items = c.fetchall()
    conn.close()
    
    return render_template('theory.html', theory_items=theory_items, discipline=discipline)

@app.route('/theory/create', methods=['GET', 'POST'])
def create_theory():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        lesson_id = request.form.get('lesson_id') if request.form.get('lesson_id') else None
        title = request.form['title']
        description = request.form.get('description', '')
        content = request.form.get('content', '')
        exercise_type = request.form.get('exercise_type', '')
        discipline = session.get('discipline', 'français')
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO theory (lesson_id, title, description, content, exercise_type, discipline)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (lesson_id, title, description, content, exercise_type, discipline))
        conn.commit()
        conn.close()
        
        flash('Ressource théorique créée avec succès!', 'success')
        return redirect(url_for('theory'))
    
    # Get lessons for dropdown
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    discipline = session.get('discipline', 'français')
    c.execute('SELECT id, title FROM lessons WHERE subject = ? ORDER BY lesson_number', (discipline,))
    lessons = c.fetchall()
    conn.close()
    
    return render_template('create_theory.html', lessons=lessons)

# Exercises routes
@app.route('/exercises')
def exercises():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    discipline = session.get('discipline', 'français')
    
    c.execute('''
        SELECT e.*, l.title as lesson_title
        FROM exercises e
        LEFT JOIN lessons l ON e.lesson_id = l.id
        WHERE e.discipline = ?
        ORDER BY e.created_at DESC
    ''', (discipline,))
    
    exercises_list = c.fetchall()
    conn.close()
    
    return render_template('exercises.html', exercises=exercises_list, discipline=discipline)

@app.route('/exercises/create', methods=['GET', 'POST'])
def create_exercise():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        lesson_id = request.form.get('lesson_id') if request.form.get('lesson_id') else None
        theory_id = request.form.get('theory_id') if request.form.get('theory_id') else None
        title = request.form['title']
        description = request.form.get('description', '')
        exercise_type = request.form['exercise_type']
        content = request.form['content']
        answer_key = request.form.get('answer_key', '')
        points = int(request.form.get('points', 10))
        discipline = session.get('discipline', 'français')
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO exercises (lesson_id, theory_id, title, description, exercise_type, content, answer_key, points, discipline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (lesson_id, theory_id, title, description, exercise_type, content, answer_key, points, discipline))
        conn.commit()
        conn.close()
        
        flash('Exercice créé avec succès!', 'success')
        return redirect(url_for('exercises'))
    
    # Get lessons and manuel items for dropdowns
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    discipline = session.get('discipline', 'français')
    c.execute('SELECT id, title FROM lessons WHERE subject = ? ORDER BY lesson_number', (discipline,))
    lessons = c.fetchall()
    c.execute('SELECT id, title FROM theory WHERE discipline = ? ORDER BY title', (discipline,))
    theory_items = c.fetchall()
    conn.close()
    
    return render_template('create_exercise.html', lessons=lessons, theory_items=theory_items)

# Portfolio routes
@app.route('/portfolio')
def portfolio():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    discipline = session.get('discipline', 'français')
    user_id = session.get('user_id')
    
    c.execute('''
        SELECT p.*, l.title as lesson_title
        FROM portfolio_items p
        LEFT JOIN lessons l ON p.lesson_id = l.id
        WHERE p.discipline = ? AND p.user_id = ?
        ORDER BY p.created_at DESC
    ''', (discipline, user_id))
    
    portfolio_items = c.fetchall()
    conn.close()
    
    return render_template('portfolio.html', portfolio_items=portfolio_items, discipline=discipline)

@app.route('/portfolio/create', methods=['GET', 'POST'])
def create_portfolio_item():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        lesson_id = request.form.get('lesson_id') if request.form.get('lesson_id') else None
        item_type = request.form['item_type']
        title = request.form['title']
        description = request.form.get('description', '')
        content = request.form.get('content', '')
        due_date = request.form.get('due_date')
        discipline = session.get('discipline', 'français')
        user_id = session.get('user_id')
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO portfolio_items (user_id, lesson_id, item_type, title, description, content, due_date, discipline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, lesson_id, item_type, title, description, content, due_date, discipline))
        conn.commit()
        conn.close()
        
        flash('Élément de portfolio créé avec succès!', 'success')
        return redirect(url_for('portfolio'))
    
    # Get lessons for dropdown
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    discipline = session.get('discipline', 'français')
    c.execute('SELECT id, title FROM lessons WHERE subject = ? ORDER BY lesson_number', (discipline,))
    lessons = c.fetchall()
    conn.close()
    
    return render_template('create_portfolio_item.html', lessons=lessons)

# Grammar Gender Exercise Routes
@app.route('/exercises/grammar/gender')
def grammar_gender_exercises():
    """Display grammar gender exercise dashboard"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    user_id = session.get('user_id')
    
    # Get user statistics
    c.execute('''
        SELECT COUNT(*) as total_sessions,
               AVG(CASE WHEN status = 'completed' THEN score * 100.0 / total_questions ELSE NULL END) as avg_score,
               MAX(score * 100.0 / total_questions) as best_score
        FROM grammar_gender_sessions 
        WHERE user_id = ?
    ''', (user_id,))
    stats = c.fetchone()
    
    # Get recent sessions
    c.execute('''
        SELECT id, session_type, score, total_questions, 
               ROUND(score * 100.0 / total_questions, 1) as percentage,
               datetime(started_at, 'localtime') as started_at,
               datetime(completed_at, 'localtime') as completed_at,
               status
        FROM grammar_gender_sessions 
        WHERE user_id = ? 
        ORDER BY started_at DESC 
        LIMIT 10
    ''', (user_id,))
    recent_sessions = c.fetchall()
    
    # Get question count by difficulty
    c.execute('''
        SELECT niveau_difficulte, COUNT(*) as count
        FROM grammar_gender_questions
        GROUP BY niveau_difficulte
        ORDER BY niveau_difficulte
    ''')
    question_distribution = c.fetchall()
    
    conn.close()
    
    return render_template('grammar_gender_dashboard.html', 
                         stats=stats, 
                         recent_sessions=recent_sessions,
                         question_distribution=question_distribution)

@app.route('/exercises/grammar/gender/practice')
def start_grammar_gender_practice():
    """Start a new grammar gender practice session"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    questions_count = request.args.get('count', 10, type=int)
    difficulty = request.args.get('difficulty', 'all')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Create new session
    user_id = session.get('user_id')
    c.execute('''
        INSERT INTO grammar_gender_sessions (user_id, session_type, questions_count, total_questions)
        VALUES (?, 'practice', ?, ?)
    ''', (user_id, questions_count, questions_count))
    session_id = c.lastrowid
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('grammar_gender_question', session_id=session_id, question_num=1))

@app.route('/exercises/grammar/gender/session/<int:session_id>/question/<int:question_num>')
def grammar_gender_question(session_id, question_num):
    """Display a specific question in a session"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Verify session belongs to user
    c.execute('SELECT * FROM grammar_gender_sessions WHERE id = ? AND user_id = ?', 
              (session_id, session.get('user_id')))
    session_data = c.fetchone()
    
    if not session_data:
        flash('Session non trouvée', 'error')
        return redirect(url_for('grammar_gender_exercises'))
    
    # Get random question not yet answered in this session
    c.execute('''
        SELECT gq.* FROM grammar_gender_questions gq
        WHERE gq.id NOT IN (
            SELECT question_id FROM grammar_gender_attempts 
            WHERE session_id = ?
        )
        ORDER BY RANDOM()
        LIMIT 1
    ''', (session_id,))
    question = c.fetchone()
    
    if not question:
        # No more questions, redirect to results
        return redirect(url_for('grammar_gender_results', session_id=session_id))
    
    # Get session progress
    c.execute('SELECT COUNT(*) FROM grammar_gender_attempts WHERE session_id = ?', (session_id,))
    answered_count = c.fetchone()[0]
    
    conn.close()
    
    progress = {
        'current': answered_count + 1,
        'total': session_data[3],  # total_questions
        'percentage': round((answered_count / session_data[3]) * 100)
    }
    
    return render_template('grammar_gender_question.html', 
                         question=question, 
                         session_id=session_id,
                         question_num=question_num,
                         progress=progress)

@app.route('/exercises/grammar/gender/session/<int:session_id>/submit', methods=['POST'])
def submit_grammar_gender_answer(session_id):
    """Submit an answer for a grammar gender question"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    question_id = request.form.get('question_id')
    user_answer = request.form.get('answer')
    time_taken = request.form.get('time_taken', 0, type=int)
    hints_used = request.form.get('hints_used', 0, type=int)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get question details including word and examples
    c.execute('''
        SELECT genre_du_nom, nom, terminaisons, exemple_usage_courant, exemple_usage_litteraire, exemple_usage_universitaire 
        FROM grammar_gender_questions WHERE id = ?
    ''', (question_id,))
    question_data = c.fetchone()
    correct_answer = question_data[0]
    word = question_data[1]
    explanation = question_data[2] if question_data[2] else None
    usage_courant = question_data[3]
    usage_litteraire = question_data[4]
    usage_universitaire = question_data[5]
    
    is_correct = user_answer.lower() == correct_answer.lower()
    
    # Calculate score: base 10 points, -5 points per hint used
    question_score = 10 - (hints_used * 5)
    if not is_correct:
        question_score = 0  # No points for incorrect answers
    
    # Save attempt
    c.execute('''
        INSERT INTO grammar_gender_attempts 
        (session_id, question_id, user_answer, is_correct, time_taken, hints_used, score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, question_id, user_answer, is_correct, time_taken, hints_used, question_score))
    
    # Update session score with points instead of just counting correct answers
    c.execute('''
        UPDATE grammar_gender_sessions 
        SET score = score + ? 
        WHERE id = ?
    ''', (question_score, session_id))
    
    # Check if session is complete
    c.execute('SELECT COUNT(*) FROM grammar_gender_attempts WHERE session_id = ?', (session_id,))
    answered_count = c.fetchone()[0]
    
    c.execute('SELECT total_questions FROM grammar_gender_sessions WHERE id = ?', (session_id,))
    total_questions = c.fetchone()[0]
    
    # Prepare JSON response with feedback data
    response_data = {
        'is_correct': is_correct,
        'correct_answer': correct_answer,
        'user_answer': user_answer,
        'word': word,
        'points_earned': question_score,
        'explanation': explanation,
        'examples': {
            'usage_courant': usage_courant,
            'usage_litteraire': usage_litteraire,
            'usage_universitaire': usage_universitaire
        },
        'session_complete': answered_count >= total_questions,
        'next_url': url_for('grammar_gender_results', session_id=session_id) if answered_count >= total_questions else url_for('grammar_gender_question', session_id=session_id, question_num=answered_count + 1)
    }
    
    if answered_count >= total_questions:
        # Mark session as completed
        c.execute('''
            UPDATE grammar_gender_sessions 
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (session_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify(response_data)

@app.route('/exercises/grammar/gender/session/<int:session_id>/results')
def grammar_gender_results(session_id):
    """Display results for a completed session"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get session data
    c.execute('''
        SELECT * FROM grammar_gender_sessions 
        WHERE id = ? AND user_id = ?
    ''', (session_id, session.get('user_id')))
    session_data = c.fetchone()
    
    if not session_data:
        flash('Session non trouvée', 'error')
        return redirect(url_for('grammar_gender_exercises'))
    
    # Get detailed results
    c.execute('''
        SELECT ga.*, gq.nom, gq.genre_du_nom, gq.exemple_usage_courant
        FROM grammar_gender_attempts ga
        JOIN grammar_gender_questions gq ON ga.question_id = gq.id
        WHERE ga.session_id = ?
        ORDER BY ga.attempted_at
    ''', (session_id,))
    attempts = c.fetchall()
    
    conn.close()
    
    # Calculate statistics
    total_questions = len(attempts)
    correct_answers = sum(1 for attempt in attempts if attempt[4])  # is_correct
    total_points = sum(attempt[8] if len(attempt) > 8 else 0 for attempt in attempts)  # score column
    max_possible_points = total_questions * 10
    total_time = sum(attempt[5] if attempt[5] else 0 for attempt in attempts)  # time_taken
    total_hints = sum(attempt[7] if len(attempt) > 7 else 0 for attempt in attempts)  # hints_used
    
    percentage = round((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    points_percentage = round((total_points / max_possible_points) * 100) if max_possible_points > 0 else 0
    
    results = {
        'session_id': session_id,
        'score': correct_answers,
        'total': total_questions,
        'percentage': percentage,
        'total_points': total_points,
        'max_possible_points': max_possible_points,
        'points_percentage': points_percentage,
        'total_time': total_time,
        'total_hints': total_hints,
        'avg_time': round(total_time / total_questions) if total_questions > 0 else 0,
        'attempts': attempts
    }
    
    return render_template('grammar_gender_results.html', results=results)

@app.route('/exercises/grammar/gender/manage')
def manage_grammar_gender_questions():
    """Manage grammar gender questions (admin only)"""
    if 'user' not in session or session.get('role') != 'teacher':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('grammar_gender_exercises'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM grammar_gender_questions 
        ORDER BY niveau_difficulte, nom
    ''')
    questions = c.fetchall()
    
    conn.close()
    
    return render_template('manage_grammar_questions.html', questions=questions)

@app.route('/exercises/grammar/gender/add-question', methods=['GET', 'POST'])
def add_grammar_gender_question():
    """Add a new grammar gender question"""
    if 'user' not in session or session.get('role') != 'teacher':
        flash('Accès non autorisé', 'error')
        return redirect(url_for('grammar_gender_exercises'))
    
    if request.method == 'POST':
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO grammar_gender_questions 
                (sub_question_id, nom, genre_du_nom, niveau_difficulte, 
                 exemple_usage_courant, exemple_usage_litteraire, 
                 exemple_usage_universitaire, terminaisons)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                request.form['sub_question_id'],
                request.form['nom'],
                request.form['genre_du_nom'],
                int(request.form['niveau_difficulte']),
                request.form.get('exemple_usage_courant', ''),
                request.form.get('exemple_usage_litteraire', ''),
                request.form.get('exemple_usage_universitaire', ''),
                request.form.get('terminaisons', '')
            ))
            conn.commit()
            flash('Question ajoutée avec succès!', 'success')
            return redirect(url_for('manage_grammar_gender_questions'))
        except sqlite3.IntegrityError:
            flash('ID de question déjà existant', 'error')
        except Exception as e:
            flash(f'Erreur: {e}', 'error')
        finally:
            conn.close()
    
    return render_template('add_grammar_question.html')

# Mathematics Exercise Routes
@app.route('/exercises/math/<subdiscipline>')
def math_exercises(subdiscipline):
    """Display mathematics exercises for a specific subdiscipline"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    valid_subdisciplines = ['algebre', 'geometrie', 'arithmetique', 'probabilites']
    if subdiscipline not in valid_subdisciplines:
        flash('Sous-discipline non valide', 'error')
        return redirect(url_for('exercises'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get exercises for mathematics with specific subdiscipline (stored in exercise_type or tags)
    c.execute('''
        SELECT * FROM exercises 
        WHERE discipline = 'mathematiques' 
        AND (exercise_type LIKE ? OR tags LIKE ?)
        ORDER BY created_at DESC
    ''', (f'%{subdiscipline}%', f'%{subdiscipline}%'))
    
    exercises_list = c.fetchall()
    conn.close()
    
    subdiscipline_names = {
        'algebre': 'Algèbre',
        'geometrie': 'Géométrie', 
        'arithmetique': 'Arithmétique',
        'probabilites': 'Probabilités'
    }
    
    return render_template('math_exercises.html', 
                         exercises=exercises_list, 
                         subdiscipline=subdiscipline,
                         subdiscipline_name=subdiscipline_names[subdiscipline])

# French Exercise Routes  
@app.route('/exercises/french/<subdiscipline>')
def french_exercises(subdiscipline):
    """Display French exercises for a specific subdiscipline"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    valid_subdisciplines = ['orthographe', 'conjugaison', 'vocabulaire']
    if subdiscipline not in valid_subdisciplines:
        flash('Sous-discipline non valide', 'error')
        return redirect(url_for('exercises'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM exercises 
        WHERE discipline = 'francais' 
        AND (exercise_type LIKE ? OR tags LIKE ?)
        ORDER BY created_at DESC
    ''', (f'%{subdiscipline}%', f'%{subdiscipline}%'))
    
    exercises_list = c.fetchall()
    conn.close()
    
    subdiscipline_names = {
        'orthographe': 'Orthographe',
        'conjugaison': 'Conjugaison',
        'vocabulaire': 'Vocabulaire'
    }
    
    return render_template('french_exercises.html', 
                         exercises=exercises_list, 
                         subdiscipline=subdiscipline,
                         subdiscipline_name=subdiscipline_names[subdiscipline])

# History Exercise Routes
@app.route('/exercises/history/<subdiscipline>')
def history_exercises(subdiscipline):
    """Display History exercises for a specific subdiscipline"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    valid_subdisciplines = ['analyse_artefact', 'ligne_temps', 'caracteristiques_historiques', 'antiquite', 'moyen_age', 'moderne']
    if subdiscipline not in valid_subdisciplines:
        flash('Sous-discipline non valide', 'error')
        return redirect(url_for('exercises'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM exercises 
        WHERE discipline = 'histoire' 
        AND (exercise_type LIKE ? OR tags LIKE ?)
        ORDER BY created_at DESC
    ''', (f'%{subdiscipline}%', f'%{subdiscipline}%'))
    
    exercises_list = c.fetchall()
    conn.close()
    
    subdiscipline_names = {
        'analyse_artefact': 'Analyse d\'artéfact',
        'ligne_temps': 'Ligne du temps',
        'caracteristiques_historiques': 'Caractéristiques historiques',
        'antiquite': 'Antiquité',
        'moyen_age': 'Moyen-Âge',
        'moderne': 'Histoire moderne'
    }
    
    return render_template('history_exercises.html', 
                         exercises=exercises_list, 
                         subdiscipline=subdiscipline,
                         subdiscipline_name=subdiscipline_names[subdiscipline])

# Geography Exercise Routes
@app.route('/exercises/geography/<subdiscipline>')
def geography_exercises(subdiscipline):
    """Display Geography exercises for a specific subdiscipline"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    valid_subdisciplines = ['carte']
    if subdiscipline not in valid_subdisciplines:
        flash('Sous-discipline non valide', 'error')
        return redirect(url_for('exercises'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM exercises 
        WHERE discipline = 'geographie' 
        AND (exercise_type LIKE ? OR tags LIKE ?)
        ORDER BY created_at DESC
    ''', (f'%{subdiscipline}%', f'%{subdiscipline}%'))
    
    exercises_list = c.fetchall()
    conn.close()
    
    subdiscipline_names = {
        'carte': 'Cartes'
    }
    
    return render_template('geography_exercises.html', 
                         exercises=exercises_list, 
                         subdiscipline=subdiscipline,
                         subdiscipline_name=subdiscipline_names[subdiscipline])

# Culture and Citizenship Exercise Routes
@app.route('/exercises/ccq/<subdiscipline>')
def ccq_exercises(subdiscipline):
    """Display Culture and Citizenship exercises for a specific subdiscipline"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    valid_subdisciplines = ['reflexion']
    if subdiscipline not in valid_subdisciplines:
        flash('Sous-discipline non valide', 'error')
        return redirect(url_for('exercises'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM exercises 
        WHERE discipline = 'culture_citoyennete' 
        AND (exercise_type LIKE ? OR tags LIKE ?)
        ORDER BY created_at DESC
    ''', (f'%{subdiscipline}%', f'%{subdiscipline}%'))
    
    exercises_list = c.fetchall()
    conn.close()
    
    subdiscipline_names = {
        'reflexion': 'Réflexion'
    }
    
    return render_template('ccq_exercises.html', 
                         exercises=exercises_list, 
                         subdiscipline=subdiscipline,
                         subdiscipline_name=subdiscipline_names[subdiscipline])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
