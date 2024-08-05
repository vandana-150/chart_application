# serializers.py
from rest_framework import serializers
from .models import User, Group, Message

class SuperUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username', 'password', "is_superuser","is_staff"]

    # def save(self):
    #     user = User.objects.create_superuser(
    #         email=self.data['email'],
    #         password=self.data['password'],
    #         username=self.data['username'],
             
    #     )
    #     return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class GetUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'id']


# class GroupSerializer(serializers.ModelSerializer):
#     members = UserSerializer(many=True, read_only=True)

#     class Meta:
#         model = Group
#         fields = ['id', 'name', 'description', 'members']

class GroupSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Group
        fields = ['id', 'host', 'name', 'description', 'participants', 'updated', 'created']
        read_only_fields = ['id', 'host', 'updated', 'created']  # Make certain fields read-only

    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        group = Group.objects.create(**validated_data)
        group.participants.set(participants)  # Add participants
        return group

class MessageSerializer(serializers.ModelSerializer):
    sender = GetUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'group', 'sender', 'content', 'created']
