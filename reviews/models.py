from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient")
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], blank=False, null=False)
    comment = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now_add=True, blank=False, null=False)
    
    def __str__(self):
        return f"Review from {self.user.name} {self.user.surnames} - {self.user.username}"
