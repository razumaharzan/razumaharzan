from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
# Create your views here.
def user_login(request):
    if request.method =="POST":
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')
        print(user_name,pass_word)
        user_info = authenticate(username=user_name, password=pass_word)
        if user_info:
            login(request, user_info)
            request.session['test'] = 'testing user session'
            return redirect('/home/')
        else:
            logout(request)
            return redirect('/login')
    return render(request,'user/user.html')
    

def register_login(request):
    if request.method == "POST":
        user_name = request.POST.get('username')
        email_id = request.POST.get('email')
        pass_word = request.POST.get('password')
        User.objects.create_user(username=user_name,email=email_id,password=pass_word)
        return redirect('/register')
    return render(request,'user/register.html')

def logout_data(request):
    logout(request)
    return redirect('/login')