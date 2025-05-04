from django import forms
from .models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm
from django.core.validators import RegexValidator


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()
    remember_me = forms.BooleanField(required=False)


class UploadFAQForm(forms.Form):
    faq = forms.FileField()


class CompanyForm(forms.Form):
    name = forms.CharField()
    website = forms.URLField()
    faq_company = forms.FileField(required=False)
    welcome_message = forms.CharField(required=False)


class RegisterForm(forms.Form):
    phone_number = forms.CharField(
        max_length=11,
        label="شماره موبایل",
        error_messages={
            'required': 'وارد کردن شماره موبایل الزامی است.',
            'max_length': 'شماره موبایل نباید بیشتر از ۱۱ رقم باشد.'
        }
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label="رمز عبور",
        error_messages={
            'required': 'رمز عبور را وارد کنید.'
        }
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        label="تکرار رمز عبور",
        error_messages={
            'required': 'تکرار رمز عبور را وارد کنید.'
        }
    )
    agree_rules = forms.BooleanField(
        required=True,
        label="موافقت با قوانین",
        error_messages={
            'required': 'لطفا برای ادامه، قوانین را بپذیرید.'
        }
    )



class UserEditForm(forms.ModelForm):
    clear_image = forms.BooleanField(
        required=False,  # این فیلد اختیاری است
        label="حذف تصویر فعلی",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = User
        fields = ['name', 'image', 'online']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'online': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
