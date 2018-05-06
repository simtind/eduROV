var up = 38;
var down = 40;
var right = 39;
var left = 37;
var key_status = {up: 0, down: 0, right: 0, left:0}

var horizontal_move = 0;
var vertical_move = 0;

var update_interval = 500;
var perceived_delay = 800;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function update_var_with_delay(variable, amount, delay){
    await sleep(delay);
    variable += amount;
}

var x = setInterval(function() {
    if (key_status[left]){
        horizontal_move += 1;
        update_var_with_delay(horizontal_move, -1, perceived_delay);
    } else if (key_status[right]){
        horizontal_move -= 1;
        update_var_with_delay(horizontal_move, +1, perceived_delay);
    }
    console.log(horizontal_move);
}, update_interval);
