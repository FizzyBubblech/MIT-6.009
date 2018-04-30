"use strict";

// RPC wrapper
function invoke_rpc(method, args, timeout, on_done){
  $("#crash").hide();
  $("#timeout").hide();
  $("#rpc_spinner").show();
  //send RPC with whatever data is appropriate. Display an error message on crash or timeout
  var xhr = new XMLHttpRequest();
  xhr.open("POST", method, true);
  xhr.setRequestHeader('Content-Type','application/json; charset=UTF-8');
  xhr.timeout = timeout;
  xhr.send(JSON.stringify(args));
  xhr.ontimeout = function () {
    $("#timeout").show();
    $("#rpc_spinner").hide();
    $("#crash").hide();
  };
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      $("#rpc_spinner").hide();
      var result = JSON.parse(xhr.responseText)
      $("#timeout").hide();
      if (typeof(on_done) != "undefined"){
        on_done(result);
      }
    } else {
      $("#crash").show();
    }
  }
}

// Resource load wrapper
function load_resource(name, on_done) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", name, true);
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      var result = JSON.parse(xhr.responseText);
      on_done(result);
    }
  }
  xhr.send();
}

// Code that runs first
$(document).ready(function(){
    // race condition if init() does RPC on function not yet registered by restart()!
    //restart();
    //init();
    invoke_rpc( "/restart", {}, 0, function() { init(); } )
});

function restart(){
  invoke_rpc( "/restart", {} )
}

//  LAB CODE

// this is inlined into infra/ui/ui.js

var canvas;
var ctx;
var state;
var board_size;
var board_state;
var xray_state = false;
var board_mask;
var board_params = {0: 5, 1: 10, 2: 15}

var canvas = null;
var context = null;

var width = 300;
var height = 300;

var dug_set = new Set();
var game_over = false;



function init_gui(){
  canvas = document.getElementById('myCanvas');
  context = canvas.getContext('2d');

  canvas.addEventListener('click', function(evt) {
    var mousePos = get_square(canvas, evt);
    if (!xray_state && !game_over && !dug_set.has(mousePos.x + "|" + mousePos.y)) {
      dig_square(mousePos.y, mousePos.x);
      dug_set.add(mousePos.x + "|" + mousePos.y);
    }
  }, false);
}

function handle_game_small_button(){
  // start small game
  init_board(0);
  document.getElementById('gameStateText').innerHTML = "NEW SMALL GAME!";
}

function handle_game_medium_button(){
  // start medium game
  init_board(1);
  document.getElementById('gameStateText').innerHTML = "NEW MEDIUM GAME!";
}

function handle_game_large_button(){
  // start large game
  init_board(2);
  document.getElementById('gameStateText').innerHTML = "NEW LARGE GAME!";
}

function handle_xray_button(){
  if (!game_over) {
    if (!xray_state) {
      document.getElementById('xray_button').innerHTML = "XRAY ON";
      xray_state = true;
    }
    else {
      document.getElementById('xray_button').innerHTML = "XRAY OFF";
      xray_state = false;
    }
    var args = {
      "game": board_state,
      "xray": xray_state,
    };
    invoke_rpc("/ui_render", args, 0, render);  
  }
  
}

function render(result){
  // calculate unit for lattice cell

  context.clearRect(0, 0, width, height);

  var ux = width / board_params[board_size];
  var uy = height / board_params[board_size];
  var cx = board_params[board_size];
  var cy = board_params[board_size];

  
  for (var x = 0; x <= cx; x += 1) {
    context.beginPath();
    context.moveTo(x * ux, 0); 
    context.lineTo(x * ux, width);
    context.strokeStyle = "#000";
    context.lineWidth = 1;
    context.stroke();
    context.closePath();
  }
    
  for (var y = 0; y <= cy; y += 1) {
    context.beginPath();
    context.moveTo(0, y * uy); 
    context.lineTo(height, y * uy);
    context.strokeStyle = "#000";
    context.lineWidth = 1;
    context.stroke();
    context.closePath();
  }
    
  for (var row = 0; row < result.length; row++) {
    for (var col = 0; col < result[row].length; col++) {
      if (result[row][col] == '_') {
        square_style_fill(col, row);
      }
      else if (result[row][col] == '.') {
        square_style_bomb(col, row);
        if (!xray_state) {
          dug_set.add(col + "|" + row);
        }
      }
      else if (result[row][col] == ' ') {
        //empty cell, pass
        if (!xray_state) {
          dug_set.add(col + "|" + row);
        }
      }
      else {
        square_style_text(col, row, result[row][col]);
        if (!xray_state) {
          dug_set.add(col + "|" + row);
        }
      }
    }
  }
}

