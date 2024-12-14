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
        # Get ECG records for the patient in reverse order reverse order is -1
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
        
        
        

# import numpy as np
# import scipy.signal as signal
# from scipy import stats
# from django.http import JsonResponse

# def detect_atrial_fibrillation(ecg_data, sampling_rate=250):
#     """
#     Detect potential Atrial Fibrillation (AF)
    
#     Key indicators:
#     1. Irregular R-R intervals
#     2. Absence of distinct P waves
#     3. Rapid and chaotic electrical activity
#     """
#     # Preprocessing
#     filtered_ecg = bandpass_filter(ecg_data)
    
#     # R-peak detection
#     r_peaks = detect_r_peaks(filtered_ecg)
    
#     # R-R interval analysis
#     rr_intervals = np.diff(r_peaks)
    
#     # AF Criteria Calculation
#     irregularity_coefficient = stats.variation(rr_intervals)
#     mean_rr_interval = np.mean(rr_intervals)
    
#     # AF Likelihood Assessment
#     if irregularity_coefficient > 0.2 and mean_rr_interval < 0.6:
#         return "High Likelihood of Atrial Fibrillation"
#     elif irregularity_coefficient > 0.15:
#         return "Possible Atrial Fibrillation"
#     else:
#         return "Normal Sinus Rhythm"

# def detect_st_segment_changes(ecg_data):
#     """
#     Detect ST Segment Abnormalities (Potential Ischemia/Heart Attack)
#     """
#     # Baseline ST segment detection
#     st_segment = extract_st_segment(ecg_data)
    
#     # Amplitude and deviation analysis
#     st_deviation = calculate_st_deviation(st_segment)
    
#     if st_deviation > 1.0:  # millimeters
#         return "Potential Myocardial Ischemia"
#     elif st_deviation > 0.5:
#         return "ST Segment Abnormality"
#     else:
#         return "Normal ST Segment"

# def detect_arrhythmias(ecg_data):
#     """
#     Comprehensive Arrhythmia Detection
#     """
#     r_peaks = detect_r_peaks(ecg_data)
    
#     # Heart Rate Variability Analysis
#     heart_rate = calculate_heart_rate(r_peaks)
    
#     # Categorize based on heart rate
#     if heart_rate < 60:
#         return "Bradycardia"
#     elif heart_rate > 100:
#         return "Tachycardia"
#     else:
#         return "Normal Heart Rate"

# def comprehensive_ecg_analysis(patient_data):
#     """
#     Perform comprehensive ECG analysis
#     """
#     # Convert data to numpy array
#     ecg_data = np.array([float(row['ECG Value']) for row in patient_data])
    
#     analysis_results = {
#         'atrial_fibrillation_risk': detect_atrial_fibrillation(ecg_data),
#         'st_segment_status': detect_st_segment_changes(ecg_data),
#         'arrhythmia_detection': detect_arrhythmias(ecg_data),
#         'data_quality': assess_data_quality(ecg_data)
#     }
    
#     return analysis_results

# def ml_ecg_analysis(request, pk):
#     try:
#         # Retrieve ECG data
#         ecgs = ECG.objects.filter(patient__pk=pk).order_by('timestamp')
        
#         if not ecgs.exists():
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'No ECG data found for this patient'
#             }, status=404)
        
#         # Convert ECG data to list of dictionaries
#         patient_data = [
#             {'Timestamp': ecg.timestamp, 'ECG Value': ecg.ecg_data} 
#             for ecg in ecgs
#         ]
        
#         # Perform comprehensive analysis
#         analysis_results = comprehensive_ecg_analysis(patient_data)
        
#         # Determine overall heart condition
#         heart_condition = assess_overall_heart_condition(analysis_results)
        
#         response_data = {
#             'patient_id': pk,
#             'heart_condition': heart_condition,
#             'detailed_analysis': analysis_results
#         }
        
#         return JsonResponse(response_data)
    
#     except Exception as e:
#         return JsonResponse({
#             'error': str(e),
#             'message': 'Advanced ECG analysis failed'
#         }, status=400)

# def assess_overall_heart_condition(analysis_results):
#     """
#     Determine overall heart condition based on analysis results
#     """
#     risk_factors = [
#         analysis_results['atrial_fibrillation_risk'],
#         analysis_results['st_segment_status'],
#         analysis_results['arrhythmia_detection']
#     ]
    
#     high_risk_conditions = [
#         "High Likelihood of Atrial Fibrillation",
#         "Potential Myocardial Ischemia",
#         "Tachycardia",
#         "Bradycardia"
#     ]
    
#     for condition in risk_factors:
#         if any(high_risk in condition for high_risk in high_risk_conditions):
#             return "High Risk - Immediate Medical Attention Required"
    
#     return "Normal - No Significant Cardiac Abnormalities Detected"

# # Note: The following functions are placeholder implementations
# # They would require more complex signal processing techniques in a real-world scenario
# def bandpass_filter(ecg_data):
#     return ecg_data  # Placeholder for actual filtering

# def detect_r_peaks(ecg_data):
#     # Simplified R peak detection
#     return np.where(np.diff(np.sign(np.diff(ecg_data))) == -2)[0]

# def extract_st_segment(ecg_data):
#     # Placeholder for ST segment extraction
#     return ecg_data

# def calculate_st_deviation(st_segment):
#     # Placeholder for ST deviation calculation
#     return np.std(st_segment)

# def calculate_heart_rate(r_peaks):
#     # Calculate heart rate from R-R intervals
#     return 60 / np.mean(np.diff(r_peaks))

# def assess_data_quality(ecg_data):
#     """
#     Assess the quality of ECG recording
#     """
#     noise_level = np.std(np.diff(ecg_data))
    
