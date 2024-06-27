import os
import sqlite3

directory = '/Users/pearlnatalia/Desktop/car/footage'

# Iterate over all files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".avi"):
        file_path = os.path.join(directory, filename)
        os.remove(file_path)
        print(f"Deleted {filename}")

#database
conn = sqlite3.connect('/Users/pearlnatalia/Desktop/car/video_data.db')
cursor = conn.cursor()

cursor.execute('DELETE FROM video_data')
cursor.execute('UPDATE video_data SET id = id - 1 WHERE id > 1;')

conn.commit()
conn.close()