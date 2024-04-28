from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserRegisterSerializer,UserSerializer,UserDetailsUpdateSerializer,AdminUserSerializer,UserUpdateSerializer
from rest_framework.exceptions import AuthenticationFailed,ParseError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from .models import ProfilePic
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter


class getAccountsRoutes(APIView):
     def get(self, request, format=None):
        routes = [
        'user/login',
        'user/register',
                    ]
        return Response(routes)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny] 

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
    

class LoginView(APIView):
        def post(self,request):
            try:
                password = request.data['password']
                username =request.data['username']

            except KeyError:
                raise ParseError('All Fields Are Required')

            if not User.objects.filter(username=username).exists():
                raise AuthenticationFailed('Invalid  Username')

            if not User.objects.filter(username=username,is_active=True).exists():
                raise AuthenticationFailed('You are blocked by admin ! Please contact admin')

            user = authenticate(username=username,password=password)
            if user is None:
                raise AuthenticationFailed('Invalid Password')

            refresh = RefreshToken.for_user(user)
            refresh["username"] = str(user.username)

            content = {
                         'refresh': str(refresh),
                         'access': str(refresh.access_token),
                         'isAdmin':user.is_superuser,
                    }

            return Response(content,status=status.HTTP_200_OK)
        


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        userEmail = User.objects.get(id=request.user.id).email
        content = {
            'user-email':userEmail,
            'user': str(request.user),  
            'auth': str(request.auth),  
        }
        return Response(content)




class UserDetails(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = User.objects.get(id=request.user.id)
       
        data = UserSerializer(user).data
        try :
            profile_pic = user.User_Profile.profile_pic
            print(profile_pic.url)
            data['profile_pic'] = request.build_absolute_uri('/')[:-1]+profile_pic.url
        except:
            profile_pic = ''
            data['profile_pic']=''
            
        content = data
        return Response(content)
    


class UserDetailsUpdate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        user_profile = ProfilePic.objects.get_or_create(user=request.user)[0]

     
        
        user_update_details_serializer = UserDetailsUpdateSerializer(
            user_profile, data=request.data, partial=True
        )
        
       
        if user_update_details_serializer.is_valid():
           
            user_update_details_serializer.save()
            return Response(user_update_details_serializer.data, status=status.HTTP_201_CREATED)
        else:
            print('error', user_update_details_serializer.errors)
            return Response(user_update_details_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        


# ----ADMIN SIDE----


class AdminUserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by('-date_joined')  
    serializer_class = AdminUserSerializer
    pagination_class = PageNumberPagination
    filter_backends = [SearchFilter]
    search_fields = ['username',  'email']

class AdminUserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = AdminUserSerializer
    lookup_field = 'id'

class AdminUserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    lookup_field = 'id'

class AdminUserDelete(generics.DestroyAPIView):
     
      def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)