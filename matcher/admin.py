from django.contrib import admin
from .models import UserProfile, Match, OTPStore

# Register UserProfile model to appear in the Django admin interface
admin.site.register(UserProfile)

# Register Match model to manage resume-job matches via admin
admin.site.register(Match)

# Register OTPStore model to monitor OTP records from admin panel
admin.site.register(OTPStore)