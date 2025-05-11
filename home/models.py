from django.db import models
from django.utils import timezone
from account.models import User
from rest_framework.authtoken.models import Token
import secrets
from django.db.models.signals import pre_delete
from django.dispatch import receiver


class Company(models.Model):
    name = models.CharField(max_length=100)  # Name of the company
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='companies',
                              default=None)  # User who owns the company
    api_key = models.CharField(max_length=255, unique=True, blank=True, null=True)  # Unique API key for company
    faq = models.FileField(upload_to='faq_uploaded', blank=True, null=True)  # FAQ file upload
    website = models.URLField(max_length=255, blank=True, null=True)  # Website URL of the company
    welcome_message = models.TextField(blank=True, null=True)  # Welcome message field
    created_at = models.DateTimeField(auto_now_add=True)  # Company creation time
    faq_embeddings = models.BinaryField(blank=True, null=True)
    faq_json = models.JSONField(blank=True, null=True)
    def generate_api_key(self):
        """
        Generate a unique API key for the company, tied to the owner's token.
        """
        if not self.api_key:
            # Get or create token for the company owner
            token, _ = Token.objects.get_or_create(user=self.owner)

            # Generate the API key combining user token, company ID, and a random string
            random_string = secrets.token_hex(8)  # Generate a shorter random string for readability
            self.api_key = f"{token.key}:{self.id}:{random_string}"
            self.save()

    def is_domain_valid(self, current_domain):
        """
        Validate if the current domain matches the company's registered website.
        """
        if not self.website:
            return False

        # نرمال‌سازی دامنه
        def normalize_domain(domain):
            domain = domain.replace("http://", "").replace("https://", "").strip("/")
            if domain.startswith("www."):
                domain = domain[4:]
            return domain

        registered_domain = normalize_domain(self.website)
        current_domain = normalize_domain(current_domain)

        # مقایسه دامنه‌های نرمال‌شده
        return current_domain == registered_domain

    def __str__(self):
        return self.name


@receiver(pre_delete, sender=Company)
def delete_faq_file(sender, instance, **kwargs):
    """
    Delete the FAQ file when a Company instance is deleted.
    """
    if instance.faq:
        instance.faq.delete(False)


class Connection(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='connections')  # Link to a company
    userEmail = models.CharField(max_length=50, blank=True, null=True)
    userNumber = models.CharField(max_length=50, blank=True, null=True)
    admin = models.CharField(max_length=50, blank=True, null=True)
    received = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.userEmail} connected to {self.admin} (Company: {self.company.name})'


class Meesages(models.Model):
    text = models.TextField()
    msg_sender = models.CharField(max_length=50, blank=True, null=True)
    msg_sender_number = models.CharField(max_length=50, blank=True, null=True)
    msg_receiver = models.CharField(max_length=50, blank=True, null=True)
    msg_receiver_number = models.CharField(max_length=50, blank=True, null=True)
    received = models.BooleanField(default=False)
    processed_by_api = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)
    create = models.DateTimeField(default=timezone.now)
    msgImg = models.CharField(max_length=255, blank=True, null=True)
    msgFile = models.FileField(upload_to='file_msg_uploaded', blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='messages', null=True,
                                blank=True)  # Link to a company
    question_embedding=models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'From {self.msg_sender} to {self.msg_receiver} (Company: {self.company.name if self.company else "N/A"}) ===> {self.text}'


# Permission Model to manage access between users and companies
class Permission(models.Model):
    giver = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='given_permissions')  # User granting the permission
    receiver = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name='received_permissions')  # User receiving the permission
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='permissions')  # Company related to the permission
    can_reply = models.BooleanField(default=False)  # Whether the receiver can reply to messages
    created_at = models.DateTimeField(auto_now_add=True)  # Permission creation date

    def __str__(self):
        return f'{self.giver.username} granted permission to {self.receiver.username} for {self.company.name}'


# مدل پلن‌های اشتراک
class SubscriptionPlan(models.Model):
    PLAN_CHOICES = (
        ('free', 'رایگان'),
        ('basic', 'یک ماهه'),
        ('premium', 'سه ماهه'),
        ('enterprise', 'یکساله'),
    )
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    message_limit = models.PositiveIntegerField(help_text="تعداد پیام‌های مجاز در دوره اشتراک")
    company_limit = models.PositiveIntegerField(help_text="تعداد کمپانی‌های مجاز")
    connected_user_limit = models.PositiveIntegerField(help_text="تعداد کاربران متصل مجاز")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="قیمت پلن به تومان")
    duration = models.DurationField(help_text="مدت زمان اعتبار اشتراک (مثلاً ۳۰ روز)")

    def __str__(self):
        return self.get_name_display()


# مدل اشتراک کاربر
class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    message_sent = models.PositiveIntegerField(default=0, help_text="تعداد پیام‌های ارسال شده در دوره فعلی")

    def is_active(self):
        if self.start_date and self.expiration_date:
            return timezone.now() < self.expiration_date
        return False

    def can_send_message(self):
        if not self.is_active():
            return False
        if self.subscription_plan and self.message_sent < self.subscription_plan.message_limit:
            return True
        return False

    def reset_period_if_expired(self):
        if self.expiration_date and timezone.now() >= self.expiration_date:
            self.start_date = None
            self.expiration_date = None
            self.message_sent = 0
            self.subscription_plan = None
            self.save()

    def __str__(self):
        return f"Subscription for {self.user.phone_number}"


# مدل تراکنش‌های پرداخت (برای درگاه زرین پال)
class PaymentTransaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پرداخت'),
        ('canceled', 'لغو شده'),
        ('failed', 'پرداخت نشده'),
        ('successful', 'پرداخت موفق'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE,
                                          related_name='payment_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="شناسه تراکنش درگاه زرین پال یا شماره سفارش")

    def __str__(self):
        return f"Payment {self.id} for {self.user.phone_number} - {self.get_status_display()}"
