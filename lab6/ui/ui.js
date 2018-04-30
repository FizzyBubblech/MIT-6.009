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

var init = function() {
    // Register autocompletion handler for search bar
    $( "#autocomplete" ).autocomplete({
       source: function (request, callback) {
            invoke_rpc("/autocomplete", {prefix: request.term, N: 5}, 1000, callback);
        }
    });

    var editor = CodeMirror.fromTextArea(document.getElementById("s04_editor"), {
      lineNumbers: false,
      extraKeys: {"Ctrl-Space": function(cm) {
        CodeMirror.showHint(cm, CodeMirror.hint.ajax, { async: true });
      }}
    });

    //editor.on("keyup", function(cm, event) {
    //  CodeMirror.showHint(cm, CodeMirror.hint.ajax, { async: true });
    //});

    CodeMirror.registerHelper(
        "hint", "ajax",
        function (mirror, callback, options) {
            var cur = mirror.getCursor();
            var tok = mirror.getTokenAt(cur);
            var matches = tok.string.match(/[^A-Za-z]/igm);
            if (matches){
              var index = tok.string.lastIndexOf(matches[matches.length-1]);
              tok.start = index+1;
              tok.string = tok.string.substring(tok.start, tok.string.length);
            }
            //invoke_rpc(method, args, timeout, on_done)
            var hint_handler = function(result) {
              callback({ list: result || [],
                         from: CodeMirror.Pos(cur.line, tok.start),
                         to: CodeMirror.Pos(cur.line, tok.end)
                       });
            };
            invoke_rpc("/autocorrect", { prefix: tok.string, N: 5 }, 1000, hint_handler);
        });

    CodeMirror.registerHelper(
      "hint", "auto",
      function (mirror, options) {
        CodeMirror.commands.autocomplete(mirror, CodeMirror.hint.ajax, { async: true })
      });
};

