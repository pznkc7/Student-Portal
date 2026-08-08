from django.shortcuts import render, redirect
from .models import StudentLeave, Student, Teacher, Department, LeaveType
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re

def _is_teacher(user):
    """True if the logged-in user has an approved Teacher profile."""
    if not user.is_authenticated:
        return False
    return Teacher.objects.filter(username=user.username, is_approved=True).exists()


def _is_student(user):
    """True if the logged-in user has an approved Student profile."""
    if not user.is_authenticated:
        return False
    return Student.objects.filter(username=user.username, is_approved=True).exists()


# ─────────────────────────────────────────────
# Main views
# ─────────────────────────────────────────────

def home(request):
    category = request.GET.get('category')
    searched = request.GET.get('searched')

    is_teacher = _is_teacher(request.user)
    is_student = _is_student(request.user)

    student_leaves = None
    if is_teacher or is_student:
        student_leaves = StudentLeave.objects.filter(is_deleted=False).select_related(
            'student', 'student__department', 'leave_type'
        )

        if searched:
            if category == 'student_id':
                student_leaves = student_leaves.filter(student__student_id__icontains=searched)
            elif category == 'name':
                student_leaves = student_leaves.filter(
                    student__first_name__icontains=searched
                ) | student_leaves.filter(student__last_name__icontains=searched)
            elif category == 'department':
                student_leaves = student_leaves.filter(student__department__name__icontains=searched)
            elif category == 'reason':
                student_leaves = student_leaves.filter(reason__icontains=searched)

    return render(request, 'crudApp1/home.html', {
        'student_leaves': student_leaves,
        'is_teacher': is_teacher,
        'is_student': is_student,
    })

@login_required(login_url='log_in')
def form(request):
    departments = Department.objects.all()
    leave_types = LeaveType.objects.all()

    if request.method == "POST":
        student_id       = request.POST.get('student_id')
        first_name       = request.POST.get('first_name')
        last_name        = request.POST.get('last_name')
        department_id    = request.POST.get('department')
        semester         = request.POST.get('semester')
        leave_type_id    = request.POST.get('leave_type')
        start_date       = request.POST.get('start_date')
        end_date         = request.POST.get('end_date')
        guardian_contact = request.POST.get('guardian_contact')
        reason           = request.POST.get('reason')

        try:
            department = Department.objects.get(id=department_id)
            leave_type = LeaveType.objects.get(id=leave_type_id)

            student, created = Student.objects.get_or_create(
                student_id=student_id,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'department': department,
                    'semester': semester,
                    's_username': request.user.username,
                    'email': request.user.email,
                }
            )

            StudentLeave.objects.create(
                student=student,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                guardian_contact=guardian_contact,
                reason=reason,
            )

            messages.success(request, 'Leave application submitted successfully.')
            return redirect('home')

        except Department.DoesNotExist:
            messages.error(request, 'Selected department does not exist.')
        except LeaveType.DoesNotExist:
            messages.error(request, 'Selected leave type does not exist.')

    return render(request, 'crudApp1/form.html', {
        'departments': departments,
        'leave_types': leave_types,
    })


def about(request):
    return render(request, 'crudApp1/about.html')


def contact(request):
    return render(request, 'crudApp1/contact.html')


@login_required(login_url='log_in')
def delete_data(request, id):
    if not _is_teacher(request.user):
        messages.error(request, 'Only teachers can perform this action.')
        return redirect('home')
    data = StudentLeave.objects.get(id=id)
    data.is_deleted = True
    data.deleted_time = timezone.now()
    data.save()
    messages.success(request, 'Leave record moved to recycle bin.')
    return redirect('home')

@login_required(login_url='log_in')
def recycle(request):
    if not _is_teacher(request.user):
        messages.error(request, 'Only teachers can access the recycle bin.')
        return redirect('home')
    data = StudentLeave.objects.filter(is_deleted=True).select_related(
        'student', 'student__department', 'leave_type'
    )
    threshold = timezone.now() - timedelta(days=7)
    expired = StudentLeave.objects.filter(is_deleted=True, deleted_time__lt=threshold)
    if expired.count() > 0:
        expired.delete()
    return render(request, 'crudApp1/recycle.html', {'data': data})


@login_required(login_url='log_in')
def restore(request, id):
    if not _is_teacher(request.user):
        messages.error(request, 'Only teachers can perform this action.')
        return redirect('home')
    leave = StudentLeave.objects.get(id=id)
    leave.is_deleted = False
    leave.deleted_time = None
    leave.save()
    messages.success(request, 'Leave record restored.')
    return redirect('home')



