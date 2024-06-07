from django.contrib import admin
from .models import Cluster, Row, Seat, StudentProfile, Guest, SeatAssignment, Timetable , Report, Message, Notification


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0


class RowAdmin(admin.ModelAdmin):
    list_display = ["id", "cluster", "number_of_seats"]
    search_fields = ["id", "cluster__name"]
    inlines = [SeatInline]


admin.site.register(Row, RowAdmin)


class SeatAdmin(admin.ModelAdmin):
    list_display = ["id", "row", "seat_number", "ticket"]
    list_filter = ["row"]
    search_fields = ["id", "row__cluster__name", "seat_number", "ticket"]


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
    list_display = ["name", "student", 'status']
    search_fields = ["name", "student__user__username"]


admin.site.register(Guest, GuestAdmin)


class SeatAssignmentAdmin(admin.ModelAdmin):
    list_display = ["user", "seat", "link"]
    list_filter = ["seat__row__cluster"]


admin.site.register(SeatAssignment, SeatAssignmentAdmin)


class ClusterAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


admin.site.register(Cluster, ClusterAdmin)


class TimetableAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'start_time', 'end_time')
    search_fields = ('event_name',)
    list_filter = ('start_time', 'end_time')
    ordering = ('start_time',)

admin.site.register(Timetable, TimetableAdmin)

class ReportAdmin(admin.ModelAdmin):
    list_display = ('reference_token', 'student', 'subject', 'is_resolved', 'created_at', 'updated_at')
    list_filter = ('is_resolved', 'created_at', 'updated_at')
    search_fields = ('reference_token', 'student__username', 'student__first_name', 'student__last_name', 'subject')
    readonly_fields = ('reference_token', 'created_at', 'updated_at')
admin.site.register(Report, ReportAdmin)

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'coordinator', 'student', 'created_at')
    list_filter = ('coordinator', 'student', 'created_at')
    search_fields = ('coordinator__username', 'coordinator__first_name', 'coordinator__last_name', 'student__username', 'student__first_name', 'student__last_name', 'content')
    readonly_fields = ('created_at',)
admin.site.register(Message, MessageAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'coordinator', 'created_at')
    list_filter = ('coordinator', 'created_at')
    search_fields = ('coordinator__username', 'coordinator__first_name', 'coordinator__last_name', 'content')
    readonly_fields = ('created_at',)
    filter_horizontal = ('users',)

admin.site.register(Notification, NotificationAdmin)
