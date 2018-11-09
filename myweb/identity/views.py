from django.shortcuts import render, redirect
from . import forms, models


# Create your views here.

# login : login/
def login(request):
    if request.session.get('is_login',None):
        return redirect('/')
    if request.method == 'POST':
        pass
    loginForm = forms.loginForm()
    return render(request, 'identity/login.html',locals())
