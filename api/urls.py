from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    ClusterList,    ClusterDetail,  RowList,    RowDetail,  StudentProfileList,
    StudentProfileDetail,   GuestList,  GuestDetail,    SeatList,    SeatDetail,
    SeatAssignmentList, SeatAssignmentDetail,   SeatingPlanList,
    UnassignedStudentListView,  UnassignedGuestListView,    create_seating_plan,
    TimetableDetailView,    TimetableListCreateView,    api_root,
    MyTokenObtainPairView,    student_update_status,    guest_update_status,
    ParentListView,    ParentDetails,    BatchStudentProfileUpload,
    BatchGuestUpload,   ReportListCreateView,   ReportDetailView,
    MessageListCreateView,  MessageDetailView,   NotificationListCreateView,
    NotificationDetailView, UserListView
)

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("", api_root),
    path('token/', MyTokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('users/', UserListView.as_view(), name='user-list'),
    path("clusters/", ClusterList.as_view(), name="cluster-list"),
    path("clusters/<int:pk>/", ClusterDetail.as_view(), name="cluster-detail"),
    path("rows/", RowList.as_view(), name="row-list"),
    path("rows/<int:pk>/", RowDetail.as_view(), name="row-detail"),
    path("students/", StudentProfileList.as_view(), name="student-list"),
    path("students/<int:pk>/", StudentProfileDetail.as_view(), name="student-detail"),
    path("students/batch/", BatchStudentProfileUpload.as_view(), name="student-batch-upload"),
    path("guests/", GuestList.as_view(), name="guest-list"),
    path("guests/<int:pk>/", GuestDetail.as_view(), name="guest-detail"),
    path("guests/batch/", BatchGuestUpload.as_view(), name="guest-batch-upload"),
    path("seats/", SeatList.as_view(), name="seat-list"),
    path("seats/<int:pk>/", SeatDetail.as_view(), name="seat-detail"),
    path('timetable/', TimetableListCreateView.as_view(), name='timetable-list'),
    path('timetable/<int:pk>/', TimetableDetailView.as_view(), name='timetable-detail'),
    path('reports/', ReportListCreateView.as_view(), name='report-list-create'),
    path('reports/<int:pk>/', ReportDetailView.as_view(), name='report-detail'),
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message-detail'),
    path('notifications/', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path("seat_assignments/", SeatAssignmentList.as_view(), name="assignment-list"),
    path("seat_assignments/<int:pk>/",SeatAssignmentDetail.as_view(),name="assignment-detail"),
    path("seating_plan/", SeatingPlanList.as_view(), name="seating-plan"),
    path("batch_student_plan/", create_seating_plan),
    path("unassigned_students/", UnassignedStudentListView.as_view(), name="unassigned-students"),
    path("unassigned_guests/", UnassignedGuestListView.as_view(), name="unassigned-guests"),
    
    # custom urls
    path("student_update_status/", student_update_status, name="student-update-status"),
    path("guest_update_status/", guest_update_status, name="guest-update-status"),
    path("parents/", ParentListView.as_view()),
    path("parents/<str:student>/", ParentDetails.as_view()),
]

urlpatterns += [
    path("auth/", include('rest_framework.urls')),
]
urlpatterns = format_suffix_patterns(urlpatterns)
