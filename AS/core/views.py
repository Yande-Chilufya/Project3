from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from core.db_setup import SessionLocal
from core.models import User, FaceEncoding
from django.contrib.auth.hashers import check_password, make_password
from core.recognition.registration import register_user_logic, create_user_directory


# Utility function to get SQLAlchemy session
def get_db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# Handle user registration (calls the registration logic from registration.py)
@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # Create a new SQLAlchemy session
        session = next(get_db())
        
        # Call the registration logic and pass the session to handle database interactions
        response = register_user_logic(data, session)  
        
        return JsonResponse(response, status=response.get('status', 200))

    return JsonResponse({'error': 'Invalid method'}, status=405)


# Handle user login
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        computer_number = data.get('computer_number')
        password = data.get('password')

        # Create a new SQLAlchemy session
        session = next(get_db())

        try:
            # Query user using SQLAlchemy instead of Django ORM
            user = session.query(User).filter_by(computer_number=computer_number).first()

            if user:
                # Check if the password is correct
                if check_password(password, user.password):
                    return JsonResponse({'message': 'Login successful', 'user_id': user.id}, status=200)
                else:
                    return JsonResponse({'error': 'Incorrect password'}, status=400)
            else:
                return JsonResponse({'error': 'User not found'}, status=404)

        finally:
            session.close()

    return JsonResponse({'error': 'Invalid method'}, status=405)


# Handle storing face encodings
@csrf_exempt
def store_face_encoding(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        encoding = data.get('encoding')  # Assume this is a string or base64 encoding

        # Create a new SQLAlchemy session
        session = next(get_db())

        try:
            # Query the user using SQLAlchemy
            user = session.query(User).filter_by(id=user_id).first()

            if user:
                # Save face encoding to the database using SQLAlchemy
                face_encoding = FaceEncoding(user_id=user_id, encoding=encoding)
                session.add(face_encoding)
                session.commit()

                # Save encoding to the user's directory
                user_directory = Path(f"face_encodings/{user_id}")
                if not user_directory.exists():
                    return JsonResponse({'error': 'User directory does not exist'}, status=500)

                encoding_file = user_directory / f"{uuid.uuid4()}.txt"
                with open(encoding_file, 'w') as file:
                    file.write(encoding)

                return JsonResponse({'message': 'Face encoding stored successfully'}, status=201)

            else:
                return JsonResponse({'error': 'User not found'}, status=404)

        finally:
            session.close()

    return JsonResponse({'error': 'Invalid method'}, status=405)
