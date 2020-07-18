/**
 * Handles keydown and keyup events
 * https://github.com/trolllabs/eduROV
 */

var last_key;

document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.keyCode != last_key){
        last_key = evt.keyCode;
        send_keydown(evt.keyCode);
    }
}

document.onkeyup = function(evt) {
    last_key = 0;
    send_keyup(evt.keyCode);
}

function send_keydown(keycode){
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/keydown" true);
    xhttp.setRequestHeader("Content-Type", "text/html");
    xhttp.send(str(keycode));
}

function send_keyup(keycode){
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/keyup", true);
    xhttp.setRequestHeader("Content-Type", "text/html");
    xhttp.send(str(keycode));
}
