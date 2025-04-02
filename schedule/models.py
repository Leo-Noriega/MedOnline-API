from django.db import models
from doctors.models import Doctor

class Weekday(models.IntegerChoices):
    MONDAY = 1, 'Monday'
    TUESDAY = 2, 'Tuesday'
    WEDNESDAY = 3, 'Wednesday'
    THURSDAY = 4, 'Thursday'
    FRIDAY = 5, 'Friday'
    SATURDAY = 6, 'Saturday'
    SUNDAY = 7, 'Sunday'


class Availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities')
    weekday = models.IntegerField(choices=Weekday.choices, blank=False, null=False)
    consultation_time = models.DurationField(blank=False, null=False, help_text="Duration of each consultation in HH:MM:SS format")
    
    def __str__(self):
        return f"Availability for {self.doctor.user.name} on {Weekday(self.weekday).label}"


class DailySchedule(models.Model):
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='daily_schedules')
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)

    def __str__(self):
        return f"Schedule for {self.availability.doctor.user.name} on {Weekday(self.availability.weekday).label} from {self.start_time} to {self.end_time}"