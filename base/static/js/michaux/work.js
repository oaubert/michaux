var michaux = {};

jQuery(document).ready(
    function($) {
        "use strict";
        // Make tags clickable
        $(".as-selection-item").contents(':not(a)').click( function () { document.location = "/base/work?f=tags_exact:" + encodeURIComponent($(this).text()); });

        // Load image as zoomable image
        $("#image").each(function () {
                             var url = $(this).attr('data-url');

                             // Display viewer
                             michaux.iviewer = $(this).iviewer({ src: url,
                                                                 zoom: 'fit', zoom_max: 500, zoom_min: 10 })
                                 .bind("ivieweronstartload", function () { $(".loading").show(); })
                                 .bind("ivieweronfinishload", function () { $(".loading").hide(); });

                             // Find vignette matching main image
                             $(".image_reference:first")
                                 .each(function () {
                                           michaux.iviewer_thumbnail = this;
                                           var frame = $("<div/>")
                                               .addClass('visible_frame')
                                               .css({
                                                        position: "absolute",
                                                        display: "none",
                                                        width: "0px",
                                                        height: "0px",
                                                        border: "2px solid red"
                                                    });
                                           $(this).append(frame);
                                           function clamp(val, min, max) {
                                               return val < min ? min : ( val > max ? max : val );
                                           }
                                           function update_frame() {
                                               var img = $(michaux.iviewer_thumbnail).find("img");
                                               var width = 1.0 * $(img).width();
                                               var height = 1.0 * $(img).height();
                                               var f = $(michaux.iviewer).iviewer('info', 'frame');
                                               frame.css({
                                                             left: Math.floor(clamp(f.x, 0, 1) * width) + 'px',
                                                             top: Math.floor(clamp(f.y, 0, 1) * height) + 'px',
                                                             width: Math.floor(clamp(f.w, 0, 1) * width) + 'px',
                                                             height: Math.floor(clamp(f.h, 0, 1) * height) + 'px',
                                                             display: 'block'
                                                         });
                                           }
                                           $(michaux.iviewer).bind("ivieweronzoom", update_frame)
                                               .bind("iviewerondrag", update_frame)
                                               .bind("ivieweronafterzoom", update_frame)
                                               .bind("ivieweronstopdrag", update_frame)
                                               .bind("ivieweronfinishload", update_frame);
                                       });
                         });
        $(".image_reference").click(function (e) {
                                        e.preventDefault();
                                        $(michaux.iviewer).iviewer('loadImage', $(this).attr('href'));
                                    });

        michaux.tag_selection = function (tagname) {
            var cote = $("#workinfo").attr('data-cote');
            console.log("Tagging ", cote, " with ", tagname);
            // FIXME: add csrf token
            $.get("/base/selection/tag/",
                  { 'selection': cote,
                    'name': tagname });
        };

        michaux.untag_selection = function (tagname) {
            var cote = $("#workinfo").attr('data-cote');
            console.log("UnTagging ", cote, " with ", tagname);
            // FIXME: add csrf token
            $.get("/base/selection/untag/",
                  { 'selection': cote,
                    'name': tagname });
        };
    });
