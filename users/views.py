from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from expenses.models import Budget
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

# Create your views here.

# Make sure to create 'users/templates/users/register.html' and 'users/templates/users/login.html' for the registration and login forms.
# Registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Change 'home' to your desired redirect URL
    else:
        form = UserCreationForm()
    return render(request, 'users/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  # Redirect to user-specific dashboard
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'users/dashboard.html', {'user': request.user})

def home(request):
    return render(request, 'users/home.html')





    
