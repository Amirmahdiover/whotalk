from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def check_subscription_btn(request):
    user=request.user
    has_subscription=False

    if hasattr(user,'subscription'):
        has_subscription=user.subscription.is_active()
    print(has_subscription)
    return JsonResponse({'subscribed':has_subscription})