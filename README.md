# ForCoast-SM-R1

### Description

This service uses a backtracking simulation to find the potential source of contaminents. A location is chosen where the contaminents are present. The duration of the backtracking simulation and the start time of the simulation must also be set. A bulletin will be produced highlighting areas with a probability of it being the contaminents source.

### How to run

* Copy following from opendrift repo to this repo:
  * opendrift folder
  * environment.yml
  * setup.py
* Containerize contents in docker
* Run the command Docker run forcoast/forcoast-sm-r1 &lt;pilot> &lt;datetime> &lt;period> &lt;lon> &lt;lat> &lt;Telegram token> &lt;Telegram chat_id>
  * Where pilot is either "galway" or "southern_north_sea"
  * Where datetime is the start date and time
  * period is the length of the simulation in hours
  * Lon and lat are for the strat point of the simulation
  * Telegram bot is used for sendingh the bulletins through messaging services
* Example of use: Docker run forcoast/forcoast-sm-r1 galway 2022-09-11T00:00:00 8 -8.95 53.20 5267228188:AAGx60FtWgHkScBb3ISFL1dp6Oq_9z9z0rw -1001558581397

### Additional information

The code is based on the OpenDrift (https://opendrift.github.io/) particle-
tracking model. Contaminants are assumed to be perfect passive tracers. 
The procedure consists of entering a number of numerical drifters into the
model domain and track its motion.

### Licence

Licensed under GPL2.0
