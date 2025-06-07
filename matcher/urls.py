from django.urls import path
from . import views

# URL patterns for the resume matcher Django application
urlpatterns = [
    # Welcome page (initial landing page with Login/Register options)
    path('', views.welcome, name='welcome'),
    # User Login page
    path('login/', views.login_view, name='login'),
    # User Registration page
    path('register/', views.register, name='register'),
    # Page to initiate password reset via email
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    # Page to verify OTP sent to email during password reset
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    # Page to enter new password after OTP verification
    path('reset_password/', views.reset_password, name='reset_password'),
    # Main dashboard after user login
    path('dashboard/', views.dashboard, name='dashboard'),
    # Index page used for uploading resumes and running the matcher
    path('index/', views.index, name='index'),
    # Logs the user out and redirects to welcome page
    path('logout/', views.logout_view, name='logout'),
    # Admin-only login page
    path('admin_login/', views.admin_login, name='admin_login'),
    # Admin dashboard for managing users and viewing match data
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Resume matcher route – compares uploaded resumes with job description
    path('matcher/', views.matcher, name='matcher'),
    # View details of a specific user (admin use)
    path('view_user/<int:user_id>/', views.view_user, name='view_user'),
    # Delete a specific user by ID (admin only, restricted for admins)
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    # View match history of a particular user (admin use)
    path('user_matches/<int:user_id>/', views.user_match_history, name='user_match_history'),
]