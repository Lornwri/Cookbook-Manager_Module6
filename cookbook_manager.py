import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection"""
    conn = None
    try:
        conn = sqlite3.connect('hipster_cookbooks.db')
        print(f"Successfully connected to SQLite {sqlite3.version}")
        return conn
    except Error as e:
        print(f"Error establishing connection: {e}")
        return None

def create_tables(conn):
    """Create tables for cookbooks, tags, and borrowing history"""
    try:
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cookbooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year_published INTEGER,
            aesthetic_rating INTEGER,
            instagram_worthy BOOLEAN,
            cover_color TEXT
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cookbook_tags (
            cookbook_id INTEGER,
            tag_id INTEGER,
            FOREIGN KEY (cookbook_id) REFERENCES cookbooks(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id),
            PRIMARY KEY (cookbook_id, tag_id)
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrowed_cookbooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cookbook_id INTEGER,
            friend_name TEXT NOT NULL,
            date_borrowed TEXT NOT NULL,
            return_date TEXT,
            FOREIGN KEY (cookbook_id) REFERENCES cookbooks(id)
        );
        """)
        
        conn.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")

def insert_cookbook(conn, cookbook):
    """Insert a new cookbook"""
    try:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO cookbooks (title, author, year_published, aesthetic_rating, instagram_worthy, cover_color)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', cookbook)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        print(f"Error inserting cookbook: {e}")
        return None

def add_recipe_tags(conn, cookbook_id, tags):
    """Add tags to a cookbook"""
    try:
        cursor = conn.cursor()
        for tag in tags:
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
            cursor.execute("""
            INSERT INTO cookbook_tags (cookbook_id, tag_id)
            SELECT ?, id FROM tags WHERE name = ?
            """, (cookbook_id, tag))
        conn.commit()
        print(f"Tags {tags} added to cookbook ID {cookbook_id}")
    except Error as e:
        print(f"Error adding tags: {e}")

def track_borrowed_cookbook(conn, cookbook_id, friend_name, date_borrowed):
    """Track borrowed cookbook"""
    try:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO borrowed_cookbooks (cookbook_id, friend_name, date_borrowed)
        VALUES (?, ?, ?)
        ''', (cookbook_id, friend_name, date_borrowed))
        conn.commit()
        print(f"Cookbook ID {cookbook_id} borrowed by {friend_name} on {date_borrowed}")
    except Error as e:
        print(f"Error tracking borrowed cookbook: {e}")

def get_all_cookbooks(conn):
    """Retrieve all cookbooks"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cookbooks")
        books = cursor.fetchall()
        for book in books:
            print(f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Year: {book[3]}, Rating: {book[4]}, Cover: {book[6]}")
        return books
    except Error as e:
        print(f"Error retrieving cookbooks: {e}")
        return []

def main():
    conn = create_connection()
    if conn:
        create_tables(conn)
        
        # Insert sample cookbooks
        cookbook1 = ('Foraged & Found', 'Oak Wavelength', 2023, 5, True, 'Forest Green')
        cookbook2 = ('The Artistic Toast', 'River Wildflower', 2023, 5, True, 'Recycled Brown')
        
        id1 = insert_cookbook(conn, cookbook1)
        id2 = insert_cookbook(conn, cookbook2)
        
        # Add tags
        if id1:
            add_recipe_tags(conn, id1, ['gluten-free', 'foraging'])
        if id2:
            add_recipe_tags(conn, id2, ['avocado', 'photogenic'])
        
        # Track borrowing
        if id1:
            track_borrowed_cookbook(conn, id1, 'Alice', '2025-02-25')
        
        # Show cookbooks
        print("\nCookbook Collection:")
        get_all_cookbooks(conn)
        
        conn.close()

if __name__ == '__main__':
    main()
