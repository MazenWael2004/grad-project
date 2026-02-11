"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model, login, logout
from .serializers import UserSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = User.objects.filter(email=email).first()

    if user and user.check_password(password):
        login(request, user)
        return Response(UserSerializer(user).data)

    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'detail': 'Successfully logged out.'})


@api_view(['GET'])
def photo_list(request):
    photos = [
        {
        "id": 1,
        "title": "Sunset",
        "discribtion":"dd",
        "url": "media\photos\488808739.jpg"
        },
        {
        "id": 2,
        "title": "a",
        "discribtion":"dd",
        "url": "media\photos\download.jpg"
        },
        {
        "id": 3,
        "title": "f",
        "discribtion":"dd",
        "url": "media\photos\Sphinx-giza-pyramids.jpg"
        },
]
    return Response(photos)
"""
