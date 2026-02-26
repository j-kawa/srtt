"use strict";

function tickClock() {
    var now = BigInt(new Date()) + timeOffset;

    const time = new Date(Number(now)).toISOString().substring(11, 19);
    document.getElementById("clock").textContent = time;

    setTimeout(tickClock, Number(1000n - now % 1000n));
}

function updateLastSync(elem) {
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
    var lastSync = document.getElementById("last-sync");

    lastSync.style.textDecoration = "underline dotted";

    if (timeOffset !== undefined) {
        tickClock();
    }
})();
