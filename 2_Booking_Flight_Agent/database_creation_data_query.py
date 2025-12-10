import sqlite3
from datetime import datetime

# Correct DB path
db_path = r"D:\LangChain Projects\Multi_Agents_Flight_Intelligence\2_Booking_Flight_Agent\airline.db"

# Create table in the correct DB
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS customer_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone_number TEXT,
    passport_number TEXT,
    date_of_birth TEXT,
    nationality TEXT,
    flight_number TEXT NOT NULL,
    operating_airline TEXT NOT NULL,
    from_city TEXT NOT NULL,
    to_city TEXT NOT NULL,
    departure_datetime TEXT NOT NULL,
    arrival_datetime TEXT NOT NULL,
    seat_number TEXT,
    price_paid REAL,
    booking_date TEXT DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()


# FIXED: always use db_path
def insert_customer_booking(
    first_name, last_name, email, phone_number, passport_number,
    date_of_birth, nationality, flight_number, operating_airline,
    from_city, to_city, departure_datetime, arrival_datetime,
    seat_number, price_paid
):
    conn = sqlite3.connect(db_path)   # <-- FIXED
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO customer_bookings (
            first_name, last_name, email, phone_number, passport_number,
            date_of_birth, nationality, flight_number, operating_airline,
            from_city, to_city, departure_datetime, arrival_datetime,
            seat_number, price_paid
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        first_name, last_name, email, phone_number, passport_number,
        date_of_birth, nationality, flight_number, operating_airline,
        from_city, to_city, departure_datetime, arrival_datetime,
        seat_number, price_paid
    ))

    conn.commit()
    conn.close()

def get_user_info(first_name, last_name, phone_number):
    conn = sqlite3.connect(db_path)   # <-- FIXED
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM customer_bookings
        WHERE first_name = ?
        AND last_name = ?
        AND phone_number = ?
    """, (first_name, last_name, phone_number))

    result = cursor.fetchall()
    conn.close()
    return result


