import sqlite3
import csv

# Path to your DB
conn = sqlite3.connect('real_estate.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

with open('users_export.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    # Write headers (adjust if you have different fields)
    writer.writerow([col[0] for col in cursor.description])
    writer.writerows(rows)

conn.close()
print("✅ Exported to users_export.csv")
