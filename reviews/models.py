from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from doctors.models import Doctor
from appointments.models import Appointment


class Review(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="appointment_reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient_review")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=False, null=False)
    comment = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    
    def __str__(self):
        return f"Review from {self.user.name} {self.user.surnames} - {self.user.username}"
