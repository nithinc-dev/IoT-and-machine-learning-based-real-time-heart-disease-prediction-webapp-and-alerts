from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from django.contrib import messages
from .models import *
def home(request):
    return render(request, 'home.html', {'a':'a'})

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PatientForm

def register(request):
    if request.method == 'POST':
        form = PatientForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Your form has been submitted successfully!")
            return redirect('register')
    else:
        form = PatientForm()
    return render(request, 'register.html', {'form': form})



from django.views.generic import ListView, DetailView

class ProfilesListView(ListView):
    template_name = 'patientProfiles.html'
    model = Patient
    context_object_name = 'patients'


class ProfileDetailView(DetailView):
    template_name = 'patientProfile.html'
    model = Patient
    
    
def map(request):
    return render(request, 'map.html', {'a':'a'})


def pundash(request):
    return render(request, 'punith.html', {'a':'a'})


class PatientsECGListView(ListView):
    template_name = 'patientsECG.html'
    model = Patient
    context_object_name = 'patients'
# class PatientECGDetailView(DetailView):
#     template_name = 'patientECG.html'
#     model = ECG


def ecgDetail(request,pk):
    ecgs = ECG.objects.filter(patient__pk=pk)
    return render(request, 'patientECG.html',{'ecgs':ecgs})

def success(request):
    messages.success(request,"success message")
    return render(request, 'home.html')


