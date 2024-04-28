from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer,TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, Token,AccessToken
from .models import ProfilePic

UserModel = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...
        
        return token

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = UserModel.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        exclude = ('password',)


class UserDetailsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePic
        fields = ['profile_pic']


# ADMIN SIDE-

# for seeing listing all users and adding new user-
# strat here-

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePic
        fields = ['profile_pic']


class AdminUserSerializer(serializers.ModelSerializer):
    User_Profile = UserProfileSerializer(required=False)

    class Meta:
        model = UserModel
        fields = ['id', 'username', 'email', 'password', 'User_Profile','is_active']
        extra_kwargs = {
            'password':{ 'write_only':True},
            'username': {'error_messages': {'required': 'Please provide the username.'}},
            'email': {'error_messages': {'required': 'Please provide the email address.'}},
            
            
        }

    def create(self, validated_data):
       
 
        profile_data = validated_data.pop('User_Profile')
        password = validated_data.pop('password',None)
        print("-=-=-=-=-=")
        print(password)
        user_instance = self.Meta.model(**validated_data)
        if password is not None:
            user_instance.set_password(password)
            user_instance.is_active=True
            user_instance.save()
            
        ProfilePic.objects.create(user=user_instance, **profile_data)
        return user_instance
    
# end here--

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['username', 'email', 'is_active']

    def update(self, instance, validated_data):
        # Update user fields
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()
        return instance
    

