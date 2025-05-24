from django.utils import timezone


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