import csv
import os
from django.core.exceptions import ObjectDoesNotExist
from Heart_Proj.settings import BASE_DIR
def export_ecg_to_csv(pk):
    """
    Export ECG data to CSV file with timestamps, creating the file if it doesn't exist.
    Data is ordered in reverse chronological order.
    """
    filename = 'madhan.csv'
    
    try:
        # Get ECG records for the patient in reverse order
        ecgs = ECG.objects.filter(patient__pk=pk).order_by('timestamp')
        
        # Create directory if it doesn't exist
        path = BASE_DIR/"csvFolder" 
        
        # Open file in write mode with newline='' to handle line endings properly
        with open(path/filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            
            # Write header row
            writer.writerow(['Timestamp (mm:ss.SSS)', 'ECG Value'])
            
            # Write data rows
            for ecg in ecgs:
                # Format timestamp to show only minutes:seconds.milliseconds
                timestamp = ecg.timestamp.strftime('%M:%S.%f')[:-3]
                writer.writerow([timestamp, ecg.ecg_data])
                
        print(f"Successfully exported ECG data to {filename}")
        return True
        
    except ObjectDoesNotExist:
        print(f"No ECG data found for patient ID: {pk}")
        return False
        
    except Exception as e:
        print(f"Error exporting ECG data: {str(e)}")
        return False

def ecgcsv(request, pk):
    # First export to CSV
    export_ecg_to_csv(pk)
    
    # Then render the template as before
    ecgs = ECG.objects.filter(patient__pk=pk)
    return render(request, 'patientECG.html', {'ecgs': ecgs})


from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import DoctorSignUpForm
from heartApp.models import Doctor

def doctor_signup_view(request):
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            login(request, doctor)
            messages.success(request, 'Successfully signed up as a doctor!')
            return redirect('doctor_dashboard')  # Create this view/URL
    else:
        form = DoctorSignUpForm()
    return render(request, 'doctor_signup.html', {'form': form})

def doctor_login_view(request):
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None and isinstance(user, Doctor):
                login(request, user)
                messages.success(request, 'Successfully logged in as a doctor!')
                return redirect('doctor_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = DoctorLoginForm()
    
    return render(request, 'doctor_login.html', {'form': form})

def doctor_logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('doctor_login')

def doctor_dashboard_view(request):
    # Ensure only logged-in doctors can access this view
    if not request.user.is_authenticated or not isinstance(request.user, Doctor):
        messages.error(request, 'You must be logged in as a doctor.')
        return redirect('doctor_login')
    return render(request, 'doctor_dashboard.html')


from django.shortcuts import render

def location_tracker_view(request):
    return render(request, 'location_tracker.html')  # Adjust path if needed



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Location, Patient
from .serializers import LocationSerializer

class LocationAPI(APIView):
    def get(self, request):
        patient_key = request.query_params.get('patient_key')
        try:
            patient = Patient.objects.get(patient_key=patient_key)
            location = patient.locations.latest('timestamp')
            serializer = LocationSerializer(location)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Patient.DoesNotExist:
            return Response({'error': 'Invalid patient key'}, status=status.HTTP_404_NOT_FOUND)
        except Location.DoesNotExist:
            return Response({'error': 'No location data found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        patient_key = request.data.get('patient_key')
        try:
            patient = Patient.objects.get(patient_key=patient_key)
            data = {
                'latitude': request.data['latitude'],
                'longitude': request.data['longitude'],
                'altitude': request.data.get('altitude'),
            }
            location = Location.objects.create(patient=patient, **data)
            serializer = LocationSerializer(location)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Patient.DoesNotExist:
            return Response({'error': 'Invalid patient key'}, status=status.HTTP_404_NOT_FOUND)




# views.py
from django.shortcuts import render
from django.http import HttpResponse
from .forms import RoleSelectionForm

def role_selection_view(request):
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            special_key = form.cleaned_data['special_key']
            
            try:
                # Find the patient using the special key
                patient = Patient.objects.get(patient_key=special_key)
                
                # Retrieve the latest location for the patient
                latest_location = patient.locations.order_by('-timestamp').first()
                
                if not latest_location:
                    form.add_error(None, "No location data available for this patient.")
                    return render(request, 'map2.html', {'form': form})
                
                latitude = latest_location.latitude
                longitude = latest_location.longitude
                altitude = latest_location.altitude

                return render(request, 'map2.html', {
                    'form': form,
                    'latitude': latitude,
                    'longitude': longitude,
                    'altitude': altitude,
                    'coords':[latitude, longitude],
                })
            except Patient.DoesNotExist:
                form.add_error('special_key', 'Invalid special key. No patient found.')
    else:
        form = RoleSelectionForm()

    return render(request, 'map2.html', {'form': form})








# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Location, Patient
# from .serializers import LocationSerializer


# @method_decorator(csrf_exempt, name="dispatch")
# class LocationAPI(APIView):
#     def post(self, request):
#         special_key = request.data.get('special_key')
#         try:
#             patient = Patient.objects.get(patient_key=special_key)
#             data = {
#                 'latitude': request.data['latitude'],
#                 'longitude': request.data['longitude'],
#                 'altitude': request.data.get('altitude'),
#             }
#             location = Location.objects.create(patient=patient, **data)
#             serializer = LocationSerializer(location)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except Patient.DoesNotExist:
#             return Response({'error': 'Invalid patient key'}, status=status.HTTP_404_NOT_FOUND)










# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import ECG
# from .serializers import ECGSerializer

# @api_view(['POST'])
# def ecg_create(request):
#     serializer = ECGSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





# views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import ECG
from .serializers import ECGBulkSerializer

# @api_view(['POST'])
# def ecg_create(request):
#     serializer = ECGBulkSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response({"message": "ECG data uploaded successfully", "count": len(serializer.validated_data['ecg_readings'])}, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# # views.py
# import logging
# logger = logging.getLogger(__name__)

# @api_view(['POST'])
# def ecg_create(request):
#     try:
#         # Log incoming request details
#         logger.info(f"Received request: {request.data}")
        
#         serializer = ECGBulkSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {
#                     "message": "ECG data uploaded successfully", 
#                     "count": len(serializer.validated_data['ecg_readings'])
#                 }, 
#                 status=status.HTTP_201_CREATED
#             )
        
#         # Log validation errors
#         logger.error(f"Validation Error: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     except Exception as e:
#         # Catch and log any unexpected errors
#         logger.error(f"Unexpected error: {str(e)}")
#         return Response(
#             {"error": "Internal server error"}, 
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )




# views.py
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

#@api_view(['POST'])
# def ecg_create(request):
#     try:
#         # Log complete incoming request
#         logger.info(f"Full Request Data: {request.data}")
#         logger.info(f"Request Body: {request.body}")
        
#         serializer = ECGBulkSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {
#                     "message": "ECG data uploaded successfully", 
#                     "count": len(serializer.validated_data['ecg_readings'])
#                 }, 
#                 status=status.HTTP_201_CREATED
#             )
        
#         # Detailed validation error logging
#         logger.error(f"Validation Errors: {serializer.errors}")
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     except Exception as e:
#         logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
#         return Response(
#             {"error": f"Internal server error: {str(e)}"}, 
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )


@api_view(['POST'])
def ecg_create(request):
    try:
        # Use request.data instead of request.body
        logger.info(f"Request Data: {request.data}")
        
        serializer = ECGBulkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "ECG data uploaded successfully", 
                    "count": len(serializer.validated_data['ecg_readings'])
                }, 
                status=status.HTTP_201_CREATED
            )
        
        logger.error(f"Validation Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Unexpected Error: {str(e)}", exc_info=True)
        return Response(
            {"error": f"Internal server error: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )