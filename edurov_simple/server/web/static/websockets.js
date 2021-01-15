
console.log("Test websockets")

// Create WebSocket connection.
const ioserver = new WebSocket('ws://localhost:8081');


console.log("Element made")

// Connection opened
ioserver.addEventListener('open', function (event) {

    console.log("Connection made")

    ioserver.send('Hello Server!');
});

// Listen for messages
ioserver.addEventListener('message', function (event) {
    try
    {
        console.log('JSON dict from server: ', JSON.parse(event.data));
    }
    catch (e) {
        console.log('Message from server ', event.data);
    }
});

actuators = {
    "vertical"  :0.0,
    "starboard" :0.0,
    "port"      :0.0,
    "lights"    :0.0
}

function dummyactuators() {
    actuators["vertical" ] += Math.random() - 0.5;
    actuators["starboard"] += Math.random() - 0.5;
    actuators["port"     ] += Math.random() - 0.5;
    actuators["lights"   ] += Math.random() - 0.5;

    ioserver.send(JSON.stringify(actuators));
    console.log("Sent data ", actuators)
}

setInterval(dummyactuators, 1000);
