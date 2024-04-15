# from accounts.models import User
# from django.db import models
# import uuid
#
#
# class Prediction(models.Model):
#     id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)
#     user = models.ForeignKey(User, related_name="predictions")
#     disease = models.CharField(max_length=255)
#     description = models.TextField()
#     precautions = models.TextField()
#     medications = models.TextField()
#     workouts = models.TextField()
#     diets = models.TextField()
