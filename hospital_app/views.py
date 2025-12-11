import pymongo
from bson.objectid import ObjectId
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# MongoDB connection
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hospital_management']
patients_collection = db['patients']
doctors_collection = db['doctors']
appointments_collection = db['appointments']

# ===== HOME PAGE =====
def home(request):
    # Demo landing page - no statistics shown
    return render(request, 'hospital_app/home.html')

# ===== PATIENT MANAGEMENT =====
@login_required
def patient_list(request):
    patients = list(patients_collection.find())
    for patient in patients:
        patient['id'] = str(patient['_id'])
    return render(request, 'hospital_app/patient_list.html', {'patients': patients})

@login_required
def add_patient(request):
    if request.method == 'POST':
        # Generate patient ID
        last_patient = patients_collection.find_one(sort=[("patient_id", -1)])
        if last_patient and 'patient_id' in last_patient:
            last_id = int(last_patient['patient_id'][3:])
            new_patient_id = f"PAT{last_id + 1:06d}"
        else:
            new_patient_id = "PAT000001"

        new_patient = {
            'patient_id': new_patient_id,
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'gender': request.POST.get('gender'),
            'address': request.POST.get('address'),
            'blood_group': request.POST.get('blood_group'),
            'emergency_contact': request.POST.get('emergency_contact'),
            'registration_date': datetime.now()
        }

        patients_collection.insert_one(new_patient)
        return redirect('patient-list')

    return render(request, 'hospital_app/add_patient.html')

@login_required
def update_patient(request, patient_id):
    patient = patients_collection.find_one({'_id': ObjectId(patient_id)})
    if not patient:
        messages.error(request, 'Patient not found.')
        return redirect('patient-list')

    if request.method == 'POST':
        updated_patient = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'date_of_birth': request.POST.get('date_of_birth'),
            'gender': request.POST.get('gender'),
            'address': request.POST.get('address'),
            'blood_group': request.POST.get('blood_group'),
            'emergency_contact': request.POST.get('emergency_contact'),
        }

        patients_collection.update_one({'_id': ObjectId(patient_id)}, {'$set': updated_patient})
        messages.success(request, 'Patient updated successfully.')
        return redirect('patient-list')

    patient['id'] = str(patient['_id'])
    return render(request, 'hospital_app/update_patient.html', {'patient': patient})

@login_required
def delete_patient(request, patient_id):
    if request.method == 'POST':
        result = patients_collection.delete_one({'_id': ObjectId(patient_id)})
        if result.deleted_count > 0:
            messages.success(request, 'Patient deleted successfully.')
        else:
            messages.error(request, 'Patient not found.')
    return redirect('patient-list')

# ===== DOCTOR MANAGEMENT =====
@login_required
def doctor_list(request):
    doctors = list(doctors_collection.find())
    for doctor in doctors:
        doctor['id'] = str(doctor['_id'])
    return render(request, 'hospital_app/doctor_list.html', {'doctors': doctors})

@login_required
def add_doctor(request):
    if request.method == 'POST':
        # Generate doctor ID
        last_doctor = doctors_collection.find_one(sort=[("doctor_id", -1)])
        if last_doctor and 'doctor_id' in last_doctor:
            last_id = int(last_doctor['doctor_id'][3:])
            new_doctor_id = f"DOC{last_id + 1:06d}"
        else:
            new_doctor_id = "DOC000001"

        new_doctor = {
            'doctor_id': new_doctor_id,
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'specialization': request.POST.get('specialization'),
            'department': request.POST.get('department'),
            'qualification': request.POST.get('qualification'),
            'experience': int(request.POST.get('experience', 0)),
            'consultation_fee': float(request.POST.get('consultation_fee', 0)),
            'availability': 'Available',
            'status': 'Active'
        }

        doctors_collection.insert_one(new_doctor)
        return redirect('doctor-list')

    return render(request, 'hospital_app/add_doctor.html')

@login_required
def update_doctor(request, doctor_id):
    doctor = doctors_collection.find_one({'_id': ObjectId(doctor_id)})
    if not doctor:
        messages.error(request, 'Doctor not found.')
        return redirect('doctor-list')

    if request.method == 'POST':
        updated_doctor = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
            'phone': request.POST.get('phone'),
            'specialization': request.POST.get('specialization'),
            'department': request.POST.get('department'),
            'qualification': request.POST.get('qualification'),
            'experience': int(request.POST.get('experience', 0)),
            'consultation_fee': float(request.POST.get('consultation_fee', 0)),
            'availability': request.POST.get('availability'),
            'status': request.POST.get('status'),
        }

        doctors_collection.update_one({'_id': ObjectId(doctor_id)}, {'$set': updated_doctor})
        messages.success(request, 'Doctor updated successfully.')
        return redirect('doctor-list')

    doctor['id'] = str(doctor['_id'])
    return render(request, 'hospital_app/update_doctor.html', {'doctor': doctor})