@login_required(login_url='log_in')
def restore_all(request):
    if not _is_teacher(request.user):
        messages.error(request, 'Only teachers can perform this action.')
        return redirect('home')
    StudentLeave.objects.filter(is_deleted=True).update(is_deleted=False, deleted_time=None)
    messages.success(request, 'All items have been restored successfully.')
    return redirect('recycle')


@login_required(login_url='log_in')
def clear_items(request):
    if not _is_teacher(request.user):
        messages.error(request, 'Only teachers can perform this action.')
        return redirect('home')
    if StudentLeave.objects.filter(is_deleted=False).exists():
        StudentLeave.objects.filter(is_deleted=False).update(
            is_deleted=True, deleted_time=timezone.now()
        )
        messages.success(request, 'All records moved to recycle bin.')
    else:
        messages.error(request, 'No records to clear.')
    return redirect('home')

@login_required(login_url='log_in')
def edit(request, id):
    if not _is_teacher(request.user):
        messages.error(request, 'Only teachers can edit records.')
        return redirect('home')
    data = StudentLeave.objects.select_related(
        'student', 'student__department', 'leave_type'
    ).get(id=id)

    departments = Department.objects.all()
    leave_types = LeaveType.objects.all()

    if request.method == "POST":
        department_id    = request.POST.get('department')
        semester         = request.POST.get('semester')
        leave_type_id    = request.POST.get('leave_type')
        start_date       = request.POST.get('start_date')
        end_date         = request.POST.get('end_date')
        guardian_contact = request.POST.get('guardian_contact')
        reason           = request.POST.get('reason')

        try:
            department = Department.objects.get(id=department_id)
            leave_type = LeaveType.objects.get(id=leave_type_id)

            data.student.department = department
            data.student.semester = semester
            data.student.save()

            data.leave_type       = leave_type
            data.start_date       = start_date
            data.end_date         = end_date
            data.guardian_contact = guardian_contact
            data.reason           = reason
            data.save()

            messages.success(request, 'Leave record updated successfully.')
            return redirect('home')

        except Department.DoesNotExist:
            messages.error(request, 'Selected department does not exist.')
        except LeaveType.DoesNotExist:
            messages.error(request, 'Selected leave type does not exist.')

    return render(request, 'crudApp1/edit.html', {
        'data': data,
        'departments': departments,
        'leave_types': leave_types,
    })


# ─────────────────────────────────────────────
# Authentication views
# ─────────────────────────────────────────────

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password, ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import PasswordChangeForm


def register(request):
    return render(request, 'auth/register.html')


