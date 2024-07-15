import sqlite3, argparse

parser = argparse.ArgumentParser()
parser.add_argument("database_name", type=str)
args = parser.parse_args()
filename = args.database_name

conn = sqlite3.connect('../data/'+filename+'.db')
cursor = conn.cursor()
cursor.execute(f'''
    SELECT * FROM "{filename}"
''')
rows = cursor.fetchall()
for row in rows:
    print(row)

# Close the connection
conn.close()