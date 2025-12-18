import tensorflow as tf
print("TF Version:", tf.__version__)

from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2
model = MobileNetV2(weights='imagenet')
print("Model loaded successfully!")
