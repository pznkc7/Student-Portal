from django.urls import path
from . views import *

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),
    path('form/', form, name='form'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('delete/<int:id>/', delete_data, name='delete_data'),
    path('recycle/', recycle, name='recycle'),
    path('edit/<int:id>/',edit, name='edit'),
    path('restore/<int:id>/', restore, name='restore'),
    path('restore_all/', restore_all, name='restore_all'),
    path('clear_items/', clear_items, name='clear_items'),

    # ___________Authentication portion start here____________
    path('register/', register, name='register'),
    path('log_in/', log_in, name='log_in'),
    path('log_out/', log_out, name='log_out'),

    path('change_password/',change_password,name='change_password'),

   path('password_reset/', auth_views.PasswordResetView.as_view(template_name="auth/password_reset.html"), name='password_reset'),
   path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name="auth/password_reset_done.html"), name='password_reset_done'),
   path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name="auth/password_reset_confirm.html"), name='password_reset_confirm'),
   path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="auth/password_reset_complete.html"), name='password_reset_complete'),
   path('user_profile/', user_profile, name='user_profile'),    
]