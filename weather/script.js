//Made by Felix (Blobtoe)


var pass_count = 0;
var passes;
//everything is 'display: none' until everything is loaded
$(document).ready(function () {

    //get all the passes
    $.ajaxSetup({
        async: false
    });
    $.getJSON("/weather/images/passes.json", function(result) {
        passes = result
    });

    
    $.ajaxSetup({
        async: true
    });

    //show the first 5 passes
    for (var i = 0; i < 5; i++) {
        while (Filter(passes[passes.length-pass_count-1]) == false) {
            pass_count++;
        }
        ShowPass(passes[passes.length-pass_count-1]);
        pass_count++;
    }

    //show the next pass when the user scrolls down enough
    $(document).on('scroll', function() {
        if ($(this).scrollTop() >= $('.pass').eq(-3).position().top) {
            while (Filter(passes[passes.length-pass_count-1]) == false) {
                pass_count++;
            }
            ShowPass(passes[passes.length-pass_count-1])
            pass_count++;
        }

        //show the back to top button when use scrolls down 2000 pixels
        if ($(this).scrollTop() >= 2000) {
            document.getElementById("top_button").style.display = "block";
        } else {
            document.getElementById("top_button").style.display = "none"
        }
    })

    ShowNextPassInfo();

    //show everything once everything is loaded
    document.getElementById("loading").style.display = "none";
    document.getElementById("next_pass").style.display = "block";
    document.getElementsByClassName("seperator")[0].style.display = "block";
    document.getElementById("main_content").style.display = "block";
    document.getElementById("footer_div").style.display = "block";

});

//copied from stack overflow or something lol
function CountDownTimer(dt, id)
{
    var end = new Date(dt).toLocaleString("en-US", {timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone});
    end = new Date(end);

    var _second = 1000;
    var _minute = _second * 60;
    var _hour = _minute * 60;
    var _day = _hour * 24;
    var timer;

    function showRemaining() {
        var now = new Date();
        var distance = end - now;
        if (distance < 0) {

            clearInterval(timer);
            document.getElementById(id).innerHTML = 'Recording Pass...';
            return;
        }
        var days = Math.floor(distance / _day);
        var hours = Math.floor((distance % _day) / _hour);
        var minutes = Math.floor((distance % _hour) / _minute);
        var seconds = Math.floor((distance % _minute) / _second);

        document.getElementById(id).innerHTML = " Next pass in about " + days + 'days ';
        document.getElementById(id).innerHTML += hours + 'hrs ';
        document.getElementById(id).innerHTML += minutes + 'mins ';
        document.getElementById(id).innerHTML += seconds + 'secs';
    }

    timer = setInterval(showRemaining, 1000);
}

function ShowNextPassInfo() {
    //next pass info
    //read all the passes of the day
    $.getJSON("/weather/scripts/daily_passes.json", function(result) {
        $.each(result, function (i, field) {
            //get the first pass with status INCOMING
            if (field.status == "INCOMING") {
                //start the countdown to the start of the next pass
                var date = new Date(0).setUTCSeconds(field.aos)

                CountDownTimer(date, 'countdown')
                //fill in info about the next pass
                document.getElementById("next_pass_sat").innerHTML = "Satellite: " + field.satellite;
                document.getElementById("next_pass_max_elev").innerHTML = "Max Elevation: " + field.max_elevation + "°";
                document.getElementById("next_pass_frequency").innerHTML = "Frequency: " + field.frequency + " Hz";
                document.getElementById("next_pass_aos").innerHTML = "AOS: " + DateToString(date);
                document.getElementById("next_pass_los").innerHTML = "LOS: " + DateToString(new Date(0).setUTCSeconds(field.los));
                return false;
            }
        })
        //if no passes are incoming (last pass of the day)
        document.getElementById("countdown").innerHTML += "Next pass unavailable";
    })
}

//toggle the visibility of the next pass info
function ToggleNextPassInfo () {
    var button = document.getElementById("next_pass_more_info_button");
    var info = document.getElementById("next_pass_info");
    if (button.value == "More Info") {
        button.value = "Less Info";
        info.style.display = "block"
    } else {
        button.value = "More Info";
        info.style.display = "none"
    }
}

function ScrollToTop() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

function DateToString(date) {
    //reformat the date into a nice string
    const dateTimeFormat = new Intl.DateTimeFormat('en', { year: 'numeric', month: 'long', day: '2-digit', hour: "numeric", minute: "2-digit", second: "2-digit", timeZoneName: "short"}) 
    const [{ value: month },,{ value: day },,{ value: year },,{value: hour},,{value: minute},,{value: second},,{value: dayPeriod},,{value: timeZoneName}] = dateTimeFormat.formatToParts(date)
    dateString = `${month} ${day}, ${year} at ${hour}:${minute}:${second} ${dayPeriod} ${timeZoneName}`
    return dateString
}