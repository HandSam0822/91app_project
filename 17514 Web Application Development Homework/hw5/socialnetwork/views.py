from email import contentmanager
from urllib import request
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from .forms import LoginForm, ProfileForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from socialnetwork.models import *
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.utils import timezone



def coldstart_action(request):
    return HttpResponseRedirect('socialnetwork/login')

@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

"""render profile page"""
@login_required
def profile_action(request):    
    context = {}
    if request.method == 'GET':                   
        context = {'form': ProfileForm(initial={"bio": request.user.profile.bio}),
                   'profile': request.user.profile
        }
        
        return render(request, 'socialnetwork/profile.html', context)
    
    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context = {'profile' : request.user.profile, 'form': form}
        return render(request, "socialnetwork/profile.html", context)    
  
    
    profile = request.user.profile        
    profile.picture = form.cleaned_data['picture']    
    profile.bio = form.cleaned_data['bio']
    profile.content_type = form.cleaned_data['picture'].content_type
    profile.save()
    return redirect(reverse("profile"))    
    
"""render global stream by fetching all posts in database"""
@login_required
def home_action(request):
    context = {}
    if request.method == 'GET':                
        context['posts'] = Post.objects.all().order_by('-creation_time')        
        return render(request, 'socialnetwork/global.html', context)
    else:      
        if 'post_text' not in request.POST or not request.POST['post_text']:
            context['error'] = "Text can't be empty."
            return render(request, 'socialnetwork/global.html', context)
        
        # eastern = timezone('US/Eastern')
        # print(datetime.now(tz))
                
        new_post = Post(text=request.POST['post_text'], 
                        user=request.user, 
                        creation_time = timezone.localtime(timezone.now()))            
        new_post.save()
        return redirect(reverse('home'))        
    

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
    
    new_profile = Profile(user = new_user, bio="")

    
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    new_user.save()
    new_profile.save()
    login(request, new_user)
    return redirect(reverse('home'))


@login_required
def other_action(request, id):   
    user = get_object_or_404(User, id=id)
    if request.method == "GET":        
        return render(request, "socialnetwork/other.html", {'profile': user.profile}) 
    
    if "follow" in request.POST:
        follow(request, id)
        print("Follllow")
    else:
        unfollow(request, id)
        print("UnFollllow")
    
    return render(request, 'socialnetwork/other.html', {"profile": user.profile})

@login_required
def get_photo(request, id):    
    profile = get_object_or_404(Profile, id=id)
    if not profile.picture:
        raise Http404

    return HttpResponse(profile.picture, content_type=profile.content_type)


@login_required
def follow(request, id):    
    user_to_follow = get_object_or_404(User, id=id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()     
        


@login_required
def unfollow(request, id):    
    user_to_unfollow = get_object_or_404(User, id=id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()
        

@login_required
def follower_action(request):
    # retrieve all global post
    follower_post = []
    if request.method == 'GET':      
        following = request.user.profile.following.all()
        all_post = Post.objects.all()
        for post in all_post:
            if post.user in following:
                follower_post.append(post)   
        follower_post.sort(reverse = True, key = lambda post : post.creation_time)

        return render(request, 'socialnetwork/follower.html', {
            "posts": follower_post
        })
