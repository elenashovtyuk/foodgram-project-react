from django.contrib import admin
from .models import User, Subscription
# Register your models here.


# регистрируем модель пользователя в админ-зоне
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # перечислим поля, которые должны отображаться в админке
    list_display = ('email', 'username', 'first_name', 'last_name', 'password')
    # по ТЗ нужно учесть фильтрацию по email и username
    list_filter = ('email', 'username')
    # также по ТЗ администратор должен иметь возможность
    # менять пароль пользователю
    search_fields = ('email', 'username')
    list_editable = ('password',)
    empty_value_display = '-пусто-'


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