#     if noise_level < 0.1:
#         return "High Quality Recording"
#     elif noise_level < 0.5:
#         return "Moderate Quality Recording"
#     else:
#         return "Low Quality Recording - Potential Interference"



from django.shortcuts import render
from django.http import JsonResponse
from .models import ECG  # Make sure to import your ECG model

def ml_ecg_analysis(request, pk):
    try:
        # Retrieve ECG data for specific patient
        ecgs = ECG.objects.filter(patient__pk=pk).order_by('timestamp')
        
        # Check if any ECG data exists
        if not ecgs.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'No ECG data found for this patient'
            }, status=404)
        
        # Basic analysis - calculate some simple metrics
        analysis_results = {
            'total_readings': ecgs.count(),
            'first_reading': ecgs.first().ecg_data,
            'last_reading': ecgs.last().ecg_data,
            'min_value': min(ecg.ecg_data for ecg in ecgs),
            'max_value': max(ecg.ecg_data for ecg in ecgs),
            'average_reading': sum(ecg.ecg_data for ecg in ecgs) / ecgs.count()
        }
        
        # Categorize basic heart condition (extremely simple logic)
        if analysis_results['average_reading'] > 2000:
            heart_condition = 'Potential Abnormality'
        else:
            heart_condition = 'Normal'
        
        # Prepare response
        response_data = {
            'patient_id': pk,
            'heart_condition': heart_condition,
            'analysis': analysis_results
        }
        
        return JsonResponse(response_data)
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'ECG analysis failed'
        }, status=400)
        
        
        
        
        
# import numpy as np
# import pandas as pd
# from django.shortcuts import render
# from django.http import JsonResponse
# from scipy import signal
# import tensorflow as tf
# from sklearn.preprocessing import StandardScaler

# def ml_ecg_analysis(request, pk):
#     """
#     Django view for ECG machine learning analysis
    
#     Args:
#         request: HTTP request
#         pk: Patient primary key
    
#     Returns:
#         JsonResponse with ECG analysis results
#     """
#     try:
#         # Retrieve ECG data for specific patient
#         ecgs = ECG.objects.filter(patient__pk=pk).order_by('timestamp')
        
#         # Convert QuerySet to pandas DataFrame
#         ecg_data = pd.DataFrame(list(ecgs.values('timestamp', 'ecg_value')))
        
#         # Preprocess ECG data
#         processed_data = preprocess_ecg_data(ecg_data)
        
#         # Extract features
#         features = extract_features(processed_data)
        
#         # Load pre-trained ML model (replace with your actual model)
#         model = load_ml_model()
        
#         # Predict heart condition
#         prediction = model.predict(features)
        
#         # Interpret results
#         heart_condition = interpret_results(prediction)
        
#         # Prepare response
#         response_data = {
#             'patient_id': pk,
#             'heart_condition': heart_condition,
#             'risk_level': calculate_risk_level(prediction),
#             'features': features
#         }
        
#         return JsonResponse(response_data)
    
#     except Exception as e:
#         return JsonResponse({
#             'error': str(e),
#             'message': 'ECG analysis failed'
#         }, status=400)

# def preprocess_ecg_data(data):
#     """
#     Preprocess ECG data
    
#     Args:
#         data: Pandas DataFrame with ECG readings
    
#     Returns:
#         Processed ECG data
#     """
#     # Convert timestamp to numerical feature
#     data['timestamp_numeric'] = pd.to_datetime(data['timestamp']).astype(int) // 10**9
    
#     # Normalize ECG values
#     scaler = StandardScaler()
#     data['ecg_normalized'] = scaler.fit_transform(data[['ecg_value']])
    
#     # Apply band-pass filter
#     b, a = signal.butter(4, [0.5, 45], btype='bandpass', fs=1000)
#     data['ecg_filtered'] = signal.filtfilt(b, a, data['ecg_value'])
    
#     return data

# def extract_features(data):
#     """
#     Extract statistical features from ECG data
    
#     Args:
#         data: Preprocessed ECG data
    
#     Returns:
#         Dictionary of extracted features
#     """
#     features = {
#         'mean': np.mean(data['ecg_value']),
#         'std': np.std(data['ecg_value']),
#         'rms': np.sqrt(np.mean(np.square(data['ecg_value']))),
#         'peak_to_peak': np.max(data['ecg_value']) - np.min(data['ecg_value']),
#         'variance': np.var(data['ecg_value']),
#         'skewness': data['ecg_value'].skew(),
#         'kurtosis': data['ecg_value'].kurtosis()
#     }
    
#     return features

# def load_ml_model():
#     """
#     Load pre-trained machine learning model
    
#     Returns:
#         Trained ML model
#     """
#     # Replace with your actual model loading logic
#     model = tf.keras.models.load_model('path/to/your/trained/model.h5')
#     return model

# def interpret_results(prediction):
#     """
#     Interpret ML model predictions
    
#     Args:
#         prediction: Model prediction results
    
#     Returns:
#         Interpreted heart condition
#     """
#     condition_map = {
#         0: 'Normal',
#         1: 'Atrial Fibrillation',
#         2: 'Potential Heart Risk'
#     }
    
#     # Assume prediction is a class index
#     return condition_map.get(np.argmax(prediction), 'Unknown')

# def calculate_risk_level(prediction):
#     """
#     Calculate heart condition risk level
    
#     Args:
#         prediction: Model prediction results
    
#     Returns:
#         Risk level string
#     """
#     risk_levels = {
#         0: 'Low Risk',
#         1: 'Moderate Risk',
#         2: 'High Risk'
#     }
    
#     return risk_levels.get(np.argmax(prediction), 'Undetermined')
    