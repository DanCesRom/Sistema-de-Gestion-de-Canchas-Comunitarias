import os
import django
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_reservas.settings')

django.setup()

from django.contrib.auth.models import User
from main.models import UserProfile
from datetime import date

def create_users():
    users_data = [
        {
            "email": "jane@example.com",
            "username": "jane",
            "password": "Test1234!",
            "first_name": "Jane",
            "last_name": "Doe",
            "dob": date(1995, 5, 20),
            "gender": "F"
        },
        {
            "email": "john@example.com",
            "username": "john",
            "password": "Test1234!",
            "first_name": "John",
            "last_name": "Smith",
            "dob": date(1990, 1, 15),
            "gender": "M"
        }
    ]

    for user_data in users_data:
        if User.objects.filter(username=user_data["username"]).exists():
            print(f"User {user_data['username']} Este usuario ya Existe.")
            continue

        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"]
        )
        profile = UserProfile.objects.create(
            user=user,
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            date_of_birth=user_data["dob"],
            gender=user_data["gender"]
        )
        print(f"Usuario Creado: {user.username} Con el Correo {user.email}")

if __name__ == "__main__":
    create_users()
