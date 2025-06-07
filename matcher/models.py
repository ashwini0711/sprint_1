from django.db import models
from django.contrib.auth.models import User

# UserProfile model to extend the default User model with additional role info
class UserProfile(models.Model):
    # Define possible user roles: Student or Employee
    ROLE_CHOICES = (
        ('Student', 'Student'),
        ('Employee', 'Employee'),
    )
    # One-to-one relationship with the built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Role field with predefined choices
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def _str_(self):
        # String representation showing username and role for easy identification
        return f'{self.user.username} - {self.role}'


# Match model to store the results of resume and job description matching
class Match(models.Model):
    # Link match to the User who uploaded the resume
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Store the filename of the resume that was matched
    resume_name = models.CharField(max_length=255)
    # Similarity score between resume and job description (percentage)
    match_score = models.FloatField()
    # Skills missing from the resume compared to job description
    missing_skills = models.TextField()
    # Timestamp for when this match record was created
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        # String representation showing user, resume, and match score
        return f'{self.user.username} - {self.resume_name} - {self.match_score}'


# OTPStore model to temporarily save OTPs sent to users for password resets
class OTPStore(models.Model):
    # Link OTP record to the User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # 6-digit OTP string
    otp = models.CharField(max_length=6)
    # Timestamp of when the OTP was generated/created
    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        # String representation showing username and OTP code
        return f'{self.user.username}-{self.otp}'