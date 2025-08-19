# flask_routes_math.py
# Add these routes to your main Flask application

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime

# Add these routes to your existing Flask app

@app.route('/math/import')
def import_math_schedule():
    """Import the complete mathematics schedule into the database"""
    try:
        # Import the complete schedule
        try:
            from complete_math_schedule import import_to_flask_db
            import_to_flask_db()
        except ImportError:
            flash('Module complete_math_schedule non trouvé. Utilisez l\'importation CSV standard avec subject="mathématiques"', 'warning')
            return redirect(url_for('import_lessons'))
        
        flash('Programme de mathématiques importé avec succès! 🎉', 'success')
        return redirect(url_for('math_schedule_overview'))
    except Exception as e:
        flash(f'Erreur lors de l\'importation: {str(e)}', 'error')
        return redirect(url_for('math_schedule_overview'))

@app.route('/math/overview')
def math_schedule_overview():
    """Display overview of the mathematics curriculum"""
    try:
        conn = sqlite3.connect('database.db')
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
        return redirect(url_for('math_schedule_overview'))

@app.route('/math/cycle/<int:cycle_number>')
def cycle_detail(cycle_number):
    """Display detailed view of a specific cycle"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Get all lessons for this cycle
        cursor.execute('''
            SELECT * FROM lessons 
            WHERE week_number = ? AND subject = 'mathématiques'
            ORDER BY day_number
        ''', (cycle_number,))
        
        lessons = cursor.fetchall()
        
        # Get progress for these lessons (if you have user authentication)
        # This assumes you have a way to identify the current user
        user_id = 1  # Replace with actual user identification
        
        lesson_ids = [lesson[0] for lesson in lessons]
        if lesson_ids:
            placeholders = ','.join('?' * len(lesson_ids))
            cursor.execute(f'''
                SELECT lesson_id, completed, completion_date, notes
                FROM student_progress 
                WHERE lesson_id IN ({placeholders}) AND user_id = ?
            ''', lesson_ids + [user_id])
            
            progress_data = {row[0]: row[1:] for row in cursor.fetchall()}
        else:
            progress_data = {}
        
        conn.close()
        
        if not lessons:
            flash(f'Aucune leçon trouvée pour le cycle {cycle_number}', 'warning')
            return redirect(url_for('math_schedule_overview'))
        
        # Add progress information to lessons
        lessons_with_progress = []
        for lesson in lessons:
            lesson_dict = {
                'id': lesson[0],
                'lesson_number': lesson[1],
                'month': lesson[2],
                'week_number': lesson[3],
                'day_number': lesson[4],
                'title': lesson[5],
                'content': lesson[6],
                'duration': lesson[7],
                'competences': lesson[8],
                'materials': lesson[9],
                'objectives': lesson[10],
                'tags': lesson[11],
                'subject': lesson[12],
                'progress': progress_data.get(lesson[0], (False, None, None))
            }
            lessons_with_progress.append(lesson_dict)
        
        return render_template('cycle_detail.html', 
                             lessons=lessons_with_progress, 
                             cycle_number=cycle_number)
    except Exception as e:
        flash(f'Erreur lors du chargement du cycle: {str(e)}', 'error')
        return redirect(url_for('math_schedule_overview'))

@app.route('/math/mark_complete/<int:lesson_id>', methods=['POST'])
def mark_complete_ajax(lesson_id):
    """Mark a lesson as complete via AJAX"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        user_id = 1  # Replace with actual user identification
        completion_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert or update progress
        cursor.execute('''
            INSERT OR REPLACE INTO student_progress 
            (lesson_id, user_id, completed, completion_date)
            VALUES (?, ?, ?, ?)
        ''', (lesson_id, user_id, True, completion_date))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Leçon marquée comme terminée'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/math/units')
def math_units():
    """Display the 5 main units of the mathematics curriculum"""
    units = [
        {
            'number': 1,
            'title': 'Arithmétique et sens du nombre',
            'cycles': '1-4',
            'lessons': '1-32',
            'description': 'Fondements arithmétiques, nombres réels, proportionnalité',
            'color': '#3B82F6',
            'icon': '🔢'
        },
        {
            'number': 2,
            'title': 'Introduction à l\'algèbre',
            'cycles': '5-8',
            'lessons': '33-64',
            'description': 'Pensée algébrique, expressions, équations de base',
            'color': '#10B981',
            'icon': '📊'
        },
        {
            'number': 3,
            'title': 'Géométrie et mesures',
            'cycles': '9-13',
            'lessons': '65-104',
            'description': 'Figures planes, solides, constructions géométriques',
            'color': '#F59E0B',
            'icon': '📐'
        },
        {
            'number': 4,
            'title': 'Statistiques et probabilités',
            'cycles': '14-16',
            'lessons': '105-128',
            'description': 'Analyse de données, sondages, probabilités de base',
            'color': '#EF4444',
            'icon': '📈'
        },
        {
            'number': 5,
            'title': 'Intégration et projets',
            'cycles': '17-20',
            'lessons': '129-160',
            'description': 'Résolution de problèmes complexes, projets intégrateurs',
            'color': '#8B5CF6',
            'icon': '🎯'
        }
    ]
    
    return render_template('math_units.html', units=units)

