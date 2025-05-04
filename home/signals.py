from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# ایمپورت مدل به صورت Lazy
def update_trusted_domains():
    from .models import Company  # وارد کردن مدل در زمان اجرا
    from django.conf import settings

    companies = Company.objects.all()
    domains = [company.website for company in companies if company.website]

    normalized_domains = [f"https://{domain.replace('http://', '').replace('https://', '').strip('/')}" for domain in domains]
    normalized_domains += [f"http://{domain.replace('http://', '').replace('https://', '').strip('/')}" for domain in domains]

    settings.CSRF_TRUSTED_ORIGINS = list(set(normalized_domains))
    settings.CORS_ALLOWED_ORIGINS = list(set(domains))

@receiver(post_save, sender=None)  # تغییر به زمان اجرا
def update_domains_on_save(sender, instance, **kwargs):
    update_trusted_domains()
