import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Patient, ECG
from django.utils import timezone

class ECGConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract patient ID from URL
        self.patient_id = self.scope['url_route']['kwargs']['patient_id']
        self.room_group_name = f'ecg_{self.patient_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Handle incoming WebSocket messages here
        data = json.loads(text_data)
        
        # Save the ECG data to the database
        await self.save_ecg_data(data)
        
        # Optionally, send the data back to WebSocket
        await self.send_ecg_data(data)

    async def send_ecg_data(self, data):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'data': data
        }))
    
    @sync_to_async
    def save_ecg_data(self, data):
        try:
            # Ensure patient exists
            patient = Patient.objects.get(id=self.patient_id)
            
            # Create ECG reading
            ECG.objects.create(
                patient=patient,
                ecg_data=data.get('ecg_data', 0),
                timestamp=timezone.now()
            )
        except Patient.DoesNotExist:
            print(f"Patient {self.patient_id} not found")
        except Exception as e:
            print(f"Error saving ECG data: {e}")

















# import json
# import asyncio
# import channels.layers
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from .models import Patient, ECG
# from django.utils import timezone

# class ECGConsumer(AsyncWebsocketConsumer):
#     # async def connect(self):
#     #     # Extract patient ID from URL
#     #     self.patient_id = self.scope['url_route']['kwargs']['patient_id']
#     #     self.room_group_name = f'ecg_{self.patient_id}'
        
#     #     # Join room group
#     #     await self.channel_layer.group_add(
#     #         self.room_group_name,
#     #         self.channel_name
#     #     )
        
#     #     await self.accept()
#     async def connect(self):
#         # Extract patient ID from URL
#         self.patient_id = self.scope['url_route']['kwargs']['patient_id']
#         self.room_group_name = f'ecg_{self.patient_id}'
        
#         # Join room group
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
        
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     async def receive(self, text_data):
#         # Handle incoming WebSocket messages here
#         data = json.loads(text_data)
#         # You can save the ECG data or process it here
        
#     async def send_ecg_data(self, data):
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'data': data
#         }))
#     async def send_ecg_data(self, data):
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'data': data
#         }))
#     # async def connect(self):
#     #     self.patient_id = self.scope['url_route']['kwargs']['patient_id']
#     #     self.room_group_name = f'ecg_{self.patient_id}'

#     #     # Debugging connection
#     #     print(f"WebSocket connected for patient_id: {self.patient_id}")

#     #     # Join room group
#     #     await self.channel_layer.group_add(
#     #         self.room_group_name,
#     #         self.channel_name
#     #     )
#     #     await self.accept()
#     # async def disconnect(self, close_code):
#     #     # Leave room group
#     #     await self.channel_layer.group_discard(
#     #         self.room_group_name,
#     #         self.channel_name
#     #     )

#     # async def receive(self, text_data):
#     #     # Parse received data
#     #     data = json.loads(text_data)
        
#     #     # Save ECG data
#     #     await self.save_ecg_data(data)
        
#     #     # Broadcast to group
#     #     await self.channel_layer.group_send(
#     #         self.room_group_name,
#     #         {
#     #             'type': 'ecg_data',
#     #             'data': data
#     #         }
#     #     )

#     # async def ecg_data(self, event):
#     #     # Send message to WebSocket
#     #     await self.send(text_data=json.dumps(event['data']))







#     @sync_to_async
#     def save_ecg_data(self, data):
#         try:
#             # Ensure patient exists
#             patient = Patient.objects.get(id=self.patient_id)
            
#             # Create ECG reading
#             ECG.objects.create(
#                 patient=patient,
#                 ecg_data=data.get('ecg_data', 0),
#                 timestamp=timezone.now()
#             )
#         except Patient.DoesNotExist:
#             print(f"Patient {self.patient_id} not found")
#         except Exception as e:
#             print(f"Error saving ECG data: {e}")










# # import json
# # import asyncio
# # import channels.layers
# # from channels.generic.websocket import AsyncWebsocketConsumer
# # from asgiref.sync import sync_to_async
# # from .models import Patient, ECG
# # import time
# # from django.utils import timezone

# # class ECGConsumer(AsyncWebsocketConsumer):
# #     async def connect(self):
# #         # Extract patient ID from URL
# #         self.patient_id = self.scope['url_route']['kwargs']['patient_id']
# #         self.room_group_name = f'ecg_{self.patient_id}'

# #         # Join room group
# #         await self.channel_layer.group_add(
# #             self.room_group_name,
# #             self.channel_name
# #         )
# #         await self.accept()

# #     async def disconnect(self, close_code):
# #         await self.channel_layer.group_discard(
# #             self.room_group_name,
# #             self.channel_name
# #         )

# #     async def receive(self, text_data):
# #         data = json.loads(text_data)
        
# #         # Save ECG data
# #         await self.save_ecg_data(data)

# #         # Broadcast to group
# #         await self.channel_layer.group_send(
# #             self.room_group_name,
# #             {
# #                 'type': 'ecg_data',
# #                 'data': data
# #             }
# #         )

# #     async def ecg_data(self, event):
# #         # Send message to WebSocket
# #         await self.send(text_data=json.dumps(event['data']))

# #     @sync_to_async
# #     def save_ecg_data(self, data):
# #         patient = Patient.objects.get(id=self.patient_id)
# #         ECG.objects.create(
# #             patient=patient,
# #             ecg_data=data['ecg_data'],
# #             timestamp=timezone.now()
# #         )