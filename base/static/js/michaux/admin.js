var michaux = {};
"use strict";

jQuery(document).ready(
    function($) {
        document.$ = $;
        $("[name$=technique]").autocomplete({ source: "/base/complete/technique",
                                              minLength: 2});
        $("[name$=support]").autocomplete({ source: "/base/complete/support",
                                            minLength: 2});
        $("[name$=serie]").autocomplete({ source: "/base/complete/serie",
                                          minLength: 2});
        $("#changelist-filter h2").click( function() { $("#changelist-filter").children("h3,ul").each(
                                                           function () {
                                                               $(this).toggleClass("closed");
                                                           });
                                                     });
});