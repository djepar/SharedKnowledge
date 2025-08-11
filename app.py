from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_FILE = 'database.db'

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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
            return redirect(url_for('index'))
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

@app.route('/calendar')
def calendar():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM lessons ORDER BY lesson_number")
    lessons = c.fetchall()
    conn.close()
    
    # Group lessons by month
    lessons_by_month = {}
    for lesson in lessons:
        month = lesson[2]
        if month not in lessons_by_month:
            lessons_by_month[month] = []
        lessons_by_month[month].append(lesson)
    
    return render_template('calendar.html', lessons_by_month=lessons_by_month)

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
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Get user statistics
    completed_lessons = 0
    books_read = 0
    avg_rating = 0
    
    if 'user_id' in session:
        # Get completed lessons count
        c.execute("SELECT COUNT(*) FROM student_progress WHERE user_id=? AND completed=1", 
                  (session['user_id'],))
        completed_lessons = c.fetchone()[0]
        
        # Get books read count
        c.execute("SELECT COUNT(*) FROM reading_log WHERE user_id=?", (session['user_id'],))
        books_read = c.fetchone()[0]
        
        # Get average rating
        c.execute("SELECT AVG(rating) FROM reading_log WHERE user_id=? AND rating IS NOT NULL", 
                  (session['user_id'],))
        avg_rating_result = c.fetchone()[0]
        avg_rating = round(avg_rating_result, 1) if avg_rating_result else 0
    
    # Get total lessons count
    c.execute("SELECT COUNT(*) FROM lessons")
    total_lessons = c.fetchone()[0]
    
    # Calculate progress percentage
    if total_lessons > 0:
        progress_percentage = round((completed_lessons / total_lessons * 100), 1)
    else:
        progress_percentage = 0
    
    conn.close()
    
    # Prepare data for template
    data = {
        'completed_lessons': completed_lessons,
        'total_lessons': total_lessons,
        'books_read': books_read,
        'avg_rating': avg_rating,
        'progress_percentage': progress_percentage
    }
    
    return render_template('dashboard.html', **data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)
