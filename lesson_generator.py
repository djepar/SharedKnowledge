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
    
    query += " ORDER BY lesson_number"
    
    c.execute(query, params)
    lessons = c.fetchall()
    
    # Get unique months and competences for filters
    c.execute("SELECT DISTINCT month FROM lessons ORDER BY lesson_number")
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
            'lesson_number': request.form.get('lesson_number', type=int),
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
                (lesson_number, month, week_number, day_number, title, content, 
                 duration, competences, materials, objectives, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    
    # Get next lesson number
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT MAX(lesson_number) FROM lessons")
    result = c.fetchone()
    next_lesson_number = (result[0] or 0) + 1
    conn.close()
    
    return render_template('create_lesson.html', next_lesson_number=next_lesson_number)

@app.route('/lesson/<int:lesson_id>/edit', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    """Edit an existing lesson"""
    if 'user' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    if request.method == 'POST':
        lesson_data = {
            'lesson_number': request.form.get('lesson_number', type=int),
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
                lesson_number=?, month=?, week_number=?, day_number=?, title=?, 
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
    
    # Get next lesson number
    c.execute("SELECT MAX(lesson_number) FROM lessons")
    result = c.fetchone()
    next_lesson_number = (result[0] or 0) + 1
    
    try:
        # Create duplicate with new lesson number
        c.execute('''
            INSERT INTO lessons 
            (lesson_number, month, week_number, day_number, title, content, 
             duration, competences, materials, objectives, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            original[11]  # tags
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
    """Import lessons from CSV or JSON"""
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
                import csv
                import io
                
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
                             duration, competences, materials, objectives, tags)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                            row.get('tags', '')
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
    
    import csv
    import io
    from flask import Response
    
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
