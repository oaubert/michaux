jQuery(document).ready(
    function($) {
        "use strict";

        if (document.michaux === undefined)
            document.michaux = {};

        // FIXME: Make that a jquery plugin?
        function draw_barchart (element) {
            var fieldname = $(element).attr('data-field');
            var minValue = parseInt($(element).attr("data-min"), 10);
            var maxValue = parseInt($(element).attr("data-max"), 10);
            var title = $(element).parents(".facetbox").find(".facetRange");
            function facet_title(min, max) {
                if (min === undefined)
                    title.text("N/C");
                else
                    title.text(min + " - " + max);
            }

            var data = $(element).find(".facetdata").map(
                function() { return { "value": parseInt($(this).attr('data-value'), 10),
                                      "count": parseInt($(this).attr('data-count'), 10) };
                           });
            var maxCount = d3.max(data, function(d) { return d.count; });
            var currentMin = d3.min(data, function(d) { return d.value; });
            var currentMax = d3.max(data, function(d) { return d.value; });
            facet_title(currentMin, currentMax);

            // add the canvas to the DOM
            var width = $(element).parents(".facetbox").width() - 16;
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
                $('#selection_popup input').remove();
                $(i).parents("form").submit();
            }

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
        }
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


        document.michaux.tag_selection = function (tagname, selection) {
            if (selection === undefined) {
                var cote = $('#infopanel:visible').attr('data-current');
                if (cote !== undefined) {
                    selection = [ cote ];
                }
            }
            if (selection !== undefined) {
                selection.forEach(function (cote) {
                                       console.log("Tagging ", cote, " with ", tagname);
                                       // FIXME: add csrf token
                                       $.get("/base/selection/tag/",
                                             { 'selection': cote,
                                               'name': tagname });
                                  });
            }
        };
        document.michaux.untag_selection = function (tagname, selection) {
            if (selection === undefined) {
                var cote = $('#infopanel:visible').attr('data-current');
                if (cote !== undefined) {
                    selection = [ cote ];
                }
            }
            if (selection !== undefined) {
                selection.forEach(function (cote) {
                                       console.log("UnTagging ", cote, " with ", tagname);
                                       // FIXME: add csrf token
                                       $.get("/base/selection/untag/",
                                             { 'selection': cote,
                                               'name': tagname });
                                  });
            }
        };

        document.michaux.resetFilter = function () {
            document.location.search = "";
        };

        document.michaux.goto_page = function (p) {
            $('#selection_popup input').remove();
            $("#current_page").attr('value', p)[0].form.submit();
        };

        document.michaux.clear_facet = function (e) {
            e.preventDefault();
            var i = $(this).parents(".facetbox").find("input").remove();
            $('#selection_popup input').remove();
            $(this).parents("form").submit();
        };

        document.michaux.toggle_facet = function (e) {
            e.preventDefault();

            var i = $(this).find("input");
            if (i.length) {
                // There is an input sibling -> the facet was active. Remove the input.
                i.remove();
                // Provide immediate feedback.
                $(this).find(".active-facet").remove();
            } else {
                // There is no input sibling. We want to activate the
                // facet: its value is the text of the .faceitemlabel element
                var field = $(this).parents(".facetbox").attr("data-field");
                $(this).append($("<input />").attr({
                                                    type: "hidden",
                                                    name: "f",
                                                    value: field + "_exact:" + $(this).find(".facetitemlabel").text()
                                                }));
            }
            // Resubmit form
            $('#selection_popup input').remove();
            $(this).parents("form").submit();
        };

        // Event bindings
        $(".facetitem").on("click", document.michaux.toggle_facet);
        $(".clear-facet").on("click", document.michaux.clear_facet);

        // Hide/show facets
        $(".facetbox:not(.active) .facetcontent").hide("fast");
        $(".facettitle").click(function() {
                                   var f = $(this).siblings(".facetcontent");
                                   $(".facetcontent").not(f).hide("fast");
                                   f.show("fast");
                               });

        $("#selection_tag").autoSuggest(document.michaux.url('complete', 'tags'), {
                                            asHtmlID: "selection_tag",
                                            startText: "Entrez le tag ici",
                                            emptyText: "Aucun résultat",
                                            limitText: "Vous ne pouvez pas faire plus de sélection",
                                            queryParam: 'q',
                                            retrieveLimit: 20,
                                            minChars: 1,
                                            neverSubmit: true,
                                            selectionAdded: function (element) {
                                                var tagname = $(element).contents(":not(a)").text();
                                                document.michaux.tag_selection(tagname.trim(), document.michaux.getSelection());
                                            },
                                            selectionRemoved: function (element) {
                                                var tagname = $(element).contents(":not(a)").text();
                                                document.michaux.untag_selection(tagname.trim(), document.michaux.getSelection());
                                                return false;
                                            }
                                        });
});
