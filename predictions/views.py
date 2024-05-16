from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .utils import get_predicted_value, helper, symptoms_dict
from django.db import transaction
from django.http import JsonResponse

import json
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class SymptomsList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"symptoms": list(symptoms_dict.keys())})


class Predict(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            # Assuming the symptoms are sent in the request body as a comma-separated string
            symptoms = request.data.get("symptoms", "")
            if not symptoms:
                raise ValueError("No symptoms provided in the request data.")

            user_symptoms = [s.strip() for s in symptoms.split(',')]

            # Predict the disease based on user symptoms
            predicted_disease = get_predicted_value(user_symptoms)

            if not predicted_disease:
                raise ValueError("Could not predict disease based on provided symptoms.")

            # Get details of the predicted disease
            desc, pre, med, die, workout = helper(predicted_disease)

            response_data = {
                "predicted_disease": predicted_disease,
                "description": f"{desc}",
                "precautions": [x for x in pre],
                "medications": med[0][1:-1].split(","), # remove [] then convert the string into array
                "workout": workout[0][1:-1].split(","),
                "diets": die[0][1:-1].split(",")
            }
            logger.info(f"Response Data: {response_data}")

            return JsonResponse(response_data, status=200)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return JsonResponse({"error": str(e)}, status=500)
