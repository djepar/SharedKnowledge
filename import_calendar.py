#!/usr/bin/env python3
"""
Script to import calendar data from CSV into the database
"""

import csv
import sqlite3
import os

def import_calendar_data():
    """Import calendar data from CSV into the database"""
    
    # Paths
    csv_path = 'Notes/calendrier_cleaned.csv'
    db_path = 'instance/classroom.db'
    
    # Check if files exist
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return False
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Create schedule table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                day_of_week TEXT,
                day_number INTEGER,
                event_type TEXT,
                p1_course TEXT,
                p2_course TEXT,
                p3_course TEXT,
                p4_course TEXT,
                UNIQUE(date)
            )
        ''')
        print("📋 Created/verified schedule table")
        
        # Clear existing schedule data
        c.execute("DELETE FROM schedule")
        print("🗑️  Cleared existing schedule data")
        
        # Import CSV data
        imported_count = 0
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                c.execute('''
                    INSERT OR REPLACE INTO schedule 
                    (date, day_of_week, day_number, event_type, p1_course, p2_course, p3_course, p4_course)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['Date'],
                    row['Day_of_Week'],
                    row['Day_Number'] if row['Day_Number'] else None,
                    row['Event_Type'],
                    row['P1_Course'] if row['P1_Course'] else None,
                    row['P2_Course'] if row['P2_Course'] else None,
                    row['P3_Course'] if row['P3_Course'] else None,
                    row['P4_Course'] if row['P4_Course'] else None
                ))
                imported_count += 1
        
        # Commit changes
        conn.commit()
        print(f"✅ Successfully imported {imported_count} calendar entries")
        
        # Verify import
        c.execute("SELECT COUNT(*) FROM schedule")
        total_count = c.fetchone()[0]
        print(f"📊 Total entries in schedule table: {total_count}")
        
        # Show some sample data
        c.execute("SELECT date, event_type, p1_course FROM schedule LIMIT 5")
        sample_data = c.fetchall()
        print("\n📅 Sample imported data:")
        for date, event_type, p1_course in sample_data:
            course_info = f" - {p1_course}" if p1_course else ""
            print(f"  {date}: {event_type}{course_info}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    print("📚 Starting calendar data import...")
    success = import_calendar_data()
    if success:
        print("\n🎉 Calendar import completed successfully!")
    else:
        print("\n💥 Calendar import failed!")