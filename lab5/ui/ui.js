"use strict";
``
// RPC wrapper
function invoke_rpc(method, args, timeout, on_done) {
  $("#crash").hide();
  $("#timeout").hide();
  $("#rpc_spinner").show();
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
  // race condition if init() does RPC on function not yet registered by restart()!
  //restart();
  //init();
  invoke_rpc("/restart", {}, 0, function () { init(); })
});

function restart() {
  invoke_rpc("/restart", {})
}

//  LAB CODE

// this is inlined into infra/ui/ui.js

var Session = function (name, capacity) {
  var that = Object.create(Session.prototype);
  var size = Math.ceil(Math.sqrt(capacity)) * 34;
  var domObject;
  var room;
  var overflow;
  var info;
  var assignedStudents = [];

  var setUp = function () {
    createRoomDomObject();
  };

  var createRoomDomObject = function () {
    domObject = $('<div class="room-container"></div>');
    info = $('<div class="room-info"><span class="name">' + name + '</span>' +
      '<div class="counter">' +
      '<span class="count">0</span>/' + capacity +
      '<span class="overfull"> (!)</span>' +
      '</div>' +
      '</div>');
    room = $('<div class="room"></div>');
    room.css({
      width: size + 'px',
      height: size + 'px'
    });
    overflow = $('<div class="overflow"></div>');
    overflow.css({
      width: size + 'px'
    });
    domObject.append(info);
    domObject.append(room);
    domObject.append(overflow);
  };

  that.getName = function () {
    return name;
  };

  that.getCapacity = function () {
    return capacity;
  };

  that.getDomObject = function () {
    return domObject;
  };

  that.assignStudent = function (student) {
    assignedStudents.push(student);
    student.assignRoom(name);
    if (assignedStudents.length > capacity) {
      overflow.append( student.getDomObject());
     room.addClass('overfull');
      info.find('.overfull').css({
        display: 'inline'
      });
    } else {
      room.append( student.getDomObject());
    }
    info.find('.count').html(assignedStudents.length);
  };

  that.reset = function () {
    room.removeClass('overfull');
    assignedStudents = [];
    info.find('.count').html(0);
    info.find('.overfull').hide();
  };

  setUp();
  Object.freeze(that);
  return that;
};

var InfoDisplay = function () {
  var that = Object.create(InfoDisplay.prototype);
  var clickedStudent;

  that.hoverIn = function (student) {
    $('.info #name').html(student.getName()).show();
    var assignedRoom = student.getAssignedRoom();
    var preferences = student.getPreferredRooms();
    var isAssignedRoomPreferred = (preferences.indexOf(assignedRoom) != -1);
    if (assignedRoom) {
      $('.info #assigned-room')
        .html(assignedRoom + (isAssignedRoomPreferred ? '' : ' (!)'))
        .show();
    } else {
      $('.info #assigned-room').html('');
    }
    $('.info #desired-rooms')
      .html(preferences.map(function (roomName) {
        return '<div>' + roomName + '</div>';
      }))
      .show();
  };

  that.hoverOut = function () {
    if (clickedStudent) {
      that.hoverIn(clickedStudent);
    }
  };

  that.clickStudent = function (student) {
    $('.clicked').removeClass('clicked');
    if (clickedStudent === student) {
      // click again to cancel
      clickedStudent = null;
    } else {
      clickedStudent = student;
      student.getDomObject().addClass('clicked');
    }
  };

  that.reset = function () {
    $('.clicked').removeClass('clicked');
    clickedStudent = null;
    resetDisplays();
  };

  var resetDisplays = function () {
    $('.info #name').html('');
    $('.info #assigned-room').html('');
    $('.info #desired-rooms').html('');
  };

  Object.freeze(that);
  return that;
};

var Student = function (name, preferences) {
  var that = Object.create(Student.prototype);
  var domObject;
  var studentBall;
  var assignedRoom;

  var setUp = function () {
    createStudentDomObject();
    domObject.hover(function () {
      infoDisplay.hoverIn(that);
    }, infoDisplay.hoverOut);
    domObject.click(function () {
      infoDisplay.clickStudent(that);
    });
  };

  var createStudentDomObject = function () {
    domObject = $('<div class="student"></div>');

    studentBall = $('<div class="student-ball"></div>');
    domObject.append(studentBall);
  };

  that.getDomObject = function () {
    return domObject;
  };

  that.assignRoom = function (room) {
    assignedRoom = room;
    var isAssignedRoomPreferred = (preferences.indexOf(assignedRoom) != -1);
    if (!isAssignedRoomPreferred) {
      studentBall.addClass('bad-room');
    }
  };

  that.reset = function () {
    assignedRoom = null;
    studentBall.removeClass('bad-room');
  };

  that.getName = function () {
    return name;
  };

  that.getPreferredRooms = function () {
    return preferences.slice();
  };

  that.getAssignedRoom = function () {
    return assignedRoom;
  };

  setUp();
  Object.freeze(that);
  return that;

};

