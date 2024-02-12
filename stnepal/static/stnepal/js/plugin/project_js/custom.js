function saveData(data, formId, dataCreateUrl, redirectUrl) {
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
            toastr.success("Data successfully saved.")
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


function loadList(id, requestedUrl) {
    $.ajax({
        method: "GET",
        url: requestedUrl,
        success: function (response) {
            data = response.data
            for (let i = 0; i < data.length; i++) {
                var option =
                    '<option value="' + data[i]['id'] + '">' + data[i]['name'] + '</option>'
                $("#" + id).append(option)
            }

        },
        error: function (response) {
            data = response.responseJSON;
            toastr.error("Internal server error.")

        },
    });
}



function otpData(data, formId, dataCreateUrl, redirectUrl) {
    var token = $("#" + formId).find("input[name=csrfmiddlewaretoken]").val();
    $.ajax({
        method: "POST",
        url: dataCreateUrl,
        headers: { "X-CSRFToken": token },
        data: JSON.stringify(data),
        contentType: "application/json",
        dataType: "json",
        success: function (response) {
            $("#emailSure").modal('hide')
            $("#" + redirectUrl).modal('show')
        },
        error: function (jhxr, status,) {
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
