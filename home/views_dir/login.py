from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from ..forms import UserLoginForm


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        next_url = request.POST.get('next', '')
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                if not data.get('remember_me'):
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(1209600)
                return redirect(next_url or 'home:chat')  # ✅ use next here
            else:
                messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')
        return render(request, 'home/login.html', {'form': form, 'next': next_url})
    else:
        next_url = request.GET.get('next', '')
        form = UserLoginForm()
        return render(request, 'home/login.html', {'form': form, 'next': next_url})



# def logins(request):
#     if request.user.is_authenticated:  # چک کردن اینکه کاربر لاگین کرده یا نه
#         return redirect('home:home')  # انتقال به صفحه‌ی مورد نظر
#     return render(request, 'home/login.html')

def logins(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url or 'home:home')
        else:
            messages.error(request, 'نام کاربری یا رمز عبور اشتباه است')

        # For GET request or failed POST
    next_url = request.GET.get('next', '')
    return render(request, 'home/login.html', {'next': next_url})