// Generated by CoffeeScript 1.6.3
(function () {
    $(function () {
        return $(".language-link").on("click", function (event) {
            event.preventDefault();
            $("input[name='language']").val($(this).data("language"));
            return $("#set-language").submit();
        });
    });

}).call(this);