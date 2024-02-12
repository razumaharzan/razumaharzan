$("#vendorRegisterForm").validate({
    rules: {
        username: "required",
        province: "required",
        district: "required",
        firstName: "required",
        lastName: "required",
        municipality: "required",
        email: "required",
        Password: "required",
        cPassword: "required",
        product: "required",
        street: "required",
        pan: "required",
        date: "required",
        phone: {
            required: true,
            digits: true,
        },
    },
    errorPlacement: function (error, element) {
        error.insertAfter(element.closest("div"));
    },
    messages: {
        firstName: {
            required: "पहिलो नाम राख्नुहोस।"
        },
        lastName: {
            required: "अन्तिम नाम राख्नुहोस।"
        },
        username: {
            required: "प्रयोगकर्ताको नाम राख्नुहोस।",
        },
        Password: {
            required: "पासवर्ड राख्नुहोस।"

        },
        cPassword: {
            required: " पुर्ण पासवर्ड राख्नुहोस।"
        },
        email: {
            required: "ईमेल राख्नुहोस।",
        },
        province: {
            required: "प्रान्त छान्नुहोस।",
        },
        district: {
            required: "जिल्ला छान्नुहोस।",
        },
        municipality: {
            required: "पालिका छान्नुहोस।",
        },
        street: {
            required: "टोल छान्नुहोस।"
        },
        phone: {
            required: "सम्पर्क नम्बर राख्नुहोस।",
            digits: "phone must be numbers only.",
        },
        product: {
            required: "उत्पादन वर्ग छान्नुहोस।",
        },
        pan: {
            required: "पान नम्बर राख्नुहोस।"
        },
        date: {
            required: "जन्ममिति राख्नुहोस।"
        }
    },
});
$("#signUpBtn").off("click").on("click", function () {
    if ($("#vendorRegisterForm").valid()) {
        var firstName = $("#firstName").val();
        var Password = $("#Password").val();
        var lastName = $("#lastName").val();
        var email = $("#email").val();
        var cPassword = $("#cPassword").val();
        var gender = $("#gender").val();
        var dateOfBirth = $("#date").val();
        var username = $("#username").val();
        var province = $("#province").val();
        var district = $("#district").val();
        var municipality = $("#municipality").val();
        var phone = $("#phone").val();
        var product = $("#product").val();
        var pan = $("#pan").val();
        var street = $("#street").val();
        var formId = "vendorRegisterForm";

        var today = new Date();
        var day = String(today.getDate()).padStart(2, '0');
        var month = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        var year = today.getFullYear();
        today = year + '-' + month + '-' + day
        console.log(today)
        if (Password !== cPassword) {
            toastr.error("पासवर्ड एउटै राख्नुहोस।")
            return false
        }
        else {
            data = {
                firstName: firstName,
                lastName: lastName,
                Password: Password,
                email: email,
                username: username,
                province: province,
                district: district,
                municipality: municipality,
                phone: phone,
                pan: pan,
                product: product,
                street: street,
                gender: gender,
                dateOfBirth: dateOfBirth
            };
            console.log(data)
            dataCreateUrl = "/vendor/signup";
            dataRedirectUrl = "/vendor/login";
            VendorRegister(data, formId, dataCreateUrl, dataRedirectUrl);
        }

    } else {
        return false;
    }
});

function provinceList() {
    $.ajax({
        method: "GET",
        url: "/province/list",
        success: function (response) {
            data = response.data
            for (let i = 0; i < data.length; i++) {
                var option =
                    '<option value="' + data[i]['id'] + '">' + data[i]['name'] + '</option>'

                $("#province").append(option)
            }
        },
        error: function (response) {
            data = response.responseJSON
        }
    })
}
$("#province").on('change', function () {
    var value = $(this).val()
    if (!value) {
        $("#province").empty().append('<option value="">SELECT</option>')
    }
    else {
        $("#district,#municipality").empty().append('<option value="">SELECT</option>')
        districtList(value)
    }
})
function districtList(provinceId) {
    $.ajax({
        method: "GET",
        data: { "data": provinceId },
        url: "/district/list",
        success: function (response) {
            data = response.data
            for (let i = 0; i < data.length; i++) {
                var option =
                    '<option value="' + data[i]['id'] + '">' + data[i]['name'] + '</option>'

                $("#district").append(option)
            }
        },
        error: function (response) {
            data = response.responseJSON
        }
    })

}
$("#district").on('change', function () {
    var provinceId = $("#province").val();
    var value = $(this).val();
    if (!value, !provinceId) {
        $("#province").empty().append('<option> SELECT</option>')
    }
    else {
        $("#municipality").empty().append('<option value=""> SELECT</option>')
        municipalityList(provinceId, value)
    }
})

function municipalityList(provinceId, districtId) {
    $.ajax({
        method: "GET",
        data: {
            "data": provinceId,
            "data1": districtId
        },
        url: "/municipality/list",
        success: function (response) {
            data = response.data
            for (let i = 0; i < data.length; i++) {
                var option =
                    '<option value="' + data[i]['id'] + '">' + data[i]['name'] + '</option>'

                $("#municipality").append(option)
            }
        },
        error: function (response) {
            data = response.responseJSON
        }
    })

}



function VendorRegister(data, formId, dataCreateUrl, redirectUrl) {
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
            toastr.success("Vendor successfully register.")
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
