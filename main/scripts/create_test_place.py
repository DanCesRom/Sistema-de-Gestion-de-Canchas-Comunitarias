import os
import django
import sys
from datetime import time

# Adjust the path to your project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_reservas.settings')

django.setup()

from main.models import Place

def create_places():
    places_data = [
        {
            "name": "Parque Mirador Sur",
            "latitude": 18.44219,
            "longitude": -69.95720,
            "open_time": time(6, 0),      # 6:00 AM
            "close_time": time(20, 0),    # 8:00 PM
            "open_days": "monday,tuesday,wednesday,thursday,friday",
            "description": "Large urban park with walking trails and sports facilities.",
            "image_url": "/static/images/map/mirador_sur.jpg",
            "sport_type": "Cycling and Skating"
        },
        {
            "name": "Estadio Quisqueya",
            "latitude": 18.48851,
            "longitude": -69.92614,
            "open_time": time(9, 0),      # 9:00 AM
            "close_time": time(22, 0),    # 10:00 PM
            "open_days": "monday,tuesday,wednesday,thursday,friday",
            "description": "Baseball stadium hosting local and international games.",
            "image_url": "/static/images/map/estadio_ quisqueya.jpg",
            "sport_type": "Baseball"
        }
        # Add more places here as needed
    ]

    for place_data in places_data:
        if Place.objects.filter(name=place_data["name"]).exists():
            print(f"Place '{place_data['name']}' already exists.")
            continue

        place = Place.objects.create(
            name=place_data["name"],
            latitude=place_data["latitude"],
            longitude=place_data["longitude"],
            open_time=place_data["open_time"],
            close_time=place_data["close_time"],
            open_days=place_data["open_days"],
            description=place_data["description"],
            image_url=place_data["image_url"],
            sport_type=place_data["sport_type"]
        )
        print(f"Created place: {place.name}")

if __name__ == "__main__":
    create_places()
