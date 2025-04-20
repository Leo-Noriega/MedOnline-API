from django.shortcuts import render, redirect
from users.models import CustomUser
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def my_appointments(request):
    user_id = request.session.get('_auth_user_id')
    if request.user.role.name not in ['Patient']:
        return redirect('login')
    else:
        return render(request, 'myAppointments.html', {'user_id': user_id}, status=200)
    
@login_required
def my_account_user (request):
    user_id = request.session.get('_auth_user_id')
    if request.user.role.name not in ['Patient']:
       return redirect('login')
    else:
        return render(request, 'myAccountUser.html', {'user_id': user_id}, status=200)
