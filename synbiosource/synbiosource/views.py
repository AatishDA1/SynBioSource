from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from dashboard.models import AllUsers

def index(request):
    """Function to load the home page."""
    return render(request, 'public/index.html')

def login_user(request):
    """Function to log a user in and if they are logged in prevent them from doing so again until they logout."""
    # Check if the user is already authenticated and redirect to homepage if true.
    if request.user.is_authenticated:
         return redirect('/')
    
    # Handles the login logic for POST requests.
    if request.method == "POST":
        # Extracts email and password from POST request.
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticates the user.
        user = authenticate(request, username=email, password=password)
        if user is not None:
            # If authentication is successful, logs the user in and set session variables.
            login(request, user)
            request.session['email'] = email;
            request.session['is_moderator'] = user.is_user_moderator()
            request.session['id'] = user.get_id()
            request.session['full_name'] = user.full_name
            return redirect('/')
        else:
            # If authentication fails, renders the login page with an error message.
            return render(request, 'auth/login.html', {"error":"There was an error logging in, please try again."})
    else:
        # For non-POST requests, renders the login page without an error message.
        return render(request, 'auth/login.html', {})

def logout_user(request):
    """Function to logout the user."""
    logout(request)
    return redirect('/')

def register_user(request):
    """Function to register a user then log them in. It also prevents them from signing-up again if they are already logged in."""
    # Checks if the user is already authenticated and redirect to the homepage if true.
    if request.user.is_authenticated:
         return redirect('/')
    
    # Processes the form submission for a POST request.
    if request.method == "POST":
            # Extracts user input from the form.
            fullname =request.POST.get('fullname')
            email =request.POST.get('email')
            password1 =request.POST.get('password1')
            password2 =request.POST.get('password2')
            
            # Checks if the email is already used by another account.
            if AllUsers.objects.filter(email=email).exists():
                print("This email is already being used.")
                return render(request,  'auth/register.html',{"error":"This email is already being used."})
            
            # Ensures the passwords match.
            if password1!=password2:
                print("Your passwords do not match.")
                return render(request, 'auth/register.html', {"error":"The passwords do not match."})
            
            # Creates a new user object with the provided details.
            user=AllUsers.objects.create(
               full_name=fullname,
               email=email, 
            )
            user.set_password(password1)
            user.save()

            # Logs the user in and set session variables.
            login(request, user)
            request.session['email']=email;
            request.session['is_moderator']=user.is_user_moderator()
            request.session['id']=user.get_id()
            request.session['full_name']=user.full_name
            
            # Redirects to the homepage after successful registration and login.
            return redirect('/')
    else:
        # For non-POST requests, instantiates and provides a blank form.
        form = UserCreationForm()

    # Renders the registration page with the form.
    return render(request, 'auth/register.html', {
        'form':form,
        })