@login_required
def delete_doctor(request, doctor_id):
    if request.method == 'POST':
        result = doctors_collection.delete_one({'_id': ObjectId(doctor_id)})
        if result.deleted_count > 0:
            messages.success(request, 'Doctor deleted successfully.')
        else:
            messages.error(request, 'Doctor not found.')
    return redirect('doctor-list')

# ===== APPOINTMENT MANAGEMENT =====
@login_required
def appointment_list(request):
    appointments = list(appointments_collection.find().sort('appointment_date', -1))
    
    # Get patient and doctor names
    for appointment in appointments:
        appointment['id'] = str(appointment['_id'])

        # Get patient name
        patient = patients_collection.find_one({'_id': appointment['patient_id']})
        appointment['patient_name'] = f"{patient['first_name']} {patient['last_name']}" if patient else "Unknown"

        # Get doctor name
        doctor = doctors_collection.find_one({'_id': appointment['doctor_id']})
        appointment['doctor_name'] = f"Dr. {doctor['first_name']} {doctor['last_name']}" if doctor else "Unknown"
    
    return render(request, 'hospital_app/appointment_list.html', {'appointments': appointments})

@login_required
def book_appointment(request):
    if request.method == 'POST':
        # Generate appointment ID
        last_appointment = appointments_collection.find_one(sort=[("appointment_id", -1)])
        if last_appointment and 'appointment_id' in last_appointment:
            last_id = int(last_appointment['appointment_id'][4:])
            new_appointment_id = f"APT{last_id + 1:06d}"
        else:
            new_appointment_id = "APT000001"

        new_appointment = {
            'appointment_id': new_appointment_id,
            'patient_id': ObjectId(request.POST.get('patient_id')),
            'doctor_id': ObjectId(request.POST.get('doctor_id')),
            'appointment_date': request.POST.get('appointment_date'),
            'time_slot': request.POST.get('time_slot'),
            'purpose': request.POST.get('purpose'),
            'notes': request.POST.get('notes', ''),
            'status': 'Scheduled',
            'created_at': datetime.now()
        }

        appointments_collection.insert_one(new_appointment)
        return redirect('appointment-list')

    # GET request - show booking form
    patients = list(patients_collection.find())
    doctors = list(doctors_collection.find())

    for patient in patients:
        patient['id'] = str(patient['_id'])
    for doctor in doctors:
        doctor['id'] = str(doctor['_id'])

    return render(request, 'hospital_app/book_appointment.html', {
        'patients': patients,
        'doctors': doctors
    })

@login_required
def update_appointment(request, appointment_id):
    appointment = appointments_collection.find_one({'_id': ObjectId(appointment_id)})
    if not appointment:
        messages.error(request, 'Appointment not found.')
        return redirect('appointment-list')

    if request.method == 'POST':
        updated_appointment = {
            'patient_id': ObjectId(request.POST.get('patient_id')),
            'doctor_id': ObjectId(request.POST.get('doctor_id')),
            'appointment_date': request.POST.get('appointment_date'),
            'time_slot': request.POST.get('time_slot'),
            'purpose': request.POST.get('purpose'),
            'notes': request.POST.get('notes', ''),
            'status': request.POST.get('status'),
        }

        appointments_collection.update_one({'_id': ObjectId(appointment_id)}, {'$set': updated_appointment})
        messages.success(request, 'Appointment updated successfully.')
        return redirect('appointment-list')

    # GET request - show update form
    patients = list(patients_collection.find())
    doctors = list(doctors_collection.find())

    for patient in patients:
        patient['id'] = str(patient['_id'])
    for doctor in doctors:
        doctor['id'] = str(doctor['_id'])

    appointment['id'] = str(appointment['_id'])
    return render(request, 'hospital_app/update_appointment.html', {
        'appointment': appointment,
        'patients': patients,
        'doctors': doctors
    })

