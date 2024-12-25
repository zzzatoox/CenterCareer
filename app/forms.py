from django import forms


class FeedbackForm(forms.Form):
    name = forms.CharField(
        label="Ваше имя",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "required": True,
            }
        ),
    )
    message = forms.CharField(
        label="Ваше сообщение",
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 5, "required": True}
        ),
    )
