import re
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class EditProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if not phone:
            return phone  # пустой телефон — ок
        if phone.startswith('+7'):
            normalized = '8' + phone[2:]
        else:
            normalized = phone
        if not re.fullmatch(r'8\d{10}', normalized):
            raise forms.ValidationError(
                'Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX'
            )
        qs = User.objects.filter(phone__in=[normalized, '+7' + normalized[1:]])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Этот номер телефона уже используется')
        return normalized

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url', '')
        if url and 'github.com' not in url:
            raise forms.ValidationError('Ссылка должна вести на github.com')
        return url


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Старый пароль',
        widget=forms.PasswordInput
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput
    )
    new_password2 = forms.CharField(
        label='Повторите новый пароль',
        widget=forms.PasswordInput
    )
