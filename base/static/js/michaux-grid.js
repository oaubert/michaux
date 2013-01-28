var michaux = {};

jQuery(document).ready(
    function($) {
        var barchart = function () {
            // Build histogram
            var data = $("a[data-year]").map( function() { return { "year": parseInt($(this).attr('data-year')),
                                                                    "count": parseInt($(this).attr('data-count')) };
                                                         });
            var minYear = parseInt($("#creationHistogram").attr("data-min"));
            var maxYear = parseInt($("#creationHistogram").attr("data-max"));
            var maxCount = d3.max(data, function(d) { return d.count; });

            // add the canvas to the DOM
            var width = $("#creationHistogram").width() - 16;
            // FIXME: determine dynamically
            var height = 120 - 30; // div height - title height

            var barchart = d3.select("#creationHistogram")
                .append("svg:svg")
                .attr("width", width)
                .attr("height", height);

            var g = barchart.append("g")
                .attr("transform", "scale(1, -1) translate(0, -" + height + ")");

            var barWidth = width / (maxYear - minYear);

            var x_scale = d3.scale.linear().domain([minYear, maxYear]).range([0, width - barWidth ]).interpolate(d3.interpolateRound).clamp(true);
            var y_scale = d3.scale.linear().domain([0, maxCount]).range([0, height - 5]);

            var brush = d3.svg.brush()
                .x(x_scale)
                .on("brush", function () {
                        var b = brush.empty() ? x_scale.domain() : brush.extent();
                        console.log(b);
                        $("#histogramRange").text(Math.floor(b[0]) + " - " + Math.floor(b[1]));
                    })
                .on("brushend", function () {
                        var sep = "&";
                        var repl = "";
                        if (! brush.empty()) {
                            var b = brush.extent();
                            var start = Math.floor(b[0]);
                            var end = Math.floor(b[1]);
                            repl = "f=creation_date_start__range:" + start + "-" + end;
                        }

                        if (! document.location.search)
                            sep = "";
                        var re = /f=creation_date_start__range:\d+-\d+/;
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
                .attr("x", function(d, index) { return x_scale(d.year); })
                .attr("y", function(d) { return 0; })
                .attr("svg:title", function(d) { return d.year + ' (' + d.count + ')'; })
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
            return d3.rebind(barchart, brush, "on");
        }();
        document.barchart = barchart;

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

        // Homemade lightbox
        $('.vignette').click(function(e) {
                                 //prevent default action (hyperlink)
                                 e.preventDefault();
                                 //Get clicked link href
                                 var image_href = $(this).attr("href");
                                 var cote = $(this).parents("div.work").attr('data-cote');
                                 // AJAX callback to insert the lightbox_info
                                 // FIXME: hardcoded URL. Should fix this.
                                 $.get(cote + '/info', function (data) {
                                           $('#info_panel').html(data);
                                           $('#info_panel').show('fast');
                                       });
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

        michaux.openFacets = function () {
                 $("div.facetbox ul").show("fast");
        };

        michaux.closeFacets = function () {
                 $("div.facetbox ul").hide("fast");
        };

        michaux.resetFilter = function () {
            document.location.search = "";
        };

        michaux.getSelection = function () {
            return $("div.work.selected").map( function () { $(this).attr('data-cote'); } );
        };
    });
