class CameraClient {
    LoadFrame(image){
        try
        {
            const tempframe = this.frame;
            this.frame = URL.createObjectURL(image);
            this.image.src = this.frame;
            if (tempframe){
                URL.revokeObjectURL(tempframe);
            }
        }
        catch (e) {
            console.log('Error while loading video frame', e);
        }
    }

    OpenHandler(event) {
        console.log("Camera server connection made");
        if (!this.image) {
            this.image = document.getElementById("image");
            this.image.style.display = "none";
        }
        this.client.send("Start");
    }

    CloseHandler(event) {
        console.log("Camera server connection closed");
        if (this.image){
            this.image.style.display = "none";
        }
    }

    MessageHandler(event) {
        this.LoadFrame(event.data);
        if (this.image.style.display == "none") {
            this.image.style.display = "block";
        }
    }

    Connect(xhttp) {
        // Create WebSocket connection.
        this.client = new WebSocket(xhttp.responseText);
        console.log("Received camera server url", xhttp.responseText);
    }

    constructor() {
        this.frame = null;
        this.image = null;
    }

}

console.log("Starting camera server");
var camera = new CameraClient();

// Get Camera Server address, and start websocket session
var xhttp = new XMLHttpRequest();
xhttp.onreadystatechange = function(){
    if (xhttp.readyState == 4 && xhttp.status == 200) {
        camera.Connect(this);
        camera.client.addEventListener('open', function (event) {camera.OpenHandler(event);});
        camera.client.addEventListener('close', function (event) {camera.CloseHandler(event);});
        camera.client.addEventListener('message', function (event) {camera.MessageHandler(event);});
    }
}
xhttp.open("GET", "?cameraserver", true);
xhttp.send();
