from django.urls import path
from .views import create_superuser, user_views, get_users, create_group, add_members, send_message, get_messages, logout, superuser_login

urlpatterns = [
    path('superuser/', create_superuser, name='create-superuser'),  # Create a superuser
    path("auth/superuser/login/", superuser_login, name="superuser_login"), #Login to superuser account

    path('users/', user_views, name='user-management'),  # Create, update, delete users
      path('users/all/', get_users, name='get-all-users'),  # Get all users
    path('users/<int:user_id>/', get_users, name='get-user'),  # Get a specific user by ID
  
    path('groups/', create_group, name='create-group'),  # Create a new group
    path('groups/<int:group_id>/add-members/', add_members, name='add-members'),  # Add members to a group
    path('groups/<int:group_id>/messages/', send_message, name='send-message'),  # Send a message to a group
    path('messages/', get_messages, name='get-messages'),  # Retrieve all messages
    path('messages/<int:group_id>/', get_messages, name='get-group-messages'),  # Retrieve messages for a specific group
    path("auth/logout/", logout, name='logout'),
]