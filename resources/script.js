"use strict";

function tick_clock() {
    var now = new Date();
    const dt = 1000 - now.getMilliseconds();

    now.setHours(now.getHours() + tz);
    const time = now.toISOString().substring(11, 19);

    document.getElementById("clock").innerHTML = time;

    setTimeout(tick_clock, dt);
}

function update_last_sync(elem) {
    const now = new Date();
    const then = new Date(elem.innerHTML);
    const minutes = BigInt(now - then) / (1000n * 60n) + 1n;

    elem.title = [
        ["day", minutes / (60n * 24n)],
        ["hour", minutes / 60n % 60n],
        ["minute", minutes % 60n],
    ].filter(
        ([name, value]) => value > 0
    ).map(([name, value]) => {
        if (value == 1) {
            return "1 " + name;
        }
        return value + " " + name + "s";
    }).join(" ") + " ago";
}

(function () {
    var last_sync = document.getElementById("last_sync");

    last_sync.style.textDecoration = "underline dotted";

    if (tz !== undefined) {
        tick_clock();
    }
})();
