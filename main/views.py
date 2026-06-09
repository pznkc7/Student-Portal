from django.shortcuts import render, redirect
from . models import StudentLeave
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from datetime import timedelta
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import re  #regular expression module for password validation



# Create your views here.
def home(request):
   
    category= request.GET.get('category') 
    searched= request.GET.get('searched')
    if searched:
        if category == 'full_name':
            student_leaves= StudentLeave.objects.filter(full_name__icontains=searched, is_delete=False)
        elif category == 'faculty':
            student_leaves= StudentLeave.objects.filter(faculty__icontains=searched, is_delete=False)
        elif category == 'roll_number':
            student_leaves= StudentLeave.objects.filter(roll_number__icontains=searched, is_delete=False)    
        elif category == 'reason':
            student_leaves= StudentLeave.objects.filter(reason__icontains=searched, is_delete=False)

    else:
            student_leaves = StudentLeave.objects.filter(is_delete=False)
    

    return render(request, 'crudApp1/home.html', {'student_leaves': student_leaves})


@login_required(login_url='log_in' )
def form(request):
    
    if request.method == "POST":
        roll_number = request.POST.get('rollnumber')
        full_name = request.POST.get('fullName')
        faculty = request.POST.get('faculty')
        semester = request.POST.get('semester')
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        guardian_contact = request.POST.get('guardianContact')
        leave_type = request.POST.get('leaveType')
        student_email = request.POST.get('email')
        reason = request.POST.get('reason')

        StudentLeave.objects.create(
            roll_number=roll_number,
            full_name=full_name,
            faculty=faculty,
            semester=semester,
            start_date=start_date,
            end_date=end_date,  
            guardian_contact=guardian_contact,
            leave_type=leave_type,      
            student_email=student_email,
            reason=reason
        )

        subject = "Regarding your leave application"
        message = render_to_string('crudApp1/msg.html', {
            'full_name': full_name,
            'roll_number': roll_number,
            'faculty': faculty,
            'semester': semester,
            'start_date': start_date,
            'end_date': end_date,
            'guardian_contact': guardian_contact,
            'leave_type': leave_type,
            'student_email': student_email,
            'reason': reason
        })
        from_email = 'khatripujan35@gmail.com'#sender's email-id
        recipient_list = [student_email] #receiver's email-id

        msg_email =EmailMessage(subject,message,from_email,recipient_list)
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=True)
    return render(request, 'crudApp1/form.html')

def about(request):
    return render(request, 'crudApp1/about.html')

def contact(request):
    return render(request, 'crudApp1/contact.html')

def delete_data(request,id):
    data = StudentLeave.objects.get(id=id) #retrives data that matches the sent id in arguments
    data.is_delete = True
    data.delete_time = timezone.now()
    data.save()
    return redirect('home')

def recycle(request):
    data = StudentLeave.objects.filter(is_delete=True) 
    threshold = timezone.now()- timedelta(days=7)  
    expired  = StudentLeave.objects.filter(is_delete=True, delete_time__lt=threshold)
    delete_count = expired.count()  
    if delete_count > 0:
        expired.delete()
        print(f'{delete_count} records permanently deleted.')
    else:
        print('No records to delete.')

    return render(request, 'crudApp1/recycle.html', {'data': data})


def restore(request,id):
    leave = StudentLeave.objects.get(id=id)
    leave.is_delete = False
    leave.save()

    return redirect('home')

def restore_all(request):
    StudentLeave.objects.filter(is_delete=True).update(is_delete=False)
    messages.success(request, 'All items have been restored successfully.')
    return redirect('recycle')

def clear_items(request):
    current_time  = timezone.now()
    StudentLeave.objects.all().update(is_delete=True,delete_time=current_time)

    return redirect('home')


def edit(request,id):
     data = StudentLeave.objects.get(id = id)  #this is existing data/old data
     if request.method == "POST": #this is newly recieved data from edit.html's form
        roll_number = request.POST.get('rollNumber')
        full_name = request.POST.get('fullName')
        faculty = request.POST.get('faculty')
        semester = request.POST.get('semester')
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        guardian_contact = request.POST.get('guardianContact')
        leave_type = request.POST.get('leaveType')
        student_email = request.POST.get('studentEmail')      
        reason = request.POST.get('reason')

        #updating old data with new data
        data.roll_number = roll_number
        data.full_name = full_name
        data.faculty = faculty
        data.semester = semester    
        data.start_date = start_date
        data.end_date = end_date
        data.guardian_contact = guardian_contact
        data.leave_type = leave_type
        data.student_email = student_email
        data.reason = reason

        data.save() #saving the latest data
        return redirect('home')


     return render(request,'crudApp1/edit.html', {'data': data})
    


#___________________________Authentication views___________________________#
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password,ValidationError
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import PasswordChangeForm,UserChangeForm

def register(request):
    if request.method == 'POST':
          
          username = request.POST['username']
          first_name = request.POST['first_name']
          last_name = request.POST['last_name']
          email = request.POST['email']
          password = request.POST['password']
          confirm_password = request.POST['confirm_password']
          
          if password == confirm_password:
                try:
                        if not email.endswith('@gmail.com'):
                            messages.error(request,'email must be a valid gmail address')
                            return redirect('register')
                        
                        if User.objects.filter(username=username).exists():
                            messages.error(request,'username already exists')
                            return redirect('register')
                        
                        elif User.objects.filter(email=email).exists():
                            messages.error(request,'email already exists')
                            return redirect('register')
                        
                        if len(password)<7:
                            messages.error(request,'passord must contain 7 characters')
                            return redirect('register')
                        
                        elif not re.search(r'[A-Z]',password):
                            messages.error(request,'password must contain at least one uppercase letter')
                            return redirect('register')

                        elif not re.search(r'[a-z]',password):
                            messages.error(request,'password must contain at least one lowercase letter')
                            return redirect('register')

                        elif not re.search(r'[0-9]',password):
                            messages.error(request,'password must contain at least one digit')
                            return redirect('register') 

                        elif not re.search(r'[!@#$%^&*(),.?":{}|<>]',password):
                            messages.error(request,'password must contain at least one special character')
                            return redirect('register')
                        

                        


                        
                        validate_password(password)

                        User.objects.create_user(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            password=password
                        )

                        messages.success(request, 'Account created successfully.')
                        return redirect('home')
                
                except ValidationError as e:
                    error_ = str(e)

                    # return redirect('register')
                    return render(request,'auth/register.html',{'error':error_})


          else:
            # return redirect('register')
            return render(request,'auth/register.html',{'error':"Passwords do not match"})


    return render(request,'auth/register.html')

def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')  # Checkbox value

        user = authenticate(request, username=username, password=password)
      

        if user is not None:

            login(request, user)
            # Set session expiry
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # Expires on browser close

            messages.success(request, f"Welcome, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('log_in')
    
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
    return render(request,'auth/change_password.html',{'form':form})

@login_required(login_url='log_in')
def user_profile(request):
    return render(request, 'auth/user_profile.html')