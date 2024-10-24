import dlib
import cv2
import numpy as np
from datetime import datetime

# Load the required dlib models
face_detector = dlib.get_frontal_face_detector()
shape_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("dlib_face_recognition_resnet_model_v1.dat")

# Store timestamps for when people first appear
timestamps = {}

def load_image(file_path):
    return dlib.load_rgb_image(file_path)

def get_face_encoding(image):
    faces = face_detector(image)
    if len(faces) == 0:
        return None
    shape = shape_predictor(image, faces[0])
    return np.array(face_rec_model.compute_face_descriptor(image, shape))

def compare_faces(known_face_encoding, face_encoding, tolerance=0.6):
    if face_encoding is None or known_face_encoding is None:
        return False
    return np.linalg.norm(known_face_encoding - face_encoding) <= tolerance

# Load known faces
yan_image = load_image("Images/Yande Chilufya.jpg")
yan_face_encoding = get_face_encoding(yan_image)

muk_image = load_image("Images/Mukuni Hakuyu.jpg")
muk_face_encoding = get_face_encoding(muk_image)

mul_image = load_image("Images/Mulewa Cheyeka.jpg")
mul_face_encoding = get_face_encoding(mul_image)

rita_image = load_image("Images/Rita Tembo.jpg")
rita_face_encoding = get_face_encoding(rita_image)

tee_image = load_image("Images/Taonga Tembo.jpg")
tee_face_encoding = get_face_encoding(tee_image)

mwi_image = load_image("Images/Mwiza.jpg")
mwi_face_encoding = get_face_encoding(mwi_image)

biden_image = load_image("Images/biden.jpg")
biden_face_encoding = get_face_encoding(biden_image)

known_face_encodings = [
    yan_face_encoding, mul_face_encoding, rita_face_encoding, mwi_face_encoding, tee_face_encoding, muk_face_encoding, biden_face_encoding
]
known_face_names = [
    "Yande Chilufya", "Rita Tembo", "Mulewa Cheyeka", "Mukuni Hakuyu", "Taonga Tembo", "Mwiza", "Biden"
]

# Initialize video capture
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Invert the video frame (mirror effect)
    frame = cv2.flip(frame, 1)

    # Convert the image from BGR color (OpenCV) to RGB color (dlib)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces in the frame
    faces = face_detector(rgb_frame)

    for face in faces:
        shape = shape_predictor(rgb_frame, face)
        face_encoding = np.array(face_rec_model.compute_face_descriptor(rgb_frame, shape))

        name = "Unknown"
        current_time = None
        for i, known_face_encoding in enumerate(known_face_encodings):
            if compare_faces(known_face_encoding, face_encoding):
                name = known_face_names[i]

                # Check if the person already has a timestamp
                if name not in timestamps:
                    timestamps[name] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                current_time = timestamps[name]
                break

        # Draw rectangle around the face
        top, right, bottom, left = face.top(), face.right(), face.bottom(), face.left()
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Display name and first appearance timestamp
        if current_time:
            label = f"{name} {current_time}"
        else:
            label = name

        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, label, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the capture and close the windows
video_capture.release()
cv2.destroyAllWindows()
