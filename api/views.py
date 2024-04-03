from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.response import Response
from .models import Cluster, Row, StudentProfile
from .serializers import ClusterSerializer, RowSerializer
from .serializers import StudentProfileSerializer

# Create your views here
# =============== API ROOT =================
@api_view(["GET"])
def api_root(request, format=None):
    return Response(
        {
            "clusters": reverse("cluster-list", request=request, format=format),
            "rows": reverse("row-list", request=request, format=format),
            "students": reverse('student-list', request=request, format=format),
        }
    )


# =============== CLUSTER ==================
class ClusterList(generics.ListCreateAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class ClusterDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


# =================== ROW ===================
class RowList(generics.ListCreateAPIView):
    queryset = Row.objects.all()
    serializer_class = RowSerializer


class RowDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Row.objects.all()
    serializer_class = RowSerializer
    

# ================= STUDENT PROFILE ==================
class StudentProfileList(generics.ListCreateAPIView):
    queryset = StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer
    

class StudentProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset =  StudentProfile.objects.all()
    serializer_class = StudentProfileSerializer