from django import forms

from .models import Plan


class PlanForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ["name", "price", "max_users", "duration_months"]
        widgets = {
            "price": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "max_users": forms.NumberInput(attrs={"min": "1"}),
            "duration_months": forms.NumberInput(attrs={"min": "1"}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        return price

    def clean_max_users(self):
        max_users = self.cleaned_data["max_users"]
        if max_users < 1:
            raise forms.ValidationError("Max users must be at least 1.")
        return max_users

    def clean_duration_months(self):
        duration_months = self.cleaned_data["duration_months"]
        if duration_months < 1:
            raise forms.ValidationError("Duration must be at least 1 month.")
        return duration_months


class ConfirmActionForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        initial=True,
        widget=forms.HiddenInput,
    )
