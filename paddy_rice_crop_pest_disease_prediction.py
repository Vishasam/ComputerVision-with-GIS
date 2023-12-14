# -*- coding: utf-8 -*-
"""Paddy rice crop pest disease prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19zBkG0oYBlZeWxSCXZBR2xuaGB_kSzEX
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install tensorflow keras numpy pandas matplotlib scikit-learn opencv-python

import os
import numpy as np
import cv2
import re
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from keras.utils import to_categorical
from keras.applications import VGG16
from keras.models import Sequential
from keras.layers import Flatten, Dense, Dropout

data_dir = '/content/drive/MyDrive/FarmWise AI/Rice Leaf Disease/rice_leaf_diseases'
label_dict = {'bacterialleafblight': 0, 'brownspot': 1, 'leafsmut': 2}

images = []
labels = []

# Traverse through each disease folder
for disease_folder in os.listdir(data_dir):
    disease_path = os.path.join(data_dir, disease_folder)
    if not os.path.isdir(disease_path):
        continue

    # Clean the folder name and get the label for the current disease folder
    cleaned_disease_folder = re.sub(r'[^a-zA-Z]', '', disease_folder).strip().lower().replace(" ", "")
    label = label_dict[cleaned_disease_folder]

    # Load images from the current disease folder
    for filename in os.listdir(disease_path):
        img_path = os.path.join(disease_path, filename)
        image = cv2.imread(img_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (128, 128))  # Resize the images to a fixed size (adjust as needed)
        images.append(image)
        labels.append(label)

images = np.array(images)
labels = np.array(labels)

# Normalize pixel values to range [0, 1]
images = images.astype('float32') / 255.0

# One-hot encode the labels
labels = to_categorical(labels, num_classes=len(label_dict))

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

# Create a data generator with data augmentation
datagen = ImageDataGenerator(
    rotation_range=20,
    width_shift_range=0.1,
    height_shift_range=0.1,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

# Fit the data generator on the training data
datagen.fit(X_train)

# Load VGG16 pre-trained model without the top (classification) layers
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(128, 128, 3))

# Freeze the base model's layers
for layer in base_model.layers:
    layer.trainable = False

# Add custom classification layers on top of the base model
model = Sequential()
model.add(base_model)
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(label_dict), activation='softmax'))

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
batch_size = 32
epochs = 20
history = model.fit(datagen.flow(X_train, y_train, batch_size=batch_size),
                    steps_per_epoch=len(X_train) // batch_size,
                    epochs=epochs, validation_data=(X_test, y_test))

# Evaluate the model on the test set
loss, accuracy = model.evaluate(X_test, y_test)
print("Test accuracy:", accuracy)

import matplotlib.pyplot as plt

# Make predictions on the test set
y_pred = model.predict(X_test)
predicted_labels = np.argmax(y_pred, axis=1)
true_labels = np.argmax(y_test, axis=1)

# Map numeric labels back to disease names
inv_label_dict = {v: k for k, v in label_dict.items()}
predicted_diseases = [inv_label_dict[label] for label in predicted_labels]
true_diseases = [inv_label_dict[label] for label in true_labels]

# Plot the images along with their true and predicted labels
plt.figure(figsize=(12, 8))
for i in range(10):  # Plot the first 10 images (you can adjust this number as needed)
    plt.subplot(2, 5, i + 1)
    plt.imshow(X_test[i])
    plt.title(f"True: {true_diseases[i]}\nPredicted: {predicted_diseases[i]}", fontsize=10)
    plt.axis('off')

plt.tight_layout()
plt.show()




