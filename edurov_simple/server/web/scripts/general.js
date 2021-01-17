/**
 * Handles sensor values and some simple GUI updates
 * https://github.com/trolllabs/eduROV
 */

var keycodes = {l:76, c:67, esc:27, enter:13, w:87, a:65, s:83, d:68, q:81, e:69};
var MOTOR_KEYS = [81, 87, 69, 65, 83, 68];
var stat = {armed:false, roll_ui:true, cinema:false,
            video_rotation:0};
var sensors = {time:0, temp:0, pressure:0, humidity:0, pitch:0, roll:0, yaw:0,
            tempWater:0, pressureWater:0, batteryVoltage:0, free_space:0,
            cpu_temp:0};
var critical = {voltage:10.0, disk_space:500.0, cpu_temp:80.0};

var actuators = {vertical:0.0, port:0.0, starboard:0.0, lights:0.0}

var sensor_interval = 500;
var interval;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function postActuators() {
    if (typeof postActuators.previous_message == "undefined" ) {
        postActuators.previous_message = "";
    }

   if (!stat.armed) {
        actuators["port"] = 0.0;
        actuators["starboard"] = 0.0;
        actuators["vertical"] = 0.0;
    }

    message = JSON.stringify(actuators);
    if (message == postActuators.previous_message) {
        return;
    }

    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "/actuator.json", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(message);

    postActuators.previous_message = message;
}

function toggle_cinema(){
    stat.cinema = !stat.cinema;
    set_cinema(stat.cinema);
}

function toggle_light(should_post_actuators=false){
    var btn = document.getElementById("lightBtn");
    if(actuators['lights'] == 1.0){
        btn.className = btn.className.replace(" active", "");
    }else{
        btn.className += " active";
    }
    actuators['lights'] = actuators['lights'] == 1.0 ? 0.0 : 1.0;

    if (should_post_actuators) {
        postActuators();
    }
}

function toggle_armed(){
    var btn = document.getElementById("armBtn");
    if(stat.armed){
        btn.className = btn.className.replace(" active", "");
    }else{
        btn.className += " active";
    }
    stat.armed = !stat.armed;
    refresh_ui();
}

function set_update_frequency(){
    var interval = prompt("Set sensor update interval in ms",sensor_interval);
    if (interval){
        if (interval<30){
            alert('Sensor frequency can not be less than 30 ms');
            interval = 30;
        }
        sensor_interval = interval;
    }
}

function toggle_roll(){
    var btn = document.getElementById("rollBtn");
    if(stat.roll_ui){
        document.getElementById("rollOverlay").style.visibility = "hidden";
        btn.className = btn.className.replace(" active", "");
    }else{
        document.getElementById("rollOverlay").style.visibility = "visible";
        btn.className += " active";
    }
    stat.roll_ui = !stat.roll_ui;
}

function stop_rov(){
    var xhttp = new XMLHttpRequest();
    xhttp.open("POST", "stop", true);
    xhttp.setRequestHeader("Content-Type", "application/text");
    xhttp.send();
}

function rotate_image(){
    stat.video_rotation += 180;
    rotation = stat.video_rotation;
    document.getElementById("image").style.transform =
        `rotate(${rotation}deg)`;
}

function get_sensor(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var response = JSON.parse(this.responseText);
            for (var key in response) {
                sensors[key] = response[key];
            }
            refresh_ui();
        }
    };
    xhttp.open("GET", "sensor.json", true);
    xhttp.send();

    // Reset interval
    interval = setInterval(function () {
        clearInterval(interval);
        get_sensor();
    }, sensor_interval);
}

function refresh_ui(){
    var roll_val = sensors.roll
    document.getElementById("rollOverlay").style.transform =
        `rotate(${roll_val}deg)`;

    for (var key in sensors){
        var element = document.getElementById(key);
        if (element){
            var val = sensors[key];
            if (isNaN(val)){
                element.innerHTML = val;
            } else{
                element.innerHTML = val.toFixed(1);
            }
        }
    }

    // Check critical system values
    var voltElem = document.getElementById("voltageTr");
    var diskElem = document.getElementById("diskTr");
    var cpuElem = document.getElementById("cpuTr");
    if (sensors.batteryVoltage < critical.voltage){
        voltElem.className = " table-danger";
    } else{
        voltElem.className = voltElem.className.replace(" table-danger", "");
    }
    if (sensors.free_space < critical.disk_space){
        diskElem.className = " table-danger";
    } else{
        diskElem.className = diskElem.className.replace(" table-danger", "");
    }
    if (sensors.cpu_temp > critical.cpu_temp){
        cpuElem.className = " table-danger";
    } else{
        cpuElem.className = cpuElem.className.replace(" table-danger", "");
    }
}

get_sensor();