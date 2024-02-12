from django.contrib import messages
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Securetech
import json
from django.http import JsonResponse
from .import validation
import requests

# Create your views here.
@login_required()
def sec_index(request):
        return render(request,'stnepal/index.html')
   
@login_required()
def home(request):
    if request.method=="POST":
        try:
            response = requests.post("http://127.0.0.1:8001/test",data=request.body,headers=request.headers)
            print(response.json())
            print(response.status_code)
            error_list, user_name, email_id, pass_word, phone_no = validation.form_edit_creat(request, None)
            if error_list:
                return JsonResponse({"error":error_list}, status=400)
            Securetech.objects.create(name = user_name, email = email_id, password = pass_word, phone=phone_no)
            return JsonResponse(response.json(),status=response.status_code)
        except Exception as exe:
            print(exe)
    return render(request,'stnepal/home.html')

@login_required()
def products(request):
    data = Securetech.objects.filter(is_delete=False)
    response = requests.get("http://127.0.0.1:8001/test") # yo chai api ko data 
    print(response.json())
    api_data = response.json()
    api_data =api_data['data']
    print(response.status_code)
    return render(request,'stnepal/products.html',{'datas':api_data})



def sec_support(request):
    if request.user.is_authenticated:  
        return render(request,'stnepal/support.html')
    else:
        return redirect('/login')

def sec_solutions(request):
    if request.user.is_authenticated:  
        return render(request,'stnepal/solutions.html')
    else:
        return redirect('/login')

def edit_item(request,pk):
    if request.user.is_authenticated:  # login page ma jaan6
        securetech = Securetech.objects.get(id=pk, is_delete=False)
        try:
            if request.method == "POST":
                error_list, user_name,email_id,pass_word,phone_no = validation.form_edit_creat(request,pk) 
                if error_list:
                    return JsonResponse({"error":error_list}, status=400)

                Securetech.objects.filter(id=pk, is_delete=False).update(name = user_name, email = email_id, password = pass_word, phone=phone_no)
                return JsonResponse({"response":"ok"}, status=200)
        except Exception as exe:
                print(exe)

        return render(request,'stnepal/edit_item.html',{'securetech':securetech})
    else:
        return redirect('/login')

   

def delete_item(request, pk):
    if request.user.is_authenticated:  
        stu = Securetech.objects.get(id=pk)
        stu.is_delete=True
        stu.save()
        messages.success(request, 'Data delete successfully')
        return redirect('/products')
    else:
        return redirect('/login')