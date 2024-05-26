from rest_framework import serializers
from .models import Cluster, Row, StudentProfile, Guest, Seat, SeatAssignment, Timetable
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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


class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Extract only the time part of the datetime fields
        representation['start_time'] = instance.start_time.strftime('%H:%M:%S')
        representation['end_time'] = instance.end_time.strftime('%H:%M:%S')
        return representation

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ["id", "row", "seat_number", "ticket"]


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
    user = UserSerializer()
    print("processing")
    class Meta:
        model = Guest
        fields = ["id" ,"user", "student", "name", "type", 'status']
        
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        
        for key, value in user_data.items():
            if(key == 'password'):
                password = value
                
        user_serializer = UserSerializer(data=user_data)
        
        if user_serializer.is_valid():
            student_username = validated_data.pop('student')
            if password:
                try:
                    # Attempt to get the student profile from the database
                    student_profile = StudentProfile.objects.get(user__username=student_username['user']['username'])
                except ObjectDoesNotExist:
                    # Handle case where the student profile does not exist
                    raise serializers.ValidationError("Student profile does not exist.")
                        # Create the guest instance with the retrieved student profile and other validated data
                
                user =user_serializer.save()
                guest = Guest(student=student_profile,user=user, **validated_data)
                guest.save()
                return guest
            else:
                raise serializers.ValidationError("Password is required")
        else:
            raise serializers.ValidationError(user_serializer.errors)
            
        
        


class SeatingPlanSerializer(serializers.ModelSerializer):
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = SeatAssignment
        fields = ['user_details']

    def get_user_details(self, obj):
        user = obj.user
        if hasattr(user, 'guest'):  # Check if the user is a guest
            guest = user.guest
            if guest.get_status_display() ==  "Expected":
                return {
                    'type': 'guest',
                    'name': guest.name,
                    'guest_type': guest.get_type_display(),  # Get display value of the 'type' field
                    'status': guest.status,  # Get display value of the 'status' field
                    'ticket': obj.seat.ticket,
                    'student': guest.student.user.username or "",
                    'username': user.username,
                }
        elif hasattr(user, 'studentprofile'):  # Check if the user is a student
            student_profile = user.studentprofile
            if student_profile.graduation_status== "EX":
                return {
                    'type': 'student',
                    'name': user.first_name +" " +  user.last_name,
                    'status': student_profile.graduation_status,
                    'ticket': obj.seat.ticket,
                    'student': user.username,
                    'username': user.username,
                    'degree_program': student_profile.degree_program,
                    'degree_level': student_profile.degree_level,
                    'college': student_profile.college,
                }
        else:
            return None  # Handle case where user type is not recognized

class SeatAssignmentSerializer(serializers.Serializer):
    username = serializers.CharField()
    ticket = serializers.CharField()

    def create(self, validated_data):
        username = validated_data.pop('username')
        ticket = validated_data.pop('ticket')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")

        try:
            seat = Seat.objects.get(ticket=ticket)
        except Seat.DoesNotExist:
            raise serializers.ValidationError("Seat does not exist")

        seat_assignment = SeatAssignment.objects.create(user=user, seat=seat)
        return seat_assignment
    def update(self, instance, validated_data):
        username = validated_data.pop('username')
        ticket = validated_data.pop('ticket')
        if not username:
            raise serializers.ValidationError("Username is required for update")
        
        if not ticket:
            raise serializers.ValidationError("Ticket is required for update")

        try:
            user = User.objects.get(username=username)
            try:
                seat = Seat.objects.get(ticket=ticket)
                instance.user = user
                instance.seat = seat
                instance.save()
                return instance
            except Seat.DoesNotExist:
                raise serializers.ValidationError("Seat does not exit")
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist")
    
        return instance

    def delete(self, instance):
        instance.delete()

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.user.username,
            'ticket': instance.seat.ticket,
            'seat_number': instance.seat.seat_number
        }

class UnassignedStudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'graduation_status', 'degree_program', 'degree_level', 'college']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Check if the student has a seat assigned
        try:
            seat_assigned = SeatAssignment.objects.get(user=instance.user.id)
            representation['seat_assigned'] = seat_assigned.seat.ticket
        except:
            representation['seat_assigned'] = None
        return representation


class UnassignedGuestSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Guest
        fields = ['id', 'user', 'name', 'type', 'student', 'status']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Check if the student has a seat assigned
        try:
            seat_assigned = SeatAssignment.objects.get(user=instance.user.id)
            representation['seat_assigned'] = seat_assigned.seat.ticket
        except:
            representation['seat_assigned'] = None
        return representation
    
    
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add group information to the token
        groups = user.groups.values_list('name', flat=True)
        token['groups'] = list(groups)
        print(token.payload)
        return token