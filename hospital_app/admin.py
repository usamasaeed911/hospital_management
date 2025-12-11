from django.contrib import admin

# Custom admin site
admin.site.site_header = "🏥 Hospital Management Admin"
admin.site.site_title = "Hospital Admin"
admin.site.index_title = "Welcome to Hospital Management Admin"

# we're using MongoDB directly, not Django models
# So we don't register Django models in admin
# All admin functionality is handled through custom views in admin_dashboard.py
