from django.urls import path
from .views import Predict, SymptomsList


urlpatterns = [
    path("symptoms/", SymptomsList.as_view(), name="symptoms"),
    path("predict/", Predict.as_view(), name="predict"),
]
