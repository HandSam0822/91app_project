from unicodedata import name
from django.urls import path
from socialnetwork import views
urlpatterns = [   
    path('home', views.home_action, name='home'),      
    path("login/", views.login_action, name="login"),        
    path("register/", views.register_action, name="register"),    
    path('logout', views.logout_action, name='logout'),
    path('profile', views.profile_action, name="profile"),
    path('follower', views.follower_action, name="follower"),
    path('LBJ', views.getLBJ_action, name="LBJ")
]
