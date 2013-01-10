resetFilter = function () {
    f = $("#filter")[0];
    f.value = "";
    f.form.submit()
}

jQuery(document).ready(
    function($) {
        var range = $("[data-start]").map( function () { var a = $(this).attr("data-start"); if (a != "None") return parseInt(a); } )
        if (range.length > 0) {
            var min = Math.min.apply(Math, range);
            var max = Math.max.apply(Math, range);

            $( "#slider-range" ).slider({
                                            range: true,
                                            min: min,
                                            max: max,
                                            values: [ min, max ],
                                            slide: function( event, ui ) {
                                                $( "#date" ).val( ui.values[ 0 ] + " - " + ui.values[ 1 ] );
                                            },
                                            stop: function(event, ui) {
                                                var count = 0;
                                                var shown = 0;
                                                $("[data-start]").each( function () {
                                                                            count += 1;
                                                                            var d = parseInt($(this).attr('data-start'));
                                                                            if (d < ui.values[0] || d > ui.values[1]) {
                                                                                $(this).hide();
                                                                            } else {
                                                                                $(this).show();
                                                                                shown += 1;
                                                                            }
                                                                        });
                                                var plural = "";
                                                if (shown > 1)
                                                    plural = "s";
                                                $("#shown").text(shown + " / " + count + " élément" + plural + " affiché" + plural);
                                                // FIXME: this should
                                                // call the facet code
                                                // (so that it works
                                                // even with
                                                // pagination) and it
                                                // will also allow to
                                                // keep the filter in
                                                // navigation history
                                            }
                                        });

            $( "#date" ).val( $( "#slider-range" ).slider( "values", 0 ) +
                              " - " + $( "#slider-range" ).slider( "values", 1 ) );
        }

        // Homemade lightbox
        $('.vignette').click(function(e) {
                                 //prevent default action (hyperlink)
                                 e.preventDefault();
                                 //Get clicked link href
                                 var image_href = $(this).attr("href");
                                 /*
                                  If the lightbox window HTML already exists in document,
                                  change the img src to to match the href of whatever link was clicked
                                  If the lightbox window HTML doesn't exists, create it and insert it.
                                  (This will only happen the first time around)
                                  */
                                 if ($('#lightbox').length > 0) { // #lightbox exists
                                     //place href as img src value
                                     $('#lightbox_content').html('<img src="' + image_href + '" />');
                                     //show lightbox window - you could use .show('fast') for a transition
                                     $('#lightbox').show();
                                 }
                                 else { //#lightbox does not exist - create and insert (runs 1st time only)
                                     //create HTML markup for lightbox window
                                     var lightbox =
                                         '<div id="lightbox">' +
                                         '<p>Click to close</p>' +
                                         '<div id="lightbox_content">' + //insert clicked link's href into img src
                                         '<img src="' + image_href +'" />' +
                                         '</div>' +
                                         '</div>';
                                     //insert lightbox HTML into page
                                     $('body').append(lightbox);
                                 }
                             });
        //Click anywhere on the page to get rid of lightbox window
        $('#lightbox').live('click', function() { //must use live, as the lightbox element is inserted into the DOM
                                $('#lightbox').hide();
                            });
    });

