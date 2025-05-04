from django.db import models
from django.contrib.auth.models import AbstractUser
import random
from django.utils import timezone
from datetime import timedelta
# Create your models here.

class User(AbstractUser):
    name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='images_uploaded', blank=True, null=True)
    online = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=11, unique=True)

    def save(self, *args, **kwargs):
        # اگر مقدار phone_number خالی نباشد، آن را در username ست کن
        if self.phone_number:
            self.username = self.phone_number
        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone_number



class PhoneOTP(models.Model):
    """
    مدلی برای ذخیره کد OTP. با شماره موبایل رابطه یک‌به‌یک دارد.
    """
    phone_number = models.CharField(max_length=11, unique=True)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)

    def generate_code(self):
        """تولید یک کد ۶ رقمی تصادفی."""
        return str(random.randint(100000, 999999))

    def is_expired(self):
        """مثلاً اعتبار ۲ دقیقه‌ای."""
        expiration_time = self.created_at + timedelta(minutes=2)
        return timezone.now() > expiration_time

    def __str__(self):
        return f"{self.phone_number} - {self.code}"