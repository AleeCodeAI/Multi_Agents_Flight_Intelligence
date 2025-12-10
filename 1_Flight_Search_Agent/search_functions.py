# =================== IMPORTING THE NECESSARY LIBRARY ===================

import sqlite3
import csv 

# =================== MAKING THE DATABASE ===================

# Corrected DB path (raw string to avoid escape issues)
db_path = r"D:\LangChain Projects\Multi_Agents_Flight_Intelligence\1_Flight_Search_Agent\flights.db"

# Connect to SQLite (creates flights.db if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create flights table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS flights (
    flight_number TEXT,
    airline TEXT,
    from_city TEXT,
    to_city TEXT,
    departure_datetime TEXT,
    arrival_datetime TEXT,
    price_economy REAL,
    price_business REAL,
    price_first REAL,
    stops INTEGER,
    duration_minutes INTEGER,
    departure_airport TEXT,
    arrival_airport TEXT,
    baggage_allowance TEXT,
    meal_available TEXT,
    wifi_available TEXT,
    aircraft_type TEXT,
    operating_days TEXT,
    flight_status TEXT
)
""")

# Save changes
conn.commit()

# Open the CSV file
with open(r"D:\LangChain Projects\Multi_Agents_Flight_Intelligence\1_Flight_Search_Agent\flights_dataset.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)  # Read CSV as dictionary

    for row in reader:
        cursor.execute("""
        INSERT INTO flights (
            flight_number, airline, from_city, to_city, departure_datetime, arrival_datetime,
            price_economy, price_business, price_first, stops, duration_minutes,
            departure_airport, arrival_airport, baggage_allowance, meal_available,
            wifi_available, aircraft_type, operating_days, flight_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["flight_number"], row["airline"], row["from_city"], row["to_city"],
            row["departure_datetime"], row["arrival_datetime"], row["price_economy"],
            row["price_business"], row["price_first"], row["stops"], row["duration_minutes"],
            row["departure_airport"], row["arrival_airport"], row["baggage_allowance"],
            row["meal_available"], row["wifi_available"], row["aircraft_type"],
            row["operating_days"], row["flight_status"]
        ))

# Commit changes to database
conn.commit()
conn.close()

# =================== SEARCH FUNCTIONS FOR DIFFERENT COLUMNS ===================

def search_by_flight_number(flight_num):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE flight_number = ?", (flight_num,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_airline(airline):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE airline = ?", (airline,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_from_city(city):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE from_city = ?", (city,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_to_city(city):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE to_city = ?", (city,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_departure_datetime(datetime):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE departure_datetime LIKE ?", (f"%{datetime}%",))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_arrival_datetime(datetime):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE arrival_datetime LIKE ?", (f"%{datetime}%",))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_price_economy(price):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE price_economy <= ?", (price,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_price_business(price):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE price_business <= ?", (price,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_price_first(price):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE price_first <= ?", (price,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_stops(stops):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE stops = ?", (stops,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_duration_minutes(duration):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE duration_minutes <= ?", (duration,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_departure_airport(airport):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE departure_airport = ?", (airport,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_arrival_airport(airport):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE arrival_airport = ?", (airport,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_baggage_allowance(baggage):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE baggage_allowance = ?", (baggage,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_meal_available(meal):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE meal_available = ?", (meal,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_wifi_available(wifi):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE wifi_available = ?", (wifi,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_aircraft_type(aircraft):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE aircraft_type = ?", (aircraft,))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_operating_days(days):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE operating_days LIKE ?", (f"%{days}%",))
    results = cursor.fetchall()
    conn.close()
    return results

def search_by_flight_status(status):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE flight_status = ?", (status,))
    results = cursor.fetchall()
    conn.close()
    return results

# =================== MAIN SEARCH FUNCTION ===================

def display_flights_clean(flights_data):
    if not flights_data:
        return "No flights found matching your criteria."
    
    result = f"\nFLIGHT SEARCH RESULTS ({len(flights_data)} flights found)\n"
    result += "=" * 100 + "\n"
    
    for i, flight in enumerate(flights_data, 1):
        (flight_number, airline, from_city, to_city, departure_datetime, 
         arrival_datetime, price_economy, price_business, price_first, stops, 
         duration_minutes, departure_airport, arrival_airport, baggage_allowance, 
         meal_available, wifi_available, aircraft_type, operating_days, flight_status) = flight
        
        duration_hrs = duration_minutes // 60
        duration_mins = duration_minutes % 60
        
        result += f"""
                    FLIGHT {i}: {flight_number}
                    Airline: {airline}
                    Route: {from_city} -> {to_city}
                    Airports: {departure_airport} to {arrival_airport}
                    Schedule: {departure_datetime} -> {arrival_datetime}
                    Duration: {duration_hrs}h {duration_mins}m | Stops: {stops}
                    Aircraft: {aircraft_type} | Status: {flight_status}
                    Prices - Economy: ${price_economy:.0f} | Business: ${price_business:.0f} | First: ${price_first:.0f}
                    Amenities - Baggage: {baggage_allowance} | Meal: {meal_available} | WiFi: {wifi_available}
                    Operating Days: {operating_days}
                    {'-' * 100}\n"""
    
    return result

def flight_search_router(criteria_dict):
    function_mapper = {
        'flight_number': search_by_flight_number,
        'airline': search_by_airline,
        'from_city': search_by_from_city,
        'to_city': search_by_to_city,
        'departure_datetime': search_by_departure_datetime,
        'arrival_datetime': search_by_arrival_datetime,
        'price_economy': search_by_price_economy,
        'price_business': search_by_price_business,
        'price_first': search_by_price_first,
        'stops': search_by_stops,
        'duration_minutes': search_by_duration_minutes,
        'departure_airport': search_by_departure_airport,
        'arrival_airport': search_by_arrival_airport,
        'baggage_allowance': search_by_baggage_allowance,
        'meal_available': search_by_meal_available,
        'wifi_available': search_by_wifi_available,
        'aircraft_type': search_by_aircraft_type,
        'operating_days': search_by_operating_days,
        'flight_status': search_by_flight_status
    }
    
    results = []
    
    for column, value in criteria_dict.items():
        if column in function_mapper:
            function_results = function_mapper[column](value)
            results.extend(function_results)
    
    unique_results = []
    seen_flight_numbers = set()
    
    for flight in results:
        flight_number = flight[0]
        if flight_number not in seen_flight_numbers:
            seen_flight_numbers.add(flight_number)
            unique_results.append(flight)
    
    data = display_flights_clean(unique_results)
    
    return data

# =================== TESTING THE FUNCTIONALITY ===================

# print("\n\nTEST 2: Search by Airline")
# print("=" * 50)
# print(flight_search_router({"airline": "Emirates"}))
# 