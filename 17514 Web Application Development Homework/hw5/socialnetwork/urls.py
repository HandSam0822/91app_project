from unicodedata import name
from django.urls import path
from socialnetwork import views
urlpatterns = [   
    path('home', views.home_action, name='home'),      
    path("login/", views.login_action, name="login"),        
    path("register/", views.register_action, name="register"),    
    path('logout', views.logout_action, name='logout'),
    path('follower', views.follower_action, name="follower"),
    path('profile', views.profile_action, name="profile"),
    path('other/<int:id>', views.other_action, name="other"),    
    path('photo/<int:id>', views.get_photo, name='photo'),
    path('follow/<int:id>', views.follow, name='follow'),
    path('unfollow/<int:id>', views.unfollow, name='unfollow')
]
