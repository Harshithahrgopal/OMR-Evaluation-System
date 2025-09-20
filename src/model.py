from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def create_model():
    model = Sequential([
        Conv2D(32, (3,3), activation='relu', input_shape=(28,28,1)),
        MaxPooling2D(2,2),
        Conv2D(64, (3,3), activation='relu'),
        MaxPooling2D(2,2),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_model(model, train_dir='data/train', val_dir='data/test', epochs=10):
    datagen = ImageDataGenerator(rotation_range=5,
                                 brightness_range=[0.8,1.2],
                                 width_shift_range=0.02,
                                 height_shift_range=0.02,
                                 rescale=1./255)
    
    train_gen = datagen.flow_from_directory(train_dir,
                                            target_size=(28,28),
                                            color_mode='grayscale',
                                            class_mode='binary',
                                            batch_size=32)
    
    val_gen = datagen.flow_from_directory(val_dir,
                                          target_size=(28,28),
                                          color_mode='grayscale',
                                          class_mode='binary',
                                          batch_size=32)
    
    model.fit(train_gen, validation_data=val_gen, epochs=epochs)
    return model
