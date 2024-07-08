import sqlite3
conn = sqlite3.connect('../data/traffic_video.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT * FROM traffic_video
''')
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()