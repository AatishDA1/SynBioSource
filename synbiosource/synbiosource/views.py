from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
# Create your views here.

def login_user(request):
    """Function to log a user in."""
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            request.sessions['email']=email;
            request.sessions['is_moderator']=user.is_user_moderator()
            request.sessions['id']=user.get_id()
            return redirect('index')
        else:
            messages.success(request, ("There was an error logging in, please try again."))
            return redirect('login')
    else:
        return render(request, 'auth/login.html', {})
    
def logout_user(request):
    """Function to log a user out."""
    logout(request)
    messages.success(request, ("You are now logged out."))
    return redirect('index')

def register_user(request):
    """Function to register a user."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(username=email, password=password)
            login(request, user)
            messages.success(request, ("Registration Successful"))
            return redirect('index')
    else:
        form = UserCreationForm()

    return render(request, 'auth/register.html', {
        'form':form,
        })