import requests

def send_to_n8n(data):
    """
    Sends a Python dictionary as JSON to the specified n8n webhook.
    
    Args:
        data (dict): The data to send to n8n.
    
    Returns:
        dict: Response from the n8n webhook (parsed as JSON if possible).
    """
    url = "http://localhost:5678/webhook/98268ad9-e026-44f4-9612-a5030f1ef890"
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Raises an error if the request failed
        
        # Try to parse JSON response, fallback to text
        try:
            return response.json()
        except ValueError:
            return {"response_text": response.text}
        
    except requests.RequestException as e:
        return {"error": str(e)}

# Example usage:
# data = {
#   "first_name": "Ali",
#   "last_name": "Seena",
#   "email": "ali.seena@example.com",
#   "phone_number": "+92-300-1234567",
#   "passport_number": "AB1234567",
#   "date_of_birth": "2007-05-10",
#   "nationality": "Pakistani",
#   "flight_number": "PK304",
#   "operating_airline": "Pakistan International Airlines",
#   "from_city": "Islamabad",
#   "to_city": "Dubai",
#   "departure_datetime": "2025-12-15 08:30",
#   "arrival_datetime": "2025-12-15 11:45",
#   "seat_number": "12A",
#   "price_paid": "$450"
# }

# data_to_send = data
# result = send_to_n8n(data_to_send)
# print(result)
# 