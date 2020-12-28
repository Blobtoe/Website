var filter_sats = [];

$(document).ready(function() {

    document.getElementById("close_popup").onclick = function() {
        HideFilterPopup()
    }

    window.onclick = function(event) {
        if (event.target == document.getElementById("filter_passes_popup")) {
            HideFilterPopup();
        }
    }
});

function ShowFilterPopup() {
    document.getElementById("filter_passes_popup").style.display = "block";
}

function HideFilterPopup() {
    document.getElementById("filter_passes_popup").style.display = "none";
}

function AddSatToFilter(e) {
    if (!filter_sats.includes(e.options[e.selectedIndex].text)) {
        filter_sats.push(e.options[e.selectedIndex].text)
        ShowSatsInFilter()
    }
}

function RemoveSatFromFilter(e) {
    var satName = e.parentNode.getElementsByTagName("span")[0].innerHTML;
    filter_sats = filter_sats.filter(e => e !== satName);
    e.parentNode.parentNode.removeChild(e.parentNode);
    ShowSatsInFilter()
}

function ShowSatsInFilter() {
    document.getElementById("sats_in_filter").innerHTML = "";
    filter_sats.forEach(sat => {
        var clone = document.getElementById("filter_sat_template").cloneNode(true);
        clone.getElementsByTagName("span")[0].innerHTML = sat;
        document.getElementById("sats_in_filter").innerHTML += clone.innerHTML;
    })

}

function ApplyFilter() {
    document.getElementById("main_content").innerHTML = "";
    pass_count = 0;

    //show the first 5 passes
    for (var i = 0; i < passes.length; i++) {
        pass = passes[i];
        if (Filter(pass)) {
            ShowPass(pass);
            pass_count += 1;
        }
    }

    /*
    for (var i = 0; i < 5; i++) {
        while (Filter(passes[passes.length - pass_count - 1]) == false) {
            pass_count++;
        }
        ShowPass(passes[passes.length - pass_count - 1]);
        pass_count++;
    }
    */

    HideFilterPopup();
}

//will return true if pass fits within filter, false if it doesnt
function Filter(path) {
    $.ajaxSetup({
        async: false
    });

    var value = null;

    $.getJSON(path, function(result) {
        if (
            (filter_sats.length == 0 || filter_sats.indexOf(result.satellite) != -1) &&
            !(document.getElementById("filter_before_date").valueAsNumber / 1000 <= result.aos) &&
            !(document.getElementById("filter_after_date").valueAsNumber / 1000 >= result.aos) &&
            !(document.getElementById("filter_min_elev").valueAsNumber >= result.max_elevation) &&
            !(document.getElementById("filter_max_elev").valueAsNumber <= result.max_elevation) &&
            !(document.getElementById("filter_min_sun").valueAsNumber >= result.sun_elev) &&
            !(document.getElementById("filter_max_sun").valueAsNumber <= result.sun_elev)
        ) {
            value = true;
        } else {
            value = false;
        }
    });

    while (value == null) {
        continue;
    }

    $.ajaxSetup({
        async: true
    });

    return value
}