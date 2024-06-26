import sqlite3
conn = sqlite3.connect('video_data.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT * FROM video_data
''')
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()