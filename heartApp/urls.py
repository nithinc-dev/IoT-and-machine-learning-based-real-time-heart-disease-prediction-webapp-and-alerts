from django.urls import path
from . import views
from django.urls import path
from .views import LocationAPI


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),  # Added trailing slash
    path('map', views.map, name='map'), 
    path('all', views.ProfilesListView.as_view(), name = "all_profiles"),
    path('all/<int:pk>', views.ProfileDetailView.as_view(), name = 'single_patient_profile'),
    path('dash', views.pundash, name = 'dash'),
    path('api/ecg/', views.ecg_create, name='ecg_create'),
    
    path('map1',views.location_tracker_view, name = 'location_tracker'),
    
    # Doctor URLs
    path('doctor/signup/', views.doctor_signup_view, name='doctor_signup'),
    path('doctor/login/', views.doctor_login_view, name='doctor_login'),
    path('doctor/logout/', views.doctor_logout_view, name='doctor_logout'),
    path('doctor/dashboard/', views.doctor_dashboard_view, name='doctor_dashboard'),
    
    
    path('api/location/', LocationAPI.as_view(), name='location-api'),
    
    
    path('map2',views.role_selection_view, name='role_map'),
    
    
    path('ecgs', views.PatientsECGListView.as_view(), name = "all_ecgs"),
    path('ecgs/<int:pk>', views.ecgDetail, name = 'single_patient_ecg'),
    
    path('ecgcsv/<int:pk>', views.ecgcsv),
    
    path('s', views.success),

]