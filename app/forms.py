from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from captcha.fields import CaptchaField


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
    email = forms.CharField(
        label="Ваш email",
        widget=forms.EmailInput(
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
        validators=[
            lambda value: ValidationError(
                "Сообщение слишком длинное. Максимум 10 000 символов."
            )
            if len(value) > 10000
            else None
        ],
    )
    captcha = CaptchaField(
        label="Введите текст с картинки",
        error_messages={"invalid": "Неверная капча. Пожалуйста, попробуйте ещё раз."},
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Пожалуйста, введите корректный email адрес.")
        return email

    def clean_message(self):
        message = self.cleaned_data["message"]

        if len(message.split()) < 10:
            raise forms.ValidationError(
                "Сообщение слишком короткое. Пожалуйста, напишите более развернуто."
            )
        if len(message) < 30:
            raise ValidationError(
                "Сообщение слишком короткое. Пожалуйста, напишите не менее 30 символов."
            )

        return message
