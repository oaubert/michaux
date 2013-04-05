jQuery(document).ready(
    function($) {
        "use strict";

        if (document.michaux === undefined)
            document.michaux = {};

        /*
         * Return the appropriate URL.
         *
         * type is the type of view: 'home' (default), 'work', 'exhibition', 'compare', 'selection', etc
         * ident is the identifier of the element (primary key) (can be a list for selection or compare)
         * action is the kind of action: 'view' (default), 'info', 'edit', 'compare'
         */
        document.michaux.url = function (type, ident, action) {
            // FIXME: find the appropriate way to determine base url
            var url = "/base/";
            if (action === undefined)
                action = 'view';

            if (type === 'home') {
                url += '/work/';
            } else if (type === 'work' || type === 'exhibition') {
                url += type + '/' + ident;
                if (action === 'info')
                    url += '/info';
                else if (action === 'edit')
                    url = '/admin' + url;
            } else if (type === 'selection') {
                // We assume that ident is an array here
                url += 'work?selection=' + ident.join(",");
                if (action === 'edit')
                    url = '/admin' + url;
            } else if (type === 'compare')
                url += '/compare/' + ident[0] + '/' + ident[1];
            return url;
        };

        document.michaux.getSelection = function () {
            return $("div.work.selected").map( function () { return $(this).attr('data-cote'); } ).toArray();
        };

        /*
         * Selection menu actions
         */
        function update_selection_menu () {
            var selection = document.michaux.getSelection();
            $('#selection_menu').text(selection.length + (selection.length > 1 ? " éléments sélectionnés" : " élément sélectionné"));
            $('#selection_popup').toggleClass("emptySelection", ! selection.length);
            $('#selection').attr('value', selection.join(","));
        }

        $("#selection_all").click( function () {
                                       $("div.work").addClass("selected");
                                       update_selection_menu();
                                   } );
        $("#selection_none").click( function () {
                                        $("div.work.selected").removeClass("selected");
                                        update_selection_menu();
                                    } );
        $("#selection_open").click( function () {
                                        var selection = document.michaux.getSelection();
                                        $("#selection").attr("value", selection.join(","))
                                            .parents("form").submit();
                                    } );
        $("#selection_compare").click( function () {
                                           var selection = document.michaux.getSelection();
                                           if (selection.length < 2)
                                               return;
                                           document.location = document.michaux.url('compare', selection);
                                       } );
        $("#selection_edit").click( function () {
                                        var selection = document.michaux.getSelection();
                                        document.location = document.michaux.url('selection', selection, 'admin');
                                    } );

        // Display a custom, basic lightbox component
        function lightbox(url, thumbnail) {
            // Add a frame rectangle div
            var frame = $("<div/>")
                           .addClass('visible_frame')
                           .css({
                                    position: "absolute",
                                    display: "none",
                                    width: "0px",
                                    height: "0px",
                                    border: "2px solid red"
                                });
            $(thumbnail).append(frame);

            function clamp(val, min, max) {
                return val < min ? min : ( val > max ? max : val );
            }
            function update_frame() {
                var img = $(document.michaux.iviewer_thumbnail).find("img");
                var width = 1.0 * $(img).width();
                var height = 1.0 * $(img).height();
                var f = $(document.michaux.iviewer).iviewer('info', 'frame');
                $(document.michaux.iviewer_frame).css({
                               left: Math.floor(clamp(f.x, 0, 1) * width) + 'px',
                               top: Math.floor(clamp(f.y, 0, 1) * height) + 'px',
                               width: Math.floor(clamp(f.w, 0, 1) * width) + 'px',
                               height: Math.floor(clamp(f.h, 0, 1) * height) + 'px',
                               display: 'block'
                           });
            }

            /*
             If the lightbox window HTML already exists in document,
             change the img src to to match the href of whatever link was clicked
             If the lightbox window HTML doesn't exist, create it and insert it.
             (This will only happen the first time).
             */
            // If lightbox is visible and already displaying url -> hide it
            if ($('#lightbox:visible').attr('data-url') == url) {
                $('.visible_frame').hide();
                $('#lightbox').hide();
                $('#grid').focus();
                return;
            }

            if (! $('#lightbox').length) {
                //#lightbox does not exist - create and insert it
                //create HTML markup for lightbox window
                //insert lightbox HTML into page
                $('body').append($('<div style="overflow: hidden" id="wrapper">').append($('<div id="lightbox">').append($('<img class="loading">'))));
                document.michaux.iviewer = $("#lightbox").iviewer({ zoom: 'fit', zoom_max: 500, zoom_min: 10 })
                    .bind("ivieweronzoom", update_frame)
                    .bind("iviewerondrag", update_frame)
                    .bind("ivieweronafterzoom", update_frame)
                    .bind("ivieweronstopdrag", update_frame)
                    .bind("ivieweronstartload", function () { $("#lightbox img").hide(); $(".loading").show(); })
                    .bind("ivieweronfinishload", function () { $("#lightbox img").show(); $(".loading").hide(); update_frame(); });
            }

            $('#lightbox').css('width', $(window).width() - 225)
                .attr('data-url', url)
                .show('fast');
            document.michaux.iviewer.iviewer('loadImage', url);
            document.michaux.iviewer_thumbnail = thumbnail;
            document.michaux.iviewer_frame = frame;
      }

        // Display infopanel about a work
        // It can be given either a .vignette anchor or a div.work element
        function display_infopanel(self) {
            var cote;
            var work;
            var vignette;
            if (typeof self === "string" || typeof self === "number") {
                cote = "" + self;
                work = $("[data-cote=" + self + "]");
                vignette = $(work).find(".vignette");
            } else if ($(self).hasClass("work")) {
                vignette = $(self).find(".vignette");
                work = self;
            } else if ($(self).hasClass("vignette")) {
                vignette = self;
                work = $(self).parents("div.work");
            }
            if (cote === undefined)
                cote = $(work).attr('data-cote');

            //Get clicked link href
            var image_href = $(vignette).attr("href");

            function navbar() {
                var prev = $(work).prev().attr('data-cote');
                var next = $(work).next().attr('data-cote');
                return '<div id="infopanel_navbar"><a id="infopanel_prev" class="' + (prev === undefined ? 'disabled" title="Pas d\'oeuvre précédente" href="" ' : 'enabled" data-cote="' + prev + '" title="Oeuvre précédente" href="javascript:document.michaux.display_infopanel(' + prev + ')"') + '>&nbsp;</a> | <a id="infopanel_next" class="' + (next === undefined ? 'disabled" title="Pas d\'oeuvre suivante" href="" ' : 'enabled" data-cote="' + next + '" title="Oeuvre suivante" href="javascript:document.michaux.display_infopanel(' + next + ')"') + '>&nbsp;</a> <a id="infopanel_close" href="javascript:document.michaux.hide_infopanel();">&nbsp;</a></div>';
            }

            $.get(document.michaux.url('work', cote, 'info'), function (data) {
                      if ($('#infopanel:visible').attr('data-current') == cote)
                      {
                          // Already displaying the infopanel
                          // Display the first image
                          $("[rel=lightbox]:first").each( function () { lightbox($(this).attr('href'), this ); } );
                      } else {
                          $('#infopanel').html(navbar() + data)
                              .attr('data-current', cote);

                          $('#infopanel').show('fast', function () {
                                                    $('#content').css("margin-right", "200px");
                                                    $("div.work.current").removeClass('current');
                                                    $('#hm' + cote).addClass('current')[0].scrollIntoView();
                                                });

                          $("[rel=lightbox]").on("click", function (e) {
                                                     e.preventDefault();
                                                     lightbox($(this).attr('href'), this);
                                                 });
                          if ($("#lightbox:visible").length > 0) {
                              // Display first image, if available, in existing lightbox. Else, close inbox.
                              if ($("[rel=lightbox]:first").each( function () { lightbox($(this).attr('href'), this ); } ).length === 0)
                                  $('#lightbox').hide();
                          }
                      }
                  });
        }

        $('.vignette').click(function(e) {
                                 //prevent default action (hyperlink)
                                 e.preventDefault();
                                 document.michaux.display_infopanel(this);
                             });

        // Select/unselect items
        $("a.selection").click(function () {
                                   $(this).parents("div.work").toggleClass("selected");
                                   update_selection_menu();
                               });

        document.michaux.display_infopanel = display_infopanel;

        document.michaux.hide_infopanel = function () {
            $("div.work.current").removeClass("current");
            $('#content').css("margin-right", "5px");
            $('#infopanel').hide('fast');
            $('#lightbox').hide();
            $('#grid').focus();
        };

        // Keyboard handling
        $(document).keypress(function (e) {
                                 if (e.which == 106 && $("#infopanel:visible").length) {
                                     // j for previous
                                     document.michaux.display_infopanel($("#infopanel_prev").attr('data-cote'));
                                 } else if (e.which == 107 && $("#infopanel:visible").length) {
                                     // k for next
                                     document.michaux.display_infopanel($("#infopanel_next").attr('data-cote'));
                                 } else if (event.which == 99 && $("#infopanel:visible").length) {
                                     // c for "Close"
                                     document.michaux.hide_infopanel();
                                 } else if (event.which == 13 && $("#infopanel:visible").length) {
                                     // Show/hide lightbox
                                     if ($("#lightbox:visible").length > 0) {
                                         $('#lightbox').hide();
                                         $('#grid').focus();
                                     } else {
                                         // Display the first image
                                         $("[rel=lightbox]:first").each( function () { lightbox($(this).attr('href'), this ); } );
                                     }
                                 }
                             });
});