@app.route('/math/unit/<int:unit_number>')
def unit_detail(unit_number):
    """Display detailed view of a specific unit"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Define unit ranges
        unit_ranges = {
            1: (1, 4),    # Cycles 1-4
            2: (5, 8),    # Cycles 5-8
            3: (9, 13),   # Cycles 9-13
            4: (14, 16),  # Cycles 14-16
            5: (17, 20)   # Cycles 17-20
        }
        
        if unit_number not in unit_ranges:
            flash('Unité non trouvée', 'error')
            return redirect(url_for('math_units'))
        
        start_cycle, end_cycle = unit_ranges[unit_number]
        
        # Get all lessons for this unit
        cursor.execute('''
            SELECT * FROM lessons 
            WHERE week_number BETWEEN ? AND ? AND subject = 'mathématiques'
            ORDER BY week_number, day_number
        ''', (start_cycle, end_cycle))
        
        lessons = cursor.fetchall()
        
        # Group lessons by cycle
        cycles = {}
        for lesson in lessons:
            cycle = lesson[3]  # week_number column
            if cycle not in cycles:
                cycles[cycle] = []
            cycles[cycle].append(lesson)
        
        conn.close()
        
        unit_info = {
            1: {'title': 'Arithmétique et sens du nombre', 'description': 'Fondements arithmétiques, nombres réels, proportionnalité'},
            2: {'title': 'Introduction à l\'algèbre', 'description': 'Pensée algébrique, expressions, équations de base'},
            3: {'title': 'Géométrie et mesures', 'description': 'Figures planes, solides, constructions géométriques'},
            4: {'title': 'Statistiques et probabilités', 'description': 'Analyse de données, sondages, probabilités de base'},
            5: {'title': 'Intégration et projets', 'description': 'Résolution de problèmes complexes, projets intégrateurs'}
        }
        
        return render_template('unit_detail.html', 
                             unit_number=unit_number,
                             unit_info=unit_info[unit_number],
                             cycles=cycles,
                             total_lessons=len(lessons))
    except Exception as e:
        flash(f'Erreur lors du chargement de l\'unité: {str(e)}', 'error')
        return redirect(url_for('math_units'))

@app.route('/math/competencies')
def competencies_overview():
    """Display overview of PFEQ competencies distribution"""
    try:
        conn = sqlite3.connect('database.db')
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

@app.route('/math/assessments')
def assessment_calendar():
    """Display major assessment moments throughout the year"""
    assessment_moments = [
        {
            'cycle': 4,
            'lesson': 32,
            'title': 'Évaluation - Arithmétique et proportionnalité',
            'type': 'Évaluation formative',
            'month': 'octobre',
            'competencies': ['C1', 'C2', 'C3']
        },
        {
            'cycle': 8,
            'lesson': 64,
            'title': 'Évaluation - Pensée algébrique',
            'type': 'Évaluation sommative',
            'month': 'décembre',
            'competencies': ['C1', 'C2']
        },
        {
            'cycle': 13,
            'lesson': 104,
            'title': 'Évaluation - Géométrie et mesures',
            'type': 'Évaluation sommative',
            'month': 'mars',
            'competencies': ['C1', 'C2', 'C3']
        },
        {
            'cycle': 16,
            'lesson': 128,
            'title': 'Évaluation - Statistiques et probabilités',
            'type': 'Projet d\'enquête',
            'month': 'avril',
            'competencies': ['C1', 'C2', 'C3']
        },
        {
            'cycle': 18,
            'lesson': 144,
            'title': 'Projet intégrateur de résolution de problèmes',
            'type': 'Projet majeur',
            'month': 'mai',
            'competencies': ['C1', 'C2', 'C3']
        },
        {
            'cycle': 20,
            'lesson': 160,
            'title': 'Évaluation finale intégrative',
            'type': 'Évaluation sommative',
            'month': 'juin',
            'competencies': ['C1', 'C2', 'C3']
        }
    ]
    
    return render_template('assessment_calendar.html', assessments=assessment_moments)

@app.route('/math/progress')
def progress_dashboard():
    """Display student progress dashboard"""
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        user_id = 1  # Replace with actual user identification
        
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

# Helper function to initialize the database with sample data
def initialize_math_database():
    """Initialize the database with the complete mathematics schedule"""
    try:
        try:
            from complete_math_schedule import import_to_flask_db
            import_to_flask_db()
            return True
        except ImportError:
            print("Module complete_math_schedule not found. Please use CSV import with subject='mathématiques'")
            return False
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

# CLI command to import schedule (if using Flask CLI)
@app.cli.command()
def import_math():
    """Import the complete mathematics schedule"""
    if initialize_math_database():
        print("✅ Mathematics schedule imported successfully!")
    else:
        print("❌ Failed to import mathematics schedule")
