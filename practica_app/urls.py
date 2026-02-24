from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página principal
    path('predict-vih/', views.predict_vih, name='predict_vih'),  # Ruta para la predicción de VIH
]