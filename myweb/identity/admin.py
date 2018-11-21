from django.contrib import admin
from .models import User, activateCode, changePasswordCode
# Register your models here.


class UserAdmin(admin.ModelAdmin):
    
    list_display = ('nickname', 'c_time', 'isActivated', 'isStu')

admin.site.register(User, UserAdmin)

class activateCodeAdmin(admin.ModelAdmin):
    
    list_display = ('user', 'code', 'c_time')

admin.site.register(activateCode, activateCodeAdmin)


class changePasswordCodeAdmin(admin.ModelAdmin):
    
    list_display = ('user', 'code', 'c_time')

admin.site.register(changePasswordCode, changePasswordCodeAdmin)
