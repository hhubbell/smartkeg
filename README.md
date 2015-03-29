# Smartkeg
##### By: Harrison Hubbell and  Christopher Young

Accurate demand forecasting is critical to successful long term business strategy. Using smarter, integrated monitoring systems for food and beverage consumption, retailers are able to take advantage of lean "JIT" supply practices, and benefits of lowered holding costs and higher satisfaction of demand are able to be realized.  Using Time Series Regression and Continuous Review Modeling the Smartkeg can accurately forecast stock supply and demand levels, and propagate this information to a wide range of interconnected devices.

The system is currently designed to be run on a Raspberry Pi board with Arch Linux ARM Operating System.  The Smartkeg system logs refrigerator temperature and beer temperature using a 3-pin temperature sensor, and consumption rates are logged using a 3-pin flow meter.  These peripherals are connected to the Raspberry Pi's GPIO pins.  The machine uses historic consumption data to build future predictions, allowing users to be notified when a refill will be necessary - and gives alerts via a web interface, which is served up through the Raspberry Pi on a simple Python stack.

## Status
This project is under active development.

## Getting Started
To try the Smartkeg Keg Monitoring system out, pull down a copy of the source onto a Raspberry Pi ARM board running Arch Linux ARM.  Modify the config.cfg.TEMPLATE file to your liking, save it as config.cfg, and run the following in the Smartkeg root directory:

```Shell
# ./build
```

Easy as that!

#### How the Build Script Works
##### Dependency Check
**Note:** This step can be skipped by including the following argument: `--no-check`

Smartkeg has the following dependencies, and the build script will check first to see if you have the following installed:

* MySQL/MariaDB
* pip
* MySQL-python
* RPi.GPIO
* qrcode
* pywebkitgtk

##### Database
**Note:** This step can be skipped by including the following argument: `--no-db`

The build script will also configure the MySQL database user and create the required tables; it will require user access with `CREATE/DROP` rights to the MySQL database.  

##### Installation
The build script will make a copy of the Smartkeg source code into the systems `/usr/local/src/` directory, and create the service files.

#### Post Install
The build script creates a systemd service file for the Smartkeg system. To run the Smartkeg system at startup on Arch Linux, run the following:
```Shell
# systemctl enable smartkeg
```

## History
Originally, the Smartkeg system scope was to gather information using distinct processes and let a web server handle displaying the information to the user; this had some very distinct drawbacks.  First, and most important, was interprocess communication.  By creating a main process that is responsible for spawning, managing, and maintaining communication with other child processes, the system becomes much more robust; the main process is now able to see into all the seperate elements of the system and asynchronously create new data models, update server responses, and read/write to the database.

Of course, this comes at a cost; particularly, the cost of developing these processes is much higher than combining pre-built components.  Large scale web servers had too large a footprint for the Smartkeg's needs.  The system required the optimal amount of control of how data is transmitted to different client devices at the lowest possible expense.

Ultimately, the Smartkeg system is lean, intellegent, responsive, and fast.  The system is able to quickly respond to each new request instantly, and push new data to clients with minimal overhead.
