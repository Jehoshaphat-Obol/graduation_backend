from rest_framework import serializers
from .models import Cluster, Row, StudentProfile, Guest, Seat, SeatAssignment
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ["id", "name"]
        



class RowSerializer(serializers.ModelSerializer):
    cluster = ClusterSerializer()
    class Meta:
        model = Row
        fields = ["id", "cluster", "number_of_seats"]


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "row", "seat_number"]


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nesting User serializer

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "user",
            "graduation_status",
            "degree_program",
            "degree_level",
            "college",
        ]


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ["id", "student", "name"]


class SeatAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatAssignment
        fields = ["id", "student", "seat"]
