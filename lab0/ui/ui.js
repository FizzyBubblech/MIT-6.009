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
var img;
var state;
var width = 1;
var height = 1;
var step = 5;

var lock = false;
var draw = null;

var polygon_cache = [];
var polygon_counter = 0;
var rectangle_cache = [];
var rectangle_counter = 0;
var line_cache = [];
var line_counter = 0;


//$(document).ready(function(){ init();});

function has(set, member) {
  for (var i in set){
    if (set[i] == member){
      return true;
    }
  }
  return false;
}

function post_process(loaded){
  for (var i in loaded) {
        $("#initial_states").append(
        "<li class=\"mdl-menu__item\" onclick=\"handle_state_select('" +
        loaded[i] +
        "')\">" +
        loaded[i] +
        "</li>")
      }
      handle_state_select(loaded[0]);
}

function draw_rect(){
  if (rectangle_cache.length < (rectangle_counter+1)) {
    rectangle_cache.push(draw.rect(1,1));
  }
  rectangle_counter ++;
  var r = rectangle_cache[rectangle_counter-1];
  r.show();
  return r;
}

function draw_polygon(){
  if (polygon_cache.length < (polygon_counter+1)) {
    polygon_cache.push(draw.polygon());
  }
  polygon_counter ++;
  var p =  polygon_cache[polygon_counter-1];
  p.show();
  return p;
}

function draw_line(x0, y0, x1, y1){
  if (line_cache.length < (line_counter+1)) {
    line_cache.push(draw.line(0,0,1,1));
  }
  line_counter ++;
  var l = line_cache[line_counter-1];
  l.plot(x0,y0, x1,y1);
  l.show();
  return l;
}

function clear_primitives(){
  polygon_counter = 0;
  rectangle_counter = 0;
  line_counter = 0;
}

function render_primitives(){
  // hide the remaining primitives
  while (polygon_counter < polygon_cache.length){
    polygon_cache[polygon_counter].hide();
    polygon_counter++;
  }
  while (rectangle_counter < rectangle_cache.length){
    rectangle_cache[rectangle_counter].hide();
    rectangle_counter++;
  }
  while (line_counter < line_cache.length){
    line_cache[line_counter].hide();
    line_counter++;
  }
}

function init_gui(){
  draw = SVG('drawing');
  draw.viewbox(0, 0, 100, 100);
  draw.height = draw.width*height/width;

  SVG.on(window, 'resize', function() { draw.spof() });
  var last_value = null;

  invoke_rpc("/ls", {"path":"resources/gasses/"}, 0, post_process);

  $("#pause_simulation").hide();
}

function handle_state_select(value){
  // load state

  var resource_loaded = function( gas ){
    state = gas.state;
    width = gas.width;
    height = gas.height;
    $("#current_state").text(value + ", a " + width + "x" + height + " square lattice gas");
    render();
  };

  load_resource("/resources/gasses/"+value, resource_loaded);

  cycle = 0;
  prev_cycle = -1;
  prev_time = 0;
}

function handle_simulate_button(){
  // start simulation
  if(!lock){
    // show / hide GUI elements
    $("#pause_simulation").show();
    $("#run_simulation").hide();
    $("#step_simulation").hide();
    // flag update sequence to run
    lock = true;
  }
}

function handle_step_button(){
  simulate_step();
}

function handle_pause_button(){
  if(lock){
    // show / hide GUI elements
    $("#pause_simulation").hide();
    $("#run_simulation").show();
    $("#step_simulation").show();

    // flag update sequence to stop
    lock = false;
  }
}

function set_cell(x, y, up, down, right, left, wall, ux, uy){
  if (wall){
    draw_rect().size(0.9*ux,0.9*uy).center((x+0.5)*ux,(y+0.5)*uy).fill("#888").opacity(0.5);
  }

  if (up){
    //draw.rect(0.2*ux,0.2*uy).center((x+0.5)*ux,(y+0.8)*uy).fill("#F00");
    draw_polygon().
      plot([[0.333*ux,0.4*uy], [0.666*ux,0.4*uy], [0.5*ux, 0.1*uy]]).
      center((x+0.5)*ux,(y+0.666)*uy).
      fill("#F00");
  }

  if (down){
    //draw.rect(0.2*ux,0.2*uy).center((x+0.5)*ux,(y+0.2)*uy).fill("#F00");
    draw_polygon().
      plot([[0.333*ux,-0.4*uy], [0.666*ux,-0.4*uy], [0.5*ux, -0.1*uy]]).
      center((x+0.5)*ux,(y+0.333)*uy).
      fill("#F00");
  }

  if (right){
    //draw.rect(0.2*ux,0.2*uy).center((x+0.2)*ux,(y+0.5)*uy).fill("#F00");
    draw_polygon().
      plot([[-0.4*ux,0.333*uy], [-0.4*ux,0.666*uy], [-0.1*ux, 0.5*uy]]).
      center((x+0.333)*ux,(y+0.5)*uy).
      fill("#F00");
  }

  if (left){
    //draw.rect(0.2*ux,0.2*uy).center((x+0.8)*ux,(y+0.5)*uy).fill("#F00");
    draw_polygon().
      plot([[0.4*ux,0.333*uy], [0.4*ux,0.666*uy], [0.1*ux, 0.5*uy]]).
      center((x+0.666)*ux,(y+0.5)*uy).
      fill("#F00");
  }
}

