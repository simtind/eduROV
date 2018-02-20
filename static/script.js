var last_key;
var pressed_keys = {};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}


document.onkeydown = function(evt) {
    evt = evt || window.event;
    if (evt.keyCode != last_key){
        pressed_keys[evt.keyCode] = 1;
        send_keys(JSON.stringify(pressed_keys))
        last_key = evt.keyCode;
    }
}

document.onkeyup = function(evt) {
    delete pressed_keys[evt.keyCode];
    send_keys(JSON.stringify(pressed_keys))
    last_key = 0;
}

function send_keys(json_string){
    console.log(json_string)
}

function alarm_me(){
    alert("Interval reached");
}

function get_sensor(){
    alert("test");
    console.log('here');
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                console.log(this.responseText);
            }
        };
    xhttp.open("GET", "sensordata.json", true);
    xhttp.send();
}
//var func = get_sensor();
//var intervalID = setInterval("func", 2000);
var intervalID_ = setInterval(function alarm_me(), 2000);

function resizeToMax(id){
    myImage = new Image()
    var img = document.getElementById(id);
    myImage.src = img.src;
    var imgRatio = myImage.width / myImage.height;
    var bodyRatio = document.body.clientWidth / document.body.clientHeight;
    if(bodyRatio < imgRatio){
        img.style.width = "100%";
    } else {
        img.style.height = "100%";
    }
}
