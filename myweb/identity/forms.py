from django import forms
from captcha.fields import CaptchaField

class loginForm(forms.Form):
    """login form"""
    username = forms.CharField(label='用户名', max_length=128, widget=forms.TextInput(attrs={'class':'form-control','readonly':'readonly'}))
    password = forms.CharField(label='密码', max_length=256, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    captcha = CaptchaField(label='验证码')


class registerForm(forms.Form):
    """ register form"""
    nickname = forms.CharField(label='用户名', max_length=128, widget=forms.TextInput(attrs={'class':'from-control'}))
    email = forms.EmailField(label='邮箱地址', widget=forms.EmailInput(attrs={'class':'form-control'}))
    password1 = forms.CharField(label='密码', max_length=256, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password2 = form.CharField(label='确认密码', max_length=256, widget=forms.PasswordInput(attrs={'class':'form-control'}))
    captcha = CaptchaField(label='验证码')

