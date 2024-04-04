from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    ClusterList,
    ClusterDetail,
    RowList,
    RowDetail,
    StudentProfileList,
    StudentProfileDetail,
    GuestList,
    GuestDetail,
    SeatList,
    SeatDetail,
    SeatAssignmentList,
    SeatAssignmentDetail,
    api_root,
)

urlpatterns = [
    path("", api_root),
    path("clusters/", ClusterList.as_view(), name="cluster-list"),
    path("clusters/<int:pk>/", ClusterDetail.as_view(), name="cluster-detail"),
    path("rows/", RowList.as_view(), name="row-list"),
    path("rows/<int:pk>/", RowDetail.as_view(), name="row-detail"),
    path("students/", StudentProfileList.as_view(), name="student-list"),
    path("students/<int:pk>/", StudentProfileDetail.as_view(), name="student-detail"),
    path("guests/", GuestList.as_view(), name="guest-list"),
    path("guests/<int:pk>/", GuestDetail.as_view(), name="guest-detail"),
    path("seats/", SeatList.as_view(), name="seat-list"),
    path("seats/<int:pk>/", SeatDetail.as_view(), name="seat-detail"),
    path("seat_assignments/", SeatAssignmentList.as_view(), name="assignment-list"),
    path("seat_assignments/<int:pk>/",SeatAssignmentDetail.as_view(),name="assignment-detail",
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
