$("#productFormId").validate({
    rules: {
        productName: "required",
        description: "required",
        productPrize: {
            required: true,
            digits: true,
        },
        manufacturedDate: "required",
    },
    errorPlacement: function (error, element) {
        error.insertAfter(element.closest("div"));
    },
    messages: {
        productName: {
            required: "Enter product name.",
        },
        description: {
            required: "Enter Description",
        },
        productPrize: {
            required: "Enter product prize",
            digits: "Prize must be digits only.",
        },
        manufacturedDate: {
            required: "Enter the manufacture date.",
        },
    },
});
$("#saveBtn").off('click').on("click", function () {
    if ($("#productFormId").valid()) {
        var productName = $("#productName").val();
        var description = $("#description").val();
        var productPrize = $("#productPrize").val();
        var manufacturedDate = $("#manufacturedDate").val();
        var product = $("#productItem").val();
        var subProduct = $("#subProduct").val();
        var photo = $("#image").attr("src")
        if (photo === "/static/image/images.jpg") {
            toastr.error("please select valid image")
        }
        else {
            var formId = "productFormId";
            data = {
                productName: productName,
                product: product,
                subProduct: subProduct ? subProduct : '',
                description: description,
                productPrize: productPrize,
                manufacturedDate: manufacturedDate,
                photo: photo
            };
            console.log(data)
            dataCreateUrl = "/product/create";
            dataRedirectUrl = "/product/create";
            saveData(data, formId, dataCreateUrl, dataRedirectUrl);

        }

    } else {
        return false;
    }
});


$("#productItem").off('click').on('change', function () {
    var value = $(this).val()
    if (!value) {
        $("#productItem").empty().append('<option value="">SELECT</option>')
    }
    else {
        $("#subProduct").empty().append('<option value="">SELECT</option>')
        subProductList(value)
    }
})
function subProductList(categoryId) {
    $.ajax({
        method: "GET",
        data: { "data": categoryId },
        url: "/sub/product/list",
        success: function (response) {
            $("#subProduct").empty()
            data = response.data
            for (let i = 0; i < data.length; i++) {
                var option =
                    '<option value="' + data[i]['id'] + '">' + data[i]['name'] + '</option>'

                $("#subProduct").append(option)
            }
        },
        error: function (response) {
            data = response.responseJSON
        }
    })

}


function loadVendorProductList() {
    $.ajax({
        method: "GET",
        data: { "data": categoryId },
        url: "/vendor/product/list",
        success: function (response) {
            $("#subProduct").empty()
            data = response.data
            for (let i = 0; i < data.length; i++) {
                var option =
                    '<option value="' + data[i]['id'] + '">' + data[i]['name'] + '</option>'

                $("#subProduct").append(option)
            }
        },
        error: function (response) {
            data = response.responseJSON
        }
    })

}