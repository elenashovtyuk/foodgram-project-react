from django.contrib import admin
from .models import User
# Register your models here.


# регистрируем модель пользователя в админ-зоне

class UserAdmin(admin.ModelAdmin):
    # перечислим поля, которые должны отображаться в админке
    list_display = ('email', 'username', 'first_name', 'last_name', 'password')
    # по ТЗ нужно учесть фильтрацию по email и username
    list_filter = ('email', 'username')
    # также по ТЗ администратор должен иметь возможность
    # менять пароль пользователю
    list_editable = ('password',)


admin.site.register(User, UserAdmin)
