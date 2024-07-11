import sqlite3
conn = sqlite3.connect('../data/07_10_2024_20_52_20.db')
cursor = conn.cursor()
cursor.execute('''
    SELECT * FROM '07_10_2024_20_52_20'
''')
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()