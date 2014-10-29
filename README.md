# Smartkeg
##### By: Harrison Hubbell and  Christopher Young

Accurate demand forecasting is critical to successful long term business strategy. Using smarter, integrated monitoring systems for food and beverage consumption, retailers are able to take advantage of lean "JIT" supply practices; benefits of lowered holding costs and higher satisfaction of demand are thus able to realize.  Using Time Series Regression and Continuous Review Modeling the Smartkeg can accurately forecast stock supply and demand levels, and propagate this information to a wide range of interconnected devices.

## Status
This project is currently under construction.

## How it works
The system is currently designed to be run on a Raspberry Pi board with Arch Linux ARM Operating System.  The Smartkeg system logs refrigerator temperature and beer temperature using a 3-pin temperature sensor, and consumption rates are logged using a 3-pin flow meter.  These peripherals are connected to the Raspberry Pi's GPIO pins.  The machine uses historic consumption data to build future predictions, allowing users to be notified when a refill will be necessary - and gives alerts via a web interface, which is served up through the Raspberry Pi on a simple Python stack.

## Getting Started
To try the Smartkeg Keg Monitoring system out, pull down a copy of the source onto a Raspberry Pi ARM board running Arch Linux ARM.  Modify the config.cfg.TEMPLATE file to your liking, save it as config.cfg, and run the following in the Smartkeg root directory:

```Shell
# ./build
```

Easy as that!

#### How the Build Script Works
##### Dependency Check
Smartkeg has the following dependencies, and the build script will check first to see if you have the following installed:

**Note:** This step can be skipped by including the following argument: `--no-check`
* MySQL (We prefer MariaDB)
* pip (For installing Python dependencies)
* MySQL-python (Python MySQL driver)
* RPi.GPIO (Python-Raspberry Pi GPIO driver)

##### Database
The build script will also configure the MySQL database user and create the required tables; it will require root access (or any user with `CREATE/DROP` rights) to your MySQL database.  It will also make a copy of the Smartkeg source code into the systems `/usr/local/src/` directory, and create the service files.

**Note:** This step can be skipped by including the following argument: `--no-db`

#### Post Install
The build script creates systemd service files for the Smartkeg system, and the Smartkeg Server. To run the Smartkeg system and the Smartkeg Server at startup on Arch Linux, run the following, respectively:
```Shell
# systemctl enable smartkeg
```
```Shell
# systemctl enable smartkeg-server
```

## History
Originally, we scoped the project to gather information using distinct processes and let a web server handle displaying the information to the user.  This had some very distinct drawbacks:
* Contention
* Data Sharing
* Bloat

## Today
Smartkeg is driven by a main process with 4 distinct child processes; Temperature Sensor, LED Display, Flow Meter, and Smartkeg Server.

## Accessing Data Through the Web
Smartkeg serves current information about its contents with a python web server, and data is asynchronously updated with JavaScript.
