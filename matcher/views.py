# Import necessary Django modules and libraries
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
# Import ML libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Import Python utilities
import re
import random
import os
# PDF processing
from PyPDF2 import PdfReader
# Local imports
from .skill_set import SKILL_KEYWORDS
from .models import Match
from .models import UserProfile
from .models import OTPStore

# -----------------------------
# Utility Functions
# -----------------------------

# Clean and normalize input text
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text

# Extract text content from uploaded PDF resume
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)    
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Generate a random 6-digit OTP for password reset
def generate_otp():
    return str(random.randint(100000, 999999))


# -----------------------------
# User Management Views
# -----------------------------

# View full details of a specific user
def view_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user_matches = Match.objects.filter(user=user)
    
    return render(request, 'view_user.html', {
        'user_obj': user,
        'matches': user_matches
    })

# Delete a user unless they are an admin
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_staff:
        messages.error(request, "Cannot delete another Admin!")
        return redirect('admin_dashboard')

    user.delete()
    messages.success(request, "User deleted successfully.")
    return redirect('admin_dashboard')


# -----------------------------
# Authentication Views
# -----------------------------

# Welcome landing page
def welcome(request):
    return render(request, 'welcome.html')

# User registration with role assignment
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']

        # Check for duplicate username or email
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')
        
        # Create user and associated profile
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        profile = UserProfile.objects.create(user=user, role=role)
        profile.save()

        messages.success(request, "Registration successful. Please login.")
        return redirect('login')
    return render(request, 'register.html')

# User login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')
    return render(request, 'login.html')

# -----------------------------
# Forgot & Reset Password Views
# -----------------------------


# Step 1: Enter email to receive OTP
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            otp = generate_otp()
            request.session['reset_email'] = email
            request.session['otp'] = otp

            send_mail(
                subject='Your OTP for Password Reset',
                message=f'Your OTP is {otp}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
            )
            messages.success(request, 'OTP sent to your email.')
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, 'Email not registered')
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')

# Step 2: Verify OTP and set new password
def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        new_password = request.POST['new_password']
        actual_otp = request.session.get('otp')
        email = request.session.get('reset_email')

        if entered_otp == actual_otp:
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful. Please log in.')
                request.session.pop('reset_email', None)
                request.session.pop('otp', None)

                return redirect('login')  # ✅ Redirect to login page
            except User.DoesNotExist:
                messages.error(request, 'User not found.')
                return redirect('verify_otp')
        else:
            messages.error(request, 'Invalid OTP.')
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')

# Optional reset password route if implemented separately
def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST['new_password']
        email = request.session.get('reset_email')

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
                        
            # Clear session data
            request.session.pop('reset_email')
            request.session.pop('otp')

            messages.success(request, 'Password reset successful. Please login.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Error resetting password')
            return redirect('forgot_password')

    return render(request, 'reset_password.html')


# -----------------------------
# Dashboard & Index Views
# -----------------------------

# User dashboard showing username
@login_required
def dashboard(request):
    return render(request, 'dashboard.html', {'username': request.user.username})

# Index page (job matcher form)
@login_required
def index(request):
    return render(request, 'index.html')

# -----------------------------
# Resume Matcher View
# -----------------------------

# Matcher to compare resumes with job description
@login_required
def matcher(request):
    results = None
    job_desc_text = ''

    if request.method == 'POST':
        job_desc_text = request.POST.get('job_desc_text', '')
        job_desc_clean = clean_text(job_desc_text)

        uploaded_files = request.FILES.getlist('resumes')
        results = []

        for file in uploaded_files:
            resume_text = extract_text_from_pdf(file)
            resume_clean = clean_text(resume_text)

            # TF-IDF Similarity
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform([resume_clean, job_desc_clean])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            similarity_score = round(similarity * 100, 2) 
            # Skill Matching
            job_skills = [skill for skill in SKILL_KEYWORDS if skill in job_desc_clean]
            resume_skills = [skill for skill in SKILL_KEYWORDS if skill in resume_clean]
            missing_skills = list(set(job_skills) - set(resume_skills))
            missing_skills_str = ', '.join(missing_skills) if missing_skills else 'None'

            # Save match record to database
            Match.objects.create(
                user=request.user,
                resume_name=file.name,
                match_score=similarity_score,
                missing_skills=missing_skills_str
            )

            # Add to display results
            results.append({
                'resume_name': file.name,
                'similarity_score': similarity_score,
                'missing_skills': missing_skills_str
            })
        # Sort results by highest match score
        results = sorted(results, key=lambda x: x['similarity_score'], reverse=True)

    return render(request, 'index.html', {'results': results, 'job_desc': job_desc_text})

# Logout
def logout_view(request):
    auth_logout(request)
    return redirect('welcome')

# -----------------------------
# Admin Views
# -----------------------------

# Admin login with staff check
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_staff:
                auth_login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Invalid admin credentials or user is not an admin.")
                return redirect('admin_login')
        else:
            messages.error(request, "Please provide both username and password.")
            return redirect('admin_login')
    
    return render(request, 'admin_login.html')

# Admin dashboard view showing all users and matches
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('admin_login')
    
    users = User.objects.all()
    matches = Match.objects.all()
    
    # Get user roles
    profiles = UserProfile.objects.select_related('user')
    user_roles = {profile.user.id: profile.role for profile in profiles}

    return render(request, 'admin_dashboard.html', {
        'users': users,
        'matches': matches,
        'user_roles': user_roles
    })

# -----------------------------
# Match History View
# -----------------------------


# View match history for a specific user
def user_match_history(request, user_id):
    user = get_object_or_404(User, id=user_id)
    matches = Match.objects.filter(user=user).order_by('-created_at')
    return render(request, 'user_match_history.html', {
        'user': user,
        'matches':matches
        })