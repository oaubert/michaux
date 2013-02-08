var michaux = {};
"use strict";

jQuery(document).ready(
    function($) {
        $("[name$=technique]").autocomplete({ source: "/base/complete/technique",
                                              minLength: 2});
        $("[name$=support]").autocomplete({ source: "/base/complete/support",
                                            minLength: 2});
        $("[name$=serie]").autocomplete({ source: "/base/complete/serie",
                                          minLength: 2});
    });
