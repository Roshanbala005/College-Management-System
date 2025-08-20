from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.contrib.auth.models import User
from .models import UserProfile, StudentDocument, DocumentCategory
from .forms import StudentRegistrationForm, DocumentUploadForm, DocumentCategoryForm

def register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to the system.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'register.html', {'form': form})

def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        if request.user.is_superuser:
            profile = UserProfile.objects.create(user=request.user, user_type='teacher')
        else:
            profile = UserProfile.objects.create(user=request.user, user_type='student')
        messages.info(request, 'Profile created for your account.')
    
    if profile.user_type == 'student':
        return student_dashboard(request)
    else:
        return teacher_dashboard(request)

@login_required
def student_dashboard(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'student':
        raise PermissionDenied
    
    documents = StudentDocument.objects.filter(student=request.user)
    categories = DocumentCategory.objects.filter(is_active=True)
    
    context = {
        'documents': documents,
        'categories': categories,
        'profile': profile,
    }
    return render(request, 'student_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'teacher':
        raise PermissionDenied
    
    search_query = request.GET.get('search', '')
    students = User.objects.filter(userprofile__user_type='student')
    
    if search_query:
        students = students.filter(
            Q(username__icontains=search_query) |
            Q(userprofile__roll_number__icontains=search_query)
        )
    
    context = {
        'students': students,
        'search_query': search_query,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def upload_document(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'student':
        raise PermissionDenied
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.student = request.user
            
            existing = StudentDocument.objects.filter(
                student=request.user, 
                category=document.category
            ).first()
            
            if existing:
                existing.document.delete()
                existing.document = document.document
                existing.notes = document.notes
                existing.save()
                messages.success(request, 'Document updated successfully!')
            else:
                document.save()
                messages.success(request, 'Document uploaded successfully!')
            
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'upload_documents.html', {'form': form})

@login_required
def view_student_documents(request, student_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'teacher':
        raise PermissionDenied
    
    student = get_object_or_404(User, id=student_id, userprofile__user_type='student')
    documents = StudentDocument.objects.filter(student=student)
    
    context = {
        'student': student,
        'documents': documents,
    }
    return render(request, 'view_student_documents.html', context)

@login_required
def download_document(request, document_id):
    document = get_object_or_404(StudentDocument, id=document_id)
    
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type == 'student' and document.student != request.user:
        raise PermissionDenied
    elif profile.user_type != 'teacher' and profile.user_type != 'student':
        raise PermissionDenied
    
    try:
        response = HttpResponse(document.document.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{document.category.name}_{document.student.username}.pdf"'
        return response
    except FileNotFoundError:
        raise Http404("Document not found")

@login_required
def manage_categories(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'teacher':
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DocumentCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.created_by = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('manage_categories')
        else:            messages.error(request, 'Please correct the errors below.')
    else:
        form = DocumentCategoryForm()
    
    categories = DocumentCategory.objects.all().order_by('-created_at')
    
    context = {
        'form': form,
        'categories': categories,
    }
    return render(request, 'manage_categories.html', context)

@login_required
def toggle_category(request, category_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.user_type != 'teacher':
        raise PermissionDenied
    
    category = get_object_or_404(DocumentCategory, id=category_id)
    category.is_active = not category.is_active
    category.save()
    
    status = "activated" if category.is_active else "deactivated"
    messages.success(request, f'Category "{category.name}" {status} successfully!')
    return redirect('manage_categories')