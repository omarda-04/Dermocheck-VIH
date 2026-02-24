import os
import numpy as np
import tensorflow as tf
import base64
from django.shortcuts import render
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from PIL import Image
from io import BytesIO

IMG_WIDTH, IMG_HEIGHT = 150, 150

MODEL_PATH = os.path.join("C:/Users/Omar Gaitan/Documents/Proyectos/Practica3/modelo_entrenado/Modelo_VIH.keras")
model = tf.keras.models.load_model(MODEL_PATH)

def predict_vih(request):
    predictions = []
    fs = FileSystemStorage()

    if request.method == 'POST':
        processed_images = []
        image_urls = []

        # Opción 1: Se envió como archivo (desde input file tradicional)
        if request.FILES.getlist('images'):
            uploaded_images = request.FILES.getlist('images')
            for uploaded_image in uploaded_images:
                filename = fs.save(uploaded_image.name, uploaded_image)
                image_path = fs.path(filename)
                image_url = fs.url(filename)
                image_urls.append(image_url)

                img = load_img(image_path, target_size=(IMG_WIDTH, IMG_HEIGHT))
                img_array = img_to_array(img) / 255.0
                processed_images.append(img_array)

        # Opción 2: Se envió una imagen base64 desde la cámara
        elif 'image_data' in request.POST:
            image_data = request.POST['image_data']
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='camera_image.' + ext)
            image_path = fs.save(data.name, data)
            image_url = fs.url(image_path)
            image_urls.append(image_url)

            # Cargar imagen en memoria para análisis
            img = Image.open(data)
            img = img.resize((IMG_WIDTH, IMG_HEIGHT))
            img_array = img_to_array(img) / 255.0
            processed_images.append(img_array)

        if processed_images:
            processed_images = np.array(processed_images)
            raw_predictions = model.predict(processed_images)
                
            for i, prediction in enumerate(raw_predictions):
                percentage = prediction[0] * 100
                print(percentage)
                if percentage >= 75:
                    mensaje = "Muy probable infección cutánea por VIH"
                    color = "#dc3545"  # Rojo
                elif percentage >= 65:
                    mensaje = "probable infección cutánea por VIH regular, asistir a centro medico"
                    color = "#ffc107"  # Amarillo
                else:
                    mensaje = "No se detecta indicios de infección cutánea por VIH"
                    color = "#28a745"  # Verde

                predictions.append({
                    'image_url': image_urls[i],
                    'percentage': f"{percentage:.2f}%",
                    'mensaje': mensaje,
                    'color': color
                })

    return render(request, 'predict_vih.html', {'predictions': predictions})

def home(request):
    return render(request, 'home.html')
