from django.db import models

class Governorate(models.Model):
    name = models.CharField(max_length=100, unique=True)  # "Cairo", "Giza", "Luxor"
    latitude = models.FloatField(help_text="Center latitude for radius queries")
    longitude = models.FloatField(help_text="Center longitude for radius queries")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Attraction(models.Model):
    name = models.CharField(max_length=200)
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='attractions')
    city = models.CharField(max_length=100)        # finer than governorate
    latitude = models.FloatField()
    longitude = models.FloatField()
    categories = models.JSONField(default=list, help_text='e.g. ["history", "culture"]')
    average_cost = models.IntegerField(help_text="Cost in EGP")
    visit_duration_hours = models.FloatField(default=2.0)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    closed_on = models.JSONField(default=list, help_text='e.g. ["Friday"]')
    best_time = models.CharField(max_length=20, blank=True, default='morning')
    popularity = models.IntegerField(default=3)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.city})"

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='hotels')
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    price_per_night = models.IntegerField(help_text="Cost per night in EGP")
    rating = models.FloatField()
    CATEGORY_CHOICES = [("budget","Budget"),("mid-range","Mid-range"),("luxury","Luxury")]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name='restaurants')
    city = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    cuisine = models.CharField(max_length=100)
    average_meal_cost = models.IntegerField(help_text="Average cost of a meal in EGP")
    rating = models.FloatField()
    specialty = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.name
