from django.contrib import admin
from .models import Connection, Meesages, Company, Permission, SubscriptionPlan, UserSubscription, PaymentTransaction


# Register your models here.
admin.site.register([Connection, Meesages, Company, Permission, SubscriptionPlan, UserSubscription, PaymentTransaction])
