from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd

from ..forms import CompanyForm
from ..models import Company
from ai_utils.build_and_save_faq_index import build_and_save_faq_index



@login_required(login_url='../login/')
def create_company(request):

    """
    Handle company creation, update, and deletion via POST request.

    This view is triggered when a user submits the "هوتاک‌ها" (create/update company) form.

    - If 'delete_company_id' is in POST data: deletes the company with that ID if the user is the owner.
    - If 'company_id' is in POST data:
        - Updates the existing company (name, website, welcome message).
        - If a new FAQ Excel file is uploaded, reads it using pandas and passes data to `build_and_save_faq_index`
          to create and store text embeddings (see that function’s docstring for details).
        - Replaces the old FAQ file if it exists.
    - If no 'company_id' is provided:
        - Creates a new company with the given form data and uploaded FAQ file.
        - Calls `build_and_save_faq_index` to generate embeddings.
        - Calls `generate_api_key()` from the model to assign a new API key.
    
    After processing, redirects back to 'home:create_company'.

    This view only accepts POST and GET methods. GET returns the company form and list of companies.
    """
    
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

                        # reading file as excel format
                        faq_excel = pd.read_excel(faq_company)
                        faq_data = [
                            {"question": row["سوال"], "answer": row["پاسخ"]}
                            for _, row in faq_excel.iterrows()
                        ]
                        build_and_save_faq_index(company.name, faq_data)

                        if company.faq:  # اگر فایل قبلی موجود است
                            company.faq.delete()  # حذف فایل از سرور
                        company.faq = faq_company  # جایگزینی فایل جدید
                    company.welcome_message = welcome_message
                    company.save()
                else:  # ایجاد شرکت جدید
                    
                    # reading file as excel format
                    faq_excel = pd.read_excel(faq_company)
                    faq_data = [
                        {"question": row["سوال"], "answer": row["پاسخ"]}
                        for _, row in faq_excel.iterrows()
                    ]
                    build_and_save_faq_index(name, faq_data)

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
