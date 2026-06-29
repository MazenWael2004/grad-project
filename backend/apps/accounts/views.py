from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions,generics
from django.contrib.auth import login, logout
from .serializers import RegisterSerializer, LoginSerializer,UserSerializer,UserUpdateSerializer
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User created successfully",
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
from rest_framework_simplejwt.tokens import RefreshToken

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Logged in successfully",
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print("User",request.user)
        print("Auth",request.auth)

        try:
            token = Token.objects.get(user=request.user)
            token.delete()
        except Token.DoesNotExist:
            print("Token does not exist for user, possibly already logged out.")
            pass

        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )
class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UpdateProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response({
                "message": "Profile updated successfully",
                "user": UserSerializer(request.user).data
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    # def tour_guidView():
    #     pass