def register_student(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        username         = request.POST.get('username')
        student_id       = request.POST.get('student_id')
        first_name       = request.POST.get('first_name')
        last_name        = request.POST.get('last_name')
        department_id    = request.POST.get('department')
        semester         = request.POST.get('semester')
        email            = request.POST.get('email')
        password         = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # ── Validation ──────────────────────────────
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if not email.endswith('@gmail.com'):
            messages.error(request, 'Email must be a valid Gmail address.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if Student.objects.filter(student_id=student_id).exists():
            messages.error(request, 'Student ID already registered.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if len(password) < 7:
            messages.error(request, 'Password must be at least 7 characters.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if not re.search(r'[A-Z]', password):
            messages.error(request, 'Password must contain at least one uppercase letter.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if not re.search(r'[a-z]', password):
            messages.error(request, 'Password must contain at least one lowercase letter.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if not re.search(r'[0-9]', password):
            messages.error(request, 'Password must contain at least one digit.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, 'Password must contain at least one special character.')
            return render(request, 'auth/register_student.html', {'departments': departments})

        try:
            validate_password(password)
            department = Department.objects.get(id=department_id)

            # Create Django auth user (inactive until approved)
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                is_active=False  # Cannot login until admin approves
            )

            # Create Student record
            Student.objects.create(
                username=username,
                student_id=student_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                semester=semester,
                department=department,
                is_approved=False,
            )

            messages.success(request, 'Registration submitted! Please wait for admin approval before logging in.')
            return redirect('log_in')

        except ValidationError as e:
            messages.error(request, str(e))
        except Department.DoesNotExist:
            messages.error(request, 'Selected department does not exist.')

    return render(request, 'auth/register_student.html', {'departments': departments})


def register_teacher(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        username         = request.POST.get('username')
        teacher_id       = request.POST.get('teacher_id')
        first_name       = request.POST.get('first_name')
        last_name        = request.POST.get('last_name')
        department_id    = request.POST.get('department')
        role             = request.POST.get('role')
        email            = request.POST.get('email')
        password         = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # ── Validation ──────────────────────────────
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if not email.endswith('@gmail.com'):
            messages.error(request, 'Email must be a valid Gmail address.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if Teacher.objects.filter(teacher_id=teacher_id).exists():
            messages.error(request, 'Teacher ID already registered.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if len(password) < 7:
            messages.error(request, 'Password must be at least 7 characters.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if not re.search(r'[A-Z]', password):
            messages.error(request, 'Password must contain at least one uppercase letter.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if not re.search(r'[a-z]', password):
            messages.error(request, 'Password must contain at least one lowercase letter.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if not re.search(r'[0-9]', password):
            messages.error(request, 'Password must contain at least one digit.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            messages.error(request, 'Password must contain at least one special character.')
            return render(request, 'auth/register_teacher.html', {'departments': departments})

        try:
            validate_password(password)
            department = Department.objects.get(id=department_id)

            # Create Django auth user but inactive until approved)
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                is_active=False  # Cannot login until admin approves
            )

            # Teacher record
            Teacher.objects.create(
                username=username,
                teacher_id=teacher_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                department=department,
                role=role,
                is_approved=False,
            )

            messages.success(request, 'Registration submitted! Please wait for admin approval before logging in.')
            return redirect('log_in')

        except ValidationError as e:
            messages.error(request, str(e))
        except Department.DoesNotExist:
            messages.error(request, 'Selected department does not exist.')

    return render(request, 'auth/register_teacher.html', {'departments': departments})


def log_in(request):
    if request.method == 'POST':
        username    = request.POST.get('username')
        password    = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
 
        # Fetch user manually so we can distinguish "wrong password" from "not approved"
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
            return redirect('log_in')
 
        if not user_obj.check_password(password):
            messages.error(request, 'Invalid username or password.')
            return redirect('log_in')
 
        if not user_obj.is_active:
            messages.error(request, 'Your account is pending admin approval. Please wait.')
            return redirect('log_in')
 
        login(request, user_obj, backend='django.contrib.auth.backends.ModelBackend')
        request.session.set_expiry(1209600 if remember_me else 0)
        messages.success(request, f'Welcome, {user_obj.username}!')
        return redirect('home')
 
    return render(request, 'auth/login.html')
 

def log_out(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('log_in')


@login_required(login_url='log_in')
def change_password(request):
    form = PasswordChangeForm(user=request.user)
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('log_in')
    return render(request, 'auth/change_password.html', {'form': form})


@login_required(login_url='log_in')
def user_profile(request):
    return render(request, 'auth/user_profile.html')




#Authentication pipeline
def complete_profile(request):
    username = request.session.get('oauth_username')
    if not username:
        messages.error(request, 'No pending Google sign-up found. Please sign in again.')
        return redirect('log_in')

    context = {
        'departments': Department.objects.all(),
        'first_name': request.session.get('oauth_first_name', ''),
        'last_name':  request.session.get('oauth_last_name', ''),
        'email':      request.session.get('oauth_email', ''),
    }

    if request.method == 'POST':
        role          = request.POST.get('role')
        department_id = request.POST.get('department')

        try:
            department = Department.objects.get(id=department_id)
        except Department.DoesNotExist:
            messages.error(request, 'Selected department does not exist.')
            return render(request, 'auth/complete_profile.html', context)

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'Something went wrong. Please sign up again.')
            return redirect('log_in')

        if role == 'student':
            student_id = request.POST.get('student_id')
            semester   = request.POST.get('semester')
            if Student.objects.filter(student_id=student_id).exists():
                messages.error(request, 'Student ID already registered.')
                return render(request, 'auth/complete_profile.html', context)
            Student.objects.create(
                username=username, student_id=student_id,
                first_name=context['first_name'], last_name=context['last_name'],
                email=context['email'], semester=semester,
                department=department, is_approved=False,
            )

        elif role == 'teacher':
            teacher_id  = request.POST.get('teacher_id')
            teacher_role = request.POST.get('teacher_role')
            if Teacher.objects.filter(teacher_id=teacher_id).exists():
                messages.error(request, 'Teacher ID already registered.')
                return render(request, 'auth/complete_profile.html', context)
            Teacher.objects.create(
                username=username, teacher_id=teacher_id,
                first_name=context['first_name'], last_name=context['last_name'],
                email=context['email'], department=department,
                role=teacher_role, is_approved=False,
            )

        else:
            messages.error(request, 'Please select a role.')
            return render(request, 'auth/complete_profile.html', context)

        for key in ('oauth_username', 'oauth_email', 'oauth_first_name', 'oauth_last_name'):
            request.session.pop(key, None)

        messages.success(request, 'Profile submitted! Please wait for admin approval before logging in.')
        return redirect('log_in')

    return render(request, 'auth/complete_profile.html', context)