import os
import tensorflow as tf
from tensorflow.keras import layers, models

def create_pipeline_and_train():
    # 1. Configuration & Parameters
    dataset_dir = "PlantVillage/PlantVillage"
    class_names_file = "class_names.txt"
    image_size = (224, 224)
    batch_size = 32
    epochs = 10
    model_save_path = "plant_disease_model.keras"

    print("--- [Step 1: Verify & Load Class Names] ---")
    if not os.path.exists(class_names_file):
        raise FileNotFoundError(f"'{class_names_file}' not found. Please ensure it exists.")
        
    with open(class_names_file, "r") as f:
        class_names = [line.strip() for line in f.read().splitlines() if line.strip()]
    num_classes = len(class_names)
    print(f"Loaded {num_classes} classes: {class_names}")

    print("\n--- [Step 2: Load and Preprocess Datasets] ---")
    # Load training dataset (80% split)
    train_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=image_size,
        batch_size=batch_size,
        class_names=class_names
    )

    # Load validation dataset (20% split)
    val_ds = tf.keras.utils.image_dataset_from_directory(
        dataset_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=image_size,
        batch_size=batch_size,
        class_names=class_names
    )

    # Optimize datasets for execution performance (prefetching)
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    print("\n--- [Step 3: Build MobileNetV2 Transfer Learning Model] ---")
    inputs = tf.keras.Input(shape=(224, 224, 3))
    
    # 3.1 Preprocessing: Rescale images from [0, 255] to [-1, 1] (as expected by MobileNetV2)
    # This compiles into true_divide and subtract layers
    x = layers.Rescaling(1.0 / 127.5, offset=-1.0)(inputs)
    
    # 3.2 Define pre-trained Base Model (weights frozen)
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False
    
    # 3.3 Construct Full Architecture
    x = base_model(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling2d")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout")(x)
    outputs = tf.keras.layers.Dense(num_classes, activation="softmax", name="dense")(x)
    
    model = models.Model(inputs, outputs, name="simple_crop_disease_model")
    model.summary()

    print("\n--- [Step 4: Compile Model] ---")
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    print("\n--- [Step 5: Train & Save Model] ---")
    print(f"Model will train for {epochs} epochs and be saved to '{model_save_path}'.")
    
    # Model training and validation execution
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=epochs
    )
    
    # Save the trained model weights
    model.save(model_save_path)
    print(f"Model saved successfully to '{model_save_path}'!")

if __name__ == "__main__":
    create_pipeline_and_train()
