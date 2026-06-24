import os
import sys
import numpy as np
import tensorflow as tf
from PIL import Image

def predict_crop_disease(image_path, model_path="plant_disease_model.keras", class_names_path="class_names.txt"):
    # 1. Verify file existence
    if not os.path.exists(image_path):
        print(f"[ERROR] Image file '{image_path}' not found.")
        return None, None
        
    if not os.path.exists(model_path):
        print(f"[ERROR] Model file '{model_path}' not found. Please train the model first.")
        return None, None
        
    if not os.path.exists(class_names_path):
        print(f"[ERROR] Class names file '{class_names_path}' not found.")
        return None, None

    # 2. Load the class names mapping
    with open(class_names_path, "r") as f:
        class_names = [line.strip() for line in f.read().splitlines() if line.strip()]

    # 3. Load the trained Keras model
    print(f"Loading trained model from '{model_path}'...")
    model = tf.keras.models.load_model(model_path)

    # 4. Load and preprocess the image
    print(f"Preprocessing image '{image_path}'...")
    # Open image and convert to RGB (discarding alpha channel if present)
    img = Image.open(image_path).convert("RGB")
    # Resize image to target dimension (224x224)
    img_resized = img.resize((224, 224))
    # Convert image to numpy array
    img_array = np.array(img_resized).astype(np.float32)
    # Expand dimensions to create batch size of 1 -> (1, 224, 224, 3)
    img_tensor = np.expand_dims(img_array, axis=0)

    # NOTE: BUG FIX (Phase 5)
    # We do NOT call tf.keras.applications.mobilenet_v2.preprocess_input() here.
    # The normalization layers (Rescaling x/127.5 - 1.0) are already built inside the keras model.
    # Preprocessing here would cause a "double preprocessing" bug, making predictions inaccurate.

    # 5. Predict the class
    print("Running model prediction inference...")
    predictions = model.predict(img_tensor, verbose=0)
    
    # 6. Extract predictions results
    predicted_idx = np.argmax(predictions[0])
    confidence_score = float(predictions[0][predicted_idx]) * 100
    predicted_class = class_names[predicted_idx]

    return predicted_class, confidence_score

if __name__ == "__main__":
    # Check if image path is provided via command-line arguments
    if len(sys.argv) < 2:
        print("\n[Usage] python predict.py <path_to_image>")
        print("Example: python predict.py uploads/test_leaf.jpg\n")
        sys.exit(1)
        
    target_image = sys.argv[1]
    cls, conf = predict_crop_disease(target_image)
    
    if cls is not None:
        print("\n=============================================")
        print("          Inference Diagnosis Result         ")
        print("=============================================")
        print(f"  Predicted Category: {cls}")
        print(f"  Confidence Rating : {conf:.2f}%")
        print("=============================================\n")
