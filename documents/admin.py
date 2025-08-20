from django.contrib import admin
from .models import UserProfile, DocumentCategory, StudentDocument

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'roll_number']
    list_filter = ['user_type']
    search_fields = ['user__username', 'roll_number']

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']

@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'category', 'uploaded_at']
    list_filter = ['category', 'uploaded_at']
    search_fields = ['student__username', 'category__name']