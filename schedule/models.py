from django.db import models
from doctors.models import Doctor
from django.core.validators import MinValueValidator, MaxValueValidator

class Weekday(models.IntegerChoices):
    MONDAY = 1, 'Monday'
    TUESDAY = 2, 'Tuesday'
    WEDNESDAY = 3, 'Wednesday'
    THURSDAY = 4, 'Thursday'
    FRIDAY = 5, 'Friday'
    SATURDAY = 6, 'Saturday'
    SUNDAY = 7, 'Sunday'


class Availability(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availabilities', blank=False, null=False)
    weekday = models.IntegerField(choices=Weekday.choices, blank=False, null=False, validators=[
            MinValueValidator(1, message="El día de la semana debe ser mínimo 1 (Lunes)"),
            MaxValueValidator(7, message="El día de la semana debe ser máximo 7 (Domingo)")
        ])
    
    def __str__(self):
        return f"Availability for {self.doctor.user.name} on {Weekday(self.weekday).label}"

    class Meta:
        db_table = ('schedule_availability'
                    '')


class DailySchedule(models.Model):
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE, related_name='daily_schedules', blank=False, null=False)
    start_time = models.TimeField(blank=False, null=False)
    end_time = models.TimeField(blank=False, null=False)

    class Meta:
        ordering = ['start_time']
        constraints = [
            models.CheckConstraint(
                check=models.Q(start_time__lt=models.F('end_time')),
                name='check_start_time_before_end_time'
            )
        ]

    def __str__(self):
        return f"Schedule for {self.availability.doctor.user.name} on {Weekday(self.availability.weekday).label} from {self.start_time} to {self.end_time}"

    class Meta:
        db_table = 'schedule_dailyschedule'