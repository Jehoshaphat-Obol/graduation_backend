from django.shortcuts import render
from rest_framework import generics, permissions
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Cluster, Row, StudentProfile, Guest, Seat, SeatAssignment, Timetable
from .serializers import (
    ClusterSerializer,
    RowSerializer,
    StudentProfileSerializer,
    GuestSerializer,
    SeatSerializer,
    SeatAssignmentSerializer,
    SeatingPlanSerializer,
    UnassignedStudentSerializer,
    UnassignedGuestSerializer,
    TimetableSerializer,
    MyTokenObtainPairSerializer,
)
import json


# API ROOT
@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "clusters": reverse("cluster-list", request=request, format=format),
            "rows": reverse("row-list", request=request, format=format),
            "seats": reverse("seat-list", request=request, format=format),
            "seat_assignments": reverse("assignment-list", request=request, format=format),
            "students": reverse("student-list", request=request, format=format),
            "guests": reverse("guest-list", request=request, format=format),
            "timetable": reverse("timetable-list", request=request, format=format),
            "seating_plan": reverse("seating-plan", request=request, format=format),
            "unassigned_student": reverse("unassigned-students", request=request, format=format),
            "unassigned_guests": reverse("unassigned-guests", request=request, format=format),
        }
    )


# CLUSTER
class ClusterList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class ClusterDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


# ROW
class RowList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Row.objects.all()
    serializer_class = RowSerializer


class RowDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Row.objects.all()
    serializer_class = RowSerializer


# STUDENT PROFILE
class StudentProfileList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


class StudentProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


# GUEST
class GuestList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class GuestDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


# SEAT
class SeatList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


class SeatDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


# SEAT ASSIGNMENT
class SeatAssignmentList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatAssignmentSerializer


class SeatAssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatAssignmentSerializer


# SEAT ASSIGNMENT
class SeatingPlanList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatingPlanSerializer
    
    
# TIMETABLE

class TimetableListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer

class TimetableDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    
# custom views
@csrf_exempt
@login_required
def create_seating_plan(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        valid_data = []
        errors = []

        for item in data:
            serializer = SeatAssignmentSerializer(data=item)
            if serializer.is_valid():
                try:
                    serializer.save()
                    valid_data.append(serializer.data)
                except IntegrityError as e:
                    errors.append({'item': item, 'error': str(e)})
            else:
                errors.append({'item': item, 'error': serializer.errors})

        return JsonResponse({'valid_data': valid_data, 'errors': errors}, safe=False, status=207)  # 207 Multi-Status

class UnassignedStudentListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = StudentProfile.objects.all()
    serializer_class = UnassignedStudentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter students who don't have a seat assigned
        queryset = queryset.exclude(user__seatassignment__isnull=False)
        queryset = queryset.exclude(graduation_status='PP')
        return queryset
    
    
class UnassignedGuestListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Guest.objects.all()
    serializer_class = UnassignedGuestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter students who don't have a seat assigned
        queryset = queryset.exclude(user__seatassignment__isnull=False)
        queryset = queryset.exclude(status = 'PP')
        return queryset
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer