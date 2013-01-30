var michaux = {};

jQuery(document).ready(
    function($) {
        // Make tags clickable
        $(".as-selection-item").contents(':not(a)').click( function () { document.location = "/base/work?f=tags_exact:" + encodeURIComponent($(this).text()); });

        // Add wheelzoom to image
        $(".display").wheelzoom();

        michaux.tag_selection = function (tagname) {
            var cote = $(".workinfo").attr('data-cote');
            console.log("Tagging ", cote, " with ", tagname);
            // FIXME: add csrf token
            $.get("/base/selection/tag/",
                  { 'selection': cote,
                    'name': tagname });
        };

        michaux.untag_selection = function (tagname) {
            var cote = $(".workinfo").attr('data-cote');
            console.log("UnTagging ", cote, " with ", tagname);
            // FIXME: add csrf token
            $.get("/base/selection/untag/",
                  { 'selection': cote,
                    'name': tagname });
        };
    });
