from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import User
from apps.classifier.models import (
    ClassifierClass,
    ClassifierModelVersion,
    TrainingImage,
    TrainingRun,
)

from .forms import ConfirmActionForm, PlanForm
from .models import PaymentMethod, Plan, Subscription, SubscriptionMember


def _normalized_status(value):
    return (value or "unknown").strip().lower()


def _currency(value):
    return Decimal(value or 0).quantize(Decimal("0.01"))


def _status_counts(subscriptions):
    counts = {}
    for subscription in subscriptions:
        status = _normalized_status(subscription.status)
        counts[status] = counts.get(status, 0) + 1
    return counts


def _plan_rows(plans=None, subscriptions=None):
    plans = list(plans if plans is not None else Plan.objects.order_by("price", "name"))
    subscriptions = list(
        subscriptions
        if subscriptions is not None
        else Subscription.objects.select_related("plan", "owner")
    )
    rows = {
        plan.pk: {
            "plan": plan,
            "subscriptions": 0,
            "active": 0,
            "pending": 0,
            "revenue": Decimal("0.00"),
        }
        for plan in plans
    }
    for subscription in subscriptions:
        row = rows.get(subscription.plan_id)
        if not row:
            continue
        row["subscriptions"] += 1
        status = _normalized_status(subscription.status)
        if status == "active":
            row["active"] += 1
            row["revenue"] += subscription.plan.price
        elif status == "pending":
            row["pending"] += 1

    for row in rows.values():
        row["revenue"] = _currency(row["revenue"])
    return list(rows.values())


def _classifier_run_rows():
    counts = {}
    for status, label in TrainingRun.Status.choices:
        counts[status] = {
            "status": status,
            "label": label,
            "count": TrainingRun.objects.filter(status=status).count(),
        }
    return counts.values()


def _analytics_context():
    subscriptions = list(
        Subscription.objects.select_related("plan", "owner")
        .prefetch_related("members")
        .order_by("-start_date", "-id")
    )
    status_counts = _status_counts(subscriptions)
    active_subscriptions = [
        subscription
        for subscription in subscriptions
        if _normalized_status(subscription.status) == "active"
    ]
    active_revenue = _currency(
        sum((subscription.plan.price for subscription in active_subscriptions), Decimal("0.00"))
    )

    return {
        "title": "Analytics Dashboard",
        "total_users": User.objects.count(),
        "staff_users": User.objects.filter(is_staff=True).count(),
        "total_plans": Plan.objects.count(),
        "total_subscriptions": len(subscriptions),
        "active_subscriptions": len(active_subscriptions),
        "pending_subscriptions": status_counts.get("pending", 0),
        "cancelled_subscriptions": (
            status_counts.get("cancelled", 0) + status_counts.get("canceled", 0)
        ),
        "subscription_members": SubscriptionMember.objects.count(),
        "payment_methods": PaymentMethod.objects.count(),
        "active_revenue": active_revenue,
        "subscription_status_rows": [
            {"status": status, "count": count}
            for status, count in sorted(status_counts.items())
        ],
        "plan_rows": _plan_rows(subscriptions=subscriptions),
        "recent_subscriptions": subscriptions[:10],
        "classifier_classes": ClassifierClass.objects.count(),
        "classifier_images": TrainingImage.objects.count(),
        "classifier_training_runs": TrainingRun.objects.count(),
        "classifier_run_rows": _classifier_run_rows(),
        "active_classifier_model": ClassifierModelVersion.objects.filter(
            is_active=True,
        ).first(),
    }


@staff_member_required
def analytics_dashboard(request):
    return render(
        request,
        "subscriptions_admin/analytics_dashboard.html",
        _analytics_context(),
    )


@staff_member_required
def plan_list(request):
    plans = Plan.objects.order_by("price", "name")
    subscriptions = Subscription.objects.select_related("plan")
    return render(
        request,
        "subscriptions_admin/plan_list.html",
        {
            "title": "Plans",
            "plan_rows": _plan_rows(plans=plans, subscriptions=subscriptions),
            "confirm_form": ConfirmActionForm(),
        },
    )


@staff_member_required
def plan_create(request):
    if request.method == "POST":
        form = PlanForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f"Plan '{plan.name}' created.")
            return redirect("subscriptions_admin:plan_detail", pk=plan.pk)
    else:
        form = PlanForm()

    return render(
        request,
        "subscriptions_admin/plan_form.html",
        {
            "title": "New Plan",
            "form": form,
        },
    )


@staff_member_required
def plan_detail(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    subscriptions = list(
        Subscription.objects.filter(plan=plan)
        .select_related("owner", "plan")
        .prefetch_related("members")
        .order_by("-start_date", "-id")
    )
    status_counts = _status_counts(subscriptions)
    active_revenue = _currency(
        sum(
            (
                subscription.plan.price
                for subscription in subscriptions
                if _normalized_status(subscription.status) == "active"
            ),
            Decimal("0.00"),
        )
    )
    return render(
        request,
        "subscriptions_admin/plan_detail.html",
        {
            "title": plan.name,
            "plan": plan,
            "subscriptions": subscriptions[:20],
            "subscription_count": len(subscriptions),
            "active_count": status_counts.get("active", 0),
            "pending_count": status_counts.get("pending", 0),
            "active_revenue": active_revenue,
            "confirm_form": ConfirmActionForm(),
        },
    )


@staff_member_required
def plan_edit(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    if request.method == "POST":
        form = PlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, f"Plan '{plan.name}' updated.")
            return redirect("subscriptions_admin:plan_detail", pk=plan.pk)
    else:
        form = PlanForm(instance=plan)

    return render(
        request,
        "subscriptions_admin/plan_form.html",
        {
            "title": f"Edit {plan.name}",
            "form": form,
            "plan": plan,
        },
    )


@staff_member_required
def plan_delete(request, pk):
    plan = get_object_or_404(Plan, pk=pk)
    redirect_url = reverse("subscriptions_admin:plan_detail", args=[plan.pk])
    if request.method != "POST":
        return redirect(redirect_url)

    form = ConfirmActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Plan deletion was not confirmed.")
        return redirect(redirect_url)

    if Subscription.objects.filter(plan=plan).exists():
        messages.error(request, "Cannot delete a plan that has subscriptions.")
        return redirect(redirect_url)

    plan_name = plan.name
    plan.delete()
    messages.success(request, f"Plan '{plan_name}' deleted.")
    return redirect("subscriptions_admin:plan_list")
