from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import PaymentMethod, Plan, Subscription, SubscriptionMember


class SubscriptionMemberInline(admin.TabularInline):
    model = SubscriptionMember
    extra = 0
    readonly_fields = ("user",)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "max_users",
        "duration_months",
        "subscription_count",
        "dashboard_link",
    )
    search_fields = ("name",)
    ordering = ("price", "name")

    def subscription_count(self, obj):
        return obj.subscription_set.count()

    def dashboard_link(self, obj):
        url = reverse("subscriptions_admin:plan_detail", args=[obj.pk])
        return format_html('<a href="{}">Open dashboard</a>', url)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("owner", "plan", "status", "start_date", "end_date", "member_count")
    list_filter = ("status", "plan", "start_date", "end_date")
    search_fields = ("owner__email", "plan__name")
    inlines = [SubscriptionMemberInline]

    def member_count(self, obj):
        return obj.members.count()


@admin.register(SubscriptionMember)
class SubscriptionMemberAdmin(admin.ModelAdmin):
    list_display = ("subscription", "user")
    list_filter = ("subscription__plan",)
    search_fields = ("subscription__owner__email", "user__email")


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ("user", "card_holder_name", "masked_card", "expiration_month", "expiration_year")
    search_fields = ("user__email", "card_holder_name", "card_number")

    def masked_card(self, obj):
        return f"****{obj.card_number[-4:]}"
