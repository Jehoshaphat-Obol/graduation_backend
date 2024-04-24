from rest_framework import serializers
from .models import Cluster, Row, StudentProfile, Guest, Seat, SeatAssignment
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password", "email", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True},  # Make password write-only
        }
    def create(Self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


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
    user = UserSerializer()
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
    
    def create(self, validated_data):
        user_data = validated_data.pop("user")
        password = None
        for field, value in user_data.items():
            if(field == 'password'):
                password = value
        user_serializer = UserSerializer(data=user_data)
        if user_serializer.is_valid():
            if password:
                # user_data["password"] = make_password(password)
                pass# Hash the password
            else:
                # Handle the case where password is not provided
                raise serializers.ValidationError("Password is required")

            user = user_serializer.save()
            student_profile = StudentProfile.objects.create(user=user, **validated_data)
            return student_profile
        else:
            raise serializers.ValidationError(user_serializer.errors)


class GuestSerializer(serializers.ModelSerializer):
    student = serializers.CharField(source="student.user.username")

    class Meta:
        model = Guest
        fields = ["id", "student", "name", "type", 'status']
        
    def create(self, validated_data):
        student_username = validated_data.pop('student')
        
        try:
            # Attempt to get the student profile from the database
            student_profile = StudentProfile.objects.get(user__username=student_username['user']['username'])
        except ObjectDoesNotExist:
            # Handle case where the student profile does not exist
            raise serializers.ValidationError("Student profile does not exist.")

        # Create the guest instance with the retrieved student profile and other validated data
        guest = Guest(student=student_profile, **validated_data)
        guest.save()
        return guest
        
        


class SeatAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeatAssignment
        fields = ["id", "student", "seat"]
