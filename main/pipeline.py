from django.shortcuts import redirect
from .models import Student, Teacher


def require_role_selection(strategy, details, user, is_new=False, *args, **kwargs):
    """
    Runs after python-social-auth creates/matches the Django User.
    Blocks access until the user has a linked Student or Teacher record.
    """
    has_role = (
        Student.objects.filter(username=user.username).exists()
        or Teacher.objects.filter(username=user.username).exists()
    )
    if has_role:
        return  # normal user, let the pipeline finish (login proceeds as usual)

    if is_new:
        user.is_active = False
        user.save(update_fields=['is_active'])

    request = strategy.request
    request.session['oauth_username']   = user.username
    request.session['oauth_email']      = user.email
    request.session['oauth_first_name'] = user.first_name
    request.session['oauth_last_name']  = user.last_name

    return redirect('complete_profile')