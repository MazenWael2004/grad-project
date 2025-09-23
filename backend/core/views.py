from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

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