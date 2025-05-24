from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta

from ..forms import RegisterForm
from ..models import SubscriptionPlan, UserSubscription
from account.models import User, PhoneOTP
import requests
from sms_ir import SmsIr
import http.client

sms_ir = SmsIr('0qUo2QMrpL6ceDATjkO1yXXxxXXxxXXxxFpXg9XBHDKfh6ou5cS6nrCBInUxWGf')


def send_otp_code(phone_number, code):
    """
    ارسال کد تأیید به یک شماره موبایل از طریق پنل sms.ir

    :param phone_number: رشته شماره موبایل گیرنده (مثال: "09123456789")
    :param code: رشته یا عدد کد OTP که باید ارسال شود
    :return: True در صورت موفقیت ارسال، False در غیر این صورت
    """
    
    conn = http.client.HTTPSConnection("api.sms.ir")
    payload ={
                "mobile": f"{phone_number}",
                "templateId": 123456,
                "parameters": [
                {
                    "name": "Code",
                    "value": "12345"
                }
                ]
            }
    payload = f"""{
    "mobile": "{phone_number}",
    "templateId": 123456,
    "parameters": [
        {
        "name": "Code",
        "value": 123456
        }
    ]
    }"""
    headers = {
        'Accept': 'text/plain',
        'Content-Type': 'application/json',
        'x-api-key': 'C48EkMG2nBLSkwvO8Xei4GJA9Jcj0ZPVWC9JAyhmiA7YbchM',
    }
    # try:
    print('---------------------------------12')
    conn.request("POST", "/v1/send/verify", payload, headers)
    res = conn.getresponse()
    data = res.read()
    response_text = data.decode("utf-8")
    # print("Response from SMS.ir:-------------------------", response_text)
        # response = requests.post(url, json=payload, headers=headers, verify=True)
        # response_dict = response.json()
    #     if response_dict.get("status") == 1:
    #         return True
    #     else:
    #         return False
    # except Exception as e:
    #     print("Error sending OTP:", e)
    #     return False


def register(request):
    """
    مرحله اول: گرفتن شماره موبایل، پسورد، تکرار پسورد و موافقت با قوانین.
    سپس تولید کد OTP و هدایت به مرحله دوم (ورود کد).
    """
    print(request)
    if request.user.is_authenticated:
        return redirect('home:chat')

    if request.method == 'POST':
        form = RegisterForm(request.POST)  # داده‌ی ارسال‌شده از فرم
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            agree_rules = form.cleaned_data['agree_rules']
            # 🔒 Check if user already exists
            if User.objects.filter(phone_number=phone_number).exists():
                messages.error(request, "این شماره موبایل قبلاً ثبت‌ نام کرده است.")
                return redirect('home:register')
        
            # بررسی هم‌خوانی پسوردها (اگر در فرم بررسی نشده باشد)
            if password1 != password2:
                messages.error(request, "رمز عبور با تکرار رمز عبور یکسان نیست.")
                return redirect('home:register')

            # نرمال‌سازی شماره موبایل
            if phone_number.startswith('+98'):
                phone_number = '0' + phone_number[3:]
            if len(phone_number) != 11 or not phone_number.startswith('09'):
                messages.error(request, "شماره موبایل معتبر وارد کنید (مثال: 09123456789).")
                return redirect('home:register')

            # ساخت یا گرفتن رکورد OTP مرتبط با این شماره
            otp_obj, created = PhoneOTP.objects.get_or_create(phone_number=phone_number)
            if not created:
                # اگر از قبل وجود دارد ولی منقضی شده، حذف و ایجاد مجدد
                if otp_obj.is_expired():
                    otp_obj.delete()
                    otp_obj = PhoneOTP.objects.create(phone_number=phone_number)

            # برای تست: نمایش کد در پیام‌ها (در عمل باید پیامک شود)
            # messages.success(request, f"کد OTP ارسال شد (تست): {otp_obj.code}")

            send_success = send_otp_code(phone_number, otp_obj.code)

            if send_success:
                messages.success(request, "کد OTP به شماره موبایل شما ارسال شد.")
            else:
                messages.error(request, "خطا در ارسال پیامک. لطفاً مجدداً تلاش کنید.")
                return redirect('home:register')

            # ذخیره در سشن تا بعد از تأیید کد، حساب را بسازیم
            request.session['register_data'] = {
                'phone_number': phone_number,
                'password': password1
            }

            return redirect('home:verify_otp')
        else:
            # اگر فرم نامعتبر باشد، خطاهای آن را در messages نمایش می‌دهیم
            for error_list in form.errors.values():
                for error in error_list:
                    messages.error(request, error)
            return redirect('home:register')
    else:
        # روش GET: نمایش فرم خالی
        form = RegisterForm()
    return render(request, 'home/register.html', {'form': form})


