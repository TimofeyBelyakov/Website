from django import forms
from snowpenguin.django.recaptcha3.fields import ReCaptchaField

from .models import Comment


# Form for comments
class CommentForm(forms.ModelForm):
    captcha = ReCaptchaField()

    class Meta:
        model = Comment
        fields = ["text", "name", "parent", "captcha"]
        widgets = {
            "name": forms.TextInput(attrs={
                "id": "contactusername",
                "class": "form-control border",
            }),
            "text": forms.Textarea(attrs={
                "id": "contactcomment",
                "class": "form-control border",
            }),
            "parent": forms.HiddenInput(attrs={
                "id": "contactparent",
            })
        }