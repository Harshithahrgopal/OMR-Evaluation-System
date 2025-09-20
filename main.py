from src.model import create_model, train_model
from src.evaluate import evaluate_sheet
import tensorflow as tf

# Train a new model
model = create_model()
model = train_model(model, epochs=10)
model.save('trained_models/omr_model.h5')

# Evaluate a sheet
model = tf.keras.models.load_model('trained_models/omr_model.h5')
results = evaluate_sheet('data/sheets/sheet1.jpg', model)
print(results)
