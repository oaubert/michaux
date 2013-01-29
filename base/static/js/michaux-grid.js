var michaux = {};

jQuery(document).ready(
    function($) {
            function draw_barchart (selector, fieldname, data, minValue, maxValue, titleselector) {
                var maxCount = d3.max(data, function(d) { return d.count; });

                // add the canvas to the DOM
                var width = $(selector).width() - 16;
                // FIXME: determine dynamically
                var height = 120 - 30; // div height - title height

                var barchart = d3.select(selector)
                    .append("svg:svg")
                    .attr("width", width)
                    .attr("height", height);

                var g = barchart.append("g")
                    .attr("transform", "scale(1, -1) translate(0, -" + height + ")");

                var barWidth = Math.max(width / (maxValue - minValue), 2);

                var x_scale = d3.scale.linear().domain([minValue, maxValue]).range([0, width - barWidth ]).interpolate(d3.interpolateRound).clamp(true);
                var y_scale = d3.scale.linear().domain([0, maxCount]).range([0, height - 5]);

                var brush = d3.svg.brush()
                    .x(x_scale)
                    .on("brush", function () {
                            var b = brush.empty() ? x_scale.domain() : brush.extent();
                            $(titleselector).text(Math.floor(b[0]) + " - " + Math.floor(b[1]));
                    })
                    .on("brushend", function () {
                            var sep = "&";
                            var repl = "";
                            if (! brush.empty()) {
                                var b = brush.extent();
                                var start = Math.floor(b[0]);
                                var end = Math.floor(b[1]);
                                repl = "f=" + fieldname + "__range:" + start + "-" + end;
                            }

                            if (! document.location.search)
                                sep = "";
                            var re = new RegExp("f=" + fieldname + "__range:\d+-\d+");
                            m = document.location.search.match(re);
                            if (m !== null) {
                                // There is already a date facet. Replace its value, or cancel it
                                document.location.search = document.location.search.replace(re, repl);
                            } else {
                            document.location.search = document.location.search + sep + repl;
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
                    .on("mouseup", function (d) {
                        });


                barchart.x = x_scale;
                barchart.y = y_scale;

                $('svg rect.bar').tipsy({
                                            gravity: 'sw',
                                            html: false
                                        });
                d3.rebind(barchart, brush, "on");
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
            // AJAX callback to insert the lightbox_info
            function navbar() {
                var prev = $(work).prev().attr('data-cote');
                var next = $(work).next().attr('data-cote');
                return '<div id="infopanel_navbar"><a id="infopanel_prev" class="' + (prev === undefined ? 'disabled" href="" ' : 'enabled" href="javascript:michaux.display_infopanel(' + prev + ')"') + '>&nbsp;</a> | <a id="infopanel_next" class="' + (next === undefined ? 'disabled" href="" ' : 'enabled" href="javascript:michaux.display_infopanel(' + next + ')"') + '>&nbsp;</a> <a id="infopanel_close" href="javascript:michaux.hide_infopanel();">&nbsp;</a></div>';
            }
            // FIXME: hardcoded URL. Should fix this.
            $.get(cote + '/info', function (data) {
                      $('#content').css("padding-right", "200px");
                      $('#info_panel').html(navbar() + data);
                      $('#info_panel').show('fast');
                      $("[rel=lightbox]").colorbox( {
                                                        preloading: false,
                                                        opacity: 0.01,
                                                        photo: true,
                                                        width: $(window).width() - 240,
                                                        height: document.body.offsetHeight - 10,
                                                        maxWidth: $(window).width() - 240,
                                                        maxHeight: document.body.offsetHeight - 10,
                                                        fixed: true,
                                                        onOpen: function () { console.log($(window).height(), document.body.offsetHeight); },
                                                        onComplete: function() { $('.cboxPhoto').wheelzoom(); }
                                                    });
                  });
        }

        // Homemade lightbox
        $('.vignette').click(function(e) {
                                 //prevent default action (hyperlink)
                                 e.preventDefault();
                                 michaux.display_infopanel(this);
                             });
        //Click anywhere on the page to get rid of lightbox window
        $('#lightbox').live('click', function() { //must use live, as the lightbox element is inserted into the DOM
                                $('#lightbox').hide();
                            });

        // Select/unselect items
        $("a.selection").click(function () {
                                   $(this).parents("div.work").toggleClass("selected");
                               });

        // Hide/show facets
        $(".facettitle").click(function() {
                                   $(this).next().slideToggle("fast");
                               });

        michaux.display_infopanel = display_infopanel;

        michaux.hide_infopanel = function () {
            $('#content').css("padding-right", "5px");
            $('#info_panel').hide('fast');
        };

        michaux.resetFilter = function () {
            document.location.search = "";
        };

        michaux.getSelection = function () {
            return $("div.work.selected").map( function () { $(this).attr('data-cote'); } );
        };
    });
