import sqlite3

def create_database(filename):
    conn = sqlite3.connect("/Users/pearlnatalia/Desktop/car/data/" + filename + ".db")
    cursor = conn.cursor()
    cursor.execute(f''' 
        CREATE TABLE IF NOT EXISTS {filename} (
        id INTEGER PRIMARY KEY,
        
        video_timestamp TEXT,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        coordinates TEXT,
        street TEXT,
       
        stop_signs BOOLEAN DEFAULT 0,
        ran_stop_sign BOOLEAN DEFAULT 0,
        
        traffic_colours TEXT,
        red_light_camera TEXT,
        ran_red_light BOOLEAN DEFAULT 0,
        
        speed DEFAULT 0,
        speed_limit DEFAULT 0,
        is_speeding BOOLEAN DEFAULT 0

        turn BOOLEAN DEFAULT 0,
        illegal_turn BOOLEAN DEFAULT 0,

        acceleration DEFAULT 0,
        crash BOOLEAN DEFAULT 0,

        fines TEXT DEFAULT 'none'

        )''')
    conn.commit()
    conn.close()


def insert_in_database(path, field, value, table):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO {table} ({field})
        VALUES (?)
    ''', (value,))
    conn.commit()
    conn.close()


def update_database(path, field, value, record_id, table):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE {table} 
        SET {field} = ?
        WHERE id = ?
    ''', (value, record_id))
    conn.commit()
    conn.close()