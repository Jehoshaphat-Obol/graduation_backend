from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import ClusterList, ClusterDetail, RowList, RowDetail, api_root
from .views import StudentProfileList, StudentProfileDetail

urlpatterns = [
    path('', api_root),
    path('clusters/',ClusterList.as_view(), name="cluster-list"),
    path('clusters/<int:pk>/', ClusterDetail.as_view(), name="cluster-detail"),
    path('rows/',RowList.as_view(), name="row-list"),
    path('rows/<int:pk>/', RowDetail.as_view(), name="row-detail"),
    path('students/', StudentProfileList.as_view(), name="student-list"),
    path('student/<int:pk>/', StudentProfileDetail.as_view(), name='student-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns)