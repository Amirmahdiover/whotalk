from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .serializers import MessageSerializer
from django.shortcuts import get_object_or_404
import os
import base64
from django.urls import reverse
from django.core.files.base import ContentFile
from .forms import *
from datetime import timedelta
from django.contrib import messages
import requests
import json
from django.utils.timezone import now
from django.shortcuts import render, redirect
import openai
from .models import *
from account.models import User, PhoneOTP
import random as rand
from django.views import View
from django.db.models import Q
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Company, Token
from datetime import datetime
from .tasks import process_message
from urllib.parse import urlparse
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import http.client
from django.utils.timezone import localtime
import logging
import uuid
from suds.client import Client
from .models import SubscriptionPlan, PaymentTransaction, UserSubscription

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'home/home.html')


def gregorian_to_jalali(gy, gm, gd):
    """
    تبدیل تاریخ میلادی (gy, gm, gd) به تاریخ شمسی.
    الگوریتم برگرفته از تبدیل‌های رایج می‌باشد.
    """
    g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    if gy > 1600:
        jy = 979
        gy -= 1600
    else:
        jy = 0
        gy -= 621
    days = (365 * gy) + ((gy + 3) // 4) - ((gy + 99) // 100) + ((gy + 399) // 400) - 80 + gd + g_d_m[gm - 1]
    jy += 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        jm = 1 + (days // 31)
        jd = 1 + (days % 31)
    else:
        jm = 7 + ((days - 186) // 30)
        jd = 1 + ((days - 186) % 30)
    return jy, jm, jd


def convert_to_jalali(dt, date_format="%Y/%m/%d ساعت %H:%M"):
    """
    تاریخ میلادی (dt) را به زمان محلی تبدیل کرده و سپس به تاریخ شمسی به فرمت مشخص شده تبدیل می‌کند.
    """
    if not dt:
        return ""
    # تبدیل dt به زمان محلی
    local_dt = timezone.localtime(dt)
    jy, jm, jd = gregorian_to_jalali(local_dt.year, local_dt.month, local_dt.day)
    formatted = date_format.replace("%Y", str(jy)) \
        .replace("%m", str(jm).zfill(2)) \
        .replace("%d", str(jd).zfill(2)) \
        .replace("%H", str(local_dt.hour).zfill(2)) \
        .replace("%M", str(local_dt.minute).zfill(2))
    return formatted


class CompanyAPIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            # Extract API key from the header (e.g., "Bearer <api_key>")
            api_key = auth_header.split(" ")[1]
            token_key, company_id, _ = api_key.split(":")
        except (IndexError, ValueError):
            raise AuthenticationFailed("Invalid API Key format.")

        try:
            # Validate the token and company
            token = Token.objects.get(key=token_key)
            company = Company.objects.get(id=company_id, api_key=api_key, owner=token.user)
        except (Token.DoesNotExist, Company.DoesNotExist):
            raise AuthenticationFailed("Invalid API Key.")

        # Return the user and additional company info in the request
        request.company = company  # Attach the company object to the request
        request.user = token.user  # Attach the user object to the request
        # 🔹 اضافه کردن اشتراک کاربر به درخواست
        try:
            request.subscription = token.user.subscription  # اشتراک کاربر
        except UserSubscription.DoesNotExist:
            request.subscription = None  # اگر اشتراک نداشت مقدار None بگیرد

        return (token.user, None)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'


# API view for handling GET and POST requests
class MessageListView(APIView):
    authentication_classes = [CompanyAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]
    openai.api_key = "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"

    def get(self, request):
        # Get today's date
        today = now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Get sender and number from query parameters
        msg_sender = request.query_params.get('msg_sender')
        msg_sender_number = request.query_params.get('msg_sender_number')

        if not msg_sender or not msg_sender_number:
            return Response({"error": "msg_sender and msg_sender_number are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Get the company associated with the request
        company = request.company

        # Get welcome message and admin image
        welcome_message = company.welcome_message or "به پشتیبانی خوش آمدید!"
        adminImg = request.user.image.url

        # Separate messages by received=True and received=False
        received_true_messages = Meesages.objects.filter(
            Q(create__gte=today) &
            Q(received=True) &
            Q(company=company) &  # Filter by company
            (
                    (Q(msg_sender=msg_sender) & Q(msg_sender_number=msg_sender_number) & Q(
                        msg_receiver=request.user.name)) |
                    (Q(msg_sender=request.user.name) & Q(msg_receiver=msg_sender) & Q(
                        msg_receiver_number=msg_sender_number))
            )
        ).order_by('create')

        received_false_messages = Meesages.objects.filter(
            Q(create__gte=today) &
            Q(received=False) &
            Q(company=company) &  # Filter by company
            (
                    (Q(msg_sender=msg_sender) & Q(msg_sender_number=msg_sender_number) & Q(
                        msg_receiver=request.user.name)) |
                    (Q(msg_sender=request.user.name) & Q(msg_receiver=msg_sender) & Q(
                        msg_receiver_number=msg_sender_number))
            )
        ).order_by('create')

        # Serialize messages with tags
        def serialize_messages(messages):
            messages_data = []
            for message in messages:
                tag = "received" if message.msg_sender == request.user.name else "sent"
                message_data = MessageSerializer(message).data
                message_data["id"] = message.id
                message_data["tag"] = tag
                message_data["msgImg"] = message.msgImg
                message_data["create"] = message.create
                message_data["msgFile"] = message.msgFile.url if message.msgFile else None
                message_data["company"] = message.company.name if message.company else None
                messages_data.append(message_data)
            return messages_data

        received_true_serialized = serialize_messages(received_true_messages)
        received_false_serialized = serialize_messages(received_false_messages)

        return Response({
            "welcome": welcome_message,
            "admin_img": adminImg,
            "received_true_messages": received_true_serialized,
            "received_false_messages": received_false_serialized,
            "admin": request.company.name
        }, status=status.HTTP_200_OK)

    def patch(self, request, message_id):
        try:
            message = Meesages.objects.get(id=message_id)
            message.received = True
            message.save()
            return Response({"message": "Message marked as received successfully."}, status=200)
        except Meesages.DoesNotExist:
            return Response({"error": "Message not found."}, status=404)

    def post(self, request):
        # print(request.data)
        data = request.data.copy()
        # دریافت فیلدهای مربوط به فایل (در صورت ارسال)
        file_base64 = data.pop('msgFile_base64', None)
        file_name = data.pop('file_name', None)

        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(msg_receiver=request.user.name, msg_receiver_number='', msgImg='',
                                      company=request.company, received=False, processed_by_api=False, msgFile='')

            if file_base64 and file_name:
                try:
                    decoded_file = base64.b64decode(file_base64)
                    message.msgFile.save(file_name, ContentFile(decoded_file))
                except Exception as e:
                    return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

            connection = Connection.objects.filter(userEmail=message.msg_sender, userNumber=message.msg_sender_number,
                                                   company=request.company).exists()
            if connection:
                Connection.objects.filter(userEmail=message.msg_sender, userNumber=message.msg_sender_number,
                                          company=request.company).delete()
                Connection.objects.create(userEmail=message.msg_sender, userNumber=message.msg_sender_number,
                                          admin=request.user.name, company=request.company)
            else:
                Connection.objects.create(userEmail=message.msg_sender, userNumber=message.msg_sender_number,
                                          admin=request.user.name, company=request.company)

            if message.msgFile:
                try:
                    file_data = message.msgFile.read()
                    encoded_file_data = base64.b64encode(file_data).decode('utf-8')
                    # در صورت نیاز، اشاره‌گر فایل را به ابتدای فایل برگردانید
                    message.msgFile.seek(0)
                except Exception as e:
                    encoded_file_data = None
            else:
                encoded_file_data = None

            file_name_saved = message.msgFile.name if message.msgFile else None

            process_message.delay(
                message.id,
                file_data=encoded_file_data,
                file_name=file_name_saved
            )
            try:
                subscription = request.user.subscription
                if subscription and subscription.is_active():
                    subscription.message_sent += 1
                    subscription.save()
            except UserSubscription.DoesNotExist:
                pass

            return Response({
                "id": message.id,
                "text": message.text,
                "msg_sender": message.msg_sender,
                "msg_receiver": message.msg_receiver,
                "msg_receiver_number": message.msg_receiver_number,
                "received": message.received,
                "processed_by_api": message.processed_by_api,
                "create": message.create,
                "msgImg": message.msgImg,
                "company": message.company.name if message.company else None,
                "msgFile": message.msgFile.url if message.msgFile else None
            }, status=status.HTTP_201_CREATED)

        return Response(
            {"error": "Validation failed", "details": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@login_required(login_url='../login/')  # در صورت عدم لاگین به صفحه اصلی هدایت می‌شود
def chat(request):
    try:
        connection = Connection.objects.filter(admin=request.user.name)
        token, _ = Token.objects.get_or_create(user=request.user)
        companies = Company.objects.filter(owner=request.user)
        return render(request, 'admin/admin-chat.html',
                      {'connection': connection, 'api_key': token.key, 'companies': companies})

    except AttributeError:
        print(AttributeError)
        return redirect('home:home')


def user_logout(request):
    logout(request)
    return redirect('home:home')


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                if not data.get('remember_me'):
                    request.session.set_expiry(0)  # سشن با بسته شدن مرورگر تمام می‌شود
                else:
                    request.session.set_expiry(1209600)
                return redirect('home:chat')
            else:
                messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
                return redirect('home:login')
    else:
        return redirect('home:home')


def logins(request):
    if request.user.is_authenticated:  # چک کردن اینکه کاربر لاگین کرده یا نه
        return redirect('home:home')  # انتقال به صفحه‌ی مورد نظر
    return render(request, 'home/login.html')


def get_company_from_api_key(request):
    data = json.loads(request.body)
    # print(data['apikey'])
    try:
        # تلاش برای پیدا کردن شرکت با استفاده از API key
        company = Company.objects.get(api_key=data['apikey'])
        return JsonResponse({'company_name': company.name, 'owner_name': company.owner.name})
    except Company.DoesNotExist:
        # اگر شرکت پیدا نشد
        return JsonResponse({'error': 'کمپانی یافت نشد!'}, status=404)


def connection(request):
    data = json.loads(request.body)
    # print(data)
    # print(request.user.name)
    company = get_object_or_404(Company, name=data['company'])
    connection = Connection.objects.filter(userEmail=data['userEmail'], userNumber=data['userNumber'],
                                           company=company).exists()
    # Online Admin
    admin = User.objects.get(is_staff=True, name=data['admin'])

    # if (len(admin) >= 2):
    #     admin = admin[rand.randint(0, len(admin) - 1)]
    # elif (len(admin) < 2 and len(admin) >= 1):
    #     admin = admin[0]
    # else:
    #     admin = 'Offline'

    # Connection
    if connection and admin != 'Offline':
        Connection.objects.filter(userEmail=data['userEmail'], userNumber=data['userNumber'], company=company).delete()
        Connection.objects.create(userEmail=data['userEmail'], userNumber=data['userNumber'], company=company,
                                  admin=admin.name)
        return JsonResponse({'connection': 'isThere', 'admin': str(admin.name), 'admin_url': admin.image.url,
                             'company_name': company.name},
                            safe=True)
    elif connection == False and admin != 'Offline':
        Connection.objects.create(userEmail=data['userEmail'], userNumber=data['userNumber'], company=company,
                                  admin=admin.name)
        return JsonResponse({'connection': 'connect', 'admin': str(admin.name), 'admin_url': admin.image.url,
                             'company_name': company.name},
                            safe=True)
    elif connection and admin == 'Offline':
        Connection.objects.filter(userEmail=data['userEmail'], userNumber=data['userNumber'], company=company).delete()
        Connection.objects.create(userEmail=data['userEmail'], userNumber=data['userNumber'], company=company,
                                  admin=admin)
        return JsonResponse(
            {'connection': 'isThere', 'admin': str(admin), 'admin_url': '../../static/home/img/chat.png',
             'company_name': company.name}, safe=True)
    else:
        Connection.objects.create(userEmail=data['userEmail'], userNumber=data['userNumber'], company=company,
                                  admin=admin)
        return JsonResponse(
            {'connection': 'connect', 'admin': str(admin), 'admin_url': '../../static/home/img/chat.png',
             'company_name': company.name}, safe=True)


# Send message view
@csrf_exempt
def user_message(request):
    data = json.loads(request.body)

    # یافتن شرکت
    company = Company.objects.filter(name=data['company']).first()

    # ذخیره پیام کاربر
    new_chat_message = Meesages.objects.create(
        text=data['msg'],
        msg_sender=data['msg_sender'],
        msg_sender_number=data['msg_sender_number'],
        msg_receiver=data['msg_receiver'],
        company=company,
        received=True,
    )

    file_name = data.get('file_name')
    file_data = data.get('file_data')

    if file_name and file_data:
        # Decode and save the file
        decoded_file = base64.b64decode(file_data)
        new_chat_message.msgFile.save(file_name, ContentFile(decoded_file))
        file_url = new_chat_message.msgFile.url if new_chat_message.msgFile and hasattr(new_chat_message.msgFile,
                                                                                        'url') else None
    else:
        file_url = None
    # پاسخ اولیه به کاربر
    response_data = {
        'msgTextType': new_chat_message.text,
        'msgSender': new_chat_message.msg_sender,
        'msg_sender_number': new_chat_message.msg_sender_number,
        'msgReceiver': new_chat_message.msg_receiver,
        'dateTimeStatus': localtime(new_chat_message.create).strftime('%H:%M:%S'),
        'msgImg': new_chat_message.msgImg,
        'fileName': file_url,
        'company_name': company.name if company else None,
        'messageId': new_chat_message.id,  # اضافه کردن ID پیام
    }
    admin_user = User.objects.get(name=new_chat_message.msg_receiver)
    # اجرای تسک در پس‌زمینه
    process_message.delay(
        message_id=new_chat_message.id,
        file_data=data.get('file_data'),
        file_name=data.get('file_name'),
    )
    print("Message ID:", new_chat_message.id)

    return JsonResponse(response_data, safe=True)


def check_response(request, message_id):
    try:
        message = get_object_or_404(Meesages, id=message_id)
        # print('message')
        # print(message)
        admin_response = Meesages.objects.filter(
            msg_sender=message.msg_receiver,
            msg_receiver=message.msg_sender,
            create__gte=message.create
        ).first()
        # print('admin_response')
        # print(admin_response)
        if admin_response:
            return JsonResponse({
                'adminResponse': {
                    'msgTextAdmin': admin_response.text,
                    'msgSender': admin_response.msg_sender,
                    'msgReceiver': admin_response.msg_receiver,
                    'msgReceiverNumber': admin_response.msg_receiver_number,
                    'dateTimeStatus': localtime(admin_response.create).strftime('%H:%M:%S'),
                    'msgImg': admin_response.msgImg,
                    'received': admin_response.received,
                    'company_name': admin_response.company.name,
                }
            }, safe=True)
        return JsonResponse({
            'adminResponse': None,
            'debug': {
                'msgReceiver': message.msg_receiver,
                'msgSender': message.msg_sender,
                'createTime': message.create,
            }
        }, safe=True)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# get message from admin to user
def admin_message(request):
    data = json.loads(request.body)
    list = []
    records = Meesages.objects.filter(msg_sender=data['msg_sender'], msg_receiver=data['msg_receiver'],
                                      msg_receiver_number=data['msg_receiver_number'], received=False)
    for rec in records:
        file_url = rec.msgFile.url if rec.msgFile and hasattr(rec.msgFile, 'url') else None
        list.append({'msgText': rec.text, 'msgSender': rec.msg_sender, 'msgReceiver': rec.msg_receiver,
                     'msgReceiverNumber': rec.msg_receiver_number, 'received': rec.received,
                     'dateTimeText': localtime(rec.create).strftime('%H:%M:%S'), 'msgImg': data['msg_sender_img'],
                     'fileName': file_url})
        rec.received = True
        rec.save()
    return JsonResponse(list, safe=False)


# get message from admin to admin
def admin_message_admin(request):
    data = json.loads(request.body)
    admin = request.user
    list = []
    records = Meesages.objects.filter(msg_receiver=data['msg_sender'], msg_sender=admin.name,
                                      msg_receiver_number=data['msg_sender_number'], received=False)
    for rec in records:
        # if rec.processed_by_api == True:
        list.append({'msgTextAdmin': rec.text, 'msgSender': rec.msg_sender, 'msgReceiver': rec.msg_receiver,
                     'msgSenderNumber': rec.msg_sender_number, 'received': rec.received,
                     'dateTimeStatus': localtime(rec.create).strftime('%H:%M:%S'), 'msgImg': str(admin.image.url)})
        rec.received = True
        rec.save()

    return JsonResponse(list, safe=False)


# get all messages sent by user to admin
def all_messages(request):
    data = json.loads(request.body)
    list = []
    # Get today's date
    today = now().date()
    messages = Meesages.objects.filter(create__date=today)
    for msg in messages:
        file_url = msg.msgFile.url if msg.msgFile and hasattr(msg.msgFile, 'url') else None
        if (msg.msg_sender == data['msg_sender'] and msg.msg_sender_number == data[
            'msg_sender_number'] and msg.msg_receiver == data['msg_sender_admin']):
            list.append({'msgText': msg.text,
                         'msgSender': msg.msg_sender,
                         'msgReceiver': msg.msg_receiver,
                         'sent_for': msg.msg_sender,
                         'dateTimeStatus': localtime(msg.create).strftime('%H:%M:%S'),
                         'fileName': file_url
                         })
        elif (msg.msg_sender == data['msg_sender_admin'] and msg.msg_receiver == data[
            'msg_sender'] and msg.msg_receiver_number == data['msg_sender_number']):
            list.append({'msgText': msg.text, 'msgSender': msg.msg_sender, 'msgReceiver': msg.msg_receiver,
                         'received_from': msg.msg_sender, 'dateTimeStatus': localtime(msg.create).strftime('%H:%M:%S'),
                         'msgImg': data['msg_sender_img'],
                         'fileName': file_url})
    return JsonResponse(list, safe=False)


def online_admin(request):
    data = json.loads(request.body)
    connection = Connection.objects.get(userEmail=data['userEmail'], userNumber=data['userNumber'])
    # Online Admin
    admin = User.objects.filter(is_staff=True, online=True)
    if (len(admin) >= 2):
        admin = admin[rand.randint(0, len(admin) - 1)]
    elif (len(admin) < 2 and len(admin) >= 1):
        admin = admin[0]
    else:
        admin = 'Offline'

    if (connection.admin == 'Offline' and admin != 'Offline'):

        Connection.objects.filter(userEmail=data['userEmail'], userNumber=data['userNumber']).update(admin=admin.name)
        dd = admin.image.url
        Meesages.objects.filter(msg_sender=data['userEmail'], msg_sender_number=data['userNumber'],
                                msg_receiver='Offline').update(msg_receiver=admin.name, msgImg=admin.image.url)
        connection.admin = admin.name
        admin_name = connection.admin
    else:
        dd = '../../static/home/img/chat.png'
        admin_name = 'Offline'

    return JsonResponse({'admin': str(admin_name), 'admin_url': str(dd)}, safe=True)


# admin connection remover
def admin_connection_remover(request):
    Connection.objects.filter(admin=request.user.name).delete()
    Meesages.objects.filter(msg_sender=request.user.name).delete()
    Meesages.objects.filter(msg_receiver=request.user.name).delete()
    return JsonResponse({'Connection': 'Removed'}, safe=False)


def admin_connections(request):
    data = json.loads(request.body)
    # company_name = request.GET.get('company')
    connection = Connection.objects.filter(admin=request.user.name, company__name=data['company'], received=False)
    list = []
    for connect in connection:
        if not connect.received:
            list.append({'userEmail': connect.userEmail, 'userNumber': connect.userNumber, 'admin': connect.admin,
                         'company': connect.company.name})
            connect.received = True
            connect.save()
    # Connection.objects.filter(admin=request.user.name, company__name=data['company'], received=False).update(
    #     received=True)
    return JsonResponse(list, safe=False)


# all admin connections
def all_admin_connections(request):
    data = json.loads(request.body)
    # print(data)
    connection = Connection.objects.filter(admin=request.user.name, company__name=data['company'], received=True)
    list = []
    for connect in connection:
        list.append({'userEmail': connect.userEmail, 'userNumber': connect.userNumber, 'admin': connect.admin,
                     'company': connect.company.name})
    # print(list)
    return JsonResponse(list, safe=False)


# send admin message to user
def send_admin_message(request):
    data = json.loads(request.body)

    admin = request.user
    company = get_object_or_404(Company, name=data['company'])
    new_chat_message = Meesages.objects.create(text=data['msg'], msg_sender=admin.name,
                                               msg_receiver_number=data['msg_receiver_number'],
                                               msg_receiver=data['msg_receiver'], msgImg=admin.image.url,
                                               company=company)
    file_name = data.get('file_name')
    file_data = data.get('file_data')
    if file_name and file_data:
        decoded_file = base64.b64decode(file_data)
        new_chat_message.msgFile.save(file_name, ContentFile(decoded_file))
    file_url = new_chat_message.msgFile.url if new_chat_message.msgFile and hasattr(new_chat_message.msgFile,
                                                                                    'url') else None
    return JsonResponse({'msgTextAdmin': new_chat_message.text, 'msgSender': new_chat_message.msg_sender,
                         'msgReceiverNumber': new_chat_message.msg_receiver_number,
                         'msgReceiver': new_chat_message.msg_receiver,
                         'dateTimeStatus': localtime(new_chat_message.create).strftime('%H:%M:%S'),
                         'msgImg': new_chat_message.msgImg,
                         'fileName': file_url,
                         'company': new_chat_message.company.name,
                         }, safe=True)


# get message from user to admin
def get_user_message(request):
    data = json.loads(request.body)
    admin = request.user
    list = []
    records = Meesages.objects.filter(msg_sender=data['msg_sender'], msg_receiver=admin.name,
                                      msg_sender_number=data['msg_sender_number'], received=False)
    for rec in records:
        file_url = rec.msgFile.url if rec.msgFile and hasattr(rec.msgFile, 'url') else None
        list.append({'msgText': rec.text, 'msgSender': rec.msg_sender, 'msgReceiver': rec.msg_receiver,
                     'msgSenderNumber': rec.msg_sender_number, 'received': rec.received,
                     'dateTimeText': localtime(rec.create).strftime('%H:%M:%S'), 'msgImg': '', 'fileName': file_url})
        rec.received = True
        rec.save()
    return JsonResponse(list, safe=False)


# get message from api to true/false
def get_api_message(request):
    data = json.loads(request.body)
    admin = request.user
    list = []
    records = Meesages.objects.filter(msg_sender=admin.name, msg_receiver=data['msg_sender'],
                                      msg_receiver_number=data['msg_sender_number'], processed_by_api=True)
    for rec in records:
        # list.append({'msgText': rec.text, 'msgSender': rec.msg_sender, 'msgReceiver': rec.msg_receiver,
        #              'msgSenderNumber': rec.msg_sender_number, 'received': rec.received,
        #              'dateTimeText': rec.create.time().strftime('%H:%M:%S'), 'msgImg': ''})
        rec.processed_by_api = False
        rec.save()
    return JsonResponse(list, safe=False)


# get all messages -> admin to user and user to admin
def get_all_messages(request):
    data = json.loads(request.body)
    admin = request.user

    # فیلتر کردن پیام‌ها با Q objects
    messages = Meesages.objects.filter(
        Q(msg_sender=data['msg_sender'], msg_sender_number=data['msg_sender_number'], msg_receiver=admin.name,
          received=True) |
        Q(msg_sender=admin.name, msg_receiver=data['msg_sender'], msg_receiver_number=data['msg_sender_number'],
          received=True)
    ).order_by('create')  # مرتب‌سازی بر اساس زمان ایجاد

    result = []
    for msg in messages:
        file_url = msg.msgFile.url if msg.msgFile and hasattr(msg.msgFile, 'url') else None
        formatted_time = localtime(msg.create).strftime('%H:%M:%S')

        # تفکیک پیام‌های ارسالی توسط کاربر و مدیر
        if msg.msg_sender == data['msg_sender']:
            result.append({
                'msgText': msg.text,
                'msgSender': msg.msg_sender,
                'msgReceiver': msg.msg_receiver,
                'sent_by_user': msg.msg_sender,
                'dateTimeStatus': formatted_time,
                'msgImg': '',  # پیام ارسالی توسط کاربر تصویر ندارد
                'fileName': file_url,
            })
        else:
            result.append({
                'msgText': msg.text,
                'msgSender': msg.msg_sender,
                'msgReceiver': msg.msg_receiver,
                'sent_by_admin': msg.msg_sender,
                'dateTimeStatus': formatted_time,
                'msgImg': admin.image.url if hasattr(admin, 'image') and admin.image else '',
                'fileName': file_url,
            })
    return JsonResponse(result, safe=False)


# new message check
def new_message(request):
    data = json.loads(request.body)
    # print(data)
    admin = request.user
    mee = Meesages.objects.filter(msg_sender=admin.name, msg_receiver=data['msg_sender2'],
                                  msg_receiver_number=data['msg_sender_number2'], processed_by_api=True)
    # print(mee)
    if (len(mee) > 0):
        return JsonResponse({'message2': 'true'}, safe=False)
    else:
        return JsonResponse({'message2': 'false'}, safe=False)


class UploadFAQView(View):
    def post(self, request, *args, **kwargs):
        if 'faq' in request.FILES:
            # عملیات ذخیره‌سازی فایل
            faq_file = request.FILES['faq']
            if request.user.faq:
                old_faq_path = request.user.faq.path
                if os.path.exists(old_faq_path):
                    os.remove(old_faq_path)
            request.user.faq = faq_file
            request.user.save()
            messages.success(request, "فایل با موفقیت بارگذاری شد.")
        else:
            messages.error(request, "لطفاً یک فایل انتخاب کنید.")
        return redirect('home:chat')

    def get(self, request, *args, **kwargs):
        return render(request, 'admin/admin-chat.html')


def get_user_ip(request):
    # Get the client's IP address
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]  # Take the first IP if there are multiple
    else:
        ip = request.META.get('REMOTE_ADDR')

    # Return the IP address in JSON format
    return JsonResponse({'ip': ip})


@login_required(login_url='../login/')
def create_company(request):
    if request.method == 'POST':
        if 'delete_company_id' in request.POST:  # حذف شرکت
            company_id = request.POST.get('delete_company_id')
            try:
                company = Company.objects.get(id=company_id, owner=request.user)
                company.delete()
                return redirect('home:create_company')  # هدایت به صفحه داشبورد پس از حذف
            except Company.DoesNotExist:
                messages.error(request, 'شرکت یافت نشد یا شما مجاز به حذف آن نیستید.')
        else:  # ایجاد یا ویرایش شرکت
            company_id = request.POST.get('company_id')

            form = CompanyForm(request.POST, request.FILES)
            if form.is_valid():
                name = form.cleaned_data['name']
                website = form.cleaned_data['website']
                faq_company = form.cleaned_data.get('faq_company', None)
                welcome_message = form.cleaned_data.get('welcome_message', '')

                if company_id:  # ویرایش شرکت
                    company = Company.objects.get(id=company_id, owner=request.user)
                    company.name = name
                    company.website = website
                    if faq_company:
                        if company.faq:  # اگر فایل قبلی موجود است
                            company.faq.delete()  # حذف فایل از سرور
                        company.faq = faq_company  # جایگزینی فایل جدید
                    company.welcome_message = welcome_message
                    company.save()
                else:  # ایجاد شرکت جدید
                    company = Company.objects.create(
                        name=name,
                        website=website,
                        faq=faq_company,
                        welcome_message=welcome_message,
                        owner=request.user
                    )
                    company.generate_api_key()  # تولید کلید API
                    company.save()

                return redirect('home:create_company')  # هدایت به صفحه داشبورد

    else:
        form = CompanyForm()

    companies = Company.objects.filter(owner=request.user)
    return render(request, 'admin/create_company.html', {'form': form, 'companies': companies})


# get all messages sent by user to admin
def welcome_message(request):
    data = json.loads(request.body)
    company = Company.objects.filter(name=data['company']).first()
    if company and company.welcome_message:  # Check if company exists and has a welcome message
        return JsonResponse({
            'msgTextAdmin': company.welcome_message,
            'msgSender': data['msg_sender_admin'],
            'msgReceiver': data['msg_sender'],
            'msgReceiverNumber': data['msg_sender_number'],
            'dateTimeStatus': datetime.now().strftime('%H:%M:%S'),
            'msgImg': data['msg_sender_img'],
            'received': True,
            'company_name': company.name,
        }, safe=True)
    else:
        return JsonResponse({'message': 'No welcome message available'}, status=204)  # No Content status


def pricing(request):
    return render(request, 'home/pricing.html')


def about_us(request):
    return render(request, 'home/about-us.html')


def contact_us(request):
    if request.method == 'POST':
        # مقادیر فیلدهای فرم را از request.POST دریافت می‌کنیم
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # تنظیم عنوان و بدنه ایمیل
        subject = 'پیام جدید از فرم تماس'
        body = f"""
            نام و نام خانوادگی: {name}
            ایمیل فرستنده: {email}
            شماره موبایل: {phone}

            متن پیام:
            {message}
            """

        # آدرس ایمیل مدیر سایت
        print(body)
        admin_email = 'me@hesaa.me'  # ایمیل مدیر یا مسئول سایت

        # ارسال ایمیل
        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,  # فرستنده (ایمیلی که در settings تنظیم کردید)
                [admin_email],  # گیرنده (ایمیل مدیر)
                fail_silently=False
            )
            messages.success(request, 'پیام شما با موفقیت ارسال شد.')
        except Exception as e:
            # در صورت بروز خطا
            messages.error(request, f'خطایی در ارسال پیام رخ داد: {e}')

        # در نهایت می‌توانید به همان صفحه برگردید یا به یک صفحه تشکر هدایت کنید
        return redirect('home:contact_us')  # یا هر مسیر دیگری که در urls.py تعریف کرده‌اید.

        # اگر متد درخواست GET باشد، فقط قالب را رندر می‌کنیم
    return render(request, 'home/contact-us.html')


def privacy_policy(request):
    return render(request, 'home/privacy-policy.html')


def send_otp_code(phone_number, code):
    """
    ارسال کد تأیید به یک شماره موبایل از طریق پنل sms.ir

    :param phone_number: رشته شماره موبایل گیرنده (مثال: "09123456789")
    :param code: رشته یا عدد کد OTP که باید ارسال شود
    :return: True در صورت موفقیت ارسال، False در غیر این صورت
    """
    url = "https://api.sms.ir/v1/send/bulk"
    payload = {
        "lineNumber": 30007487133023,
        "messageText": f"هوتاک\nکد تایید: {code}",
        "mobiles": [phone_number],
        "sendDateTime": None
    }
    headers = {
        'X-API-KEY': 'wjYeGsHfY5mZKDklIS75gyxFt9LMZW2Erkp90cNuZIVWOfbL',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers, verify=True)
        response_dict = response.json()
        if response_dict.get("status") == 1:
            return True
        else:
            return False
    except Exception as e:
        print("Error sending OTP:", e)
        return False


def register(request):
    """
    مرحله اول: گرفتن شماره موبایل، پسورد، تکرار پسورد و موافقت با قوانین.
    سپس تولید کد OTP و هدایت به مرحله دوم (ورود کد).
    """
    if request.user.is_authenticated:
        return redirect('home:chat')

    if request.method == 'POST':
        form = RegisterForm(request.POST)  # داده‌ی ارسال‌شده از فرم
        if form.is_valid():
            phone_number = form.cleaned_data['phone_number']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            agree_rules = form.cleaned_data['agree_rules']

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


@csrf_exempt
def validate_domain_and_get_api_key(request):
    print('out valid state')
    """
    Validate the domain from Referer header and return the API key for the corresponding company.
    """
    if request.method == "OPTIONS":
        response = HttpResponse()
        # استفاده از Origin در صورت موجود بودن، در غیر اینصورت ست کردن *
        origin = request.headers.get("Origin", "*")
        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        response["Access-Control-Allow-Credentials"] = "true"
        return response

    if request.method == "POST":
        try:
            domain = None
            # ابتدا بررسی هدر Origin
            origin = request.headers.get("Origin")
            if origin:
                parsed_origin = urlparse(origin)
                domain = parsed_origin.hostname
                # logger.info(f"Origin header: {origin}, extracted domain: {domain}")
            # در صورت عدم وجود Origin، به هدر Referer مراجعه می‌کنیم
            if not domain:
                referer = request.headers.get("Referer")
                logger.info(f"Referer header: {referer}")
                if not referer:
                    return JsonResponse({"error": "Referer header is missing"}, status=403)
                parsed_referer = urlparse(referer)
                domain = parsed_referer.hostname
                # logger.info(f"Extracted domain from Referer: {domain}")
            if not domain:
                return JsonResponse({"error": "Invalid domain extraction"}, status=400)

            companies = Company.objects.all()
            for company in companies:
                if company.is_domain_valid(domain):
                    user_subscription = company.owner.subscription if hasattr(company.owner, 'subscription') else None
                    if not user_subscription or not user_subscription.can_send_message():
                        return JsonResponse({"error": "Subscription expired or not found"}, status=403)

                    response = JsonResponse({"api_key": company.api_key, "valid": True})
                    # اضافه کردن هدرهای CORS در صورت وجود Origin
                    if origin:
                        response["Access-Control-Allow-Origin"] = origin
                        response["Access-Control-Allow-Credentials"] = "true"
                    return response

            return JsonResponse({"error": "Unauthorized domain"}, status=403)

        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required(login_url='../login/')
def edit_user(request):
    user = request.user
    password_form = CustomPasswordChangeForm(user)
    user_form = UserEditForm(instance=user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, request.FILES, instance=user)
        password_form = CustomPasswordChangeForm(user, request.POST)

        # اگر فرم اطلاعات کاربر ارسال شده باشد
        if 'user_info_submit' in request.POST:
            if user_form.is_valid():
                if user_form.cleaned_data.get('clear_image'):
                    user.image.delete(save=False)  # تصویر فعلی را حذف کن
                user_form.save()
                messages.success(request, 'اطلاعات شما با موفقیت به‌روزرسانی شد.')
                return redirect('home:edit_user')

        # اگر فرم تغییر رمز عبور ارسال شده باشد
        elif 'password_change_submit' in request.POST:
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'رمز عبور شما با موفقیت تغییر یافت.')
                return redirect('home:edit_user')

    return render(request, 'admin/edit_user.html', {
        'user_form': user_form,
        'password_form': password_form,
    })


MERCHANT_ID = settings.ZARINPAL_MERCHANT_ID
ZARINPAL_WEBSERVICE = settings.ZARINPAL_WEBSERVICE


@login_required(login_url='../login/')
def subscription_view(request):
    """
    نمایش صفحه خرید اشتراک (subscription.html)؛ کاربر یکی از پلن‌های موجود را انتخاب می‌کند.
    """
    try:
        user_subscription = request.user.subscription
    except UserSubscription.DoesNotExist:
        user_subscription = None

        # اگر اشتراکی موجود و فعال باشد
    if user_subscription and user_subscription.expiration_date and timezone.now() < user_subscription.expiration_date:
        jalali_expiration = convert_to_jalali(user_subscription.expiration_date)
        message = f"شما دارای اشتراک فعالی تا تاریخ {jalali_expiration} هستید، لطفاً تا پایان آن صبر کنید."
        return render(request, "admin/subscription_already_active.html", {"message": message})

    plans = SubscriptionPlan.objects.all().order_by('duration')

    if request.method == "POST":
        selected_plan_id = request.POST.get("plan_id")
        try:
            selected_plan = SubscriptionPlan.objects.get(id=selected_plan_id)
        except SubscriptionPlan.DoesNotExist:
            return render(request, "admin/subscription.html", {
                "plans": plans,
                "error": "پلن انتخاب شده نامعتبر است."
            })

        # ایجاد یک شماره سفارش به کمک uuid (اولین بخش از uuid)
        order_number = str(uuid.uuid4()).split('-')[0]
        # ایجاد یک رکورد پرداخت با وضعیت اولیه pending
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

    return render(request, "admin/subscription.html", {"plans": plans})


@login_required(login_url='../login/')  # در صورت عدم لاگین به صفحه اصلی هدایت می‌شود
def subscription_intermediate_view(request, order_number):
    """
    نمایش صفحه واسط (subscription_intermediate.html) که اطلاعات خرید اشتراک شامل نام کاربر،
    تاریخ خرید، پلن انتخابی، شماره سفارش و وضعیت پرداخت را نمایش می‌دهد.
    """
    transaction = get_object_or_404(PaymentTransaction, transaction_id=order_number, user=request.user)
    purchase_date_jalali = convert_to_jalali(transaction.created_at, "%Y/%m/%d %H:%M")
    context = {
        "user_name": request.user.get_full_name() or request.user.username,
        "purchase_date": purchase_date_jalali,
        "selected_plan": transaction.subscription_plan,
        "order_number": transaction.transaction_id,
        "payment_status": transaction.get_status_display(),
    }
    return render(request, "admin/subscription_intermediate.html", context)


@login_required(login_url='../login/')  # در صورت عدم لاگین به صفحه اصلی هدایت می‌شود
def payment_request_view(request, order_number):
    """
    ارسال درخواست پرداخت به درگاه زرین پال.
    """
    try:
        transaction = PaymentTransaction.objects.get(transaction_id=order_number, user=request.user)
    except PaymentTransaction.DoesNotExist:
        return HttpResponse("سفارش مورد نظر یافت نشد.", status=404)

    amount = transaction.amount  # مبلغ به تومان
    description = f"پرداخت اشتراک {transaction.subscription_plan.get_name_display()} برای {request.user.username}"
    email = request.user.email or ""
    mobile = getattr(request.user, "phone_number", "")
    callback_url = request.build_absolute_uri(reverse("home:payment_verify"))

    client = Client(ZARINPAL_WEBSERVICE)
    result = client.service.PaymentRequest(MERCHANT_ID,
                                           amount,
                                           description,
                                           email,
                                           mobile,
                                           callback_url)
    if result.Status == 100:
        # به‌روزرسانی شماره سفارش با Authority دریافتی از زرین پال
        transaction.transaction_id = result.Authority
        transaction.save()
        # هدایت به درگاه پرداخت
        return redirect("https://www.zarinpal.com/pg/StartPay/" + result.Authority)
    else:
        context = {
            "error": "خطا در ارسال درخواست به درگاه پرداخت.",
            "order_number": transaction.transaction_id,
            "payment_status": transaction.get_status_display(),
            "selected_plan": transaction.subscription_plan,
            "user_name": request.user.get_full_name() or request.user.username,
            "purchase_date": timezone.now(),
        }
        return render(request, "admin/subscription_intermediate.html", context)


@login_required(login_url='../login/')  # در صورت عدم لاگین به صفحه اصلی هدایت می‌شود
def payment_verify_view(request):
    """
    ویوی callback پس از بازگشت از درگاه زرین پال. بررسی وضعیت پرداخت و فعال‌سازی اشتراک کاربر در صورت موفقیت.
    """
    client = Client(ZARINPAL_WEBSERVICE)
    status = request.GET.get("Status")
    authority = request.GET.get("Authority")

    try:
        transaction = PaymentTransaction.objects.get(transaction_id=authority, user=request.user, status="pending")
    except PaymentTransaction.DoesNotExist:
        return HttpResponse("سفارش مورد نظر یافت نشد.", status=404)

    if status == "OK":
        amount = transaction.amount
        result = client.service.PaymentVerification(MERCHANT_ID, authority, amount)
        if result.Status == 100:
            transaction.status = "successful"
            transaction.save()

            # فعال‌سازی اشتراک کاربر
            now = timezone.now()
            expiration = now + transaction.subscription_plan.duration
            try:
                user_subscription = request.user.subscription
            except UserSubscription.DoesNotExist:
                user_subscription = UserSubscription(user=request.user)
            user_subscription.subscription_plan = transaction.subscription_plan
            user_subscription.start_date = now
            user_subscription.expiration_date = expiration
            user_subscription.message_sent = 0
            user_subscription.save()

            # پس از پرداخت موفق، هدایت به صفحه admin-chat.html (آدرس این صفحه در پروژه شما باید تنظیم شود)
            return redirect("admin_chat")
        else:
            transaction.status = "failed"
            transaction.save()
            context = {
                "error": f"پرداخت با خطا مواجه شد. کد خطا: {result.Status}",
                "order_number": transaction.transaction_id,
                "payment_status": transaction.get_status_display(),
                "selected_plan": transaction.subscription_plan,
                "user_name": request.user.get_full_name() or request.user.username,
                "purchase_date": timezone.now(),
            }
            return render(request, "admin/subscription_intermediate.html", context)
    else:
        transaction.status = "failed"
        transaction.save()
        context = {
            "error": "پرداخت توسط کاربر لغو شده یا با خطا مواجه شده است.",
            "order_number": transaction.transaction_id,
            "payment_status": transaction.get_status_display(),
            "selected_plan": transaction.subscription_plan,
            "user_name": request.user.get_full_name() or request.user.username,
            "purchase_date": timezone.now(),
        }
        return render(request, "admin/subscription_intermediate.html", context)


@login_required(login_url='../login/')  # در صورت عدم لاگین به صفحه اصلی هدایت می‌شود
def factor_view(request):
    """
    نمایش صفحه فاکتور (factor.html) که شامل لیست تراکنش‌های پرداخت کاربر است.
    """
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by("-created_at")
    for transaction in transactions:
        # تبدیل تاریخ میلادی به شمسی
        transaction.jalali_date = convert_to_jalali(transaction.created_at, "%Y/%m/%d")
        # حذف ممیز از مبلغ (به صورت تبدیل به int)
        transaction.amount_int = int(transaction.amount)
    return render(request, "admin/factor.html", {"transactions": transactions})
