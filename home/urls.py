from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .views import UploadFAQView, MessageListView
from .views_dir.create_company import create_company
from .views_dir.user_auth_otp import register,verify_otp_view,forgot_password_view,forgot_password_verify_otp_view,reset_password_view
from .views_dir.login import user_login,logins
from .views_dir.check_sub import check_subscription_btn
from .views_dir.pricing_check_auth import pricing,choose_plan

app_name='home'

urlpatterns = [
     path('', views.home, name='home'),
     path('chat/', views.chat, name='chat'),
     path('logout/', views.user_logout, name='logout'),
     path('user_login/', user_login, name='user_login'),
     path('login/', logins, name='login'),
     # Connection
     path('connect/', views.connection, name='connect'),
     # send message form user to admin
     path('send-message/', views.user_message, name='sendMessage'),
     # get message from admin to user
     path('admin-message/', views.admin_message, name='admin-message'),
     # get message from admin to admin
     path('admin-message-admin/', views.admin_message_admin, name='admin-message-admin'),
     # get all messages -> sent by user for admin and sent by admin for user
     path('all-messages/', views.all_messages, name='all-messages'),
     # online admin finder
     path('online-admin/', views.online_admin, name='online-admin'),
     # admin connection remover
     path('admin-connection-remover/', views.admin_connection_remover, name='admin-connection-remover'),
     # admin connections
     path('admin-connections/', views.admin_connections, name='admin-connections'),
     # all admin connections
     path('all-admin-connections/', views.all_admin_connections, name='all-admin-connections'),
     # Send admin message to user
     path('send-admin-message/', views.send_admin_message, name='send-admin-message'),
     # get User message to admin
     path('get-user-message/', views.get_user_message, name='get-user-message'),
     # get all messages -> panel admin to user and user to admin
     path('get-all-messages/', views.get_all_messages, name='get-all-messages'),
     # new message check
     path('new-message/', views.new_message, name='new-message'),
     # upload faq questions
     path('upload-faq/', UploadFAQView.as_view(), name='upload_faq'),
     # API get
     path('get-api-message/', views.get_api_message, name='get-api-message'),
     # API
     path('api/messages/', MessageListView.as_view(), name='message-list'),
     # User IP
     path('get-ip/', views.get_user_ip, name='get_user_ip'),
     # get user's company
     path('get-company-from-api-key/', views.get_company_from_api_key, name='get_company_from_api_key'),
     # Create Company
     path('create-company/', create_company, name='create_company'),
     # Welcome Message
     path('welcome-message/', views.welcome_message, name='welcome-message'),
     path('check-response/<int:message_id>/', views.check_response, name='check_response'),
     path('pricing/', pricing, name='pricing'),
     path('about-us/', views.about_us, name='about_us'),
     path('contact-us/', views.contact_us, name='contact_us'),
     path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
     path('register/', register, name='register'),
     path('api/messages/<int:message_id>/mark_as_received/', MessageListView.as_view(), name='message-detail'),
     path('api/validate_domain_and_get_api_key/', views.validate_domain_and_get_api_key,
          name='validate_domain_and_get_api_key'),
     path('verify_otp/', verify_otp_view, name='verify_otp'),
     # forget passwords
     path('forgot-password/', forgot_password_view, name='forgot_password'),
     path('forgot-password/verify-otp/', forgot_password_verify_otp_view, name='forgot_password_verify_otp'),
     path('forgot-password/reset/', reset_password_view, name='reset_password'),
     path('edit-user/', views.edit_user, name='edit_user'),
     path('subscription/', views.subscription_view, name='subscription'),
     path('subscription/intermediate/<str:order_number>/', views.subscription_intermediate_view,
          name='subscription_intermediate'),
     path('payment/request/<str:order_number>/', views.payment_request_view, name='payment_request'),
     path('payment/verify/', views.payment_verify_view, name='payment_verify'),
     path('factor/', views.factor_view, name='factor'),
     path('check-subscription/', check_subscription_btn, name='check_subscription'),
     path('choose-plan/', choose_plan, name='choose_plan'),
     path('sentry-debug/', views.trigger_error),
]