def verify_otp_view(request):
    """
    مرحله دوم: گرفتن کد OTP از کاربر. اگر صحیح بود، کاربر ساخته/آپدیت شده و لاگین می‌شود.
    """
    register_data = request.session.get('register_data')
    if not register_data:
        messages.error(request, "ابتدا فرم ثبت‌نام را پر کنید.")
        return redirect('home:register')

    phone_number = register_data.get('phone_number')
    if request.method == 'POST':
        code = request.POST.get('otp_code')
        if not code:
            messages.error(request, "کد تأیید را وارد کنید.")
            return redirect('home:verify_otp')

        try:
            otp_obj = PhoneOTP.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            messages.error(request, "کد OTP برای این شماره یافت نشد.")
            return redirect('home:register')

        if otp_obj.is_expired():
            messages.error(request, "کد تأیید منقضی شده است. دوباره تلاش کنید.")
            otp_obj.delete()
            return redirect('home:register')

        if otp_obj.code == code:
            # تأیید موفق
            otp_obj.is_verified = True
            otp_obj.save()

            password = register_data['password']

            # ساخت یا یافتن کاربر
            user, created = User.objects.get_or_create(phone_number=phone_number)
            user.set_password(password)
            user.save()
            free_plan = SubscriptionPlan.objects.filter(name='free').first()
            if free_plan:
                UserSubscription.objects.get_or_create(
                    user=user,
                    defaults={
                        'subscription_plan': free_plan,
                        'start_date': timezone.now(),
                        'expiration_date': timezone.now() + timedelta(days=7),
                        'message_sent': 0
                    }
                )
            # لاگین
            login(request, user)
            # messages.success(request, "ثبت‌نام/ورود شما با موفقیت انجام شد.")

            # پاکسازی سشن
            del request.session['register_data']
            return redirect('home:home')  # یا هر صفحه‌ی دیگر
        else:
            messages.error(request, "کد تأیید اشتباه است.")
            return redirect('home:verify_otp')

    return render(request, 'home/verify_otp.html')


def forgot_password_view(request):
    """
    مرحله ۱: گرفتن شماره تماس برای ارسال کد OTP جهت بازیابی رمز عبور.
    """
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')

        # 1) بررسی وجود کاربر
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            messages.error(request, "کاربری با این شماره تماس یافت نشد.")
            return redirect('home:forgot_password')

        # 2) ساخت یا دریافت PhoneOTP
        otp_obj, created = PhoneOTP.objects.get_or_create(phone_number=phone_number)

        # 3) خالی کردن فیلد code تا در مدل کد جدید تولید شود
        otp_obj.code = ''
        otp_obj.is_verified = False
        otp_obj.save()

        # 4) ارسال پیامک
        send_success = send_otp_code(phone_number, otp_obj.code)

        if not send_success:
            messages.error(request, "خطا در ارسال پیامک. لطفاً مجدداً تلاش کنید.")
            return redirect('home:forgot_password')

        # 5) ذخیره اطلاعات در سشن تا در مراحل بعدی استفاده شود
        request.session['forgot_data'] = {
            'phone_number': phone_number
        }

        messages.success(request, "کد تأیید برای شما ارسال شد.")
        return redirect('home:forgot_password_verify_otp')
    else:
        return render(request, 'home/forgot_password.html')


def forgot_password_verify_otp_view(request):
    """
    مرحله ۲: گرفتن کد OTP. اگر صحیح و منقضی نشده باشد، به مرحله ریست پسورد می‌رود.
    """
    forgot_data = request.session.get('forgot_data')
    if not forgot_data:
        messages.error(request, "لطفاً ابتدا شماره تماس را وارد کنید.")
        return redirect('home:forgot_password')

    phone_number = forgot_data.get('phone_number')

    if request.method == 'POST':
        code = request.POST.get('otp_code')
        if not code:
            messages.error(request, "کد تأیید را وارد کنید.")
            return redirect('home:forgot_password_verify_otp')

        try:
            otp_obj = PhoneOTP.objects.get(phone_number=phone_number)
        except ObjectDoesNotExist:
            messages.error(request, "کد OTP برای این شماره یافت نشد.")
            return redirect('home:forgot_password')

        # بررسی انقضای OTP
        if otp_obj.is_expired():
            messages.error(request, "کد تأیید منقضی شده است. لطفاً مجدداً تلاش کنید.")
            otp_obj.delete()
            return redirect('home:forgot_password')

        if otp_obj.code == code:
            # تأیید موفق
            otp_obj.is_verified = True
            otp_obj.save()
            return redirect('home:reset_password')
        else:
            messages.error(request, "کد تأیید اشتباه است.")
            return redirect('home:forgot_password_verify_otp')

    return render(request, 'home/forgot_password_verify_otp.html')


def reset_password_view(request):
    """
    مرحله ۳: وارد کردن رمز عبور جدید و تغییر پسورد کاربر.
    """
    forgot_data = request.session.get('forgot_data')
    if not forgot_data:
        messages.error(request, "ابتدا مراحل فراموشی رمز عبور را طی کنید.")
        return redirect('home:forgot_password')

    phone_number = forgot_data.get('phone_number')

    # بررسی کنیم که کد تأیید این شماره قبلاً وریفای شده باشد
    try:
        otp_obj = PhoneOTP.objects.get(phone_number=phone_number)
    except ObjectDoesNotExist:
        messages.error(request, "کد OTP برای این شماره یافت نشد.")
        return redirect('home:forgot_password')

    if not otp_obj.is_verified:
        messages.error(request, "ابتدا کد تأیید را وارد کنید.")
        return redirect('home:forgot_password_verify_otp')

    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if new_password1 != new_password2:
            messages.error(request, "رمزهای عبور مطابقت ندارند.")
            return redirect('home:reset_password')

        # تغییر پسورد کاربر
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            messages.error(request, "کاربر با این شماره وجود ندارد.")
            return redirect('home:forgot_password')

        user.set_password(new_password1)
        user.save()

        # لاگین کاربر (اختیاری)
        login(request, user)

        # پاک کردن اطلاعات فراموشی از سشن
        del request.session['forgot_data']

        # messages.success(request, "رمز عبور با موفقیت تغییر کرد.")
        return redirect('home:home')

    return render(request, 'home/reset_password.html')
