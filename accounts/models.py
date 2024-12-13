# from django.db import models
# from django.contrib.auth.models import AbstractUser, BaseUserManager


# from django.contrib.auth.models import AbstractUser
# from django.db import models

# from django.db import models
# from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission

# class CustomerManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

# class Customer(AbstractUser):
#     email = models.EmailField(unique=True)
    
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []
    
#     objects = CustomerManager()
    
#     groups = models.ManyToManyField(
#         Group,
#         related_name='customer_set',
#         blank=True,
#         verbose_name='groups'
#     )
    
#     user_permissions = models.ManyToManyField(
#         Permission,
#         related_name='customer_set',
#         blank=True,
#         verbose_name='user permissions'
#     )
    
#     def __str__(self):
#         return self.email


# class CustomerManager(BaseUserManager):
#     def create_user(self, username, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         # Remove username from create_user method
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

# class Customer(AbstractUser):
#     email = models.EmailField(unique=True)
    
#     USERNAME_FIELD = 'email'  # Change this to email
#     REQUIRED_FIELDS = []  # Remove 'email' as it's already the USERNAME_FIELD
    
#     objects = CustomerManager()
    
#     def __str__(self):
#         return self.email  # or self.username if you want

# class CustomerManager(BaseUserManager):
#     def create_user(self, username, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(username=username, email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

# class Customer(AbstractUser):
#     email = models.EmailField(unique=True)
    
#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['email']
    
#     objects = CustomerManager()

#     def __str__(self):
#         return self.username