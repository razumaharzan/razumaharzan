$("#userRegister").validate({
    rules: {
        username: "required",
        email: "required",
        password: "required",
        cPassword: "required",
        date: "required",
    },
    errorPlacement: function (error, element) {
        error.insertAfter(element.closest("div"));
    },
    messages: {
        username: {
            required: "Enter your user name.",
        },
        password: {
            required: "Enter the password"

        },
        cPassword: {
            required: "Enter confirm password."
        },
        email: {
            required: "Enter the email. ",
        },
        date: {
            required: "Enter the date of birth."
        }
    },
});
$("#signUpBtn").off("click").on("click", function () {
    if ($("#userRegister").valid()) {
        var Password = $("#password").val();
        var email = $("#email").val();
        var cPassword = $("#cPassword").val();
        var gender = $("#gender").val();
        var dateOfBirth = $("#dateOfBirth").val();
        var username = $("#username").val();
        var formId = "userRegister";
        var today = new Date();
        var day = String(today.getDate()).padStart(2, '0');
        var month = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        var year = today.getFullYear();
        today = year + '-' + month + '-' + day
        if (Password !== cPassword) {
            toastr.error("Password must be match.")
            return false
        }
        else {
            data = {
                password: Password,
                email: email,
                username: username,
                gender: gender,
                dateOfBirth: dateOfBirth
            };
            console.log(data)
            dataCreateUrl = "/user/register";
            dataRedirectUrl = "/login";
            userRegister(data, formId, dataCreateUrl, dataRedirectUrl);
        }

    } else {
        return false;
    }
});



function userRegister(data, formId, dataCreateUrl, redirectUrl) {
    var token = $("#" + formId).find("input[name=csrfmiddlewaretoken]").val();
    $.ajax({
        method: "POST",
        url: dataCreateUrl,
        headers: { "X-CSRFToken": token },
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: "json",

        success: function (response) {
            data = response;
            toastr.success("User successfully register.")
            window.setTimeout(function () {
                window.location = redirectUrl;
            }, 2000);

        },
        error: function (response) {
            data = response.responseJSON;
            if (data === undefined) {
                toastr.error("Internal server error.")
            }
            else {
                if (data.hasOwnProperty('error')) {
                    var li = ''
                    for (let i = 0; i < data['error'].length; i++) {
                        li += '<li>' + data['error'][i] + '</li>'
                    }
                    toastr.error(li)
                }
                else {
                    li = '<li>' + data['resultDescription'] + '</li>'
                    toastr.error(li)
                }
            }
        },
    });
}
