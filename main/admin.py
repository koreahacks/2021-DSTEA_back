from django.contrib import admin
from main.models import *

# Register your models here.
@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    pass

@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass