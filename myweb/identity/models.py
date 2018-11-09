from django.db import models

# Create your models here.

#  Create User

class User(models.Model):
    nickname = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    phoneNumber = models.CharField(max_length=11, null=True)
    qqNumber = models.CharField(max_length=16, null=True)
    weChatNumber = models.CharField(max_length=50,null=True) 
    c_time = models.DateTimeField(auto_now_add=True)
    isActivated = models.BooleanField(default=False)  # has/hasn't click the activatationlink
    isStu = models.BooleanField(default=False)   # is student or not 

    def __unicode__(self):
        return self.nickname
    
    class Meta:
        ordering = ['-c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'

class activateCode(models.Model):
    """
    activate code
    """
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User',on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.user.nickname + ":" + self.code
    
    class Meta:
        ordering = ["-c_time"]
        verbose_name = "确认码"
        verbose_name_plural = "确认码"


class changePasswordCode(models.Model):
    """
    change password code
    """
    code = models.CharField(max_length=256)
    user = models.OneToOneField('User',on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)
    
    def __unicode__(self):
        return self.user.nickname + ":" + self.code
    
    class Meta:
        ordering = ['-c_time']
        verbose_name = "修改码"
        verbose_name_plural = "修改码"

    
