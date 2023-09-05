from django.urls import path, include
from .views import UserRegisterView, UserLoginView, UserLogoutView, index, profile_view, update_profile, homepage_view, send_friend_request, accept_friend_request, search_user_request, chat_view, UserApiView
from rest_framework import routers

# Code I wrote starts here

# Creating a default router for our API views.
router = routers.DefaultRouter()

# Registering the UserApiView with the router under the prefix 'user'.
router.register(r'user', UserApiView)

# URL configuration for the application.
urlpatterns = [
    # User registration view.
    path('register/', UserRegisterView.as_view(), name='register'),
    
    # User login view.
    path('login/', UserLoginView.as_view(), name='login'),

    # User logout view.
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # Index or main landing page view.
    path('', index, name='index'),
    
    # Profile view for a user identified by their user ID.
    path('profile/<int:user_id>/', profile_view, name='profile'),
    
    # Profile update view for a user identified by their user ID.
    path('profile/update/<int:user_id>/', update_profile, name='update_profile'),
    
    # Home or dashboard page view after user logs in.
    path('home/', homepage_view, name='homepage'),
    
    # Send friend request to another user identified by their user ID.
    path('send_friend_request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    
    # Accept a friend request identified by its ID.
    path('accept_friend_request/<int:friend_request_id>/', accept_friend_request, name='accept_friend_request'),
    
    # Search for users.
    path('search_user_request/', search_user_request, name='search_user_request'),
    
    # Chat view for communication with another user identified by their user ID.
    path('chat/<int:user_id>/', chat_view, name='chat'),
    
    # Include all API endpoints provided by the router.
    path('api/', include(router.urls)),
]

# Code I wrote ends here