var randomInt = function (max) {
  return Math.ceil(Math.random() * max);
};

var randomCase = function () {
  var testCase = [{}, {}];

  sessions = {};
  var numSess = randomInt(5);
  var totalCapacity = 0;
  for (var i = 0; i < numSess; i++) {
    var name = "Session " + i;
    var capacity = randomInt(15);
    var session = Session(name, capacity);
    sessions[name] = session;
    testCase[1][name] = capacity;
    totalCapacity += capacity;
  }

  students = {};
  var numStudents = Math.max(randomInt(totalCapacity * .3),
    randomInt(totalCapacity * 1.1));
  // Can't let it get too large
  numStudents = Math.min(numStudents, 18);
  var sessionNames = Object.keys(sessions);
  for (var i = 0; i < numStudents; i++) {
    var preferences = new Set([]);
    var numPrefs = randomInt(5);
    for (var j = 0; j < numPrefs; j++) {
      var sessionName = sessionNames[randomInt(sessionNames.length) - 1];
      preferences.add(sessionName);
    }
    var name = 'Student ' + i;
    preferences = Array.from(preferences);
    var stud = Student(name, preferences);
    testCase[0][name] = preferences;
    students[name] = stud;
  }

  return testCase;
};

var cleanup = function (students, rooms) {
  $('.starter').html('');
  $('.rooms').html('');
  $('.no-assignments-found').css({
    visibility: 'hidden'
  });
  $('.shadow-student-ball-container').remove();
  infoDisplay.reset();
};

var setCase = function (testName) {
  $("#case").html(testName);
  selectedCase = testName;
}

var setup = function (testCaseName) {
  $('.loader').show();
  cleanup();

  var testCaseData = testCases[testCaseName];
  var student_preferences = testCaseData[0];
  var session_capacities = testCaseData[1];

  students = {};
  for (var studentName in student_preferences) {
    var student = Student(studentName, student_preferences[studentName]);
    students[studentName] = student;

    $('.starter').append(student.getDomObject());
    student.reset();
  }

  sessions = {};
  for (var sessionName in session_capacities) {
    var session = Session(sessionName, session_capacities[sessionName]);
    sessions[sessionName] = session;

    session.reset();
    $('.rooms').append(session.getDomObject());
  }

  $('.reset').hide();
  $('.assign').attr('disabled', false).show();
  $('.loader').hide();
}

var assign = function (assignments) {
  infoDisplay.hoverOut();
  $('.assign').hide();
  $('.reset').css({
    display: 'inline-block'
  });
  $('.loader').hide();
  if (assignments === null) {
    $('.no-assignments-found').css({
      visibility: 'visible'
    });
    return;
  }
  var assigned = {};
  for (var assignment in assignments) {
    var correct = assignments[assignment];
    if (correct) {
      var nameList = assignment.split('_');
      var studentName = nameList[0];
      var sessionName = nameList[1];

      sessions[sessionName].assignStudent(students[studentName]);
      assigned[studentName] = "";
    }
  }

  for (var studentName in students) {
    // if there is any student unassigned, assign them to a preferred session
    if (!(studentName in assigned)) {
      var student = students[studentName];
      var sessionName = student.getPreferredRooms[0];
      sessions[sessionName].assignStudent(student);
    }
  }
}

var save = function (text, name) {
  name = name + '.json';
  var a = document.createElement("a");
  var file = new Blob([text], { type: 'text/plain' });
  a.href = URL.createObjectURL(file);
  a.download = name;
  a.click();
}

var testCases;
var selectedCase;
var students = {};
var sessions = {};

var infoDisplay = InfoDisplay();

var init = function () {
  // list test case data into view
  var setUpCases = function (data) {
    testCases = data;
    for (var test_case_name in data) {
      var test_case_data = data[test_case_name];
      $("#cases").append($("<li class=\"mdl-menu__item\" onclick=\"setCase('" + test_case_name + "')\">" + test_case_name + "</li>"));
    }
    setCase(Object.keys(data)[0]);
    setup(selectedCase);
  };
  init_gui();
  invoke_rpc("/load_data", {}, 0, setUpCases);
};

var init_gui = function () {
  $('.assign').click(function () {
    invoke_rpc("/ui_assign", testCases[selectedCase], 0, assign);
    $('.assign').attr('disabled', true);
    $('.loader').show();
  });

  $('.reset').click(function () {
    setup(selectedCase);
  });

  $('.random').click(function () {
    var random = "Random";
    setCase(random);
    testCases[random] = randomCase();
    setup(random);
  });

  $('.save').click(function () {
    save(
      JSON.stringify(testCases[selectedCase]),
      (new Date()).getTime().toString());
  });
};
