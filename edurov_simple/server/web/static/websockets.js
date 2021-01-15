
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
    console.log('Message from server ', event.data);
});
ioserver.addEventListener('message', function (event) {
    console.log('Message from server ', event.data);
    console.log('As JSON dict: ', JSON.parse(event.data));
});
