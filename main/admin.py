from django.contrib import admin
from .models import Department, Student, Teacher, LeaveType, StudentLeave
from django.contrib.auth.models import User


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'student_id', 'department', 'semester', 'is_approved')
    list_filter = ('is_approved', 'department')
    list_editable = ('is_approved',)
    search_fields = ('username', 'first_name', 'last_name', 'email', 'student_id')
    actions = ['approve_students', 'reject_students']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Sync Django User.is_active with is_approved on every save
        User.objects.filter(username=obj.username).update(is_active=obj.is_approved)

    @admin.action(description='Approve selected students')
    def approve_students(self, request, queryset):
        for student in queryset:
            student.is_approved = True
            student.save()
            User.objects.filter(username=student.username).update(is_active=True)
        self.message_user(request, f'{queryset.count()} student(s) approved.')

    @admin.action(description='Reject selected students')
    def reject_students(self, request, queryset):
        for student in queryset:
            student.is_approved = False
            student.save()
            User.objects.filter(username=student.username).update(is_active=False)
        self.message_user(request, f'{queryset.count()} student(s) rejected.')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'teacher_id', 'department', 'role', 'is_approved')
    list_filter = ('is_approved', 'department', 'role')
    list_editable = ('is_approved',)
    search_fields = ('username', 'first_name', 'last_name', 'email', 'teacher_id')
    actions = ['approve_teachers', 'reject_teachers']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Sync Django User.is_active with is_approved on every save
        User.objects.filter(username=obj.username).update(is_active=obj.is_approved)

    @admin.action(description='Approve selected teachers')
    def approve_teachers(self, request, queryset):
        for teacher in queryset:
            teacher.is_approved = True
            teacher.save()
            User.objects.filter(username=teacher.username).update(is_active=True)
        self.message_user(request, f'{queryset.count()} teacher(s) approved.')

    @admin.action(description='Reject selected teachers')
    def reject_teachers(self, request, queryset):
        for teacher in queryset:
            teacher.is_approved = False
            teacher.save()
            User.objects.filter(username=teacher.username).update(is_active=False)
        self.message_user(request, f'{queryset.count()} teacher(s) rejected.')


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(StudentLeave)
class StudentLeaveAdmin(admin.ModelAdmin):
    list_display = ('student', 'leave_type', 'start_date', 'end_date', 'reason')

 