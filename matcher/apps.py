from django.apps import AppConfig

# Configuration class for the 'matcher' app
class MatcherConfig(AppConfig):
    # Default primary key field type for models in this app
    default_auto_field = 'django.db.models.BigAutoField'
    # Name of the app (should match the folder name)
    name='matcher'