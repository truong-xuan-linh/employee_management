var timer;
var seconds = localStorage.getItem('seconds') ? parseInt(localStorage.getItem('seconds')) : 0;

function startTimer() {
    timer = setInterval(function() {
        seconds++;
        localStorage.setItem('seconds', seconds);
        var minutes = Math.floor(seconds / 60);
        var secondsDisplay = seconds % 60;
        var timerElement = document.getElementById('timer');
        timerElement.textContent =
            (minutes < 10 ? "0" + minutes : minutes) + ":" +
            (secondsDisplay < 10 ? "0" + secondsDisplay : secondsDisplay);

        // Change the color of the timer based on the number of seconds
        if (seconds >= 35) {
            timerElement.style.color = 'red';
        } else if (seconds >= 30) {
            timerElement.style.color = 'orange';
        } else {
            timerElement.style.color = 'black';
        }
    }, 1000);
}

if (localStorage.getItem('startTimer') === 'true') {
    startTimer();
    localStorage.removeItem('startTimer'); // remove the item so the timer doesn't start again on refresh
}

window.onload = function() {
    // Update the timer display immediately when the page loads
    var seconds = localStorage.getItem('seconds') ? parseInt(localStorage.getItem('seconds')) : 0;
    var minutes = Math.floor(seconds / 60);
    var secondsDisplay = seconds % 60;
    var timerElement = document.getElementById('timer');
    timerElement.textContent =
        (minutes < 10 ? "0" + minutes : minutes) + ":" +
        (secondsDisplay < 10 ? "0" + secondsDisplay : secondsDisplay);

    // Change the color of the timer based on the number of seconds
    if (seconds >= 35) {
        timerElement.style.color = 'red';
    } else if (seconds >= 30) {
        timerElement.style.color = 'orange';
    } else {
        timerElement.style.color = 'black';
    }


    var rows = document.querySelectorAll('#training-table tbody tr');
    var allDone = Array.from(rows).every(function(row) {
        return row.classList.contains('completed');
    });

    if (allDone) {
        document.getElementById('training-table').style.display = 'none'; // Hide the table
        document.getElementById('new-history').style.display = 'block';
        document.getElementById('timer').style.display = 'none'; // Hide the timer
        localStorage.removeItem('seconds'); // Clear the timer
    } else {
        if (localStorage.getItem('startTimer') !== 'true') {
            startTimer(); // Start the timer
        }
        setTimeout(function() {
            location.reload();
        }, 3000);
    }
};