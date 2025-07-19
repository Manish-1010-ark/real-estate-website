# seed_properties.py

import sqlite3
import os

# Path to the SQLite DB
DB_PATH = os.path.join('instance', 'real_estate.db')

# Connect and create table if not exists
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Insert 2 new properties
cursor.execute("""
INSERT INTO properties (id, title, description, price, location, area, status, features, images)
VALUES (6, 'Cozy 2BHK Flat in Behala', 'Well-ventilated flat with modern kitchen and balcony.',
        4800000, 'Behala, Kolkata', 950, 'Available',
        '2 BHK,1 Bath,Balcony,Modular Kitchen', 'property6.jpg')
""")

cursor.execute("""
INSERT INTO properties (id, title, description, price, location, area, status, features, images)
VALUES (7, 'Duplex Penthouse in Rajarhat', 'Two-level penthouse with rooftop garden and city views.',
        13000000, 'Rajarhat, Kolkata', 2700, 'Available',
        '4 BHK,3 Baths,Rooftop Garden,Duplex Design', 'property7.jpg,property7b.jpg')
""")

conn.commit()
conn.close()

print("✅ Seeded 2 new properties into real_estate.db")
