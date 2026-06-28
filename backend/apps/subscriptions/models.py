from xml.dom import ValidationErr

from django.db import models
from django.conf import settings


class Plan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_users = models.IntegerField(default=1)
    duration_months = models.PositiveSmallIntegerField(default=1)
    def __str__(self):
        return self.name


class Subscription(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True
    )
    status = models.CharField(max_length=50, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.owner} - {self.plan.name}"


class SubscriptionMember(models.Model):
    subscription = models.ForeignKey(
        Subscription, on_delete=models.CASCADE, related_name="members"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, unique=True
    )

    def __str__(self):
        return f"{self.user} in {self.subscription}"


class PaymentMethod(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_methods",
    )

    card_holder_name = models.CharField(max_length=255)
    card_number = models.CharField(max_length=19)  
    expiration_month = models.PositiveSmallIntegerField()
    expiration_year = models.PositiveSmallIntegerField()

    def clean(self):
        if not 1 <= self.expiration_month <= 12:
            raise ValidationErr(
                {"expiration_month": "Month must be between 1 and 12."}
            )

        if (
            self.pk is None
            and self.user.payment_methods.count() >= 3
        ):
            raise ValidationErr(
                "A user can have at most 3 payment methods."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.card_holder_name} - ****{self.card_number[-4:]}"