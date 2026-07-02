from django import forms
from django.conf import settings

from .models import ClassifierClass


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        if hasattr(files, "getlist"):
            return files.getlist(name)
        return files.get(name)


class MultipleImageField(forms.ImageField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return super().clean(data, initial)
        if not isinstance(data, (list, tuple)):
            data = [data]
        return [forms.ImageField.clean(self, item, initial) for item in data]


class ClassifierClassForm(forms.ModelForm):
    class Meta:
        model = ClassifierClass
        fields = ["name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ClassifierClassUpdateForm(forms.ModelForm):
    class Meta:
        model = ClassifierClass
        fields = ["name", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class ConfirmActionForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        initial=True,
        widget=forms.HiddenInput,
    )


class TrainingImageUploadForm(forms.Form):
    images = MultipleImageField(
        label="Images",
        required=True,
        widget=MultipleFileInput(attrs={"multiple": True}),
    )


class ClassifierClassChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name} ({obj.images.count()} images)"


class TrainingRunStartForm(forms.Form):
    classes = ClassifierClassChoiceField(
        queryset=ClassifierClass.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )
    epochs = forms.IntegerField(min_value=1, max_value=100, initial=8)
    batch_size = forms.IntegerField(min_value=1, max_value=64, initial=4)
    learning_rate = forms.FloatField(min_value=0.000001, max_value=1.0, initial=0.001)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["classes"].queryset = ClassifierClass.objects.filter(
            is_active=True,
        ).prefetch_related("images")

    def clean_classes(self):
        classes = self.cleaned_data["classes"]
        min_images = getattr(settings, "CLASSIFIER_MIN_IMAGES_PER_CLASS", 15)
        underfilled = [
            artifact_class.name
            for artifact_class in classes
            if artifact_class.images.count() < min_images
        ]
        if underfilled:
            raise forms.ValidationError(
                "Each selected class needs at least %(minimum)s images. Underfilled: %(classes)s",
                params={
                    "minimum": min_images,
                    "classes": ", ".join(underfilled),
                },
            )
        return classes

    def training_config(self):
        return {
            "epochs": self.cleaned_data["epochs"],
            "batch_size": self.cleaned_data["batch_size"],
            "lr": self.cleaned_data["learning_rate"],
        }


class PromoteModelVersionForm(ConfirmActionForm):
    pass
