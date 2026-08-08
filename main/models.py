from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Student(models.Model):
    username = models.CharField(max_length=100)
    student_id = models.CharField(max_length=6, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    semester = models.PositiveIntegerField()
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="students"
    )
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Teacher(models.Model):

    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Coordinator', 'Coordinator'),
        ('Teacher', 'Teacher'),
    )

    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    teacher_id = models.CharField(max_length=6, unique=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="teachers"
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class StudentLeave(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT
    )

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField()
    guardian_contact = models.CharField(max_length=13)

    is_deleted = models.BooleanField(default=False)
    deleted_time = models.DateTimeField(null=True, blank=True)

    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.leave_type}"