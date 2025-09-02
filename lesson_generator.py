# lesson_generator.py - Add these routes to your app.py

@app.route('/lessons')
def lessons_list():
    """Display all lessons with filtering and search"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Get filter parameters
    month_filter = request.args.get('month', '')
    competence_filter = request.args.get('competence', '')
    search_query = request.args.get('search', '')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Build query with filters
    query = "SELECT * FROM lessons WHERE 1=1"
    params = []
    
    if month_filter:
        query += " AND month = ?"
        params.append(month_filter)
    
    if competence_filter:
        query += " AND competences LIKE ?"
        params.append(f"%{competence_filter}%")
    
    if search_query:
        query += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
    
    query += " ORDER BY id"
    
    c.execute(query, params)
    lessons = c.fetchall()
    
    # Get unique months and competences for filters
    c.execute("SELECT DISTINCT month FROM lessons ORDER BY id")
    months = [row[0] for row in c.fetchall()]
    
    c.execute("SELECT DISTINCT competences FROM lessons WHERE competences IS NOT NULL")
    competences = list(set([comp.strip() for row in c.fetchall() for comp in row[0].split(',') if comp.strip()]))
    
    conn.close()
    
    return render_template('lessons_list.html', 
                         lessons=lessons, 
                         months=months, 
                         competences=competences,
                         current_filters={
                             'month': month_filter,
                             'competence': competence_filter,
                             'search': search_query
                         })

@app.route('/lesson/create', methods=['GET', 'POST'])
def create_lesson():
    """Create a new lesson"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        lesson_data = {
            'month': request.form['month'],
            'week_number': request.form.get('week_number', type=int),
            'day_number': request.form.get('day_number', type=int),
            'title': request.form['title'],
            'content': request.form['content'],
            'duration': request.form.get('duration', 75, type=int),
            'competences': request.form.get('competences', ''),
            'materials': request.form.get('materials', ''),
            'objectives': request.form.get('objectives', ''),
            'tags': request.form.get('tags', '')
        }
        
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        try:
            c.execute('''
                INSERT INTO lessons 
                (month, week_number, day_number, title, content, 
                 duration, competences, materials, objectives, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(lesson_data.values()))
            
            conn.commit()
            flash(f"Leçon '{lesson_data['title']}' créée avec succès!", 'success')
            return redirect(url_for('lessons_list'))
            
        except sqlite3.IntegrityError as e:
            flash(f"Erreur d'intégrité de la base de données: {e}", 'error')
        except Exception as e:
            flash(f"Erreur lors de la création: {e}", 'error')
        finally:
            conn.close()
    
    return render_template('create_lesson.html')

@app.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    """Edit an existing lesson"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if request.method == 'POST':
        lesson_data = {
            'month': request.form['month'],
            'week_number': request.form.get('week_number', type=int),
            'day_number': request.form.get('day_number', type=int),
            'title': request.form['title'],
            'content': request.form['content'],
            'duration': request.form.get('duration', 75, type=int),
            'competences': request.form.get('competences', ''),
            'materials': request.form.get('materials', ''),
            'objectives': request.form.get('objectives', ''),
            'tags': request.form.get('tags', '')
        }
        
        try:
            c.execute('''
                UPDATE lessons SET 
                month=?, week_number=?, day_number=?, title=?, 
                content=?, duration=?, competences=?, materials=?, objectives=?, 
                tags=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', tuple(lesson_data.values()) + (lesson_id,))
            
            conn.commit()
            flash("Leçon mise à jour avec succès!", 'success')
            return redirect(url_for('lesson_detail', lesson_id=lesson_id))
            
        except Exception as e:
            flash(f"Erreur lors de la mise à jour: {e}", 'error')
    
    # Get lesson data
    c.execute("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    lesson = c.fetchone()
    conn.close()
    
    if not lesson:
        flash("Leçon non trouvée", 'error')
        return redirect(url_for('lessons_list'))
    
    return render_template('edit_lesson.html', lesson=lesson)

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
    
    try:
        # Create duplicate without lesson number
        c.execute('''
            INSERT INTO lessons 
            (month, week_number, day_number, title, content, 
             duration, competences, materials, objectives, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            original[1],  # month
            original[2],  # week_number
            original[3],  # day_number
            f"[COPIE] {original[4]}",  # title
            original[5],  # content
            original[6],  # duration
            original[7],  # competences
            original[8],  # materials
            original[9], # objectives
            original[10]  # tags
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

# Duplicate import route removed - using the one in app.py instead

@app.route('/lessons/export')
def export_lessons():
    """Export lessons to CSV"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM lessons ORDER BY id")
    lessons = c.fetchall()
    conn.close()
    
    import csv
    import io
    from flask import Response
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'id', 'month', 'week_number', 'day_number', 
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
