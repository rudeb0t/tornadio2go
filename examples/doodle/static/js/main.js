/*
 * Ported from tornadio2-draw sample app by Hyliker Cheung.
 * See: https://github.com/hyliker/tornadio2-draw
 *
 */
var app = {
  socket: null,
  canvas: null, 
  strokeStyle: '#'+Math.floor(Math.random()*16777215).toString(16),
  messageCount: 0,
  latencyTotal: 0,
  latencies: [0, 0],
  currentTime: 0,
  timeDiff: 0,
  init: function () {
    var socket = io.connect();
    app.socket = socket;

    socket.on('calibrate', function(message) {
        var data = JSON.parse(message);
        var roundtrip = (new Date()).getTime() - app.currentTime;
        app.timeDiff = Math.round(data.timestamp - roundtrip / 2 - app.currentTime);
        console.log('browserTime: ' + app.currentTime);
        console.log('serverTime: ' + data.timestamp);
        console.log('roundtripTime: ' + roundtrip);
        console.log('halftripTime: ' + roundtrip / 2);
        console.log('timeDiff: ' + app.timeDiff);
        socket.emit('update');
    });
    socket.on("connect", function () {
        app.currentTime = (new Date()).getTime();
        socket.emit('calibrate', JSON.stringify({timestamp:app.currentTime}));
      app.log("socket connected");
    });

    socket.on("online", function (number) {
        app.log(number +  " online users");
    });

    socket.on("disconnect", function () {
      app.log("socket disconnect");
    });

    socket.on("message", function (message) {
      app.log(message);
    });

    socket.on("clear", function () {
      app.clear();
    });

    socket.on("draw", function (message) {
        var drawData = JSON.parse(message);
        if (drawData.timestamp) {
            var diff = ((new Date()).getTime() + app.timeDiff) - drawData.timestamp;
            if (app.latencies[0] == 0 || app.latencies[0] > diff) {
                app.latencies[0] = diff;
            }
            if (app.latencies[1] == 0 || app.latencies[1] < diff) {
                app.latencies[1] = diff;
            }
            app.messageCount = app.messageCount + 1;
            app.latencyTotal = app.latencyTotal + diff;
            $('#latency-info').html('Average Latency: ' + diff.toFixed(4) + ' ms; Min/Max: ' + app.latencies[0].toFixed(4) + '/' + app.latencies[1].toFixed(4) + '; Samples: ' + app.messageCount);
        }
        app.draw(drawData);
    });

    $(window).on('beforeunload',function(){ app.socket.disconnect(); });

    var isMouseDown = false;
    var mouseX, mouseY, moveToPos, lineToPos;

    var canvas = app.canvas = $("#canvas").get(0);

    canvas.width = window.screen.width;
    canvas.height = window.screen.height;

    $("#canvas").mousedown(function (evt) {
        isMouseDown = true;
        mouseX = evt.pageX - this.offsetLeft;
        mouseY = evt.pageY - this.offsetTop;
        moveToPos = {x: mouseX, y: mouseY};
    });

    $("#canvas").mouseup(function (evt) {
        isMouseDown = false;
    });

    $("#canvas").mouseout(function (evt) {
        isMouseDown = false;
    });

    $("#canvas").mousemove(function (evt) {
        if (isMouseDown) {
          mouseX = evt.pageX - this.offsetLeft;
          mouseY = evt.pageY - this.offsetTop;
          lineToPos = {x: mouseX, y: mouseY};
          app.draw({moveToPos: moveToPos, lineToPos: lineToPos, strokeStyle: app.strokeStyle}, true);
          moveToPos = lineToPos;
        }
    });

    $("#clear").click(function (evt) {
        socket.emit("clear");
        app.clear();
    });

  },
  log: function (message) {
    $("#debug-bar").html(message);
  },
  clear: function () {
      var ctx = app.canvas.getContext("2d");
      ctx.clearRect(0, 0, app.canvas.width, app.canvas.height);
      app.messageCount = 0;
      app.latencyTotal = 0;
      app.latencies = [0, 0];
      $('#latency-info').html('Average Latency: 0 ms; Min/Max: 0/0; Samples: 0');
  },
  draw: function (drawData, emit) {
    var moveToPos = drawData.moveToPos;
    var lineToPos = drawData.lineToPos;
    var strokeStyle = drawData.strokeStyle;

    var ctx = app.canvas.getContext("2d");
    ctx.strokeStyle = strokeStyle;
    ctx.lineJoin = "round";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(moveToPos.x, moveToPos.y);
    ctx.lineTo(lineToPos.x, lineToPos.y);
    ctx.closePath();
    ctx.stroke();

    if (emit) {
      var drawMessage = JSON.stringify({moveToPos: moveToPos, lineToPos: lineToPos, strokeStyle: strokeStyle});
      app.socket.emit("draw", drawMessage);
    }
  }
};
_.bindAll(app);

$(function () {
    app.init();
});
