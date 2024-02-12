import json
from .models import Securetech

def form_edit_creat(request,pk):
    data = json.loads(request.body)
    error_list = []
    user_name = data.get("username")
    if not user_name:
        error_list.append('Username can not be blank.')

    email_id = data.get("email")
    if not email_id:
        error_list.append('Email can not be blank.')

    pass_word = data.get("password")
    if not pass_word:
        error_list.append('Password can not be blank.')

    phone_no = data.get("phone")
    if not phone_no:
        error_list.append('Phone can not be blank.')
    else:
        if pk:
            if Securetech.objects.filter(phone=phone_no).exclude(id=pk).exists():
                error_list.append('abcd')
        else:
            if Securetech.objects.filter(phone=phone_no).exists():
                error_list.append('abcd')

    return  error_list, user_name,email_id,pass_word,phone_no