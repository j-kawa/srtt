# SRTT (SimRail timetables) generator

This is the source code of the SRTT project, a web-based,
[SimRail](https://simrail.eu/pl/gry/simrail-2021) timetable viewer for
the multi-player mode.

The reference instance is hosted [here](https://srtt.sokora.dev/).

## How it works

The project is functionally split into three parts:

1) The timetable synchronization part -- official, publicly
   available APIs are queried for data needed to generate the
   timetables:

   * https://panel.simrail.eu:8084/servers-open -- available servers,
   * https://api1.aws.simrail.eu:8082/api/getAllTimetables -- timetables,
   * https://api1.aws.simrail.eu:8082/api/getTimeZone -- timezones.

   Then, raw output is saved to disk.

2) The running trains scanning part -- timetables acquired in the
   first part lack the correct information about actual trains'
   parameters. Again, official APIs are queried:

   * https://panel.simrail.eu:8084/trains-open -- currently running trains,
   * https://api1.aws.simrail.eu:8082/api/getTime -- servers' times.

   Then, processed output is saved into an sqlite database.

3) The web-site generation part -- data saved in previous phases is
   used to generate the timetables -- as a collection of static files
   (HTML, JS, CSS, etc.).

For usage details, please invoke `python srtt.py -h` for help.

## Requirements

* Python 3.9,
* a web server -- if one wishes to host it.
