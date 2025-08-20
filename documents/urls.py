from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('upload/', views.upload_document, name='upload_document'),
    path('student/<int:student_id>/', views.view_student_documents, name='view_student_documents'),
    path('download/<int:document_id>/', views.download_document, name='download_document'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/toggle/<int:category_id>/', views.toggle_category, name='toggle_category'),
]