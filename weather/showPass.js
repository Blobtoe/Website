//add and show a pass to the website from its json file path
function ShowPass(path) {
    $.ajaxSetup({
        async: false
    });

    //create clone of template
    var clone = document.getElementById("pass_template").cloneNode(true);
    document.getElementById("main_content").innerHTML = document.getElementById("main_content").innerHTML + clone.innerHTML;

    //get the clone in the document html (last div with id=pass)
    var pass = document.getElementsByClassName("pass")[document.getElementsByClassName("pass").length - 1]

    $.getJSON(path, function(result) {
        var date = new Date(0).setUTCSeconds(result.aos)

        //get date difference between now and the time of the pass
        var delta_time = Math.round(Date.now()/1000 - new Date(date).getTime()/1000);
        var delta_days = Math.floor(delta_time/86400)
        var delta_hours = Math.floor((delta_time-delta_days*86400)/3600)
        var delta_mins = Math.floor(((delta_time-delta_days*86400)-delta_hours*3600)/60)

        //show the delta in a nice string
        if (delta_days != 0) {
            pass.getElementsByClassName("delta_time")[0].innerHTML += delta_days + " day" + (delta_days === 1 ? "" : "s")
            if (delta_hours != 0) {
                pass.getElementsByClassName("delta_time")[0].innerHTML += ", "
            }
        }
        if (delta_hours != 0) {
            pass.getElementsByClassName("delta_time")[0].innerHTML += delta_hours + " hour" + (delta_hours === 1 ? "" : "s")
            if (delta_mins != 0) {
                pass.getElementsByClassName("delta_time")[0].innerHTML += " and "
            }
        }
        if (delta_mins != 0) {
            pass.getElementsByClassName("delta_time")[0].innerHTML += delta_mins + " minute" + (delta_mins === 1 ? "" : "s")
        }
        pass.getElementsByClassName("delta_time")[0].innerHTML += " ago."

        //add the name the title of the pass
        pass.getElementsByClassName("pass_title")[0].innerHTML = DateToString(date);
        pass.getElementsByClassName("main_image")[0].setAttribute("src", result.main_image);
        pass.getElementsByClassName("main_image_link")[0].setAttribute("href", result.main_image);
        

        //loop only show the div that matched the satellite's type
        var pass_info = pass.getElementsByClassName("pass_info")[0]
        for (var j = 0; j < pass_info.children.length; j++) {
            if (pass_info.children[j].getAttribute("class") == result.type) {
                //add general information
                pass_info.children[j].getElementsByClassName("sat")[0].innerHTML = "Satellite: " + result.satellite;
                pass_info.children[j].getElementsByClassName("max_elev")[0].innerHTML = "Max elevation: " + result.max_elevation + "°";
                pass_info.children[j].getElementsByClassName("frequency")[0].innerHTML = "Frequency: " + result.frequency + " Hz";
                pass_info.children[j].getElementsByClassName("sun_elev")[0].innerHTML = "Sun Elevation: " + result["sun_elev"] + "°"; 
            
                //add all the links
                for (var key in result.links) {
                    if (result.links[key] == result.main_image) {
                        pass.getElementsByClassName("description")[0].innerHTML = document.getElementsByClassName(key)[0].innerHTML;
                    }

                    pass.getElementsByClassName(key)[0].setAttribute("href", result.links[key])
                    pass.getElementsByClassName(key)[0].style.display = "inline";
                }
            } else {
                //hide divs of different types
                pass_info.children[j].style.display = "none";
            }
            
        }
    });

    $.ajaxSetup({
        async: true
    });
}