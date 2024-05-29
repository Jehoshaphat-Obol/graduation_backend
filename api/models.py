from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
class Cluster(models.Model):
    name = models.CharField(max_length=100)
    # You might want to add additional fields like location or capacity
    
    def __str__(self):
        return self.name

class Row(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    number_of_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cluster}-R{self.pk}"

class Seat(models.Model):
    row =models.ForeignKey(Row, on_delete=models.CASCADE)
    seat_number = models.PositiveIntegerField()
    ticket = models.CharField(max_length=250, default="")
    
    def __str__(self):
        return f"{self.ticket}"
    
    class Meta:
        ordering = ['row', 'seat_number']
        unique_together = ['row', 'seat_number'] # the same seat number can't re-occur on the same row

class StudentProfile(models.Model):
    class Status(models.TextChoices):
        EXPECTED = 'EX', 'Expected'
        POSTPONED = 'PP', 'Postponed'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    graduation_status = models.CharField(max_length=2, default=Status.EXPECTED, choices=Status.choices)
    degree_program = models.CharField(max_length=100)
    degree_level = models.CharField(max_length=100)
    college = models.CharField(max_length=100)
    
    # Add more fields as needed
    
    def __str__(self):
        return self.user.username

class Guest(models.Model):
    class Type(models.TextChoices):
        PARENT = 'PRT', 'Parent'
        VIP = 'VIP', 'VIP'

    class Status(models.TextChoices):
        EXPECTED = 'EX', 'Expected'
        POSTPONED = 'PP', 'Postponed'
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, default=None, blank=True, null=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=3, default=Type.PARENT, choices=Type.choices)
    status = models.CharField(max_length=2, default=Status.EXPECTED, choices=Status.choices)

    def save(self, *args, **kwargs):
        if self.student:
            guest_count = Guest.objects.filter(student=self.student).count()
            
            if self.pk:
                guest_count -= 1
            if guest_count >= 2:
                raise ValidationError(f"The student {self.student} can not have more than 2 guests")
            
        super().save(*args, **kwargs)
    # Add more fields as needed


    def __str__(self):
        return self.name

class SeatAssignment(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, blank=True,  null=True)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    # Add more fields like seat number if needed
    
    def __str__(self):
        return f"{self.user}"
    
    class Meta:
        unique_together = ['user', 'seat']
    

class Timetable(models.Model):
    event_name = models.CharField(max_length=100)
    event_description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.event_name
    
    class Meta:
        ordering = ['-start_time']