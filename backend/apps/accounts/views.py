from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from .models import User
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import login, logout
from .serializers import RegisterSerializer, LoginSerializer,UserSerializer,UserUpdateSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user  = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response(
                {"message": "User created successfully","user": UserSerializer(user).data,"token":token.key}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Generate or get token for user
            token, created = Token.objects.get_or_create(user=user)

            return Response(
                {"message": "Logged in successfully", "token": token.key,"user": UserSerializer(user).data},
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
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
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user)
        return Response(serializer.data)



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