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
import json
from django.core.serializers.json import DjangoJSONEncoder
import pytz

"""
@login_required in the <add_comment> and <add_follower_comment> should be removed
because it would cause error in <_my_json_error_response>, and point will be dedcuted.
But in reality, it should be added.
"""
local_tz = pytz.timezone('US/Eastern') 

"""Redirect users to home page if url is "" """
def coldstart_action(request):
    return HttpResponseRedirect('socialnetwork/home')

"""Logout account and redirect to login page"""
@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

"""If request.method == 'GET', render profile page with ProfileForm,
If request.method == 'POST', 
1. check data in the form is valid 
2. parse data from request.POST 
3. update request.user.profile 
4. render profile page
"""
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

    context = {'form': ProfileForm(initial={"bio": request.user.profile.bio}),
              'profile': request.user.profile
              }
    return render(request, 'socialnetwork/profile.html', context)    
    
"""If request.method == 'GET', render global.html (the posts will be fetch in global.js)
If request.method == 'POST', a new post request is created
1. validation check
2. create a new post and save in database
3. call json dump serializer to update global posts and comments
"""
@login_required
def home_action(request):
    context = {}
    if request.method == 'GET':                
        return render(request, 'socialnetwork/global.html', {})

    if not 'post_text' in request.POST or not request.POST['post_text']:
        context['error'] = "Text can't be empty."
        return render(request, 'socialnetwork/global.html', context)
            
    new_post = Post(text=request.POST['post_text'], 
                    user=request.user, 
                    creation_time = timezone.localtime(timezone.now()))            
    
    new_post.save()
    return get_post_json_dumps_serializer(request)           
    
""" 
1. Validation check (login status -> request method -> valid content -> 
valid post id(not empty / numeric / not out of bound))
2. Create Comment object and save in database
3. Call json dump serializer to update global posts and comments
"""
def add_comment(request):       
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", 405)        
    
    if not 'comment_text' in request.POST or not request.POST['comment_text']:        
        return _my_json_error_response("Comment can't be empty", 400)
    
    if not 'post_id' in request.POST or not request.POST['post_id']:
        return _my_json_error_response("post_id can't be empty", 400)        
    
    if not request.POST['post_id'].isnumeric():
        return _my_json_error_response("post_id must be numeric", 400)        
    
    if Post.objects.count() < int(request.POST["post_id"]):
        return _my_json_error_response("Can't find any post with post id" + request.POST["post_id"], 400)
    
    # After validation check, create Comment object -> save in database -> call json dump serializer to update global posts and comments
    post = Post.objects.get(id=request.POST["post_id"])
    new_comment = Comment(user=request.user, post = post, 
                        text = request.POST['comment_text'],
                        creation_time = timezone.localtime(timezone.now()))    
    
    new_comment.save()
    return get_post_json_dumps_serializer(request)

"""Do almost the same thing in add_comment except that calling
get_follower_post_json_dumps_serializer to update posts and comments in following page
instead of global page
"""
def add_follower_comment(request):       
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", 405)        
    
    if not 'comment_text' in request.POST or not request.POST['comment_text']:        
        return _my_json_error_response("Comment can't be empty", 400)

    if not 'post_id' in request.POST or not request.POST['post_id']:
        return _my_json_error_response("post_id can't be empty", 400)        
    
    if not request.POST['post_id'].isnumeric():
        return _my_json_error_response("post_id must be numeric", 400)        
    
    
    if Post.objects.count() < int(request.POST["post_id"]):
        return _my_json_error_response("Can't find any post with post id" + request.POST["post_id"], 400)
    
    post = Post.objects.get(id=request.POST["post_id"])
    new_comment = Comment(user=request.user, post = post, 
                        text = request.POST['comment_text'],
                        creation_time = timezone.localtime(timezone.now()))    
    
    new_comment.save()
    return get_follower_post_json_dumps_serializer(request)

"""If request.method == 'GET' render LoginForm 
If request.method == 'POST',
1. Create LoginForm object and filled with data from request.POST
2. Form validation
3. User authentication
4. render global page
"""
def login_action(request):
    context = {}
    # Display empty LoginForm if GET request
    if request.method == 'GET':
        context['form'] = LoginForm()        
        return render(request, 'socialnetwork/login.html', context)

    # Creates a LoginForm with parameter from request.POST
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse("home"))    

