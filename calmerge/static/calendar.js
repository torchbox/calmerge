document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var calendarMessage = document.getElementById('calendar-message');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        headerToolbar: {
            start: 'title',
            center: '',
            end: 'today prev,next dayGridMonth,listYear,multiMonthYear'
        },
        initialView: 'listYear',
        events: {
            url: calendarEl.dataset.url,
            format: 'ics',
        },
        eventSourceSuccess: function() {
            calendarMessage.style.display = 'none';
        },
        eventSourceFailure: function() {
            calendarMessage.innerText = "Loading the calendar failed. Please try again later, or check your browser's developer console for more details."
        },
        eventDidMount: function(info) {
            info.el.title = info.event.title;
        }
    });

    calendar.render();
  });
