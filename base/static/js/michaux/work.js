var michaux = {};
"use strict";

jQuery(document).ready(
    function($) {
        // Make tags clickable
        $(".as-selection-item").contents(':not(a)').click( function () { document.location = "/base/work?f=tags_exact:" + encodeURIComponent($(this).text()); });

        function draw_frame(vignette) {
            var rubber = $(vignette).find(".rubber_band");
            var thumbnail = $(vignette).find("img");
            var width = 1.0 * $(thumbnail).width();
            var height = 1.0 * $(thumbnail).height();
            // Generate a callback function to display a zoomed rectangle over the thumbnail
            return function(x, y, w, h) {
                rubber.css({
                               left: Math.floor(x * width) + 'px',
                               top: Math.floor(y * height) + 'px',
                               width: Math.floor(w * width) + 'px',
                               height: Math.floor(h * height) + 'px',
                               display: 'block'
                           });
                return false;
            };
        }

        // Add wheelzoom to image
        $("[rel=lightbox]").append($("<div/>")
                                   .addClass('rubber_band')
                                   .css({
                                            position: "absolute",
                                            display: "none",
                                            width: "0px",
                                            height: "0px",
                                            border: "2px solid red"
                                        }));
        $(".display").wheelzoom({callback: draw_frame($("[rel=lightbox]"))});

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
