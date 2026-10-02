# =====================================================
# AidSense - REAL-TIME INJURY DETECTION
# TensorFlow + OpenCV Version
# =====================================================

# =====================================================
# IMPORTS
# =====================================================

import tensorflow as tf
import numpy as np
import cv2

# =====================================================
# LOAD MODEL
# =====================================================

model = tf.keras.models.load_model(
    "model/aidSense_model.h5"
)

print("MODEL LOADED")

# =====================================================
# CLASS LABELS
# =====================================================

classes = [
    "Burn",
    "Cut"
]

# =====================================================
# START CAMERA
# =====================================================

cap = cv2.VideoCapture(0)

print("CAMERA STARTED")

# =====================================================
# PREPROCESS FUNCTION
# =====================================================

def preprocess(frame):

    img = cv2.resize(
        frame,
        (224,224)
    )

    img = img / 255.0

    img = np.expand_dims(
        img,
        axis=0
    )

    return img

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # ================================================
    # PREPROCESS FRAME
    # ================================================

    processed = preprocess(frame)

    # ================================================
    # PREDICT
    # ================================================

    prediction = model.predict(
        processed,
        verbose=0
    )

    index = np.argmax(prediction)

    confidence = float(
        np.max(prediction)
    )

    injury = classes[index]

    confidence_percent = round(
        confidence * 100,
        2
    )

    # ================================================
    # SEVERITY LOGIC
    # ================================================

    if confidence_percent > 85:

        severity = "CRITICAL"

    elif confidence_percent > 60:

        severity = "MEDIUM"

    else:

        severity = "LOW"

    # ================================================
    # DISPLAY TEXT
    # ================================================

    text = f"{injury} | {confidence_percent}% | {severity}"

    cv2.putText(

        frame,

        text,

        (20,40),

        cv2.FONT_HERSHEY_SIMPLEX,

        1,

        (0,255,0),

        2

    )

    # ================================================
    # SHOW CAMERA WINDOW
    # ================================================

    cv2.imshow(

        "AidSense Real-Time Detection",

        frame

    )

    # ================================================
    # PRESS Q TO EXIT
    # ================================================

    if cv2.waitKey(1) & 0xFF == ord('q'):

        break

# =====================================================
# RELEASE CAMERA
# =====================================================

cap.release()

cv2.destroyAllWindows()
