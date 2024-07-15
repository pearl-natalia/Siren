import sqlite3

def create_database(tablename):
    #creating a database
    conn = sqlite3.connect('../data/'+tablename+'.db')
    cursor = conn.cursor()
    cursor.execute(f''' 
        CREATE TABLE IF NOT EXISTS "{tablename}" (
        id INTEGER PRIMARY KEY,
        real_time TEXT,
        
        video_timestamp TEXT,
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


def create_new_row(tablename, field, value):
    conn = sqlite3.connect('../data/'+tablename+'.db')
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO "{tablename}" ({field})
        VALUES (?)
    ''', (value,))
    conn.commit()
    conn.close()


def update_row_database(field, value, record_id, tablename):
    conn = sqlite3.connect('../data/'+tablename+'.db')
    cursor = conn.cursor()
    cursor.execute(f'''
        UPDATE "{tablename}"
        SET {field} = ?
        WHERE id = ?
    ''', (value, record_id))
    conn.commit()
    conn.close()

def get_database_value(tablename, index, field):
    conn = sqlite3.connect('../data/'+tablename+'.db')
    cursor = conn.cursor()
    cursor.execute(f'''SELECT COUNT(*) FROM "{tablename}" ''')
    count = cursor.fetchone()[0]
    id = count + index + 1
    cursor.execute(f'''SELECT {field} FROM "{tablename}" WHERE id={id}''')
    value = cursor.fetchone()
    cursor.close()
    conn.close()
    return value

def get_database_length(tablename):
    conn = sqlite3.connect('../data/'+tablename+'.db')
    cursor = conn.cursor()
    cursor.execute(f'''SELECT COUNT(*) FROM "{tablename}" ''')
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count

