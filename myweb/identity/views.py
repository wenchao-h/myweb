from django.shortcuts import render, redirect
from . import forms, models
import hashlib
import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives


# Create your views here.

# index : /
def index(request):
    return render(request, 'base.html', locals())

# login : identity/login/
def login(request):
    if request.session.get('is_login',None):
        return redirect('/')
    if request.method == 'POST':
        loginForm = forms.loginForm(request.POST)
        if loginForm.is_valid():
            email = loginForm.cleaned_data['email']
            password = loginForm.cleaned_data['password']
            try:
                user = models.User.objects.get(email=email)
            except:        
                message = '用户不存在，请先注册'
                location = 'register'
                return render(request, 'identity/confirm.html', locals())
            if not user.isActivated:
                message = '用户未激活，请先激活'
                return render(request, 'identity/message.html', locals())
            if user.password == hashCode(password):
                request.session['is_login'] = True    # 记录session 
                request.session['user_id'] = user.id
                request.session['user_name'] = user.nickname
                return redirect('/')
            else:
                message = '密码错误，请重新输入'
                return render(request, 'identity/login.html', locals())
        else:
            return render(request, 'identity/login.html', locals())
    loginForm = forms.loginForm()
    return render(request, 'identity/login.html',locals())

# logout : identity/logout/
def logout(request):
    if not request.session.get('is_login', None):
        return redirect('/')
    request.session.flush()
    return redirect('/')
# register: identity/register/
def register(request):
    if request.session.get('is_login',None):
        return redirect('/')
    if request.method == 'POST':
        registerForm = forms.registerForm(request.POST)
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
                try:
                    newUser = models.User()
                    newUser.nickname = nickname
                    newUser.email = email
                    newUser.password = hashCode(password1) #将密码加密
                    newUser.save()
                    code = confirmCode(newUser)  #生成确认码
                    sendEmail(email,key='activate', code=code)   #发送激活邮件 
                except Exception as e:
                    message = str(e) + ', please try again or contact the manager' 
                    return render(request, 'identity/register.html', locals())
                    
                message = '请前往注册邮箱，进行激活'
                return render(request, 'identity/message.html', locals()) 
        else:
            message = 'wrong captcha,please check your input'
            data = registerForm.cleaned_data
            registerForm = forms.registerForm(data)
            return render(request, 'identity/register.html', locals())
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

def sendEmail(email, **kwargs):
    """ send activation link or send password-change link 
    kwargs: code=code,key=key
    """
    subject = "from 47.95.112.248"
    textContent = ''' welcome to my website '''
    htmlContent = '''<p>感谢注册<a href="http://47.95.112.248:8080/identity/{key}/?code={code}" target=blank>http://47.95.112.248</a>,this is my site</p>
<p>please click the link to {key}</p>
<p>this link is expired in {days} days'''
    formatDict = dict({'days':settings.CONFIRM_DAYS}, **kwargs)
    htmlContent = htmlContent.format(**formatDict)
    msg = EmailMultiAlternatives(subject, textContent, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(htmlContent, "text/html")
    msg.send()

# user activate : /identity/activate/
def userActivate(request):
    """ user activate """
    code = request.GET['code']
    message = ''
    try:
        activateCode = models.activateCode.objects.get(code=code)
    except:
        message = '无效的确认请求，如有疑问，请联系管理员'
        return render(request, 'identity/message.html', locals())
    c_time = activateCode.c_time
    now = datetime.datetime.now()
    if now > c_time.replace(tzinfo=None) + datetime.timedelta(settings.CONFIRM_DAYS):
        activateCode.user.delete()
        message = '链接已过期，请重新注册'
        return render(request, 'identity/message.html', locals())
    else:
        activateCode.user.isActivated = True
        activateCode.user.save()
        activateCode.delete()
        message = '注册成功，请登录'
        location = 'login'
        return render(request, 'identity/confirm.html', locals())

def changeCode(user):
    """ generate change password code"""
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    code = hashCode(user.nickname, now)
    models.changePasswordCode.objects.create(code=code, user=user)
    return code

# change password : /identity/changepassword/
def changePassword(request):
    """ change password """
    if request.method == 'GET':
        code = request.GET.get('code', None)
        if not code:
            changePasswordForm = forms.changePasswordForm()
            return render(request, 'identity/changepassword.html', locals())
        #message = ''
        try:
            changePasswordCode = models.changePasswordCode.objects.get(code=code)
        except Exception as e:
            message = str(e) + '， 无效的修改请求，如有疑问请联系管理员'
            return render(request, 'identity/message.html', locals())
        c_time = changePasswordCode.c_time
        now = datetime.datetime.now()
        if now > c_time.replace(tzinfo=None) + datetime.timedelta(settings.CONFIRM_DAYS):
            changePasswordCode.delete()
            message = '链接已过期，请重新申请修改密码'
            location = 'login'
            return render(request, 'identity/confirm.html', locals())
        else:
            try:
                nickname = changePasswordCode.user.nickname
                email = changePasswordCode.user.email
            except Exception as e:
                message = str(e) + ', 用户不存在'
                return render(request, 'identity/message.html', locals())
            newPasswordForm = forms.newPasswordForm({'nickname':nickname, 'email':email})
            return render(request, 'identity/changepassword.html', locals())
    if request.method == 'POST':
        if request.POST.get('password1', ''):
            newPasswordForm = forms.newPasswordForm(request.POST)
            if newPasswordForm.is_valid():
                email = newPasswordForm.cleaned_data['email']
                p1 = newPasswordForm.cleaned_data['password1']
                p2 = newPasswordForm.cleaned_data['password2']
                if p1 != p2:
                    message = 'passwords must be the same, please check your input'
                    return render(request, 'identity/changepassword.html', locals())
                try:
                    user = models.User.objects.get(email=email)
                    user.password = hashCode(p1)
                    user.save()
                    models.changePasswordCode.objects.get(user=user).delete()
                except Exception as e:
                    message = str(e) + ', 请联系管理员'
                    return render(request, 'identity/message.html', locals())
                message = '密码修改成功，请重新登录'
                location = 'login'
                return render(request, 'identity/confirm.html', locals())
            else:
                message = 'please check your input'
                return render(request, 'identity/changepassword.html', locals())        
        else:
            changePasswordForm = forms.changePasswordForm(request.POST)
            if changePasswordForm.is_valid():
                email = changePasswordForm.cleaned_data['email']
                try:
                    user = models.User.objects.get(email=email)
                except:
                    message = '用户不存在，请先注册'
                    location = 'register'
                    return render(request, 'identity/confirm.html', locals())
                code = changeCode(user)
                sendEmail(email,key='changepassword',code=code)
                message = '请到邮箱点击修改链接进行密码修改'
                return render(request, 'identity/message.html', locals())
            else:
                message = 'please check your input'
                return render(request, 'identity/changepassword.html', locals())


