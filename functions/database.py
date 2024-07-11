import sqlite3

def create_database(tablename):
    conn = sqlite3.connect("../data/" + tablename + ".db")
    cursor = conn.cursor()
    cursor.execute(f''' 
        CREATE TABLE IF NOT EXISTS "{tablename}" (
        id INTEGER PRIMARY KEY,
        
        video_timestamp TEXT,
        date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        coordinates TEXT,
        street TEXT,
       
        stop_sign BOOLEAN DEFAULT 0,
        ran_stop_sign BOOLEAN DEFAULT 0,
        
        traffic_colours TEXT,
        red_light_camera TEXT,
        ran_red_light BOOLEAN DEFAULT 0,
        
        speed DEFAULT 0,
        speed_limit DEFAULT 0,
        is_speeding BOOLEAN DEFAULT 0,

        turn BOOLEAN DEFAULT 0,
        turn_restriction BOOLEAN DEFAULT 0,

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
        INSERT INTO "{table}" ({field})
        VALUES (?)
    ''', (value,))
    conn.commit()
    conn.close()


def update_database(path, field, value, record_id, table):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE "{table}"
        SET {field} = ?
        WHERE id = ?
    ''', (value, record_id))
    conn.commit()
    conn.close()

def get_database_value(path, table, index, field):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    table_name = table
    cursor.execute(f'''SELECT COUNT(*) FROM "{table_name}" ''')
    count = cursor.fetchone()[0]
    id = count + index + 1
    value = cursor.execute(f'''{field} FROM "{table_name}" WHERE id={id}''')
    cursor.close()
    conn.close()
    return value

def get_database_length(path, table):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    table_name = table
    cursor.execute(f'''SELECT COUNT(*) FROM "{table_name}" ''')
    count = cursor.fetchone()[0]
    return count

