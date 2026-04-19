from tensorflow.keras.models import load_model

# Load the model
model = load_model("plant_model.h5")

# Print summary
model.summary()
