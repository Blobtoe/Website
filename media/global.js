var header = `
<div id="menu">
    <ul>
        <li><a name="weather" href="/weather/">Weather</a></li>
        <li><a name="projects" href="/projects/">Projects</a></li>
        <li><a name="home" href="/.">Home</a></li>
    </ul>
    <div id="title">
        <h1> </h1>
    </div>
</div>

<style>
    #menu {
        text-align: center;
        padding: 0;
        margin: 0;

        position: relative;
        height: 200px;
        background-color: #2b2b2b;
    }
    
    #menu ul {
        position: absolute;
        top: 20px;
        right: 20px;
        list-style-type: none;
        overflow: hidden;
        margin: 0;
        padding: 0;
    }

    #menu ul li {
        float: right;
    }

    #menu ul li a {
        color: whitesmoke;
        text-decoration: none;
        display: block;
        text-align: center;
        padding: 10px;
    }

    #menu ul li a:hover {
        color: rgb(161, 161, 161);
    }

    #title {
        padding-top: 70px;
        paddin-bottom: 1em;
    }

    #title h1 {
        font-family: 'Titillium Web', sans-serif;
        color: whitesmoke;
        font-size: 4vw;
        border-bottom: 5px solid red;
        display: inline;
    }
</style>
`

footer = `

<div id="footer">
    <h1>Handcrafted by Felix Perron</h1>
    <div id="line"></div>
    <h2>felixxperron@gmail.com</h2>
</div>

<style>
    #footer {
        width: 100%;
        height: 100px;
        background-color: #2b2b2b;
        text-align: center;
        color: whitesmoke;
    }

    #footer h1 {
        padding-top: 10px;
        margin: 0;
    }

    #line {
        height: 2px;
        background-color: red;
        width: 50%;
        margin: 5px auto;
    }

    #footer h2 {
        margin: 0;
    }
</style>

`

$(document).ready(function () {
    $('#header').prepend(header);
    $('#footer_div').prepend(footer)
});