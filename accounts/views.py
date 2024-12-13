# # accounts/views.py
# from django.shortcuts import render, redirect
# from django.contrib.auth import login, authenticate, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .forms import UserSignUpForm, UserUpdateForm
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserSignUpForm, UserUpdateForm

def signup_view(request):
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Successfully signed up!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserSignUpForm()
    
    # return render(request, 'accounts/signup.html', {'form': form})
    return render(request, 'base.html', {'form': form})
    

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Successfully logged in! Welcome {user.username}')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    # return render(request, 'accounts/login.html')
    return render(request, 'base.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Successfully logged out! the user ')
    return redirect('login')
# def signup_view(request):
#     if request.method == 'POST':
#         form = UserSignUpForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             messages.success(request, 'Successfully signed up!')
#             return redirect('home')
#     else:
#         form = UserSignUpForm()
#     return render(request, 'accounts/signup.html', {'form': form})


# from .models import Customer

# def signup_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         email = request.POST['email']
        
#         # Check if username or email already exists
#         if Customer.objects.filter(username=username).exists():
#             messages.error(request, 'Username already exists.')
#             return render(request, 'accounts/signup.html')
        
#         if Customer.objects.filter(email=email).exists():
#             messages.error(request, 'Email already exists.')
#             return render(request, 'accounts/signup.html')
        
#         # Create new customer
#         customer = Customer.objects.create_user(
#             username=username, 
#             email=email,
#             password=password
#         )
        
#         login(request, customer)
#         messages.success(request, 'Successfully signed up!')
#         return redirect('home')
    
#     return render(request, 'accounts/signup.html')


# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             messages.success(request, 'Successfully logged in!')
#             return redirect('home')
#         else:
#             messages.error(request, 'Invalid username or password.')
#     return render(request, 'accounts/login.html')


# def signup_view(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         username = request.POST['username']
#         password = request.POST['password']
       
#         # Check if username or email already exists
#         if Customer.objects.filter(email=email).exists():
#             messages.error(request, 'Email already exists.')
#             return render(request, 'accounts/signup.html')
       
#         # Create new customer
#         customer = Customer.objects.create_user(
#             username=username,
#             email=email,
#             password=password
#         )
       
#         login(request, customer)
#         messages.success(request, 'Successfully signed up!')
#         return redirect('home')
   
#     return render(request, 'accounts/signup.html')

# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST['email']  # Change from username to email
#         password = request.POST['password']
#         user = authenticate(request, username=email, password=password)
#         if user is not None:
#             login(request, user)
#             messages.success(request, 'Successfully logged in!')
#             return redirect('home')
#         else:
#             messages.error(request, 'Invalid email or password.')
#     return render(request, 'accounts/login.html')


# @login_required
# def profile_view(request):
#     if request.method == 'POST':
#         form = UserUpdateForm(request.POST, instance=request.user)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Profile updated successfully!')
#             return redirect('profile')
#     else:
#         form = UserUpdateForm(instance=request.user)
#     return render(request, 'accounts/profile.html', {'form': form})

# def logout_view(request):
#     logout(request)
#     messages.success(request, 'Successfully logged out!')
#     return redirect('login')

