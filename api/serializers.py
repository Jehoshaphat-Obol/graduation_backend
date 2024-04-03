from rest_framework import serializers
from .models import Cluster, Row, StudentProfile, Guest

class ClusterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cluster
        fields = ['name']


class RowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Row
        fields = ['cluster', 'number_of_seats']

        
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['user', 'graduation_status', 'degree_program', 'degree_level', 'college']

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = ['student', 'name']