from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from dashboard.models import AllUsers
import jwt
import os
from datetime import datetime, timedelta

SCREATE = os.getenv('SCREATE')

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
                messages.error(request, "This email is already being used.", extra_tags="danger")   
                return render(request, 'auth/register.html')
            
            # Ensures the passwords match.
            if password1!=password2:
                messages.error(request, "Your passwords do not match.", extra_tags="danger")
                return render(request, 'auth/register.html')
            
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

def forgot_password(request):
    """Function to send an email to a user with a link that allows them reset their password if they have forgotten it"""
    # Checks if the user is already authenticated and redirects them to the homepage if true.
    if request.user.is_authenticated:
         return redirect('/')
    
    # Process the form submission to get the user's email and send the password reset email.
    if request.method == "POST":
        email = request.POST.get("email")
        user = AllUsers.objects.filter(email=email).first()

        # Check if the email exists in the system.
        if user is not None:
            # Notify user about the password reset email if their account exists.
            messages.info(request, "An email has been sent to you with instructions on how to reset your password.", extra_tags="secondary")

            # Create a JWT token that expires in 1 hour.
            jwt_token = jwt.encode({"id": user.id, "exp": datetime.now() + timedelta(hours=1)}, SCREATE, algorithm="HS256")
            link = f"https://synbiosource-04151ad4f184.herokuapp.com/reset-password/{jwt_token}"

            # Send password reset email.
            send_mail(
                'Password Reset',
                f'Please use the following link to reset your password: {link}. Note that this link will expire in 1 hour.',
                os.getenv('EMAIL_HOST_USER'),  # From email.
                [user.email],                 # Recipient.
                fail_silently=False,
            )

            return redirect('/forgot-password')
        else:
            # Inform user if the email is not found in the system.
            messages.error(request, "The email provided does not exist in our system.", extra_tags="danger")
            return redirect('/forgot-password')
    
    # Render the forgot password page.
    return render(request, 'auth/forgot_password.html')

def reset_password(request,token):
    """Function that allows a user to reset their password using a secure token."""
    # Handle the form submission for POST requests.
    if request.method == "POST":
        try:
            # Decode the JWT token to verify its authenticity and get the user ID.
            decoded_token = jwt.decode(token, SCREATE, algorithms=["HS256"])
            user_id = decoded_token["id"]
            exp_time = decoded_token["exp"]

            # Check if the token has expired based on the current time.
            if datetime.now() > datetime.fromtimestamp(exp_time):
                messages.error(request, "The token has expired, please go back and request another link.", extra_tags="danger")
            else:
                # Retrieve the new password and confirmation from the POST data.
                password = request.POST.get("new_password")
                confirm_password = request.POST.get("confirm_password")

                # Check if the new password and confirmation match.
                if password != confirm_password:
                    messages.error(request, "Your passwords do not match.", extra_tags="danger")
                else:
                    # Retrieve the user by ID, set the new password, and save the user object.
                    user = AllUsers.objects.get(id=user_id)
                    user.set_password(password)
                    user.save()

                    # Notify the user of successful password reset.
                    messages.info(request, "Password has been reset successfully, you can now log in.", extra_tags="secondary")

                    # Redirect to the login page.
                    return redirect('/login')
        except:
            # Handle any exceptions that occur during processing.
            messages.error(request, "Something went wrong.", extra_tags="danger")

        # Redirect back to the reset password page if there were issues.
        return redirect('/reset-password/' + token)

    # Render the reset password form.
    return render(request, 'auth/reset_password.html')