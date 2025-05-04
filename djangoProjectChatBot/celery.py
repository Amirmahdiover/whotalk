from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# تنظیم متغیر محیطی برای پروژه
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProjectChatBot.settings')

# ایجاد اپلیکیشن Celery
app = Celery('djangoProjectChatBot')

# بارگذاری تنظیمات Celery از تنظیمات Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# شناسایی و بارگذاری تسک‌ها از اپلیکیشن‌های ثبت‌شده در پروژه
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
