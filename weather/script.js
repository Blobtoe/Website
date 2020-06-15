var pass = `
<div class="pass">
    <div id="another_div">
        <h1 id="pass_title">Date and Time</h1>
        <div id="container">
            <div id="main_image">
                <img src="../weather/images/06-14-2020_21-25/NOAA1520200614-195709.a.png" alt="" srcset="">
            </div>
            <div id="side_links">
                <ul>
                    <li><a href="">img1</a></li>
                    <li><a href="">img2</a></li>
                    <li><a href="">img3</a></li>
                    <li><a href="">img4</a></li>
                </ul>
            </div>
        </div>
    </div>
</div>

<style>

    #container {
        display: inline-flex;
        padding: 10px;
        height: 30em;
        margin-top: 20px;
    }

    #pass_title {
        font-size: 50px;
        padding: 0;
        margin: 0;
        margin-left: 20px;
    }

    #main_image {
        margin-right: 25px;
    }

    #main_image img {
        height: 30em;
        float: left;
    }

    #side_links {

    }

    #side_links ul {
        list-style-type: none;
        padding: 0;
    }

    #side_links ul li {
        padding-top: 2em;
    }

    #side_links ul li a {
        font-size: 40px;
        text-decoration: none;
        color: black;
    }
</style>

`

$(document).ready(function () {
    $("#main_content").prepend(pass);
});