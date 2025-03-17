from django.db import models

class Weekday(models.IntegerChoices):
    MONDAY = 1, 'Monday'
    TUESDAY = 2, 'Tuesday'
    WEDNESDAY = 3, 'Wednesday'
    THURSDAY = 4, 'Thursday'
    FRIDAY = 5, 'Friday'
    SATURDAY = 6, 'Saturday'
    SUNDAY = 7, 'Sunday'

class Availability(models.Model):
    doctor = models.ForeignKey('Doctor', on_delete=models.CASCADE, related_name='availabilities')
    weekday = models.IntegerField(choices=Weekday.choices, blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)
    
    def __str__(self):
        return f"Availability from {self.doctor.user.username}"