"""If request.method == 'GET' render RegisterForm 
If request.method == 'POST',
1. Create RegisterForm object and filled with data from request.POST
2. Form validation
3. User authentication
4. render global page
"""
def register_action(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a RegisterForm with parameter from request.POST
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    
    # Create User objects, save it to the database, and authenticate it for login action
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    
    new_user.save()
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    
    # Create Profile objects, save it to the database (Profile and User has OneToOneRelation)
    new_profile = Profile(user = new_user, bio="")
    new_profile.save()
    login(request, new_user)
    return redirect(reverse("home"))    


""" Check other User's profile
If request.method == 'GET', check the user exist or not(get_object_or_404) 

If request.method == 'POST', it is to follow or unfollow other user
1. if request.POST contains "follow", follow the user, else run unfollow
2. render other's profile page (Button's text will be decided in other.html)
"""
@login_required
def other_action(request, id):   
    user = get_object_or_404(User, id=id)
    if request.method == "GET":                      
        return render(request, "socialnetwork/other.html", {'profile': user.profile}) 
    
    if "follow" in request.POST:
        follow(request, id)        
    else:
        unfollow(request, id)        
    
    return render(request, 'socialnetwork/other.html', {"profile": user.profile})

"""Add userToFollow to request.user's profile list"""
@login_required
def follow(request, id):    
    user_to_follow = get_object_or_404(User, id=id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()     
        

"""reomve userToUnfollow from request.user's profile list"""
@login_required
def unfollow(request, id):    
    user_to_unfollow = get_object_or_404(User, id=id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()

"""other.html will call get_photo to render the profile picture"""
@login_required
def get_photo(request, id):    
    profile = get_object_or_404(Profile, id=id)
    if not profile.picture:
        raise Http404

    return HttpResponse(profile.picture, content_type=profile.content_type)


"""Check the request method is valid, and render posts that 
post by the user's followers
"""
@login_required
def follower_action(request):
    if request.method != 'GET':      
        return _my_json_error_response("You must use a GET request for this operation", 405)        
    
    # retrieve all posts that post by the user's followers
    follower_post = []
    following = request.user.profile.following.all()
    all_post = Post.objects.all()
    for post in all_post:
        if post.user in following:
            follower_post.append(post)   
    follower_post.sort(reverse = True, key = lambda post : post.creation_time)

    return render(request, 'socialnetwork/follower.html', {
        "posts": follower_post
    })
  

"""validate the request and return global post and comment in json format
"""
def get_post_json_dumps_serializer(request):    
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    post_data = []
    posts = Post.objects.all().order_by('creation_time')        
    for post in posts:        
        my_item = {
            "id": post.id,
            "user": {"first_name": post.user.first_name, "last_name": post.user.last_name, "id": post.user.id},
            "text": post.text,            
            "creation_time": utc_to_local(post.creation_time).strftime("%m/%d/%Y %I:%M %p")
        }
        
        post_data.append(my_item)
    
    comment_data = []
    comments = Comment.objects.all().order_by('creation_time')
    for comment in comments:        
        my_item = {
            "id": comment.id,
            "post_id": comment.post.id, 
            "user": {"first_name": comment.user.first_name, "last_name": comment.user.last_name, 
                     "id": comment.user.id},
            "text": comment.text,
            "creation_time": utc_to_local(comment.creation_time).strftime("%m/%d/%Y %I:%M %p")                        
        }
        
        comment_data.append(my_item)
    
    response_data = {
        "posts": post_data,
        "comments": comment_data
    }
    response_json = json.dumps(response_data, cls=DjangoJSONEncoder)
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response

"""validate the request and return follower's post and comment in json format
"""
def get_follower_post_json_dumps_serializer(request):   
    if not request.user.id:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    

    post_data = []
    comment_data = []
    following = request.user.profile.following.all()

    for user in following:
        posts = Post.objects.filter(user = user).order_by('creation_time');
        for post in posts:                
            post_item = {
                "id": post.id,
                "user": {"first_name": post.user.first_name, "last_name": post.user.last_name, "id": post.user.id},
                "text": post.text,                   
                "creation_time": utc_to_local(post.creation_time).strftime("%m/%d/%Y %I:%M %p")                    
                }
            post_data.append(post_item)
            comments = Comment.objects.filter(post=post).order_by('creation_time')
            for comment in comments:
                comment_item = {
                        "id": comment.id,
                        "post_id": comment.post.id, 
                        "user": {"first_name": comment.user.first_name, "last_name": comment.user.last_name, 
                        "id": comment.user.id},
                        "text": comment.text,
                        "creation_time": utc_to_local(comment.creation_time).strftime("%m/%d/%Y %I:%M %p") 
                }
                comment_data.append(comment_item)
    
    response_data = {
        "posts": post_data,
        "comments": comment_data
    }
    response_json = json.dumps(response_data, cls=DjangoJSONEncoder)        
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'        
    return response


"""Helper function for returning customize HttpResponse"""
def _my_json_error_response(message, status=200):    
    response_json = '{ "error": "' + message + '" }'    
    return HttpResponse(response_json, content_type='application/json', status=status)

"""Transform utc time to local(US/Eastern) timezone"""
def utc_to_local(utc_dt):            
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)