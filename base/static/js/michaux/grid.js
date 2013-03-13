var michaux = {};
"use strict";

jQuery(document).ready(
    function($) {
        // FIXME: Make that a jquery plugin?
        function draw_barchart (element) {
            var fieldname = $(element).attr('data-field');
            var minValue = parseInt($(element).attr("data-min"));
            var maxValue = parseInt($(element).attr("data-max"));
            var title = $(element).find(".facetRange");
            function facet_title(min, max) {
                if (min === undefined)
                    title.text("N/C");
                else
                    title.text(min + " - " + max);
            };

            var data = $(element).find(".facetdata").map(
                function() { return { "value": parseInt($(this).attr('data-value')),
                                      "count": parseInt($(this).attr('data-count')) };
                           });
            var maxCount = d3.max(data, function(d) { return d.count; });
            var currentMin = d3.min(data, function(d) { return d.value; });
            var currentMax = d3.max(data, function(d) { return d.value; });
            facet_title(currentMin, currentMax);

            // add the canvas to the DOM
            var width = $(element).width() - 16;
            // FIXME: determine dynamically
            var height = 120 - 30; // div height - title height - slider height

            var barchart = d3.select(element)
                .append("svg:svg")
                .attr("width", width)
                .attr("height", height);

            var g = barchart.append("g")
                .attr("transform", "scale(1, -1) translate(0, -" + height + ")");

            var barWidth = Math.max(width / (maxValue - minValue), 2);

            var x_scale = d3.scale.linear().domain([minValue, maxValue]).range([0, width - barWidth ]).interpolate(d3.interpolateRound).clamp(true);
            var y_scale = d3.scale.linear().domain([0, maxCount]).range([0, height - 5]);

            function select_range(start, end) {
                var val = fieldname + "__range:" + start + "-" + end;
                var i = $(element).siblings("input");
                if (i.length) {
                    // There is already an input field. Simply replace its value.
                    i.attr("value", val);
                } else {
                    // No input field. Create it.
                    i = $("<input />").attr({
                                                type: "hidden",
                                                name: "f",
                                                value: val
                                            });
                    $(element).after(i);
                }
                $(i).parents("form").submit();
            };

            var brush = d3.svg.brush()
                .x(x_scale)
                .on("brush", function () {
                        var b = brush.empty() ? x_scale.domain() : brush.extent();
                        facet_title(Math.floor(b[0]), Math.floor(b[1]));
                    })
                .on("brushend", function () {
                        if (! brush.empty()) {
                            var b = brush.extent();
                            select_range(Math.floor(b[0]), Math.floor(b[1]));
                        } else {
                            select_range();
                            }
                    });

            g.selectAll("line")
                .data(y_scale.ticks(5))
                .enter().append("line")
                .attr("x1", 0)
                .attr("x2", width)
                .attr("y1", y_scale)
                .attr("y2", y_scale)
                .style("stroke", "#ccc");

            var g_brush = g.append("g")
                .attr("class", "x brush")
                .call(brush)
                .selectAll("rect")
                .attr("y", 0)
                .attr("height", height);

            g.selectAll(".bar")
                .data(data)
                .enter()
                .append("svg:rect")
                .attr("class", "bar")
                .attr("x", function(d, index) { return x_scale(d.value); })
                .attr("y", function(d) { return 0; })
                .attr("svg:title", function(d) { return d.value + ' (' + d.count + ')'; })
                .attr("height", function(d) { return y_scale(d.count); })
                .attr("width", barWidth)
                .on("mousedown", function (d) {
                        select_range(d.value, d.value);
                    });


            barchart.x = x_scale;
            barchart.y = y_scale;

            $('svg rect.bar').tipsy({
                                        gravity: 'sw',
                                        html: false
                                    });
            d3.rebind(barchart, brush, "on");

            // Add slider
            var slider = $("<div />").addClass("facetslider").
                attr("id", fieldname + '_range_slider');
            $(element).after(slider);
            slider.slider({
                              range: true,
                              min: minValue,
                              max: maxValue,
                              values: [ currentMin, currentMax ],
                              slide: function(event, ui) {
                                  var range = ui.values;
                                  facet_title(range[0], range[1]);
                              },
                              stop: function(event, ui) {
                                  var range = ui.values;
                                  select_range(range[0], range[1]);
                              }
                          });

            return barchart;
        };
        $(".barchartwidget").each( function () {
                                       draw_barchart(this);
                                   });

        $( "#zoomslider" ).slider({
                                      range: false,
                                      min: 1,
                                      max: 200,
                                      value: 100 * ($("#grid").css('zoom') || 1),
                                      slide: function(event, ui) {
                                          var z = ui.value / 100.0;
                                          $("#grid").css( { zoom: z, "-moz-transform": "scale(" + z + ")" } );
                                      }
                                      });

        $("#selection_open").click( function () {
                                        var selection = michaux.getSelection();
                                        $("#selection").attr("value", selection.join(","))
                                            .parents("form").submit();
                                    } );
        $("#selection_compare").click( function () {
                                           var selection = michaux.getSelection();
                                           if (selection.length < 2)
                                               return;
                                           document.location.pathname = document.location.pathname + '../compare/' + selection[0] + '/' + selection[1];
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
                var img = $(michaux.iviewer_thumbnail).find("img");
                var width = 1.0 * $(img).width();
                var height = 1.0 * $(img).height();
                var f = $(michaux.iviewer).iviewer('info', 'frame');
                $(michaux.iviewer_frame).css({
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
                michaux.iviewer = $("#lightbox").iviewer({ zoom: 'fit', zoom_max: 500, zoom_min: 10 })
                    .bind("ivieweronzoom", update_frame)
                    .bind("iviewerondrag", update_frame)
                    .bind("ivieweronafterzoom", update_frame)
                    .bind("ivieweronstopdrag", update_frame)
                    .bind("ivieweronstartload", function () { $("#lightbox img").hide(); $(".loading").show(); })
                    .bind("ivieweronfinishload", function () { $("#lightbox img").show(); $(".loading").hide(); update_frame(); });
            };

            $('#lightbox').css('width', $(window).width() - 225)
                .attr('data-url', url)
                .show('fast');
            michaux.iviewer.iviewer('loadImage', url);
            michaux.iviewer_thumbnail = thumbnail;
            michaux.iviewer_frame = frame;
      }

        // Display infopanel about a work
        // It can be given either a .vignette anchor or a div.work element
        function display_infopanel(self) {
            var cote = undefined;
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
                return '<div id="infopanel_navbar"><a id="infopanel_prev" class="' + (prev === undefined ? 'disabled" title="Pas d\'oeuvre précédente" href="" ' : 'enabled" data-cote="' + prev + '" title="Oeuvre précédente" href="javascript:michaux.display_infopanel(' + prev + ')"') + '>&nbsp;</a> | <a id="infopanel_next" class="' + (next === undefined ? 'disabled" title="Pas d\'oeuvre suivante" href="" ' : 'enabled" data-cote="' + next + '" title="Oeuvre suivante" href="javascript:michaux.display_infopanel(' + next + ')"') + '>&nbsp;</a> <a id="infopanel_close" href="javascript:michaux.hide_infopanel();">&nbsp;</a></div>';
            }

            // FIXME: hardcoded URL. Should fix this.
            $.get(cote + '/info', function (data) {
                      if ($('#info_panel:visible').attr('data-current') == cote)
                      {
                          // Already displaying the infopanel
                          // Display the first image
                          $("[rel=lightbox]:first").each( function () { lightbox($(this).attr('href'), this ); } );
                      } else {
                          $('#info_panel').html(navbar() + data)
                              .attr('data-current', cote);

                          $('#info_panel').show('fast', function () {
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
                              if ($("[rel=lightbox]:first").each( function () { lightbox($(this).attr('href'), this ); } ).length == 0)
                                  $('#lightbox').hide();
                          }
                      }
                  });
        };

        $('.vignette').click(function(e) {
                                 //prevent default action (hyperlink)
                                 e.preventDefault();
                                 michaux.display_infopanel(this);
                             });

        // Select/unselect items
        $("a.selection").click(function () {
                                   $(this).parents("div.work").toggleClass("selected");
                                   var selection = michaux.getSelection();
                                   $('#selection_menu').text(selection.length + (selection.length > 1 ? " éléments sélectionnés" : " élément sélectionné"));
                                   $('#selection').attr('value', selection.join(","));
                               });

        // Hide/show facets
        $(".facetbox:not(.active) .facetcontent").hide("fast");
        $(".facettitle").click(function() {
                                   var f = $(this).siblings(".facetcontent");
                                   $(".facetcontent").not(f).hide("fast");
                                   f.show("fast");
                               });

        michaux.display_infopanel = display_infopanel;

        michaux.hide_infopanel = function () {
            $("div.work.current").removeClass("current");
            $('#content').css("margin-right", "5px");
            $('#info_panel').hide('fast');
            $('#lightbox').hide();
            $('#grid').focus();
        };

        michaux.resetFilter = function () {
            document.location.search = "";
        };

        michaux.getSelection = function () {
            return $("div.work.selected").map( function () { return $(this).attr('data-cote'); } ).toArray();
        };

        michaux.goto_page = function (p) {
            $("#current_page").attr('value', p)[0].form.submit();
        };

        michaux.clear_facet = function (e) {
            e.preventDefault();
            var i = $(this).parents(".facetbox").find("input").remove();
            $(this).parents("form").submit();
        };

        michaux.toggle_facet = function (e) {
            e.preventDefault();
            var i = $(this).siblings("input");
            if (i.length) {
                // There is an input sibling -> the facet was active. Remove the input.
                i.remove();
            } else {
                // There is no input sibling. We want to activate the
                // facet: its value is the text of the activating
                // anchor.
                // The active-facet anchor (which can also call
                // toggle_facet) cannot be it in this case, since it
                // is present only if the facet is defined.
                var field = $(this).parents(".facetbox").attr("data-field");
                $(this).after($("<input />").attr({
                                                      type: "hidden",
                                                      name: "f",
                                                      value: field + "_exact:" + $(this).text()
                                                  }));
            }
            // Resubmit form
            $(this).parents("form").submit();
        };
        $(".facetitemlabel").on("click", michaux.toggle_facet);
        $(".active-facet").on("click", michaux.toggle_facet);
        $(".clear-facet").on("click", michaux.clear_facet);

        // Keyboard handling
        $(document).keypress(function (e) {
                                 if (e.which == 107 && $("#info_panel:visible").length) {
                                     // k for previous
                                     michaux.display_infopanel($("#infopanel_prev").attr('data-cote'));
                                 } else if (e.which == 106 && $("#info_panel:visible").length) {
                                     // j for next
                                     michaux.display_infopanel($("#infopanel_next").attr('data-cote'));
                                 } else if (event.which == 99 && $("#info_panel:visible").length) {
                                     // c for "Close"
                                     michaux.hide_infopanel();
                                 } else if (event.which == 13 && $("#info_panel:visible").length) {
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
