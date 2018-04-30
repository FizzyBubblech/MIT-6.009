"use strict";
``
// RPC wrapper
function invoke_rpc(method, args, timeout, on_done) {
  $("#crash").hide();
  $("#timeout").hide();
  $("#rpc_spinner").show();
  $('#rpc_status').css({
    visibility: 'visible',
  })
  //send RPC with whatever data is appropriate. Display an error message on crash or timeout
  var xhr = new XMLHttpRequest();
  xhr.open("POST", method, true);
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.timeout = timeout;
  xhr.send(JSON.stringify(args));
  xhr.ontimeout = function () {
    $("#timeout").show();
    $("#rpc_spinner").hide();
    $("#crash").hide();
  };
  xhr.onloadend = function () {
    if (xhr.status === 200) {
      $("#rpc_spinner").hide();
      var result = JSON.parse(xhr.responseText)
      $("#timeout").hide();
      if (typeof (on_done) != "undefined") {
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
  xhr.onloadend = function () {
    if (xhr.status === 200) {
      var result = JSON.parse(xhr.responseText);
      on_done(result);
    }
  }
  xhr.send();
}

// Code that runs first
$(document).ready(function () {
  invoke_rpc("/restart", {}, 0, function () { init(); })
});

function restart() {
  invoke_rpc("/restart", {})
}

//  LAB CODE

// this is inlined into infra/ui/ui.js
var InfoDisplay = function () {
  var that = Object.create(InfoDisplay.prototype);
  var clickedStudent;

  var updateButtonLabels = function(studentName) {
    if (studentName) {
      $('#cliques-for').removeClass('bad').val(studentName);
      $('#is-for').removeClass('bad').val(studentName);
    } else {
      $('#cliques-for').val('');
      $('#is-for').val('');
    }
  }

  that.hoverIn = function (studentName) {
    var student = students[studentName];
    $('.info #name').html(student.getName()).css({
      visibility: 'visible'
    });
    var interests = student.getInterests();
    $('.info #interests')
      .html(getArrAsString(interests))
      .css({
        visibility: 'visible'
      });
  };

  that.hoverOut = function () {
    if (clickedStudent) {
      that.hoverIn(clickedStudent.getName());
    }
  };

  that.unClickStudent = function(studentName) {
    if (studentName){
      var student = students[studentName];
      
      if (clickedStudent === student) {
        // click again to cancel
        clickedStudent = null;
      }
    }
  }

  that.clickStudent = function (studentName) {
    var student = students[studentName];
    $('.clicked').attr('class', 'node');
    if (clickedStudent === student) {
      // click again to cancel
      that.unClickStudent(studentName);
      studentName = '';
    } else {
      clickedStudent = student;
      $('.node:contains("'+studentName+'")').filter(function() {
        return $(this).find('title').text() == studentName;
      }).attr("class", "node clicked");; 
    }
    updateButtonLabels(studentName);
  };

  that.getClickedStudentName = function() {
    if (clickedStudent) {
      return clickedStudent.getName();
    }
  }

  that.selectClickedStudent = function() {
    if (clickedStudent) {
      $('.node:contains("'+clickedStudent.getName()+'")').attr("class", "node clicked");;
    }
  }

  that.reset = function () {
    $('.clicked').removeClass('clicked');
    clickedStudent = null;
    resetDisplays();
  };

  var resetDisplays = function () {
    $('.info #name').html('Placeholder').css({
      visibility: 'hidden'
    });
    $('.info #interests').html('Placeholder').css({
      visibility: 'hidden'
    });
    
    updateButtonLabels();
  };

  Object.freeze(that);
  return that;
};

var getArrAsString = function(arr) {
  return arr.map(function(item, i) {
    return (i !== 0 ? ' ':'') + item;
  }).join();
}

var Student = function (name, interests) {
  var that = Object.create(Student.prototype);
  that.getName = function () {
    return name;
  };

  that.getInterests = function () {
    return interests.slice();
  };
  
  Object.freeze(that);
  return that;
};

var cleanup = function (students, rooms) {
  $('#graph').html('');
  $('.list').html('');
  $('.students-in-item').html('');
  infoDisplay.reset();

};

var setCase = function (testName) {
  $("#case").html(testName);
  selectedSchool = testName;
}

var friendshipsToGraph = function(friendships) {
  var graph = {
    "nodes": [],
    "links": []
  }
  var students = Object.keys(friendships);
  students.forEach(function(student) {
    graph.nodes.push({
      "name": student,
      "value": student,
      "group": 1
    });
    friendships[student].forEach(function(friend) {
      // We know that the student came from the students list,
      // and it is unique, so it will have a proper index
      graph.links.push({
        "source": students.indexOf(student),
        "target": students.indexOf(friend),
        "value": 1,
        "edge_color": "#999"
      });
    });
  });

  return graph;
}

var save = function (text, name) {
  name = name + '.json';
  var a = document.createElement("a");
  var file = new Blob([text], { type: 'text/plain' });
  a.href = URL.createObjectURL(file);
  a.download = name;
  a.click();
}

var setupImmybox = function(elt) {
  var student_choices = [];
  for (var studentName in students) {
    student_choices.push({text: studentName, value: studentName});
  }
  elt.immybox();
  elt.immybox('setChoices', student_choices);
}

var setGraphFromFriendships = function(friendships) {
  var graph = friendshipsToGraph(friendships);
  window.graph = graph;
  drawForce(graph);
}

var setup = function (testCaseName) {
  $('.loader').show();
  cleanup();

  invoke_rpc("/ui_setup_school", testCaseName, 0, function(friendships) {
    // If successful, make this list of student info
    students = {};
    schools[testCaseName].forEach(function(studentInfo) {
      var name = studentInfo[0];
      var interests = studentInfo.slice(1);
      students[name] = Student(name, interests);
    });

    setGraphFromFriendships(friendships);
      
    setupImmybox($('#cliques-for'));
    setupImmybox($('#is-for'));
    $('.loader').hide();    
  });
}

var updateStudentsInList = function(students) {
  $('.students-in-item').html(getArrAsString(students));
}

var updateList = function(studentName, listOfThings) {
  var list = $('.list');
  list.html('');
  listOfThings.forEach(function (thing, i) {
    var item = $('<button class="mdl-button mdl-js-button mdl-button--raised mdl-js-ripple-effect btn item">'+i+'</button>');
    item.click(function() {
      updateGraphAndList(studentName, thing);
    });
    list.append(item);
  });
 
};

var updateGraphAndList = function(studentName, clique) {
  updateStudentsInList(clique);
  updateGraph(studentName, clique, true);
};

var schools;
var selectedSchool;
var students = {};

var infoDisplay = InfoDisplay();

var init = function () {
  var setUpSchoolInfo = function (data) {
    // data is 
    var schoolNames = Object.keys(data);
    schools = data
    schoolNames.forEach(function(name) {
      $("#cases").append($("<li class=\"mdl-menu__item\" onclick=\"setCase('" + name + "')\">" + name + "</li>"));
    });
    // also sets the selected school to that school
    setCase(schoolNames[0]);
    setup(selectedSchool);
    $('.loader').hide();
  };
  init_gui();
  $('.loader').show();
  invoke_rpc("/load_data", {}, 0, setUpSchoolInfo);
};

var init_gui = function () {
  $('.reset').click(function () {
    setup(selectedSchool);
  });

  $('.add-student').click(function() {
    var text = $('#add-modal').clone();
    
    showDialog({
      title: 'Add Student',
      text: text,
      onLoaded: function() {
        var addButton = $('.dialog-container #positive');
        addButton.attr('disabled', true);
        $('.dialog-container #new-student-name')
        .unbind()
        .on('input', function() {
          var $this = $(this);
          if ($this.val() in students) {
            $this.addClass('bad');
            addButton.attr('disabled', true);
          } else {
            $this.removeClass('bad');
            addButton.attr('disabled', false);
          }
        });
      },
      negative: {
          title: 'Cancel'
      },
      positive: {
          title: 'Add',
          onClick: function() {
            var name = $('.dialog-container #new-student-name').val();
            var interests = $('.dialog-container #new-student-interests').val().split(',').map(function(interest) {
              return interest.trim();
            });
            $('.loader').show();
            var studentInfo = [name].concat(interests);
            invoke_rpc("/ui_add_student", studentInfo, 0, function(friendships) {
              students[name] = Student(name, interests);
              setGraphFromFriendships(friendships);
              setupImmybox($('#cliques-for'));
              setupImmybox($('#is-for'));
              $('.loader').hide();   
            });
        }
      },
    });
    
  });

  $('.update-student').click(function() {
    var text = $('#update-modal').clone();

    showDialog({
      title: 'Update Student',
      text: text,
      onLoaded: function() {
        var updateButton = $('.dialog-container #positive');
        // the order of updating input matters!
        var input = $('.dialog-container #student-name');
        input
        .unbind()
        .on('input', function() {
          var $this = $(this);
          var name = $this.val()
          if (!(name in students)) {
            $this.addClass('bad');
            updateButton.attr('disabled', true);
          } else {
            $this.removeClass('bad');
            $('.dialog-container #student-interests').val(getArrAsString(students[name].getInterests()));
            updateButton.attr('disabled', false);
          }
        });
        setupImmybox(input);
        var clickedStudent = infoDisplay.getClickedStudentName(); 
        if (clickedStudent) {
          input.val(clickedStudent);
          $('.dialog-container #student-interests').val(getArrAsString(students[clickedStudent].getInterests()));
          input.removeClass('bad');
          updateButton.removeClass('bad');
          updateButton.attr('disabled', false);
        } else {
          input.addClass('bad');
          updateButton.addClass('bad');
          updateButton.attr('disabled', true);
        }    
      },
      negative: {
          title: 'Cancel'
      },
      positive: {
          title: 'Update',
          onClick: function() {
            var name = $('.dialog-container #student-name').val()
            var interests = $('.dialog-container #student-interests').val().split(',').map(function(interest) {
              return interest.trim();
            });
            $('.loader').show();
            var studentInfo = [name].concat(interests);
            invoke_rpc("/ui_update_student", studentInfo, 0, function(friendships) {
              students[name] = Student(name, interests);
              setGraphFromFriendships(friendships);
              setupImmybox($('#cliques-for'));
              setupImmybox($('#is-for'));
              $('.loader').hide();   
            });
        }
      },
    });
  });

  $('.remove-student').click(function() {
    var text = $('#remove-modal').clone();

    showDialog({
      title: 'Remove Student',
      text: text,
      onLoaded: function() {
        var removeButton = $('.dialog-container #positive');
        // the order of updating input matters!
        var input = $('.dialog-container #student-name');
        input
        .unbind()
        .on('input', function() {
          var $this = $(this);
          var name = $this.val()
          if (!(name in students)) {
            $this.addClass('bad');
            removeButton.attr('disabled', true);
          } else {
            $this.removeClass('bad');
            removeButton.attr('disabled', false);
          }
        });
        setupImmybox(input);
        var clickedStudent = infoDisplay.getClickedStudentName();
        if (clickedStudent) {
          input.val(clickedStudent);
          input.removeClass('bad');
          removeButton.removeClass('bad');
          removeButton.attr('disabled', false);
        } else {
          input.addClass('bad');
          removeButton.addClass('bad');
          removeButton.attr('disabled', true);
        }
      },
      negative: {
          title: 'Cancel'
      },
      positive: {
          title: 'Remove',
          onClick: function() {
            var name = $('.dialog-container #student-name').val()
            $('.loader').show();
            invoke_rpc("/ui_remove_student", name, 0, function(friendships) {
              delete students[name];
              setGraphFromFriendships(friendships);
              infoDisplay.unClickStudent(name);
              setupImmybox($('#cliques-for'));
              setupImmybox($('#is-for'));
              $('.loader').hide();   
            });
        }
      },
    });
  });


  $('.all-cliques').click(function() {
    $('.loader').show();
    invoke_rpc("/ui_get_cliques", {}, 0, function(allCliques) {
      updateList(null, allCliques);
      if (allCliques.length === 0) {
        updateGraphAndList(null, []);
      } else {
        updateGraphAndList(null, allCliques[0]);
      }
      $('.loader').hide();
    });
  });

  $('.student-cliques').click(function() {
    var selectedStudent = $('#cliques-for').val();
    if (selectedStudent in students) {
      $('.loader').show();
      invoke_rpc("/ui_get_cliques_for_student", selectedStudent, 0, function(cliques) {
        updateList(selectedStudent, cliques);
        if (cliques.length === 0) {
          updateGraphAndList(selectedStudent, []);
        } else {
          updateGraphAndList(selectedStudent, cliques[0]);
        }   
        $('.loader').hide();    
      });    
    }
  });

  $('#is-for').on('input', function() {
    var $this = $(this);
    var name = $this.val();
    if (!(name in students)) {
      $this.addClass('bad');
    } else {
      $this.removeClass('bad');
    }
  });

  $('#cliques-for').on('input', function() {
    var $this = $(this);
    var name = $this.val();
    if (!(name in students)) {
      $this.addClass('bad');
    } else {
      $this.removeClass('bad');
    }
  });

  $('.student-is').click(function() {
    var selectedStudent = $('#is-for').val();
    if (selectedStudent in students) {
      $('.loader').show();
      invoke_rpc("/ui_find_independent_set", selectedStudent, 0, function(indSet) {
        updateList(selectedStudent, [indSet]);
        updateGraphAndList(selectedStudent, indSet);
        $('.loader').hide();
      });    
    }
  });

  $('.cliques-of-size').click(function() {
    var n = parseInt($('.lab-actions input').val());
    n = n? n:0;
    $('.loader').show();
    invoke_rpc("/ui_get_cliques_size_n", n, 0, function(allCliques) {
      updateList(null, allCliques);
      if (allCliques.length === 0) {
        updateGraphAndList(null, []);
      } else {
        updateGraphAndList(null, allCliques[0]);
      }
      $('.loader').hide();
    });
  });

  $('.save').click(function () {
    var saveFormat = [];
    for (var studentName in students) {
      var student = students[studentName];
      saveFormat.push([student.getName()].concat(student.getInterests()));
    }

    save(
      JSON.stringify(saveFormat),
      (new Date()).getTime().toString());
  });
};



// D3-related mess
function getColor(groupNumber){
  switch(groupNumber) {
    case 1:
      return "#389ce2";
    case 2:
      return "#FFB401";
    case 3:
      return "#1f77b4";
    case 4:
      return "#2ca02c"
    default:
      return "#389ce2";
  }
}

function getValuebyId(val){
  if (window.graph) {
    return window.graph.nodes[val].value;
  } else { return null; }
}

var force;

function handle_resize(){
  var width = document.getElementById('graph').offsetWidth;
  var height = document.getElementById('graph').offsetHeight;
  force.size([width, height]).resume();
}
window.onresize = handle_resize;

function drawForce(graph) {
  var svg = d3.select("#graph")
              .html('')
              .append("svg")
              .attr("width", "100%")
              .attr("height", "100%");

  force = d3.layout.force()
                    .charge(-120)
                    .linkDistance(50);

  handle_resize();

  force.nodes(graph.nodes)
       .links(graph.links)
       .linkDistance(150)
       .start();

  var link = svg.selectAll(".link")
                .data(graph.links)
                .enter().append("line")
                .attr("class", "link")
                .attr('stroke', function (d) {
                  return d.edge_color;
                })
                .style("stroke-width", function (d) {
                  return d.value;
                });

  var node = svg.selectAll(".node")
                .data(graph.nodes)
                .enter().append("circle")
                .attr("class", "node")
                .attr("r", 12)
                .style("fill", function (d) {
                  return getColor(d.group);
                })
                .call(force.drag);

  node.append("title") .text(function (d) { return d.name; });

  force.on("tick", function () {
      link.attr("x1", function (d) {
          return d.source.x;
      })
      .attr("y1", function (d) {
        return d.source.y;
      })
      .attr("x2", function (d) {
        return d.target.x;
      })
      .attr("y2", function (d) {
        return d.target.y;
      });

      node.attr("cx", function (d) { return d.x; })
          .attr("cy", function (d) { return d.y; });
  });

  infoDisplay.selectClickedStudent();

  $('.node').hover(function () {
    infoDisplay.hoverIn($(this).find('title').text());
  }, infoDisplay.hoverOut)
  $('.node').click(function() {
    infoDisplay.clickStudent($(this).find('title').text());
  });
}

function updateGraph(selected, values, mark_edges) {
  if (window.graph) {
    var graph = window.graph;

    // reset the graph
    // clear selected nodes
    for (var i = 0; i < graph.nodes.length; i++) {
      if (graph.nodes[i].value == selected) {
        graph.nodes[i].group = 2;
      } else {
        graph.nodes[i].group = 1;
      }
    }
    // clear selected edges
    for (var i = 0; i < graph.links.length; i++) {
      graph.links[i].edge_color = "#999999";
      graph.links[i].value = 1;
    }

    // Select all nodes in values
    for (var i = 0; i < graph.nodes.length; i++) {
      // if node is in values but isn't bacon, select it
      var g_val = graph.nodes[i].value;
      if ((g_val != selected) && (values.indexOf(g_val) >= 0)){
        graph.nodes[i].group = 4;
      }
    }

    // select all edges between values
    if (mark_edges) {
      for (var i = 0; i < graph.links.length; i++) {
        // figure out what this edge connects
        var x, y;
        if (typeof graph.links[i].source == "object"){
          x = graph.links[i].source.value;
          y = graph.links[i].target.value;
        } else {
          x = getValuebyId(graph.links[i].source);
          y = getValuebyId(graph.links[i].target);
        }

        // is this edge connecting nodes in values?
        var ix, iy;
        ix = values.indexOf(x);
        iy = values.indexOf(y);
        if ((ix>=0) && (iy>=0)){
          graph.links[i].edge_color = "#333333";
          graph.links[i].value = 2;
        }
      }
    }

    drawForce(graph);
  }
}


/* Dialog library from https://jsfiddle.net/w5cpw7yf/*/
function showDialog(options) {
  options = $.extend({
      id: 'orrsDiag',
      title: null,
      text: null,
      negative: false,
      positive: false,
      cancelable: true,
      contentStyle: null,
      onLoaded: false
  }, options);

  // remove existing dialogs
  $('.dialog-container').remove();
  $(document).unbind("keyup.dialog");

  $('<div id="' + options.id + '" class="dialog-container"><div class="mdl-card mdl-shadow--16dp"></div></div>').appendTo("body");
  var dialog = $('#orrsDiag');
  var content = dialog.find('.mdl-card');
  if (options.contentStyle != null) content.css(options.contentStyle);
  if (options.title != null) {
      $('<h5>' + options.title + '</h5>').appendTo(content);
  }
  if (options.text != null) {
    content.append($('<p></p>')).append(options.text);
  }
  if (options.negative || options.positive) {
      var buttonBar = $('<div class="mdl-card__actions dialog-button-bar"></div>');
      if (options.negative) {
          options.negative = $.extend({
              id: 'negative',
              title: 'Cancel',
              onClick: function () {
                  return false;
              }
          }, options.negative);
          var negButton = $('<button class="mdl-button mdl-js-button mdl-js-ripple-effect" id="' + options.negative.id + '">' + options.negative.title + '</button>');
          negButton.click(function (e) {
              e.preventDefault();
              if (!options.negative.onClick(e))
                  hideDialog(dialog)
          });
          negButton.appendTo(buttonBar);
      }
      if (options.positive) {
          options.positive = $.extend({
              id: 'positive',
              title: 'OK',
              onClick: function () {
                  return false;
              }
          }, options.positive);
          var posButton = $('<button class="mdl-button mdl-button--colored mdl-js-button mdl-js-ripple-effect" id="' + options.positive.id + '">' + options.positive.title + '</button>');
          posButton.click(function (e) {
              e.preventDefault();
              if (!options.positive.onClick(e))
                  hideDialog(dialog)
          });
          posButton.appendTo(buttonBar);
      }
      buttonBar.appendTo(content);
  }
  componentHandler.upgradeDom();
  if (options.cancelable) {
      dialog.click(function () {
          hideDialog(dialog);
      });
      $(document).bind("keyup.dialog", function (e) {
          if (e.which == 27)
              hideDialog(dialog);
      });
      content.click(function (e) {
          e.stopPropagation();
      });
  }
  setTimeout(function () {
      dialog.css({opacity: 1});
      if (options.onLoaded)
          options.onLoaded();
  }, 1);
}

function hideDialog(dialog) {
  $(document).unbind("keyup.dialog");
  dialog.css({opacity: 0});
  setTimeout(function () {
      dialog.remove();
  }, 400);
}