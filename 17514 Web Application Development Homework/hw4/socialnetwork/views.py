from email import contentmanager
from multiprocessing import context
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .forms import EntryForm, LoginForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required

def coldstart_action(request):
    return HttpResponseRedirect('socialnetwork/home')

@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

"""render profile page"""
@login_required
def profile_action(request):
    if request.method == 'GET':
        return render(request, 'socialnetwork/profile.html', {})
    
"""render global stream by fetching all posts in database"""
@login_required
def home_action(request):
    context = {}
    if request.method == 'GET':        
        return render(request, 'socialnetwork/global.html', context)
    else:        
        return render(request, 'socialnetwork/global.html', context)
    

def login_action(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()        
        return render(request, 'socialnetwork/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('home'))


@login_required
def follower_action(request):
    if request.method == 'GET':
        return render(request, 'socialnetwork/follower.html', {})

@login_required
def getLBJ_action(request):
    return render(request, "socialnetwork/LBJ.html")


