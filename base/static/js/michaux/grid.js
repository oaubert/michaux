jQuery(document).ready(
    function ($) {
        "use strict";

        if (document.michaux === undefined) {
            document.michaux = {};
        }
        // FIXME: Make that a jquery plugin?
        function draw_barchart(element) {
            var fieldname = $(element).attr('data-field');
            var minValue = parseInt($(element).attr("data-min"), 10);
            var maxValue = parseInt($(element).attr("data-max"), 10);
            var title = $(element).parents(".facetbox").find(".facetRange");
            function facet_title(min, max) {
                if (min === undefined) {
                    title.text("N/C");
                } else {
                    title.text(min + " - " + max);
                }
            }

            var data = $(element).find(".facetdata").map(function () {
                return { "value": parseInt($(this).attr('data-value'), 10),
                         "count": parseInt($(this).attr('data-count'), 10) };
            });
            var maxCount = d3.max(data, function (d) { return d.count; });
            var currentMin = d3.min(data, function (d) { return d.value; });
            var currentMax = d3.max(data, function (d) { return d.value; });
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
                        if (!brush.empty()) {
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
                .attr("x", function (d, index) { return x_scale(d.value); })
                .attr("y", function (d) { return 0; })
                .attr("svg:title", function (d) { return d.value + ' (' + d.count + ')'; })
                .attr("height", function (d) { return y_scale(d.count); })
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
                              slide: function (event, ui) {
                                  var range = ui.values;
                                  facet_title(range[0], range[1]);
                              },
                              stop: function (event, ui) {
                                  var range = ui.values;
                                  select_range(range[0], range[1]);
                              }
                          });

            return barchart;
        }
        $(".barchartwidget").each(function () {
            draw_barchart(this);
        });

        $("#zoomslider").slider({
            range: false,
            min: 1,
            max: 200,
            value: 100 * ($("#grid").css('zoom') || 1),
            slide: function (event, ui) {
                var z = ui.value / 100.0;
                $("#grid").css({ zoom: z, "-moz-transform": "scale(" + z + ")" });
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

        document.michaux.sort_facet = function (e) {
            var box = $(this).parents(".facetbox");
            e.preventDefault();
            var crit = box[0].dataset.sorter || "count";
            if (crit === "count") {
                // Sort alphabetically
                box.find(".facetcontent ul>li").tsort();
                box[0].dataset.sorter = "label";
            } else {
                // Reverse sort by itemcount
                box.find(".facetcontent ul>li").tsort({data: 'itemcount', order: 'desc', useVal: true});
                box[0].dataset.sorter = "count";
            }
        };

        var Latinise = {};
        Latinise.latin_map = {"Á":"A","Ă":"A","Ắ":"A","Ặ":"A","Ằ":"A","Ẳ":"A","Ẵ":"A","Ǎ":"A","Â":"A","Ấ":"A","Ậ":"A","Ầ":"A","Ẩ":"A","Ẫ":"A","Ä":"A","Ǟ":"A","Ȧ":"A","Ǡ":"A","Ạ":"A","Ȁ":"A","À":"A","Ả":"A","Ȃ":"A","Ā":"A","Ą":"A","Å":"A","Ǻ":"A","Ḁ":"A","Ⱥ":"A","Ã":"A","Ꜳ":"AA","Æ":"AE","Ǽ":"AE","Ǣ":"AE","Ꜵ":"AO","Ꜷ":"AU","Ꜹ":"AV","Ꜻ":"AV","Ꜽ":"AY","Ḃ":"B","Ḅ":"B","Ɓ":"B","Ḇ":"B","Ƀ":"B","Ƃ":"B","Ć":"C","Č":"C","Ç":"C","Ḉ":"C","Ĉ":"C","Ċ":"C","Ƈ":"C","Ȼ":"C","Ď":"D","Ḑ":"D","Ḓ":"D","Ḋ":"D","Ḍ":"D","Ɗ":"D","Ḏ":"D","ǲ":"D","ǅ":"D","Đ":"D","Ƌ":"D","Ǳ":"DZ","Ǆ":"DZ","É":"E","Ĕ":"E","Ě":"E","Ȩ":"E","Ḝ":"E","Ê":"E","Ế":"E","Ệ":"E","Ề":"E","Ể":"E","Ễ":"E","Ḙ":"E","Ë":"E","Ė":"E","Ẹ":"E","Ȅ":"E","È":"E","Ẻ":"E","Ȇ":"E","Ē":"E","Ḗ":"E","Ḕ":"E","Ę":"E","Ɇ":"E","Ẽ":"E","Ḛ":"E","Ꝫ":"ET","Ḟ":"F","Ƒ":"F","Ǵ":"G","Ğ":"G","Ǧ":"G","Ģ":"G","Ĝ":"G","Ġ":"G","Ɠ":"G","Ḡ":"G","Ǥ":"G","Ḫ":"H","Ȟ":"H","Ḩ":"H","Ĥ":"H","Ⱨ":"H","Ḧ":"H","Ḣ":"H","Ḥ":"H","Ħ":"H","Í":"I","Ĭ":"I","Ǐ":"I","Î":"I","Ï":"I","Ḯ":"I","İ":"I","Ị":"I","Ȉ":"I","Ì":"I","Ỉ":"I","Ȋ":"I","Ī":"I","Į":"I","Ɨ":"I","Ĩ":"I","Ḭ":"I","Ꝺ":"D","Ꝼ":"F","Ᵹ":"G","Ꞃ":"R","Ꞅ":"S","Ꞇ":"T","Ꝭ":"IS","Ĵ":"J","Ɉ":"J","Ḱ":"K","Ǩ":"K","Ķ":"K","Ⱪ":"K","Ꝃ":"K","Ḳ":"K","Ƙ":"K","Ḵ":"K","Ꝁ":"K","Ꝅ":"K","Ĺ":"L","Ƚ":"L","Ľ":"L","Ļ":"L","Ḽ":"L","Ḷ":"L","Ḹ":"L","Ⱡ":"L","Ꝉ":"L","Ḻ":"L","Ŀ":"L","Ɫ":"L","ǈ":"L","Ł":"L","Ǉ":"LJ","Ḿ":"M","Ṁ":"M","Ṃ":"M","Ɱ":"M","Ń":"N","Ň":"N","Ņ":"N","Ṋ":"N","Ṅ":"N","Ṇ":"N","Ǹ":"N","Ɲ":"N","Ṉ":"N","Ƞ":"N","ǋ":"N","Ñ":"N","Ǌ":"NJ","Ó":"O","Ŏ":"O","Ǒ":"O","Ô":"O","Ố":"O","Ộ":"O","Ồ":"O","Ổ":"O","Ỗ":"O","Ö":"O","Ȫ":"O","Ȯ":"O","Ȱ":"O","Ọ":"O","Ő":"O","Ȍ":"O","Ò":"O","Ỏ":"O","Ơ":"O","Ớ":"O","Ợ":"O","Ờ":"O","Ở":"O","Ỡ":"O","Ȏ":"O","Ꝋ":"O","Ꝍ":"O","Ō":"O","Ṓ":"O","Ṑ":"O","Ɵ":"O","Ǫ":"O","Ǭ":"O","Ø":"O","Ǿ":"O","Õ":"O","Ṍ":"O","Ṏ":"O","Ȭ":"O","Ƣ":"OI","Ꝏ":"OO","Ɛ":"E","Ɔ":"O","Ȣ":"OU","Ṕ":"P","Ṗ":"P","Ꝓ":"P","Ƥ":"P","Ꝕ":"P","Ᵽ":"P","Ꝑ":"P","Ꝙ":"Q","Ꝗ":"Q","Ŕ":"R","Ř":"R","Ŗ":"R","Ṙ":"R","Ṛ":"R","Ṝ":"R","Ȑ":"R","Ȓ":"R","Ṟ":"R","Ɍ":"R","Ɽ":"R","Ꜿ":"C","Ǝ":"E","Ś":"S","Ṥ":"S","Š":"S","Ṧ":"S","Ş":"S","Ŝ":"S","Ș":"S","Ṡ":"S","Ṣ":"S","Ṩ":"S","Ť":"T","Ţ":"T","Ṱ":"T","Ț":"T","Ⱦ":"T","Ṫ":"T","Ṭ":"T","Ƭ":"T","Ṯ":"T","Ʈ":"T","Ŧ":"T","Ɐ":"A","Ꞁ":"L","Ɯ":"M","Ʌ":"V","Ꜩ":"TZ","Ú":"U","Ŭ":"U","Ǔ":"U","Û":"U","Ṷ":"U","Ü":"U","Ǘ":"U","Ǚ":"U","Ǜ":"U","Ǖ":"U","Ṳ":"U","Ụ":"U","Ű":"U","Ȕ":"U","Ù":"U","Ủ":"U","Ư":"U","Ứ":"U","Ự":"U","Ừ":"U","Ử":"U","Ữ":"U","Ȗ":"U","Ū":"U","Ṻ":"U","Ų":"U","Ů":"U","Ũ":"U","Ṹ":"U","Ṵ":"U","Ꝟ":"V","Ṿ":"V","Ʋ":"V","Ṽ":"V","Ꝡ":"VY","Ẃ":"W","Ŵ":"W","Ẅ":"W","Ẇ":"W","Ẉ":"W","Ẁ":"W","Ⱳ":"W","Ẍ":"X","Ẋ":"X","Ý":"Y","Ŷ":"Y","Ÿ":"Y","Ẏ":"Y","Ỵ":"Y","Ỳ":"Y","Ƴ":"Y","Ỷ":"Y","Ỿ":"Y","Ȳ":"Y","Ɏ":"Y","Ỹ":"Y","Ź":"Z","Ž":"Z","Ẑ":"Z","Ⱬ":"Z","Ż":"Z","Ẓ":"Z","Ȥ":"Z","Ẕ":"Z","Ƶ":"Z","Ĳ":"IJ","Œ":"OE","ᴀ":"A","ᴁ":"AE","ʙ":"B","ᴃ":"B","ᴄ":"C","ᴅ":"D","ᴇ":"E","ꜰ":"F","ɢ":"G","ʛ":"G","ʜ":"H","ɪ":"I","ʁ":"R","ᴊ":"J","ᴋ":"K","ʟ":"L","ᴌ":"L","ᴍ":"M","ɴ":"N","ᴏ":"O","ɶ":"OE","ᴐ":"O","ᴕ":"OU","ᴘ":"P","ʀ":"R","ᴎ":"N","ᴙ":"R","ꜱ":"S","ᴛ":"T","ⱻ":"E","ᴚ":"R","ᴜ":"U","ᴠ":"V","ᴡ":"W","ʏ":"Y","ᴢ":"Z","á":"a","ă":"a","ắ":"a","ặ":"a","ằ":"a","ẳ":"a","ẵ":"a","ǎ":"a","â":"a","ấ":"a","ậ":"a","ầ":"a","ẩ":"a","ẫ":"a","ä":"a","ǟ":"a","ȧ":"a","ǡ":"a","ạ":"a","ȁ":"a","à":"a","ả":"a","ȃ":"a","ā":"a","ą":"a","ᶏ":"a","ẚ":"a","å":"a","ǻ":"a","ḁ":"a","ⱥ":"a","ã":"a","ꜳ":"aa","æ":"ae","ǽ":"ae","ǣ":"ae","ꜵ":"ao","ꜷ":"au","ꜹ":"av","ꜻ":"av","ꜽ":"ay","ḃ":"b","ḅ":"b","ɓ":"b","ḇ":"b","ᵬ":"b","ᶀ":"b","ƀ":"b","ƃ":"b","ɵ":"o","ć":"c","č":"c","ç":"c","ḉ":"c","ĉ":"c","ɕ":"c","ċ":"c","ƈ":"c","ȼ":"c","ď":"d","ḑ":"d","ḓ":"d","ȡ":"d","ḋ":"d","ḍ":"d","ɗ":"d","ᶑ":"d","ḏ":"d","ᵭ":"d","ᶁ":"d","đ":"d","ɖ":"d","ƌ":"d","ı":"i","ȷ":"j","ɟ":"j","ʄ":"j","ǳ":"dz","ǆ":"dz","é":"e","ĕ":"e","ě":"e","ȩ":"e","ḝ":"e","ê":"e","ế":"e","ệ":"e","ề":"e","ể":"e","ễ":"e","ḙ":"e","ë":"e","ė":"e","ẹ":"e","ȅ":"e","è":"e","ẻ":"e","ȇ":"e","ē":"e","ḗ":"e","ḕ":"e","ⱸ":"e","ę":"e","ᶒ":"e","ɇ":"e","ẽ":"e","ḛ":"e","ꝫ":"et","ḟ":"f","ƒ":"f","ᵮ":"f","ᶂ":"f","ǵ":"g","ğ":"g","ǧ":"g","ģ":"g","ĝ":"g","ġ":"g","ɠ":"g","ḡ":"g","ᶃ":"g","ǥ":"g","ḫ":"h","ȟ":"h","ḩ":"h","ĥ":"h","ⱨ":"h","ḧ":"h","ḣ":"h","ḥ":"h","ɦ":"h","ẖ":"h","ħ":"h","ƕ":"hv","í":"i","ĭ":"i","ǐ":"i","î":"i","ï":"i","ḯ":"i","ị":"i","ȉ":"i","ì":"i","ỉ":"i","ȋ":"i","ī":"i","į":"i","ᶖ":"i","ɨ":"i","ĩ":"i","ḭ":"i","ꝺ":"d","ꝼ":"f","ᵹ":"g","ꞃ":"r","ꞅ":"s","ꞇ":"t","ꝭ":"is","ǰ":"j","ĵ":"j","ʝ":"j","ɉ":"j","ḱ":"k","ǩ":"k","ķ":"k","ⱪ":"k","ꝃ":"k","ḳ":"k","ƙ":"k","ḵ":"k","ᶄ":"k","ꝁ":"k","ꝅ":"k","ĺ":"l","ƚ":"l","ɬ":"l","ľ":"l","ļ":"l","ḽ":"l","ȴ":"l","ḷ":"l","ḹ":"l","ⱡ":"l","ꝉ":"l","ḻ":"l","ŀ":"l","ɫ":"l","ᶅ":"l","ɭ":"l","ł":"l","ǉ":"lj","ſ":"s","ẜ":"s","ẛ":"s","ẝ":"s","ḿ":"m","ṁ":"m","ṃ":"m","ɱ":"m","ᵯ":"m","ᶆ":"m","ń":"n","ň":"n","ņ":"n","ṋ":"n","ȵ":"n","ṅ":"n","ṇ":"n","ǹ":"n","ɲ":"n","ṉ":"n","ƞ":"n","ᵰ":"n","ᶇ":"n","ɳ":"n","ñ":"n","ǌ":"nj","ó":"o","ŏ":"o","ǒ":"o","ô":"o","ố":"o","ộ":"o","ồ":"o","ổ":"o","ỗ":"o","ö":"o","ȫ":"o","ȯ":"o","ȱ":"o","ọ":"o","ő":"o","ȍ":"o","ò":"o","ỏ":"o","ơ":"o","ớ":"o","ợ":"o","ờ":"o","ở":"o","ỡ":"o","ȏ":"o","ꝋ":"o","ꝍ":"o","ⱺ":"o","ō":"o","ṓ":"o","ṑ":"o","ǫ":"o","ǭ":"o","ø":"o","ǿ":"o","õ":"o","ṍ":"o","ṏ":"o","ȭ":"o","ƣ":"oi","ꝏ":"oo","ɛ":"e","ᶓ":"e","ɔ":"o","ᶗ":"o","ȣ":"ou","ṕ":"p","ṗ":"p","ꝓ":"p","ƥ":"p","ᵱ":"p","ᶈ":"p","ꝕ":"p","ᵽ":"p","ꝑ":"p","ꝙ":"q","ʠ":"q","ɋ":"q","ꝗ":"q","ŕ":"r","ř":"r","ŗ":"r","ṙ":"r","ṛ":"r","ṝ":"r","ȑ":"r","ɾ":"r","ᵳ":"r","ȓ":"r","ṟ":"r","ɼ":"r","ᵲ":"r","ᶉ":"r","ɍ":"r","ɽ":"r","ↄ":"c","ꜿ":"c","ɘ":"e","ɿ":"r","ś":"s","ṥ":"s","š":"s","ṧ":"s","ş":"s","ŝ":"s","ș":"s","ṡ":"s","ṣ":"s","ṩ":"s","ʂ":"s","ᵴ":"s","ᶊ":"s","ȿ":"s","ɡ":"g","ᴑ":"o","ᴓ":"o","ᴝ":"u","ť":"t","ţ":"t","ṱ":"t","ț":"t","ȶ":"t","ẗ":"t","ⱦ":"t","ṫ":"t","ṭ":"t","ƭ":"t","ṯ":"t","ᵵ":"t","ƫ":"t","ʈ":"t","ŧ":"t","ᵺ":"th","ɐ":"a","ᴂ":"ae","ǝ":"e","ᵷ":"g","ɥ":"h","ʮ":"h","ʯ":"h","ᴉ":"i","ʞ":"k","ꞁ":"l","ɯ":"m","ɰ":"m","ᴔ":"oe","ɹ":"r","ɻ":"r","ɺ":"r","ⱹ":"r","ʇ":"t","ʌ":"v","ʍ":"w","ʎ":"y","ꜩ":"tz","ú":"u","ŭ":"u","ǔ":"u","û":"u","ṷ":"u","ü":"u","ǘ":"u","ǚ":"u","ǜ":"u","ǖ":"u","ṳ":"u","ụ":"u","ű":"u","ȕ":"u","ù":"u","ủ":"u","ư":"u","ứ":"u","ự":"u","ừ":"u","ử":"u","ữ":"u","ȗ":"u","ū":"u","ṻ":"u","ų":"u","ᶙ":"u","ů":"u","ũ":"u","ṹ":"u","ṵ":"u","ᵫ":"ue","ꝸ":"um","ⱴ":"v","ꝟ":"v","ṿ":"v","ʋ":"v","ᶌ":"v","ⱱ":"v","ṽ":"v","ꝡ":"vy","ẃ":"w","ŵ":"w","ẅ":"w","ẇ":"w","ẉ":"w","ẁ":"w","ⱳ":"w","ẘ":"w","ẍ":"x","ẋ":"x","ᶍ":"x","ý":"y","ŷ":"y","ÿ":"y","ẏ":"y","ỵ":"y","ỳ":"y","ƴ":"y","ỷ":"y","ỿ":"y","ȳ":"y","ẙ":"y","ɏ":"y","ỹ":"y","ź":"z","ž":"z","ẑ":"z","ʑ":"z","ⱬ":"z","ż":"z","ẓ":"z","ȥ":"z","ẕ":"z","ᵶ":"z","ᶎ":"z","ʐ":"z","ƶ":"z","ɀ":"z","ﬀ":"ff","ﬃ":"ffi","ﬄ":"ffl","ﬁ":"fi","ﬂ":"fl","ĳ":"ij","œ":"oe","ﬆ":"st","ₐ":"a","ₑ":"e","ᵢ":"i","ⱼ":"j","ₒ":"o","ᵣ":"r","ᵤ":"u","ᵥ":"v","ₓ":"x" };
        document.michaux.latinise = function (s) {
            return s.replace(/[^A-Za-z0-9\[\] ]/g, function(a) { return Latinise.latin_map[a] || a; });
        };

        document.michaux.clean_label = function (s) {
            return document.michaux.latinise(s).replace(/[^a-zA-Z_]/g, "_");
        };

        document.michaux.highlight_facet = function (e) {
            e.preventDefault();
            var field = $(this).parents(".facetbox").attr("data-field");
            var text = $(this).find(".facetitemlabel").text();
            text = (text === "?" ? "unknown" : text);
            $("." + field + "-" + document.michaux.clean_label(text)).addClass("highlight");
        };

        document.michaux.unhighlight_facet = function (e) {
            e.preventDefault();
            $(".highlight").removeClass("highlight");
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
        $(".facetitem").on("mouseenter", document.michaux.highlight_facet);
        $(".facetitem").on("mouseleave", document.michaux.unhighlight_facet);
        $(".facetsorter").on("click", document.michaux.sort_facet);

        // Hide/show facets
        $(".facetbox:not(.active) .facetcontent").hide("fast");
        $(".facettitle").click(function () {
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
