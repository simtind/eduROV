
class IOClient{

    dummyactuators() {
        this.actuators["vertical" ] += Math.random() - 0.5;
        this.actuators["starboard"] += Math.random() - 0.5;
        this.actuators["port"     ] += Math.random() - 0.5;
        this.actuators["lights"   ] += Math.random() - 0.5;

        this.client.send(JSON.stringify(this.actuators));
        console.log("Sent data ", this.actuators)
    }

    OpenHandler(event) {
        console.log("I/O Server Connection made");
        this.client.send("Start");

        setInterval(dummyactuators, 1000);
    }

    MessageHandler(event) {
        try
        {
            console.log('JSON dict from server: ', JSON.parse(event.data));
        }
        catch (e) {
            console.log('Message from server ', event.data);
        }
    }

    CloseHandler(event) {
        console.log("I/O server connection closed");
    }

    Connect(xhttp) {
        // Create WebSocket connection.
        this.client = new WebSocket(xhttp.responseText);
        console.log("Received I/O server url", xhttp.responseText)
    }

    constructor() {
        this.actuators = {
            "vertical"  :0.0,
            "starboard" :0.0,
            "port"      :0.0,
            "lights"    :0.0
        }
    }
}


console.log("Starting I/O server");
var io = new IOClient();

// Get Camera Server address, and start websocket session
var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function(){
    if (xhttp.readyState == 4 && xhttp.status == 200) {
        io.Connect(this);
        io.client.addEventListener('open', function (event) {io.OpenHandler(event);});
        io.client.addEventListener('close', function (event) {io.CloseHandler(event);});
        io.client.addEventListener('message', function (event) {io.MessageHandler(event);});
    }
}
xhttp.open("GET", "?ioserver", true);
xhttp.send();
