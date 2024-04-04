from django.contrib import admin
from .models import Cluster, Row, Seat, StudentProfile, Guest, SeatAssignment


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0


class RowAdmin(admin.ModelAdmin):
    list_display = ["id", "cluster", "number_of_seats"]
    search_fields = ["id", "cluster__name"]
    inlines = [SeatInline]


admin.site.register(Row, RowAdmin)


class SeatAdmin(admin.ModelAdmin):
    list_display = ["id", "row", "seat_number"]
    list_filter = ["row"]
    search_fields = ["id", "row__cluster__name", "seat_number"]


admin.site.register(Seat, SeatAdmin)


class StudentProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "graduation_status",
        "degree_program",
        "degree_level",
        "college",
    ]
    list_filter = ["graduation_status", "degree_program", "degree_level", "college"]
    search_fields = ["user__username", "degree_program", "college"]


admin.site.register(StudentProfile, StudentProfileAdmin)


class GuestAdmin(admin.ModelAdmin):
    list_display = ["name", "student"]
    search_fields = ["name", "student__user__username"]


admin.site.register(Guest, GuestAdmin)


class SeatAssignmentAdmin(admin.ModelAdmin):
    list_display = ["student", "seat"]
    list_filter = ["seat__row__cluster"]
    search_fields = ["student__user__username", "seat__row__cluster__name"]


admin.site.register(SeatAssignment, SeatAssignmentAdmin)


class ClusterAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


admin.site.register(Cluster, ClusterAdmin)
