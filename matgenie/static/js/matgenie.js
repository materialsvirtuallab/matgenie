$(function() {
    $("#tabs").tabs();
    //$("#select-function").selectmenu();
    $(".button").button();

    $("#select-function").change(function() {
        var val;
        val = $("#select-function").val();
        alert("#input-" + val);
        $("#input-" + val).show();
    });

    $('.dropbox').on(
        'dragover',
        function(e) {
            e.preventDefault();
            e.stopPropagation();
        }
    )
    $('.dropbox').on(
        'dragenter',
        function(e) {
            e.preventDefault();
            e.stopPropagation();
        }
    )
    $('.dropbox').on(
        'drop',
        function(e) {
            if (e.originalEvent.dataTransfer) {
                if (e.originalEvent.dataTransfer.files.length) {
                    e.preventDefault();
                    e.stopPropagation();
                    var opid = $(this).attr('id');
                    var url = 'matgenie/rest/' + opid.split("-")[1];
                    var data = new FormData();
                    var files = e.originalEvent.dataTransfer.files;
                    if ((opid == "drop-compare") && ((files.length < 2) || (files.length > 5))) {
                        alert("Only 2-5 files at a time supported!");
                    } else if ((opid == "drop-surfaces") && (files.length > 1)) {
                        alert("Only one file at a time supported!");
                    } else {
                        $.each(files, function(i, file) {
                            data.append('file-' + i, file);
                        });
                        var other_data = $(this).closest("form").serializeArray();
                        $.each(other_data, function(key, input) {
                            data.append(input.name, input.value);
                        });
                        $.ajax({
                            url: url,
                            data: data,
                            cache: false,
                            contentType: false,
                            processData: false,
                            type: 'POST',
                            success: function(data) {
                                if (opid == "drop-convert") {
                                    displayConvert(data);
                                } else if (opid == "drop-symmetry") {
                                    displaySymmetry(data);
                                } else if (opid == "drop-surfaces") {
                                    displaySurfaces(data);
                                } else if (opid == "drop-xrd") {
                                    displayXRD(data);
                                } else if (opid == "drop-compare") {
                                    displayCompare(data);
                                }
                            },
                            error: function(xhr, ajaxOptions, thrownError) {
                                var m = $.parseJSON(xhr.responseText);
                                $("#div-results").empty();
                                $("#div-results").append($('<p class="p-error">' + m["error"] + '</p>'));
                                $("#div-results-wrapper").show();
                            }

                        });

                    }
                }
            }
        }
    );

});


function displayConvert(data) {
    $("#div-results").empty();
    var r = data["results"];
    $("#div-results").append($('<textarea rows="20" cols="50" id="textarea-results"></textarea>'));

    for (var f in r) {
        $("#textarea-results").append(f + "\n---\n" + r[f] + "\n");
    }

    $("#div-results-wrapper").show();
}


function displaySymmetry(data) {
    var r = data["results"];
    var table = '<table class="table-results"><thead><tr><th>Filename</th><th>International symbol</th><th>International number</th><th>Crystal system</th><th>Hall</th><th>Point group</th></tr></thead><tbody>';
    for (var f in r) {
        table += "<tr>"
        table += "<td>" + f + "</td>";
        table += "<td>" + r[f]["international"] + "</td>";
        table += "<td>" + r[f]["number"] + "</td>";
        table += "<td>" + r[f]["crystal_system"] + "</td>";
        table += "<td>" + r[f]["hall"] + "</td>";
        table += "<td>" + r[f]["point_group"] + "</td>";
        table += "</tr>";
    }
    table += "<tbody></table>";
    $("#div-results").empty();
    $("#div-results").append($(table));
    $(".table-results").DataTable();

    $("#div-results-wrapper").show();
}


function displayXRD(data) {
    var r = data["results"];
    $("#div-results").empty();
    for (var f in r) {
        $("#div-results").append($('<div class="div-subresult"><h4>' + f + "</h4>" + r[f] + '</div>'));
    }
    $("#div-results-wrapper").show();
}


function displaySurfaces(data) {
    $("#div-results").empty();
    $("#div-results").append($('<textarea rows="20" cols="50" id="textarea-results"></textarea>'));

    for (var f in data["results"]) {
        $("#textarea-results").append("Slab " + f + "\n-----\n" + data["results"][f] + "\n\n");
    }

    $("#div-results-wrapper").show();
}


function displayCompare(data) {
    var table = '<table class="table-results"><thead><tr><th>Filename 1</th><th>Filename 2</th><th>Matches?</th><th>Mapping</th><th>Min. RMS (&#8491;)</th></tr></thead><tbody>';
    for (var f in data["results"]) {
        var d = data["results"][f]
        table += "<tr>"
        table += "<td>" + d["files"][0] + "</td>";
        table += "<td>" + d["files"][1] + "</td>";
        table += "<td>" + d["match_found"] + "</td>";
        table += "<td>";
        for (var k in d["mapping"]) {
            table += k + "&harr;" + d["mapping"][k] + "<br>";
        }
        table += "</td>";
        table += "<td>" + d["rms"] + "</td>";
        table += "</tr>";
    }
    table += "<tbody></table>";
    $("#div-results").empty();
    $("#div-results").append($(table));

    $("#div-results-wrapper").show();
    $(".table-results").DataTable();

}
