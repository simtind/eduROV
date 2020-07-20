/**
 * Handles gamepad events
 * If not handle_in_browser it sends the event to the server
 * https://github.com/trolllabs/eduROV
 */

var gamepadIndex;
var gamepadInterval;

var armed_pressed = false;
var light_pressed = false;
var cinema_pressed = false;

var skip_send = true;

var sensitivity = 0.4;

function buttonPressed(b) {
    if (typeof(b) == "object") {
        return b.pressed;
    }
    return b == 1.0;
}

function cartesian2Polar(x, y){
    distance = Math.sqrt(x*x + y*y)
    radians = Math.atan2(y,x) //This takes y first
    polarCoor = { distance:distance, radians:radians }
    return polarCoor
}

function pollGamepad() {
    var gamepads = navigator.getGamepads();
    if (gamepads.length <= gamepadIndex || gamepads[gamepadIndex] == null) {
        return;
    }

    var gamepad = gamepads[gamepadIndex];

    var armedButton = gamepad.buttons[3];
    var lightButton = gamepad.buttons[2];
    var cinemaButton = gamepad.buttons[1];

    var polar = cartesian2Polar(-gamepad.axes[2], -gamepad.axes[3]); 

    polar.distance = Math.min(polar.distance, 1.0);
    if (polar.radians < 0) {
        polar.distance *= -1;
        polar.radians *= -1;
    }

    polar.radians /= Math.PI;

    if (polar.distance >= 0) {
        actuators["port"] = polar.distance * polar.radians;
        actuators["starboard"] = polar.distance * (1 - polar.radians);
    }
    else {
        actuators["port"] = polar.distance * (1 - polar.radians);
        actuators["starboard"] = polar.distance * polar.radians;
    }

    actuators["vertical"] = gamepad.axes[1];

    // Add dead-band so a centered joystick sends 0.
    actuators["port"] = Math.abs(actuators["port"]) < 0.1 ? 0.0 : actuators["port"];
    actuators["starboard"] = Math.abs(actuators["starboard"]) < 0.1 ? 0.0 : actuators["starboard"];
    actuators["vertical"] = Math.abs(actuators["vertical"]) < 0.1 ? 0.0 : actuators["vertical"];

    if (buttonPressed(armedButton) && !armed_pressed) {
        toggle_armed();
    }
    armed_pressed = buttonPressed(armedButton);

    if (buttonPressed(lightButton) && !light_pressed) {
        toggle_light();
    }
    light_pressed = buttonPressed(lightButton);

    if (buttonPressed(cinemaButton) && !cinema_pressed) {
        toggle_cinema();
    }
    cinema_pressed = buttonPressed(cinemaButton);

    postActuators();
}

function gamepadHandler(event, connecting) {
    if (connecting) {
        if (gamepadIndex != null)
        {
            return;
        }
        gamepadIndex = event.gamepad.index;
        console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
            event.gamepad.index, event.gamepad.id,
            event.gamepad.buttons.length, event.gamepad.axes.length);

        gamepadInterval = setInterval(pollGamepad, 100);
    }
    else {
        if (gamepadIndex == event.gamepad.index) {
            console.log("Gamepad disconnected from index %d", gamepadIndex);
            gamepadIndex = null;
            clearInterval(gamepadInterval);
        }
    }
}

window.addEventListener("gamepadconnected", function(e) { gamepadHandler(e, true); }, false);
window.addEventListener("gamepaddisconnected", function(e) { gamepadHandler(e, false); }, false);

