function toTimeString(seconds) {
  return (new Date(seconds * 1000)).toUTCString().match(/(\d\d:\d\d:\d\d)/)[0];
}

function startTimer() {
  var timerElem = $('.timer');
  var duration = timerElem.text();
  var a = duration.split(':');
  var seconds = (+a[0]) * 60 * 60 + (+a[1]) * 60 + (+a[2]);
  setInterval(function() {
    seconds--;
    if (seconds >= 0) {
      timerElem.html(toTimeString(seconds));
    }
  }, 1000);
}
$(window).on('load', function () {
  $('form').submit(function(){
    startTimer()
  });
});
