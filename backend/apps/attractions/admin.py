from django.contrib import admin
from .models import Governorate, Attraction, Hotel, Restaurant

@admin.register(Governorate)
class GovernorateAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude')
    search_fields = ('name',)

@admin.register(Attraction)
class AttractionAdmin(admin.ModelAdmin):
    list_display = ('name', 'governorate', 'city', 'average_cost', 'popularity')
    list_filter = ('governorate', 'city', 'popularity')
    search_fields = ('name', 'city', 'description')

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'governorate', 'city', 'price_per_night', 'category', 'rating')
    list_filter = ('governorate', 'city', 'category')
    search_fields = ('name', 'city')

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'governorate', 'city', 'cuisine', 'average_meal_cost', 'rating')
    list_filter = ('governorate', 'city', 'cuisine')
    search_fields = ('name', 'city', 'cuisine')
