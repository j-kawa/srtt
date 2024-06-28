# SRTT (SimRail timetables) generator

This is the source code of the SRTT project, a web-based,
[SimRail](https://simrail.eu/pl/gry/simrail-2021) timetable viewer for
the multi-player mode.

The reference instance is hosted [here](https://srtt.sokora.dev/).

## How it works

The project is functionally split into two phases:

1) The synchronization phase -- the official, publicly available
   APIs are queried for data needed to generate the timetables:

   * https://panel.simrail.eu:8084/servers-open -- available servers,
   * https://api1.aws.simrail.eu:8082/api/getAllTimetables -- timetables,
   * https://api1.aws.simrail.eu:8082/api/getTimeZone -- timezones.

   Then, raw output is saved to disk.

2) The web-site generation phase -- data saved in previous phase is
   used to generate the timetables -- as a collection of static files
   (HTML, JS, CSS, etc.).

For usage details, please invoke `srtt.py -h` for help.

## Requirements

* Python 3.9 or higher,
* a web server -- if one wishes to host it.
