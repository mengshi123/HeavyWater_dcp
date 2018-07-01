$(document).ready(function(){
    $('#changeInput').click(function(){
        // Change to input text
        if ($('#InputBox').attr('type') === 'file') {
            var box = $('#InputBox');
            box.attr("type", "text");
            box.attr("name", "text");
            box.attr("placeholder", "Please input text here. Words separated by spaces");
            box.removeAttr("accept");

            var form = $('#form');
            form.attr("method", "get");
            form.removeAttr("enctype");

            var button = $(this);
            button.text("Choose to upload a file");

            var submit = $("#submit");
            submit.removeAttr("disabled");
        }
        // Change to upload file
        else if ($('#InputBox').attr('type') === 'text') {
            var box = $("#InputBox");
            box.attr("type", "file");
            box.attr("name", "file");
            box.attr("accept", ".csv");
            box.removeAttr("placeholder");

            var form = $("#form");
            form.attr("method", "post");
            form.attr("enctype", "multipart/form-data");

            var button = $(this);
            button.text("Choose to input text");

            var submit = $("#submit");
            submit.attr("disabled", "true");
        }
    });

    // Enable submit button until a file selected
    $('#InputBox').change(function(){
        if ($(this).attr('type') === 'file'){
            if ($(this).val()) {
                $('#submit').removeAttr('disabled');
            } else {
                $('#submit').attr('disabled', 'flase');
            }
        }
    });
});
