from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Job, Resume, Application, InterviewAttempt

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("SkillBridge", {"fields": ("role", "company_name")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("SkillBridge", {"fields": ("email", "role", "company_name")}),)

admin.site.register(Profile)
admin.site.register(Job)
admin.site.register(Resume)
admin.site.register(Application)
admin.site.register(InterviewAttempt)
