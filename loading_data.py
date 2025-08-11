import sqlite3
import pandas as pd
from pathlib import Path

def create_database_schema(db_path="database.db"):
    """
    Create the database schema based on the Excel file columns
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop table if it exists to recreate with fresh data
    cursor.execute("DROP TABLE IF EXISTS french_words")
    
    # Create table with appropriate schema
    create_table_query = """
    CREATE TABLE french_words (
        sub_question_id TEXT PRIMARY KEY,
        nom TEXT NOT NULL,
        genre_du_nom TEXT NOT NULL,
        niveau_de_difficulte INTEGER NOT NULL,
        exemple_usage_courant TEXT,
        exemple_usage_litteraire TEXT,
        exemple_usage_universitaire TEXT,
        terminaisons TEXT
    )
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()
    print("Database schema created successfully!")

def load_excel_to_database(excel_file_path, db_path="database.db"):
    """
    Load Excel file data into the SQLite database
    """
    try:
        # Read Excel file
        df = pd.read_excel(excel_file_path)
        
        # Clean column names (remove spaces, convert to lowercase with underscores)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('é', 'e').str.replace('è', 'e')
        
        # Rename columns to match our schema
        column_mapping = {
            'sub-question_id': 'sub_question_id',
            'sub_question_id': 'sub_question_id',
            'nom': 'nom',
            'genre_du_nom': 'genre_du_nom', 
            'niveau_de_difficulte': 'niveau_de_difficulte',
            'exemple_usage_courant': 'exemple_usage_courant',
            'exemple_usage_litteraire': 'exemple_usage_litteraire',
            'exemple_usage_universitaire': 'exemple_usage_universitaire',
            'terminaisons': 'terminaisons'
        }
        
        # Apply column mapping if columns exist
        existing_columns = df.columns.tolist()
        for old_name, new_name in column_mapping.items():
            if old_name in existing_columns:
                df.rename(columns={old_name: new_name}, inplace=True)
        
        print(f"Excel file columns: {df.columns.tolist()}")
        print(f"Data shape: {df.shape}")
        
        # Connect to database and insert data
        conn = sqlite3.connect(db_path)
        
        # Insert data into the table
        df.to_sql('french_words', conn, if_exists='replace', index=False)
        
        conn.close()
        print(f"Successfully loaded {len(df)} records into the database!")
        
        return df
        
    except Exception as e:
        print(f"Error loading Excel file: {str(e)}")
        return None

def create_sample_data(db_path="database.db"):
    """
    Create sample data based on the provided examples
    """
    sample_data = [
        ("QAG1-1", "soleil", "masculin", 3, "Un soleil radieux brille dans le ciel", 
         "Le soleil, ce dieu d'or, s'endort dans son royaume pourpre", 
         "L'imagerie solaire dans la poésie romantique française", 
         "-eil (exception car mots en -eil peuvent être féminins comme abeille)"),
        
        ("QAG1-2", "amour", "masculin", 3, "Un grand amour de jeunesse", 
         "Les amours défuntes hantent ses vers (usage poétique au féminin)", 
         "L'amour courtois dans la littérature médiévale", "exception"),
        
        ("QAG1-3", "mer", "féminin", 3, "La mer est agitée aujourd'hui", 
         "La mer, la grande mer consolatrice (Baudelaire)", 
         "La symbolique de la mer dans l'œuvre de Victor Hugo", "exception"),
        
        ("QAG1-4", "automne", "masculin", 3, "Un automne pluvieux", 
         "L'automne languissant berçait leur rêverie", 
         "L'imaginaire de l'automne dans la poésie symboliste", "ambigu"),
        
        ("QAG1-5", "orchidée", "féminin", 1, "Une belle orchidée blanche", 
         "L'orchidée sauvage parsemait la forêt", 
         "Taxonomie des orchidées tropicales", "typiquement féminin"),
        
        ("QAG1-6", "pétale", "masculin", 3, "Un pétale de rose", 
         "Les pétales embaumés tombaient en pluie", 
         "Morphologie du pétale dans les angiospermes", "ambigu")
    ]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert sample data
    insert_query = """
    INSERT INTO french_words 
    (sub_question_id, nom, genre_du_nom, niveau_de_difficulte, 
     exemple_usage_courant, exemple_usage_litteraire, exemple_usage_universitaire, terminaisons)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    cursor.executemany(insert_query, sample_data)
    conn.commit()
    conn.close()
    
    print(f"Successfully inserted {len(sample_data)} sample records!")

def query_database(db_path="database.db"):
    """
    Query the database to verify data was loaded correctly
    """
    conn = sqlite3.connect(db_path)
    
    # Get all records
    df = pd.read_sql_query("SELECT * FROM french_words", conn)
    
    print("\nDatabase contents:")
    print(df.to_string(index=False))
    
    # Get some statistics
    print(f"\nTotal records: {len(df)}")
    print(f"Unique genres: {df['genre_du_nom'].unique()}")
    print(f"Difficulty levels: {sorted(df['niveau_de_difficulte'].unique())}")
    
    conn.close()
    return df

def main():
    """
    Main function to execute the database creation and data loading
    """
    db_path = "database.db"
    
    print("Step 1: Creating database schema...")
    create_database_schema(db_path)
    
    print("\nStep 2: Loading sample data...")
    create_sample_data(db_path)
    
    print("\nStep 3: Verifying data...")
    query_database(db_path)
    
    print(f"\nDatabase '{db_path}' has been created successfully!")
    print("\nTo load your own Excel file, use:")
    print("load_excel_to_database('your_file.xlsx')")

if __name__ == "__main__":
    main()