@login_required
def delete_appointment(request, appointment_id):
    if request.method == 'POST':
        result = appointments_collection.delete_one({'_id': ObjectId(appointment_id)})
        if result.deleted_count > 0:
            messages.success(request, 'Appointment deleted successfully.')
        else:
            messages.error(request, 'Appointment not found.')
    return redirect('appointment-list')

# ===== SEARCH FUNCTIONALITY =====
def search_patients(request):
    query = request.GET.get('q', '')
    
    search_criteria = {}
    if query:
        search_criteria['$or'] = [
            {'first_name': {'$regex': query, '$options': 'i'}},
            {'last_name': {'$regex': query, '$options': 'i'}},
            {'patient_id': {'$regex': query, '$options': 'i'}},
            {'email': {'$regex': query, '$options': 'i'}},
            {'phone': {'$regex': query, '$options': 'i'}}
        ]
    
    if search_criteria:
        patients = list(patients_collection.find(search_criteria))
    else:
        patients = list(patients_collection.find())
    
    for patient in patients:
        patient['id'] = str(patient['_id'])
    
    return render(request, 'hospital_app/search_patients.html', {
        'patients': patients,
        'query': query,
        'total_results': len(patients)
    })

@login_required
def search_doctors(request):
    query = request.GET.get('q', '')
    specialization_filter = request.GET.get('specialization', '')
    department_filter = request.GET.get('department', '')
    
    search_criteria = {}
    
    if query:
        search_criteria['$or'] = [
            {'first_name': {'$regex': query, '$options': 'i'}},
            {'last_name': {'$regex': query, '$options': 'i'}},
            {'doctor_id': {'$regex': query, '$options': 'i'}},
            {'specialization': {'$regex': query, '$options': 'i'}}
        ]
    
    if specialization_filter:
        search_criteria['specialization'] = specialization_filter
    
    if department_filter:
        search_criteria['department'] = department_filter
    
    if search_criteria:
        doctors = list(doctors_collection.find(search_criteria))
    else:
        doctors = list(doctors_collection.find())
    
    for doctor in doctors:
        doctor['id'] = str(doctor['_id'])
    
    # Get unique specializations and departments for filters
    specializations = doctors_collection.distinct('specialization')
    departments = doctors_collection.distinct('department')
    
    return render(request, 'hospital_app/search_doctors.html', {
        'doctors': doctors,
        'query': query,
        'specializations': specializations,
        'departments': departments,
        'selected_specialization': specialization_filter,
        'selected_department': department_filter,
        'total_results': len(doctors)
    })

@login_required
def search_appointments(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    date_filter = request.GET.get('date', '')

    search_criteria = {}

    if query:
        search_criteria['appointment_id'] = {'$regex': query, '$options': 'i'}

    if status_filter:
        search_criteria['status'] = status_filter

    if date_filter:
        search_criteria['appointment_date'] = date_filter

    appointments = list(appointments_collection.find(search_criteria).sort('appointment_date', -1))

    # Get patient and doctor names
    for appointment in appointments:
        appointment['id'] = str(appointment['_id'])

        # Get patient name
        patient = patients_collection.find_one({'_id': appointment['patient_id']})
        appointment['patient_name'] = f"{patient['first_name']} {patient['last_name']}" if patient else "Unknown"

        # Get doctor name
        doctor = doctors_collection.find_one({'_id': appointment['doctor_id']})
        appointment['doctor_name'] = f"Dr. {doctor['first_name']} {doctor['last_name']}" if doctor else "Unknown"

    return render(request, 'hospital_app/search_appointments.html', {
        'appointments': appointments,
        'query': query,
        'selected_status': status_filter,
        'selected_date': date_filter,
        'total_results': len(appointments)
    })

# ===== STAFF AUTHENTICATION =====
def staff_signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('staff_dashboard')
            except IntegrityError:
                form.add_error('username', 'A user with this username already exists.')
    else:
        form = UserCreationForm()

    return render(request, 'hospital_app/staff_signup.html', {'form': form})

def staff_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('staff_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'hospital_app/staff_login.html', {'form': form})

def staff_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def staff_dashboard(request):
    # Get statistics for staff dashboard
    total_patients = patients_collection.count_documents({})
    total_doctors = doctors_collection.count_documents({})
    
    today = datetime.now().date()
    today_appointments = appointments_collection.count_documents({
        'appointment_date': str(today)
    })
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'today_appointments': today_appointments,
        'user': request.user,
    }
    return render(request, 'hospital_app/staff_dashboard.html', context)