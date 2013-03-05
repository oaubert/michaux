var michaux = {};
"use strict";

jQuery(document).ready(
    function($) {
            function draw_barchart (selector, fieldname, data, minValue, maxValue, titleselector) {
                var maxCount = d3.max(data, function(d) { return d.count; });
                var currentMin = d3.min(data, function(d) { return d.value; });
                var currentMax = d3.max(data, function(d) { return d.value; });
                if (currentMin === undefined || currentMax === undefined) {
                    $(titleselector).text("N/C");
                } else {
                    $(titleselector).text(currentMin + " - " + currentMax);
                }

                // add the canvas to the DOM
                var width = $(selector).width() - 16;
                // FIXME: determine dynamically
                var height = 120 - 30; // div height - title height - slider height

                var barchart = d3.select(selector)
                    .append("svg:svg")
                    .attr("width", width)
                    .attr("height", height);

                var g = barchart.append("g")
                    .attr("transform", "scale(1, -1) translate(0, -" + height + ")");

                var barWidth = Math.max(width / (maxValue - minValue), 2);

                var x_scale = d3.scale.linear().domain([minValue, maxValue]).range([0, width - barWidth ]).interpolate(d3.interpolateRound).clamp(true);
                var y_scale = d3.scale.linear().domain([0, maxCount]).range([0, height - 5]);

                function select_range(start, end) {
                    var sep = "&";
                    var repl = "";
                    if (start !== undefined && end !== undefined)
                        repl = "f=" + fieldname + "__range:" + start + "-" + end;

                    if (! document.location.search)
                        sep = "";
                    var re = new RegExp("f=" + fieldname + "__range:\\d+-\\d+");
                    m = document.location.search.match(re);
                    if (m !== null) {
                        // There is already a date facet. Replace its value, or cancel it
                        document.location.search = document.location.search.replace(re, repl);
                    } else {
                        document.location.search = document.location.search + sep + repl;
                    }
                };

                var brush = d3.svg.brush()
                    .x(x_scale)
                    .on("brush", function () {
                            var b = brush.empty() ? x_scale.domain() : brush.extent();
                            $(titleselector).text(Math.floor(b[0]) + " - " + Math.floor(b[1]));
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
                var slidername = fieldname + '_range_slider';
                $(selector).after('<div class="facetslider" id="' + slidername + '"></div>');
                $('#' + slidername).slider({
                                range: true,
                                min: minValue,
                                max: maxValue,
                                values: [ currentMin, currentMax ],
                                slide: function(event, ui) {
                                    var range = ui.values;
                                    $(titleselector).text(range[0] + " - " + range[1]);
                                },
                                stop: function(event, ui) {
                                    var range = ui.values;
                                    select_range(range[0], range[1]);
                                }
                            });

                return barchart;
            };


        document.datechart = draw_barchart("#creationHistogram",
                                           "creation_date_start",
                                           $("#creationHistogram [data-year]").map(
                                               function() { return { "value": parseInt($(this).attr('data-year')),
                                                                     "count": parseInt($(this).attr('data-count')) };
                                                          }),
                                           parseInt($("#creationHistogram").attr("data-min")),
                                           parseInt($("#creationHistogram").attr("data-max")),
                                           "#histogramRange");

        document.heightchart = draw_barchart("#heightHistogram",
                                             "height",
                                             $("#heightHistogram [data-height]").map(
                                                 function() { return { "value": parseInt($(this).attr('data-height')),
                                                                       "count": parseInt($(this).attr('data-count')) };
                                                            }),
                                             parseInt($("#heightHistogram").attr("data-min")),
                                             parseInt($("#heightHistogram").attr("data-max")),
                                             "#heightRange");

        document.widthchart = draw_barchart("#widthHistogram",
                                             "width",
                                            $("#widthHistogram [data-width]").map(
                                                function() { return { "value": parseInt($(this).attr('data-width')),
                                                                      "count": parseInt($(this).attr('data-count')) };
                                                           }),
                                            parseInt($("#widthHistogram").attr("data-min")),
                                            parseInt($("#widthHistogram").attr("data-max")),
                                            "#widthRange");

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
                                        document.location.search = document.location.search + '&selection=' + selection.join(",");
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
                frame.css({
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
                    $('#lightbox').hide();
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
                    .bind("ivieweronstartload", function () { $(".loading").show(); })
                    .bind("ivieweronfinishload", function () { $(".loading").hide(); update_frame(); });
            };

            // FIXME: add Loading info, it may take a while to load/update image
            $('#lightbox').css('width', $(window).width() - 225)
                .attr('data-url', url)
                .show('fast');
            michaux.iviewer.iviewer('loadImage', url);
            michaux.iviewer_thumbnail = thumbnail;
      }

        // Display infopanel about a work
        // It can be given either a .vignette anchor or a div.work element
        function display_infopanel(self) {
            var work;
            var vignette;
            if (typeof self === "string" || typeof self === "number") {
                work = $("[data-cote=" + self + "]");
                vignette = $(work).find(".vignette");
            } else if ($(self).hasClass("work")) {
                vignette = $(self).find(".vignette");
                work = self;
            } else if ($(self).hasClass("vignette")) {
                vignette = self;
                work = $(self).parents("div.work");
            }

            //Get clicked link href
            var image_href = $(vignette).attr("href");
            var cote = $(work).attr('data-cote');

            function navbar() {
                var prev = $(work).prev().attr('data-cote');
                var next = $(work).next().attr('data-cote');
                return '<div id="infopanel_navbar"><a id="infopanel_prev" class="' + (prev === undefined ? 'disabled" href="" ' : 'enabled" href="javascript:michaux.display_infopanel(' + prev + ')"') + '>&nbsp;</a> | <a id="infopanel_next" class="' + (next === undefined ? 'disabled" href="" ' : 'enabled" href="javascript:michaux.display_infopanel(' + next + ')"') + '>&nbsp;</a> <a id="infopanel_close" href="javascript:michaux.hide_infopanel();">&nbsp;</a></div>';
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
                                                    // Reset zoom for all images
                                                    $("div.work").css({ zoom: 1, "-moz-transform": "scale(1)" });
                                                    $('#hm' + cote).animate({zoom: 1.3, "-moz-transform": "scale(1.3)"})[0].scrollIntoView();
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
        $(".facetcontent").hide("fast", function () {
                                    $(".active-facet").parents(".facetcontent").show();
                                    $(".barchartbox .active-facet").parent().next().show();
                                });
        $(".facettitle").click(function() {
                                   $(".facetcontent").hide("fast");
                                   $(this).next().show("fast");
                               });

        michaux.display_infopanel = display_infopanel;

        michaux.hide_infopanel = function () {
            $("div.work").css({zoom: 1, "-moz-transform": "scale(1)"});
            $('#content').css("margin-right", "5px");
            $('#info_panel').hide('fast');
            $('#lightbox').hide();
        };

        michaux.resetFilter = function () {
            document.location.search = "";
        };

        michaux.getSelection = function () {
            return $("div.work.selected").map( function () { return $(this).attr('data-cote'); } ).toArray();
        };
    });
