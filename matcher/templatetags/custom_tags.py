from django import template

# Create a new template library to register custom filters
register = template.Library()

# Custom filter to get a value from a dictionary by key in templates
@register.filter
def get_item(dictionary, key):
    # Return the value for the given key, or 'N/A' if key is not found
    return dictionary.get(key,'N/A')