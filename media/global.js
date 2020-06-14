header = `

<div id="menu">
    <ul>
        <li><a name="weather" href="/weather/">Weather</a></li>
        <li><a name="projects" href="/projects/">Projects</a></li>
        <li><a name="home" href="/">Home</a></li>
    </ul>
    <div id="title">
        <h1></h1>
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
        padding-top: 90px;
    }

    #title h1 {
        font-family: 'Titillium Web', sans-serif;
        color: whitesmoke;
        font-size: 60px;
        border-bottom: 5px solid red;
        display: inline;
    }
</style>

`

$(document).ready(function () {
    $('#header').prepend(header);
  });