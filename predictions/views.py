from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .utils import get_predicted_value, helper


class Predict(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Assuming the symptoms are sent in the request body as a comma-separated string
        symptoms = request.data.get("symptoms", "")
        user_symptoms = [s.strip() for s in symptoms.split(',')]

        # Predict the disease based on user symptoms
        predicted_disease = get_predicted_value(user_symptoms)

        # Get details of the predicted disease
        desc, pre, med, die, workout = helper(predicted_disease)

        response_data = {
            "predicted_disease": predicted_disease,
            "description": desc,
            "precautions": pre,
            "medications": med,
            "workout": workout,
            "diets": die
        }

        return Response(response_data)
