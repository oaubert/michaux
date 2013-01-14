var michaux = {};

jQuery(document).ready(
    function($) {
        // Make tags clickable
        $(".as-selection-item").contents(':not(a)').click( function () { document.location = "/base/work?f=tags_exact:" + encodeURIComponent($(this).text()); });
    });
