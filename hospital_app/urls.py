from django.urls import path
from django.contrib.auth import views as auth_views  # ADD THIS LINE
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('patients/', views.patient_list, name='patient-list'),
    path('patients/add/', views.add_patient, name='add-patient'),
    path('patients/update/<str:patient_id>/', views.update_patient, name='update-patient'),
    path('patients/delete/<str:patient_id>/', views.delete_patient, name='delete-patient'),
    path('doctors/', views.doctor_list, name='doctor-list'),
    path('doctors/add/', views.add_doctor, name='add-doctor'),
    path('doctors/update/<str:doctor_id>/', views.update_doctor, name='update-doctor'),
    path('doctors/delete/<str:doctor_id>/', views.delete_doctor, name='delete-doctor'),
    path('appointments/', views.appointment_list, name='appointment-list'),
    path('appointments/book/', views.book_appointment, name='book-appointment'),
    path('appointments/update/<str:appointment_id>/', views.update_appointment, name='update-appointment'),
    path('appointments/delete/<str:appointment_id>/', views.delete_appointment, name='delete-appointment'),
    path('search/patients/', views.search_patients, name='search-patients'),
    path('search/doctors/', views.search_doctors, name='search-doctors'),
    path('search/appointments/', views.search_appointments, name='search-appointments'),
    # Staff Authentication URLs
    path('staff/signup/', views.staff_signup, name='staff_signup'),
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    
    # Password Reset URLs (Built-in Django)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='hospital_app/password_reset.html'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='hospital_app/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='hospital_app/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='hospital_app/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
]