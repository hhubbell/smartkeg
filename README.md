# Smartkeg

##### By: Harrison Hubbell and  Christopher Young

Never run out of beer with smarter, integrated, monitoring systems.

### Status
This project is still under construction; some parts are currently not in a working state, while others may not have been implemented yet.

### How it works
Smartkeg logs refrigerator temperature, beer temperature, and consumption rates to help facilitate ordering and cost management.  The machine uses historic consumption data and future predictions to analyze when a refill will be necessary - and gives alerts via email and a web interface, which is served up through the Raspberry Pi on a simple Python stack.

### History
Originally, we scoped the project to gather information using distinct processes and let a web server handle displaying the information to the user.  This had some very distinct drawbacks:
1. Contention
2. Data Sharing
3. Bloat

### Today
Smartkeg is driven by a main process with 4 distinct child processes; Temperature Sensor, LED Display, Flow Meter, and Smartkeg Server.

### Accessing Data Through the Web
Smartkeg serves current information about its contents with a python web server, and data is asynchronously updated with JavaScript.
