from django.shortcuts import render
from rest_framework import generics, permissions, status
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
import json
from django.db.models import Q

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
    StudentStatusUpdateSerializer,
    GuestStatusUpdateSerializer,
    ParentSerializer,
)

from .permissions import (
    IsCoordinator,
    IsStudent,
    OnlyCoordinatorCanCreate,
    IsGuest,
)


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
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class ClusterDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


# ROW
class RowList(generics.ListAPIView):
    queryset = Row.objects.all()
    serializer_class = RowSerializer


class RowDetail(generics.RetrieveAPIView):
    queryset = Row.objects.all()
    serializer_class = RowSerializer


# STUDENT PROFILE
class StudentProfileList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


class StudentProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer


# GUEST
class GuestList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class GuestDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


# SEAT
class SeatList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


class SeatDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


# SEAT ASSIGNMENT
class SeatAssignmentList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatAssignmentSerializer


class SeatAssignmentDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = SeatAssignment.objects.all()
    serializer_class = SeatAssignmentSerializer


# SEAT ASSIGNMENT
class SeatingPlanList(generics.ListAPIView):
    serializer_class = SeatingPlanSerializer
    
    def get_queryset(self):
        user = self.request.user
        link = self.request.query_params.get('link', None)
        
        if link is not None:
            queryset = SeatAssignment.objects.filter(link=link)
            return queryset
        # determine the user group
        if(user.groups.filter(name='coordinator').exists()):
            queryset = SeatAssignment.objects.all()
            return queryset
        elif(user.groups.filter(name='student').exists()):
            students_guest = Guest.objects.filter(student__user=user)
            guest_users = students_guest.values_list('user', flat=True)
            guest = list(guest_users)
            queryset = SeatAssignment.objects.filter(Q(user=user) | Q(user__in=guest))
            return queryset
        elif(user.groups.filter(name='guest').exists()):
            students_guest = Guest.objects.filter(student__user=user)
            guest_users = students_guest.values_list('user', flat=True)
            guest = list(guest_users)
            queryset = SeatAssignment.objects.filter(Q(user=user) | Q(user__in=guest))
            return queryset
        else:
            queryset = SeatAssignment.objects.none()
            
# TIMETABLE

class TimetableListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, OnlyCoordinatorCanCreate]
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    

class TimetableDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = Timetable.objects.all()
    serializer_class = TimetableSerializer
    
class ParentListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    queryset = Guest.objects.all()
    serializer_class = ParentSerializer
    
    def get_queryset(self):
        student = self.request.user
        queryset = Guest.objects.filter(student__user__username=student)
        return queryset
    
class ParentDetails(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsStudent]
    queryset = Guest.objects.all()
    serializer_class = ParentSerializer
    
    def get_queryset(self):
        student = self.request.student
        queryset = Guest.objects.filter(student=student)
        return queryset

@api_view(['PUT', 'GET'])
@permission_classes([permissions.IsAuthenticated, IsStudent])
def student_update_status(request):
    user = request.user
    user = StudentProfile.objects.get(user__id=user.id)
    
    if request.method == 'PUT':
        serializer = StudentStatusUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        serializer = StudentStatusUpdateSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT', 'GET'])
@permission_classes([permissions.IsAuthenticated, IsGuest])
def guest_update_status(request):
    user = request.user
    user = Guest.objects.get(user__id=user.id)
    
    if request.method == 'PUT':
        serializer = GuestStatusUpdateSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'GET':
        serializer = GuestStatusUpdateSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
# custom views
@csrf_exempt
@permission_classes([permissions.IsAuthenticated, IsCoordinator])
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
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = StudentProfile.objects.all()
    serializer_class = UnassignedStudentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter students who don't have a seat assigned
        queryset = queryset.exclude(user__seatassignment__isnull=False)
        queryset = queryset.exclude(graduation_status='PP')
        return queryset
    
    
class UnassignedGuestListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
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