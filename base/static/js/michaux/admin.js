django.jQuery(document).ready(
    function($) {
        "use strict";
        document.$ = $;
        var completable_fields = ["technique", "support", "serie", "authentication_source"];

        // Move navbar to header
        $("ul.navbar").insertBefore("#grp-admin-title");

        completable_fields.forEach(function(s) {
                                       $("[name$=" + s + "]").autocomplete({ source: "/base/complete/" + s,
                                                                             minLength: 2});
                                   });

        $("#changelist-filter h2").click( function() { $("#changelist-filter").children("h3,ul").each(
                                                           function () {
                                                               $(this).toggleClass("closed");
                                                           });
                                                     });
});