function set_window(x, y, d, v, h, wall, ux, uy){
  // draw wall
  if (wall){
    draw_rect().size(0.9*ux,0.9*uy).center((x+0.5)*ux,(y+0.5)*uy).fill("#888").opacity(0.5);
  }

  // draw density
  draw_rect().size(0.9*ux,0.9*uy).opacity(d*d).center((x+0.5)*ux,(y+0.5)*uy).fill("#F00");
  //draw.rect(0.9*ux,0.9*uy).opacity(0.5*d).center((x+0.5)*ux,(y+0.5)*uy).fill("#F00");
  //draw.ellipse(2*d*ux,2*d*uy).opacity(0.5*d).center((x+0.5)*ux,(y+0.5)*uy).fill("#F00");

  // draw dimension vector
  draw_line().plot((x+0.5)*ux,(y+0.5)*uy, (x+0.5+h)*ux,(y+0.5-v)*uy).stroke({ width: 0.5, color: '#00F' })
}

function render(){
  // break into cells, compute direction vectors
  // plot magnitude and direction as RGB
  if ((width <1) || (height <1)) {
    alert("bad dimensions");
    return;
  }

  clear_primitives();

  // calculate unit for lattice cell
  var vector = false;
  var sx = 1;
  var sy = 1;
  var ux = 100 / width;
  var uy = 100 / height;
  var cx = width;
  var cy = height;
  if ((width > 16) || (height > 16)){
    vector = true;
    sx = ~~(width / 16);
    sy = ~~(height / 16);
    ux = ~~(100 / 16);
    uy = ~~(100 / 16);
    cx = 16;
    cy = 16;
  }

  // draw grid
  for (var x=1; x<cx; x++){
    draw_line(x*ux,0, x*ux,100).stroke({ width: 0.1, color: '#AAA' });
  }

  for (var y=1; y<cy; y++){
    draw_line(0,y*uy, 100,y*uy).stroke({ width: 0.1, color: '#AAA' });
  }



  if (vector){
    // draw lattice windows
    for (var x=0; x<16; x++){
      for (var y=0; y<16; y++){
        var d = 0.0;
        var v = 0.0;
        var h = 0.0;
        var wall = false;
        // compute window density and direction
        for (var i=0; i<sx; i++){
          for (var j=0; j<sy; j++){
            s = state[sx*x+i+(sy*y+j)*width];

            up = has(s,"u");
            down = has(s,"d");
            right = has(s,"r");
            left = has(s,"l");

            v += up ? 1 : 0;
            v += down ? -1 : 0;
            h += right ? 1 : 0;
            h += left ? -1 : 0;

            d += up ? 1 : 0;
            d += down ? 1 : 0;
            d += right ? 1 : 0;
            d += left ? 1 : 0;

            wall |= has(s,"w");
          }
        }

        // normalize
        d = Math.min(1.0, d/(4*sx*sy));
        h = h/(sx*sy);
        v = v/(sx*sy);

        set_window(x, y, d, v, h, wall, ux, uy);
      }
    }
  } else {
    // draw lattice cells
    for (var x=0; x<width; x++){
      for (var y=0; y<height; y++){
        var s = state[x+y*width];

        var up = has(s,"u");
        var down = has(s,"d");
        var right = has(s,"r");
        var left = has(s,"l");
        var wall = has(s,"w");

        set_cell(x, y, up, down, right, left, wall, ux, uy);
      }
    }
  }

  render_primitives();
}

function init_simulation(){
  state = new Array(width*height);
  // NOTE: what the what was that re/ float v and h members?
}

function simulate_step_help(result){
  width = result.width
  height = result.height
  state = result.state

  cycle = cycle + 1;

  render();
}

function simulate_step(){
  var args = { "gas": {
                        "width": width,
                        "height": height,
                        "state": state
                        }
                      };
  invoke_rpc("/next", args, 0, simulate_step_help)

}

var cycle = 0;
var prev_cycle = -1;
var prev_time = 0;

function init(){
  init_simulation();
  init_gui();

  var step_function = function(){
    if(lock){
      //if ((cycle > prev_cycle) && (Date.now() - prev_time > 50)){
      if (cycle > prev_cycle){
        // remember when this frame occurred
        prev_cycle = cycle;
        prev_time = Date.now();

        // perform one step of the simulation
        simulate_step();
        render();
      }
    }

    // Repeat
    setTimeout(step_function, step);
  }

  step_function();
}







