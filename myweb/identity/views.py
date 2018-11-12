from django.shortcuts import render, redirect
from . import forms, models
import hashlib
import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


# Create your views here.

# login : login/
def login(request):
    if request.session.get('is_login',None):
        return redirect('/')
    if request.method == 'POST':
        pass
    loginForm = forms.loginForm()
    return render(request, 'identity/login.html',locals())


# register: register/
def register(request):
    if request.session.get('is_login',None):
        return redirect('/')
    if request.method == 'POST':
        registerForm = forms.registerForm(request.POST)
        #message = 'please check your input'
        if registerForm.is_valid():
            nickname = registerForm.cleaned_data['nickname']
            email = registerForm.cleaned_data['email']
            password1 = registerForm.cleaned_data['password1']
            password2 = registerForm.cleaned_data['password2']
            if password1 != password2:
                message = 'passwords are not the same, please check again'
                return render(request, 'identity/register.html', locals())
            else:
                sameEmail = models.User.objects.filter(email=email)
                if sameEmail:
                    message = 'the email is already registered, please check again'
                    return render(request, 'identity/register.html', locals())
                newUser = models.User()
                newUser.nickname = nickname
                newUser.email = email
                newUser.password = hashCode(password1) #将密码加密
                newUser.save()
                code = confirmCode(newUser)  #生成确认码
                sendEmail(email, code)   #发送激活邮件 
                message = '请前往注册邮箱，进行激活'
                return render(request, 'identity/confirm.html', locals()) 
    registerForm = forms.registerForm()
    return render(request, 'identity/register.html', locals())

def hashCode(s,salt='myweb'):
    """ generate hash code """
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())
    return h.hexdigest()
 
def confirmCode(user):
    """ generate confirm code """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hashCode(user.nickname, now)
    models.activateCode.objects.create(code=code, user=user)
    return code

def sendEmail(email, code):
    """ send activation link """
    subject = "from 47.95.112.248"
    textContent = ''' welcome to my website '''
    htmlContent = '''<p>感谢注册<a href="http://47.95.112.248:8080/identity/confirm/?code={}" target=blank>http://47.95.112.248</a>,this is my site</p>
<p>please click the link to activate</p>
<p>this link is expired in {} days'''.format(code, settings.CONFIRM_DAYS)
    msg = EmailMultiAlternatives(subject, textContent, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(htmlContent, "text/html")
    msg.send()


