import uuid
import os
import dlib
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from django.contrib.auth.hashers import make_password
from core.models import User, FaceEncoding

# Load dlib models
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

# Utility function to create user directory for face encodings
def create_user_directory(user_id):
    user_dir = Path(f"face_encodings/{user_id}")
    if not user_dir.exists():
        user_dir.mkdir(parents=True, exist_ok=True)
        return user_dir
    return None

# Function to get face encoding from an image
def get_face_encoding(image_path):
    image = dlib.load_rgb_image(image_path)
    faces = face_detector(image)
    if len(faces) == 0:
        return None
    shape = shape_predictor(image, faces[0])
    return np.array(face_rec_model.compute_face_descriptor(image, shape))

# Function to handle user registration logic and process face encodings
def register_user_logic(data, image_paths, session: Session):
    # Extract user information from the provided data
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    computer_number = data.get('computer_number')
    age = data.get('age')
    sex = data.get('sex')
    course = data.get('course')
    department = data.get('department')
    password = make_password(data.get('password'))  # Encrypt the password

    # Create user with unique UUID
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        first_name=first_name,
        last_name=last_name,
        computer_number=computer_number,
        age=age,
        sex=sex,
        course=course,
        department=department,
        password=password
    )
    session.add(new_user)
    session.commit()

    # Create a directory for the user to store face encodings
    user_directory = create_user_directory(user_id)

    # Process the images and generate face encodings
    encodings = []
    for image_path in image_paths:
        encoding = get_face_encoding(image_path)
        if encoding is not None:
            encodings.append(encoding)
            # Save encoding to the database
            new_encoding = FaceEncoding(user_id=user_id, encoding=encoding.tolist())
            session.add(new_encoding)

    session.commit()  # Commit all the encodings to the database

    if encodings:
        return {'message': 'User registered and face encodings stored successfully', 'user_id': user_id, 'status': 201}
    else:
        return {'error': 'Face encodings could not be processed', 'status': 500}

