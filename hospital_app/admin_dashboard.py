from datetime import datetime
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hospital_management']

class HospitalAdminSite(admin.AdminSite):
    site_header = "🏥 Hospital Management Admin"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('stats/', self.admin_view(self.stats_view), name='stats'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        # Get statistics
        total_patients = db.patients.count_documents({})
        total_doctors = db.doctors.count_documents({})
        today_appointments = db.appointments.count_documents({
            'appointment_date': str(datetime.now().date())
        })
        
        context = {
            'total_patients': total_patients,
            'total_doctors': total_doctors,
            'today_appointments': today_appointments,
            'title': 'Hospital Dashboard',
        }
        return render(request, 'admin/dashboard.html', context)
    
    def stats_view(self, request):
        # Get statistics data for charts
        import json
        stats = {
            'patients_by_gender': list(db.patients.aggregate([
                {"$group": {"_id": "$gender", "count": {"$sum": 1}}}
            ])),
            'doctors_by_specialization': list(db.doctors.aggregate([
                {"$group": {"_id": "$specialization", "count": {"$sum": 1}}}
            ])),
        }
        return render(request, 'admin/stats.html', {'stats': stats})

# Create custom admin instance
admin_site = HospitalAdminSite(name='hospital_admin')