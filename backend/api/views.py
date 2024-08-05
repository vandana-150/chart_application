# views.py
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth import authenticate

from .models import User, Group, Message
from .serializers import SuperUserSerializer, UserSerializer, GroupSerializer, MessageSerializer, GetUserSerializer

@api_view(['POST'])
def create_superuser(request):
    """
    API view to create a superuser.
    """
    try:
        serializer = SuperUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "status": True,
                     "message": "User created successfully",
                     "data": serializer.data
                },
             status=status.HTTP_201_CREATED
            )
        
        return Response(
            {
              "status": False,
               "message": "User has already been registered",
               "error": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {
                "status": False,
                "message": "Something went wrong issue with the server",
                "error": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    
@api_view(['POST'])
def superuser_login(request):
    """
    Log in a superuser and return access and refresh tokens.
    """
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(email=email, password=password)

        if user is None:
            return Response(
                {
                "status": False,
                "error": "Invalid credentials"
                }, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if the user is a superuser
        if not user.is_superuser:
            return Response(
                {
                    "status": False,
                    "error": "User is not a superuser"
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
         return Response(
                {
                    "status": False,
                    "message": "Something went wrong issue with the server",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["POST", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def user_views(request):

    if request.method == "POST":
        try:
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Successfuly registered"
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {
                    "status": False,
                    "message": "Failed to register",
                    "error": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong issue with the server",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "PATCH":
        try:
            # Get the User object
            user_obj = get_object_or_404(User, id=request.data["id"])

            # Serialize the User object with the updated data
            serializer = UserSerializer(
                instance=user_obj, data=request.data, partial=True
            )

            # If the serializer is valid, save the data and return a success
            # response
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status" : True,
                        "message": f"{list(request.data.keys())} are updated",
                    },
                    status=status.HTTP_205_RESET_CONTENT,
                )

            # If the serializer is not valid, return an error response with the
            # validation errors
            return Response(
               {
                   "status": False,
                   "message": "Unable to update the user data",
                   "error": serializer.errors
               },
               status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            # If there is an exception,  return an error response with the error message
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong issue with the server",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    elif request.method == "DELETE":
        try:
            user_obj = User.objects.get(id=request.GET.get("id", ""))
            user_obj.delete()
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong issue with the server",
                    "error": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(
            {
               "status" : True,
                "message": "User is successfully deleted"
            },
            status=status.HTTP_204_NO_CONTENT
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_users(request, user_id=None):
    """
    API view to get all users or a single user by ID.
    """
    if user_id is not None:
        try:
            user = User.objects.get(id=user_id)
            serializer = GetUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist as e:
            return Response(
                {
                    "status": False,
                    "message": "User not found",
                    "error": str(e)
                }, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    # If no user_id is provided, return all users
    try:
        users = User.objects.all()
        serializer = GetUserSerializer(users, many=True)
        return Response(
            {
              "status": True,
               "message": "Data retrieved successfully",
              "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
                {
                    "status": False,
                    "message": "Something went wrong issue with the server",
                    "error": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    """
    Create a new group with participants.
    """
    try:
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(host=request.user)   # Set the host to the authenticated user
            return Response(
                    {
                        "status": True,
                        "message" : "Group created successfully",
                        "data": serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
        return Response(
                {
                    "status": False,
                    "message": "Unable to create the group",
                    "error": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
       return Response(
                {
                    "status": False,
                    "message": "Something went wrong issue with the server",
                    "error": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_members(request, group_id):
    """
    Add members to an existing group.
    """
    group = get_object_or_404(Group, id=group_id)

    if group.host.id != request.user.id:
        return Response(
                    {
                        "status": False,
                        "message": "You do not have permission to edit this resource.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
    #Need to remind the user that the participant is already been added
    user_ids = request.data.get('user_ids', [])
    users = User.objects.filter(id__in=user_ids)
    group.participants.add(*users)
    serializer = GroupSerializer(group)
    return Response(
        {
           "status": True,
           "message": "Members added successfully to the group",
           "data": serializer.data
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, group_id):
    """
    Send a message to a specific group.
    """
    group = get_object_or_404(Group, id=group_id)
    request.data['group'] = group_id
    serializer = MessageSerializer(data=request.data)
    if serializer.is_valid():
        message = serializer.save(group=group, sender=request.user)
        return Response(
            {
              "status": True,
               "message": "Message sent successfully",
               "data": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    return Response( 
        {
            "status": False,
            "message": "Unable to send the message",
            "error": serializer.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages(request, group_id=None):
    """
    Retrieve messages for a specific group or all messages if no group_id is provided.
    """
    try:
        if group_id:
            group = get_object_or_404(Group, id=group_id)
            messages = group.message_set.all()
        else:
            messages = Message.objects.all()
        
        serializer = MessageSerializer(messages, many=True)
        return Response(
            {
              "status": True,
               "message": "Messages retrieved successfully",
               "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
                {
                    "status": False,
                    "message": "Something went wrong issue with the server",
                    "error": str(e)
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):

    try:
        # Get the refresh token from the request data
        refresh_token = request.data["refresh_token"]

        # Create a RefreshToken object with the refresh token
        token = RefreshToken(refresh_token)

        # Blacklist the refresh token to invalidate it
        token.blacklist()

        # Return a success response with a status code of 205
        return Response(
            {
                "status": True,
                "message": "Successfully logged out"
            },
            status=status.HTTP_205_RESET_CONTENT,
        )

    except Exception as _e:
        # If there is an exception while logging out, log the exception with
        # request user ID and return a bad request response with a status code of
        # 400
        return Response(
            {
                "status": False,
                "message": "Unable to logout",
                "error": str(_e)
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )
