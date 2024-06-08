from django.shortcuts import render
from rest_framework import generics, permissions, status
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, transaction
from django.contrib.auth.decorators import login_required
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404


import json, csv

from .models import Cluster, Row, StudentProfile, Guest, Seat, SeatAssignment, Timetable, Report, Notification, Message
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
    ReportSerializer,
    MessageSerializer,
    NotificationSerializer,
    UserSerializer,
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
            "reports": reverse("report-list-create", request=request, format=format),
            "messages": reverse("message-list-create", request=request, format=format),
            "notifications": reverse("notification-list-create", request=request, format=format),
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

class BatchStudentProfileUpload(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'detail': 'No file Uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            csv_file = csv.reader(file.read().decode('utf-8').splitlines())
            headers = next(csv_file)
            headers = [x.strip() for x in headers]
            
            created_profiles = []
            failed_profiles = []
            for row in csv_file:
                data=dict(zip(headers, row))
                user_data = {
                    'username': data['username'],
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'password': data['password'],
                }
                
                profile_data = {
                    'user': user_data,
                    'graduation_status': data['graduation_status'],
                    'degree_program': data['degree_program'],
                    'degree_level': data['degree_level'],
                    'college': data['college'],
                }
                
                profile_serializer = StudentProfileSerializer(data=profile_data)
                if profile_serializer.is_valid():
                    profile_serializer.save()
                    created_profiles.append(profile_serializer.data)
                else:
                    failed_profiles = {
                        "name": user_data['username'],
                        "error": profile_serializer.errors,
                        }

            return JsonResponse({'created_profiles': created_profiles, "failed_profiles": failed_profiles}, status=status.HTTP_201_CREATED)
                    
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# GUEST
class GuestList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer
    
class BatchGuestUpload(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsCoordinator]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'detail': 'No file Uploaded.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            csv_file = csv.reader(file.read().decode('utf-8').splitlines())
            headers = next(csv_file)
            headers = [x.strip() for x in headers]
            failed = created = []
            for row in csv_file:
                data=dict(zip(headers, row))
                formated_data = {
                    "student": data["student"],
                    "name": data["name"],
                    "password": data["password"],
                    "type": data["type"],
                    "status": data["status"],
                    "user": {
                        "username": data["name"],
                        "password": data["password"],
                    }
                }
                guest_serializer = GuestSerializer(data=formated_data)
                if(guest_serializer.is_valid()):
                    guest_serializer.save()
                    created.append(guest_serializer.data)
                else:
                    failed.append(guest_serializer.data)
            return JsonResponse({'created': created, 'failed': failed}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

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
    
    
class ReportListCreateView(generics.ListCreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if(user.groups.filter(name='coordinator').exists()):
            return Report.objects.all();
        return Report.objects.filter(student=self.request.user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, OnlyCoordinatorCanCreate]


    def perform_create(self, serializer):
        student_id = self.request.data.get('student')
        report_id = self.request.data.get('report')
        
        # Fetch the student and report instances
        student = get_object_or_404(User, id=student_id)
        report = get_object_or_404(Report, id=report_id) if report_id else None
        
        serializer.save(coordinator=self.request.user, student=student, report=report)
    
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='coordinator').exists():
            return Message.objects.all()
        else:
            return Message.objects.filter(student=user)

class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationListCreateView(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, OnlyCoordinatorCanCreate]


    def perform_create(self, serializer):
        serializer.save(coordinator=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='coordinator').exists():
            # If the user is a coordinator, return all notifications
            return Notification.objects.all()
        else:
            # If the user is not a coordinator, return notifications sent to them
            return Notification.objects.filter(users=user)
class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserListView(APIView):
    permission_classes = [permissions.IsAuthenticated | IsCoordinator]

    def get(self, request, *args, **kwargs):
        if request.user.groups.filter(name='coordinator').exists():
            students = User.objects.filter(groups__name='student')
            guests = User.objects.filter(groups__name='guest')
            users = students.union(guests)
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        return Response({})