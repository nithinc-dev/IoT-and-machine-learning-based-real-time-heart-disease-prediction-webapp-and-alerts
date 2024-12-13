from django import forms
from .models import Patient, Disease, Doctor

# class PatientForm(forms.ModelForm):
#     doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())
#     class Meta:
#         model = Patient
#         fields = ['name', 'age', 'dob', 'gender', 'profile_picture', 'doctor', 'diseases']
#         widgets = {
#             'dob': forms.SelectDateWidget(years=range(1900, 2025)),
#             'gender': forms.Select(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")]),
#             'diseases': forms.CheckboxSelectMultiple,
            
#         }


from django import forms
from .models import Patient, Doctor, Disease

class PatientForm(forms.ModelForm):
    # doctor = forms.ModelChoiceField(queryset=Doctor.objects.all(), label="Select your docctor")
    # diseases = forms.ModelMultipleChoiceField(
    #     queryset=Disease.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    # )
    doctor = forms.ModelMultipleChoiceField(queryset=Doctor.objects.all(), label="Select your docctor")
    #doctor = forms.CharField(max_length=250, label="enter your doctors name")
    diseases = forms.ModelMultipleChoiceField(
        queryset=Disease.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        # required=False,
    )
    patient_email = forms.CharField(max_length=50, label="Enter patient's email address")
    care_taker_email1 = forms.CharField(max_length=50, label="Enter primary care-taker's email address")
    care_taker_email2 = forms.CharField(max_length=50, label="Enter  secondary care-taker's email address")
    doctor_email = forms.CharField(max_length=50, label="Enter doctor's email address")
    patient_key = forms.CharField(max_length=50, label="Enter patient id")
    
    class Meta:
        model = Patient
        fields = [
            'name',
            'age',
            'dob',
            'gender',
            'profile_picture',
            'doctor',
            'diseases',
            'patient_email',
            'patient_key',
            'care_taker_email1',
            'care_taker_email2',
            'doctor_email',
        ]
        widgets = {
            'dob': forms.SelectDateWidget(years=range(1900, 2025)),
            'gender': forms.Select(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")]),
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'patient_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'care_taker_email1': forms.EmailInput(attrs={'class': 'form-control'}),
            'care_taker_email2': forms.EmailInput(attrs={'class': 'form-control'}),
            'doctor_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'patient_key': forms.TextInput(attrs={'class': 'form-control'}),
        }


      
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Doctor

class DoctorSignUpForm(UserCreationForm):
    class Meta:
        model = Doctor
        fields = ['name', 'email', 'qualification', 'hospital', 'password1', 'password2']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user  
    
from django import forms
from django.contrib.auth import authenticate
from .models import Doctor

class DoctorLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None or not isinstance(user, Doctor):
                raise forms.ValidationError("Invalid email or password.")
        
        return cleaned_data
# from django import forms
# from .models import *
# from django.utils import timezone

# class PatientForm(forms.Form):
#     patient_name = forms.CharField(max_length=100, label="Enter the patient name")
#     dob = forms.DateField(
#     widget=forms.SelectDateWidget(years=range(1900, 2025)), 
#     label="Date of birth"
# )
#     age = forms.IntegerField()
#     gender = forms.ChoiceField(choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")])  # Added choices
#     profile_picture = forms.ImageField()
#     diseases = forms.ModelMultipleChoiceField(
#         queryset=Disease.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=True,
#         label="Diseases"  # Changed from "Project Languages"
#     )
#     doctor = forms.ModelChoiceField(queryset=Doctor.objects.all())  # Corrected 'doctor' to 'Doctor'


# class PatientForm(forms.Form):
#     patient_name = forms.CharField(max_length=100, label="Enter the patient name")
#     dob = forms.DateField(widget=forms.SelectDateWidget, label="Date of birth")
#     age = forms.PositiveIntegerField()
#     gender = forms.ChoiceField()#drop down choice
#     profile_picture = forms.ImageField()
#     diseases = forms.ModelMultipleChoiceField(
#         queryset=Disease.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         required=True,
#         label="Project Languages"
#     )
#     doctor = forms.ModelChoiceField(queryset=doctor.objects.all())
    
    # def save(self):
    #     if not self.is_valid():
    #         raise ValueError("The form contains invalid data")
        
    #     patient = Patient.objects.create(name=self.cleaned_data['patient_name'],
    #                                      age=self.cleaned_data['age'],
    #                                      dob= self.cleaned_data['dob'],
    #                                      gender=self.cleaned_data['gender'], profile picture)
        
    #     for disease in self.cleaned_data['diseases']:
    #         patient.diseases.add(disease)
            
    #     patient.doctor.add(self.cleaned_data['doctor'])
    
    
    
# forms.py
from django import forms

class RoleSelectionForm(forms.Form):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('caretaker', 'Caretaker')
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, label="Select Role")
    special_key = forms.CharField(max_length=100, widget=forms.PasswordInput, label="Enter Special Key")
   