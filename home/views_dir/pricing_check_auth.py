from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from ..models import SubscriptionPlan, PaymentTransaction
from utils.convert_to_jalali import convert_to_jalali  # adjust if this is in another place
import uuid

def pricing(request):
    return render(request, 'home/pricing.html')

@login_required(login_url='../login/')
def choose_plan(request):
    plan_key = request.GET.get('plan')  # e.g. '1month', '3month', 'enterprise'

    try:
        selected_plan = SubscriptionPlan.objects.get(name=plan_key)
    except SubscriptionPlan.DoesNotExist:
        return render(request, "home/pricing.html", {
            "error": "پلن انتخاب شده نامعتبر است."
        })

    # ✅ You can optionally handle custom logic based on the plan name
    if plan_key == '1month':
        print('Selected: 1month')
    elif plan_key == '3month':
        print('Selected: 3month')
    elif plan_key == 'enterprise':
        print('Selected: enterprise')

    # ✅ Now run your full transaction logic
    order_number = str(uuid.uuid4()).split('-')[0]

    transaction = PaymentTransaction.objects.create(
        user=request.user,
        subscription_plan=selected_plan,
        amount=int(selected_plan.price),
        status="pending",
        transaction_id=order_number,
    )

    context = {
        "user_name": request.user.get_full_name() or request.user.username,
        "purchase_date": convert_to_jalali(timezone.now(), "%Y/%m/%d"),
        "selected_plan": selected_plan,
        "order_number": transaction.transaction_id,
        "payment_status": transaction.get_status_display(),
    }

    return render(request, "admin/subscription_intermediate.html", context)
