django.jQuery(document).ready(
    function ($) {
        "use strict";
        document.$ = $;
        var completable_fields = ["technique", "support", "serie", "authentication_source"];

        // Move navbar to header
        $("ul.navbar").insertBefore("#grp-admin-title");

        // Transform help text into tooltips
        $(".grp-help").each(function () {
            $(this).siblings("input,select,textarea").attr("title", $(this).text());
        })
            .hide();

        completable_fields.forEach(function (s) {
            $("[name$=" + s + "]").autocomplete({ source: "/base/complete/" + s,
                                                  minLength: 2});
        });
    });
