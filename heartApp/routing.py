from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/ecg/(?P<patient_id>\d+)/$', consumers.ECGConsumer.as_asgi()),
]






# from django.urls import re_path
# from . import consumers

# websocket_urlpatterns = [
#     re_path(
#         r'ws/ecg/(?P<patient_id>\d+)/$', 
#         consumers.ECGConsumer.as_asgi()
#     ),
# ]



