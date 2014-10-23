# Smartkeg

##### By: Harrison Hubbell and  Christopher Young

Never run out of beer with smarter, integrated, monitoring systems.

### Status
This project is still under construction; some parts are currently not in a working state, while others may not have been implemented yet.

### How it works
Smartkeg logs refrigerator temperature, beer temperature, and consumption rates to help facilitate ordering and cost management.  The machine uses historic consumption data and future predictions to analyze when a refill will be necessary - and gives alerts via email and a web interface, which is served up through the Raspberry Pi on a simple Python stack.

### Getting Started
To try the Smartkeg Keg Monitoring system out, pull down a copy of the source onto a Raspberry Pi ARM board.  As of now this script supports only Arch Linux ARM.  Modify the config.cfg.TEMPLATE file to your liking, save it as config.cfg, and run the following in the Smartkeg root directory:
`# ./build`
Easy as that!
Smartkeg has the following dependencies, the build script will check to see if you have the following installed:
* MySQL (We prefer MariaDB)
* pip (For installing Python dependencies)
* MySQL-python (Python MySQL driver)
* RPi.GPIO (Python-Raspberry Pi GPIO driver)
The build script will configure the MySQL database user and create the required tables; it will require root access (or any user with `CREATE/DROP` rights) to your MySQL database.  It will also make a copy of the Smartkeg source code into te systems `/usr/local/src/` directory, and create the service files.
To run the Smartkeg system at startup on Arch Linux, run the following:
`# systemctl enable smartkeg`
To run the Smartkeg web server at startup on Arch Linux, run the following:
`# systemctl enable smartkeg-server`

### History
Originally, we scoped the project to gather information using distinct processes and let a web server handle displaying the information to the user.  This had some very distinct drawbacks:
* Contention
* Data Sharing
* Bloat

### Today
Smartkeg is driven by a main process with 4 distinct child processes; Temperature Sensor, LED Display, Flow Meter, and Smartkeg Server.

### Accessing Data Through the Web
Smartkeg serves current information about its contents with a python web server, and data is asynchronously updated with JavaScript.
