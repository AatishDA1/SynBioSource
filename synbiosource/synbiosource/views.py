from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from dashboard.models import AllUsers

def index(request):
    """Function to load the home page and process any logout requests."""
    if request.method == "POST":
            logout(request)
            return render(request, 'public/index.html', {"message":"You are now logged out."})
    return render(request, 'public/index.html')

def login_user(request):
    """Function to log a user in."""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            request.session['email']=email;
            request.session['is_moderator']=user.is_user_moderator()
            request.session['id']=user.get_id()
            request.session['full_name']=user.full_name
            return redirect('/')
        else:
            return render(request, 'auth/login.html', {"error":"There was an error logging in, please try again."})
    else:
        return render(request, 'auth/login.html', {})
    
def register_user(request):
    """Function to register a user."""
    if request.method == "POST":
            fullname =request.POST.get('fullname')
            email =request.POST.get('email')
            password1 =request.POST.get('password1')
            password2 =request.POST.get('password2')
            print('fullname=>',fullname)
            if AllUsers.objects.filter(email=email).exists():
                print("This email is already being used.")
                return render(request,  'auth/register.html',{"error":"This email is already being used."})
            if password1!=password2:
                print("Your passwords do not match.")
                return render(request, 'auth/register.html', {"error":"The passwords do not match."})
            user=AllUsers.objects.create(
               full_name=fullname,
               email=email, 
            )
            user.set_password(password1)
            user.save()
            login(request, user)
            request.session['email']=email;
            request.session['is_moderator']=user.is_user_moderator()
            request.session['id']=user.get_id()
            request.session['full_name']=user.full_name
            return redirect('/')
    else:
        form = UserCreationForm()

    return render(request, 'auth/register.html', {
        'form':form,
        })