function render_result_dig(result) {
  board_state = result[0];
  var args = {
    "game": board_state,
    "xray": xray_state,
  };
  invoke_rpc("/ui_render", args, 0, render);

  if (result[1] == "victory") {
    document.getElementById('gameStateText').innerHTML = "YOU WIN - YOU CLEARED THE BOARD!";
    game_over = true;
    var args = {
      "game": board_state,
      "xray": true,
    };
    invoke_rpc("/ui_render", args, 0, render);
  }
  else if (result[1] == "defeat") {
    document.getElementById('gameStateText').innerHTML = "YOU LOSE - YOU DUG A BOMB!";
    game_over = true;
    var args = {
      "game": board_state,
      "xray": true,
    };
    invoke_rpc("/ui_render", args, 0, render);
  }
  else if (result[1] == "ongoing") {
    document.getElementById('gameStateText').innerHTML = "GOOD MOVE - YOU DUG " + result[2] + " SQUARES!";
  }
  else {
    document.getElementById('gameStateText').innerHTML = "ERROR - CHECK YOUR GAME STATUS!";
  }
}

function dig_square(row, col){
  var args = {
    "game": board_state,
    "row": row,
    "col": col
  };
  invoke_rpc("/ui_dig", args, 0, render_result_dig);
}

function render_result_new_game(result){
  board_state = result
  
  var args = {
    "game": board_state,
    "xray": xray_state,
  };
  invoke_rpc("/ui_render", args, 0, render);
}

function init_board(size){
  //board_size:
  //0 = small (5 x 5)
  //1 = medium (10 x 10)
  //2 = large (15 x 15)

  document.getElementById('xray_button').innerHTML = "XRAY OFF";
  xray_state = false;
  game_over = false;
  dug_set.clear();
  
  var num_bombs = board_params[size];
  board_size = size;
  var bomb_list = [];
  
  var bomb_set = new Set();

  for (var i = 0; i < num_bombs; i++) {
    var row = Math.floor(Math.random() * (board_params[board_size]));
    var col = Math.floor(Math.random() * (board_params[board_size]));
    bomb_set.add(row + "|" + col);
  }

  for (var value of bomb_set) {
    var token = value.split("|");
    bomb_list.push([parseInt(token[0]), parseInt(token[1])]);
  }

  var args = {
    "num_rows": board_params[board_size],
    "num_cols": board_params[board_size],
    "bombs": bomb_list
  };
  invoke_rpc("/ui_new_game", args, 0, render_result_new_game);
}

function init(){
  init_board(0);
  init_gui();
}

function get_square(canvas, evt) {
    var rect = canvas.getBoundingClientRect();
    return {
        x: Math.floor((evt.clientX - rect.left) / (width / board_params[board_size])),
        y: Math.floor((evt.clientY - rect.top) / (height / board_params[board_size]))
    };
}

function square_style_fill(x, y){
    context.beginPath();
    context.fillStyle = "gray"
    context.fillRect((x * width / board_params[board_size]) + 2, (y * height / board_params[board_size]) + 2, width / board_params[board_size] - 4, height / board_params[board_size] - 4);
    context.closePath();
}

function square_style_bomb(x, y){
    context.beginPath();
    context.fillStyle = "#FF4081"
    context.arc((x * width / board_params[board_size]) + (width / board_params[board_size] / 2), (y * height / board_params[board_size]) + (height / board_params[board_size] / 2), width / board_params[board_size] / 2 - 4, 0, Math.PI*2, true);
    context.fill()
    context.closePath();
}

function square_style_text(x, y, text){
    context.beginPath();
    context.fillStyle = "#389ce2";
    if (board_size == 0) {
      context.font = "20px Arial";
      context.fillText(text, (x * width / board_params[board_size]) + (width / board_params[board_size] / 2) - 5, (y * height / board_params[board_size]) + (height / board_params[board_size] / 2) + 5);
    }
    else if (board_size == 1) {
      context.font = "15px Arial";
      context.fillText(text, (x * width / board_params[board_size]) + (width / board_params[board_size] / 2) - 5, (y * height / board_params[board_size]) + (height / board_params[board_size] / 2) + 5);
    }
    else {
      context.font = "10px Arial";
      context.fillText(text, (x * width / board_params[board_size]) + (width / board_params[board_size] / 2) - 2.5, (y * height / board_params[board_size]) + (height / board_params[board_size] / 2) + 2.5);
    }
    context.fill()
    context.closePath();
}





