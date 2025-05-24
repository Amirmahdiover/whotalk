from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
import json
from ..forms import CompanyForm
from ..models import Company
from ai_utils.save_faq_embeddings_for_company import save_faq_embeddings_for_company
from django.core.exceptions import ValidationError

def merge_faq_default(faq_excel):
    data = {
        'سوال': [
            'سلام',
        ],
        'پاسخ': [
            'سلام دوست عزیز! چطور می‌تونم کمکتون کنم؟',
        ]
        }
    df = pd.DataFrame(data)
    pd_merged=pd.concat([df, faq_excel], ignore_index=True)
    faq_data = [
        {"question": row["سوال"], "answer": row["پاسخ"]}
        for _, row in pd_merged.iterrows()
    ]
    return faq_data



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
                faq_changed = True  # default assumption


                
                if company_id:  # ویرایش شرکت
                    company = Company.objects.get(id=company_id, owner=request.user)
                    company.name = name
                    company.website = website
                    if faq_company:
                        def are_excels_equal(file1, file2):
                            try:
                                with file1.open("rb") as f:
                                    df1 = pd.read_excel(f)
                                df2 = pd.read_excel(file2)
                                df1 = df1.sort_index(axis=1).sort_values(by=df1.columns.tolist()).reset_index(drop=True)
                                df2 = df2.sort_index(axis=1).sort_values(by=df2.columns.tolist()).reset_index(drop=True)
                                return df1.equals(df2)
                            except Exception as e:
                                raise ValidationError(f"Excel file is not valid or readable: {str(e)}")
                        if company.faq:  # اگر فایل قبلی موجود است
                            try:
                                faq_changed = not are_excels_equal(company.faq, faq_company)
                            except Exception as e:
                                print(f"Excel comparison failed: {e}")
                                faq_changed = True
                        else:
                            faq_changed = True
                        if faq_changed:
                            if company.faq:
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
                if faq_changed:
                        # Read Excel

                    faq_excel = pd.read_excel(faq_company)
                    faq_data=merge_faq_default(faq_excel=faq_excel)
                    company.faq_json=faq_data
                    company.save()
                    save_faq_embeddings_for_company(company, faq_data)
                return redirect('home:create_company')  # هدایت به صفحه داشبورد

    else:
        form = CompanyForm()

    companies = Company.objects.filter(owner=request.user)
    return render(request, 'admin/create_company.html', {'form': form, 'companies': companies})
