/**
 * Handles gamepad events
 * If not handle_in_browser it sends the event to the server
 * https://github.com/trolllabs/eduROV
 */

var keycodes = {w:87, a:65, s:83, d:68, q:81, e:69};

var gamepadIndex;
var gamepadInterval;

var elevationState = "idle";
var planeMovementState = "idle";

var armed_pressed = false;
var light_pressed = false;
var cinema_pressed = false;

var skip_send = false;

var sensitivity = 0.4;

function buttonPressed(b) {
    if (typeof(b) == "object") {
        return b.pressed;
    }
    return b == 1.0;
}

function send_keydown(keycode){
    if (skip_send) {
        console.log("Key " + keycode + " down.");
        return;
    }

    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/keydown="+keycode, true);
    xhttp.setRequestHeader("Content-Type", "text/html");
    xhttp.send(null);
}

function send_keyup(keycode){
    if (skip_send) {
        console.log("Key " + keycode + " up.");
        return;
    }

    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/keyup="+keycode, true);
    xhttp.setRequestHeader("Content-Type", "text/html");
    xhttp.send(null);
}

function clearPlaneMovementState() {
    if (planeMovementState == "forward") {
        send_keyup(keycodes.q);
        send_keyup(keycodes.e);
    }
    else if (planeMovementState == "back") {
        send_keyup(keycodes.a);
        send_keyup(keycodes.d);
    }
    else if (planeMovementState == "right") {
        send_keyup(keycodes.q);
        send_keyup(keycodes.d);
    }
    else if (planeMovementState == "left") {
        send_keyup(keycodes.e);
        send_keyup(keycodes.a);
    }

    console.log("Clearing state " + planeMovementState);

    planeMovementState = "idle";
}

function setPlaneMovementState(target_state) {
    if (planeMovementState != target_state)
    {
        clearPlaneMovementState();

        console.log("Set state " + target_state);

        if (target_state == "forward") {
            send_keydown(keycodes.q);
            send_keydown(keycodes.e);
        }
        else if (target_state == "back") {
            send_keydown(keycodes.a);
            send_keydown(keycodes.d);
        }
        else if (target_state == "right") {
            send_keydown(keycodes.q);
            send_keydown(keycodes.d);
        }
        else if (target_state == "left") {
            send_keydown(keycodes.e);
            send_keydown(keycodes.a);
        }
    }

    planeMovementState = target_state;
}

function pollGamepad() {
    var gamepads = navigator.getGamepads();
    if (gamepads.length == 0) {
        return;
    }

    var gamepad = gamepads[0];
    var elevationAxis = gamepad.axes[1]
    var leftRightAxis = gamepad.axes[2]
    var forwardBackAxis = gamepad.axes[3]

    var armedButton = gamepad.buttons[3]
    var lightButton = gamepad.buttons[2]
    var cinemaButton = gamepad.buttons[1]

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

    if (elevationAxis > sensitivity) {
        // Going up

        // Meaning, we're no longer going down
        if (elevationState == "down") {
            send_keyup(keycodes.s);
        }

        // And we should start going up if we weren't
        if (elevationState != "up") {
            send_keydown(keycodes.w);
        }

        elevationState = "up";
    }
    else if (elevationAxis < -sensitivity) {
        // Going down

        // Meaning, we're no longer going up
        if (elevationState == "up") {
            send_keyup(keycodes.w);
        }

        // And we should start going down if we weren't
        if (elevationState != "down") {
            send_keydown(keycodes.s);
        }

        elevationState = "down";
    }

    if (forwardBackAxis > sensitivity) {
        setPlaneMovementState("back");
    }
    else if (forwardBackAxis < -sensitivity) {
        setPlaneMovementState("forward");
    }
    else if (leftRightAxis > sensitivity) {
        setPlaneMovementState("right");
    }
    else if (leftRightAxis < -sensitivity) {
        setPlaneMovementState("left");
    }
    else {
        setPlaneMovementState("idle");
    }
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

