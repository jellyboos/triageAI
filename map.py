import googlemaps
import os
from dotenv import load_dotenv

import geocoder


# Replace with your actual API key
load_dotenv()

API_KEY = os.getenv('MAPS_API_KEY')
if not API_KEY:
    raise ValueError("MAPS_API_KEY not found in environment variables")

# Initialize Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

def get_current_gps_coordinates():
    g = geocoder.ip('me')
    if g.latlng:
        return g.latlng
    else:
        return None



def find_nearest_emergency_rooms(radius=5000, max_results=5):
    """
    Find nearby emergency rooms based on current location.

    Args:
        latitude (float): User's current latitude
        longitude (float): User's current longitude
        radius (int): Search radius in meters
        max_results (int): Max number of emergency rooms to return

    Returns:
        List[str]: Names of nearby emergency rooms
    """
    latitude, longitude = get_current_gps_coordinates()
    location = (latitude, longitude)

    try:
        results = gmaps.places_nearby(
            location=location,
            radius=radius,
            keyword="emergency room",
            type="hospital"
        )

        # Extract and return names of hospitals
        emergency_rooms = [
            {
                'name': place['name'],
                'vicinity': place.get('vicinity', place.get('formatted_address', '')),
                'place_id': place.get('place_id', ''),
                # add more fields if needed
            }
            for place in results.get("results", [])[:max_results]
        ]

        return emergency_rooms

    except Exception as e:
        print(f"Error fetching emergency rooms: {e}")
        return []


if __name__ == "__main__":
    # Example: downtown Los Angeles

    er_list = find_nearest_emergency_rooms()
    print("Nearest Emergency Rooms:")
    for i, name in enumerate(er_list, 1):
        print(f"{i}. {name['name']} - {name['vicinity']}")