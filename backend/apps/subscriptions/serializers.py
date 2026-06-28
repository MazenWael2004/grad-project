from rest_framework import serializers
from .models import PaymentMethod, Plan


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["id", "name", "price", "max_users","duration_months"]


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "card_holder_name",
            "card_number",
            "expiration_month",
            "expiration_year",
        ]
        read_only_fields = ["id"]
