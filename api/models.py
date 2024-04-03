from django.db import models
from django.contrib.auth.models import User

class Cluster(models.Model):
    name = models.CharField(max_length=100)
    # You might want to add additional fields like location or capacity
    
    def __str__(self):
        return self.name

class Row(models.Model):
    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)
    number_of_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"Row {self.pk} in {self.cluster}"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    graduation_status = models.BooleanField(default=False)
    degree_program = models.CharField(max_length=100)
    degree_level = models.CharField(max_length=100)
    college = models.CharField(max_length=100)
    # Add more fields as needed
    
    def __str__(self):
        return self.user.username

class Guest(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    # Add more fields as needed
    
    def __str__(self):
        return self.name

class SeatAssignment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    row = models.ForeignKey(Row, on_delete=models.CASCADE)
    # Add more fields like seat number if needed
    
    def __str__(self):
        return f"{self.student} seated at {self.row}"