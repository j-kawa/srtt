"use strict";

function tick_clock() {
    var now = BigInt(new Date()) + time_offset;

    const time = new Date(Number(now)).toISOString().substring(11, 19);
    document.getElementById("clock").textContent = time;

    setTimeout(tick_clock, Number(1000n - now % 1000n));
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

    if (time_offset !== undefined) {
        tick_clock();
    }
})();
