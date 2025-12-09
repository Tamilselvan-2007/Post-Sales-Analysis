import sqlite3

conn = sqlite3.connect('voltage_data.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS voltage_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voltage REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("Database created!")
