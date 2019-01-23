# ABM project: Traffic!
For the ABM project in our Master, we will try to implement an Agent-Based traffic model.

## Authors
Cormac Berkery, (12288160)
Jordan Earle, (12297127)
Steven Schoenmaker, (10777679),
Natasja Geitje Wezel, (11027649),
Linda Wouters (11000139)

## Planning
## Basic model:
### Evironment:
* Single grid

Pedestrian:
* One lane up
* One lane down

Car:
* One lane to the left
* One lane to the right

* Traffic lights (nonphysical)
* Cars leave one cell open in front of the pedestrian lanes


### Agents:
Pedestrian
* Occupies one cell
* Speed 1 cell per timestep
* If green go, if red stop

Car
* Occupies 2x3 cells
* Speed 1 cell per timestep
* If green and no pedestrian in front

### Flow
* Cars
* Pedestrians spawn with exponential distribution with mean=3



## TODO:
- Drive into the grid/ drive out of the grid for cars: measure waiting time for level of service
- Pedestrians: spawn around the same distance, also measure time of crossing for los

- Nagel-Schreckenberg for cars
- Different pedestrian spawning? Also nagel-schreckenberg? (waves)
- Multiple lanes for pedestrians
- Acceleration

- Figure out what kind of updating schedule to use (Random for now?)

Crowding
- Continuous grid
- Vision
- Rules if light goes orange
- Determine size of agents and road


Experimentation
- Middle part
- Go through red or no light (rules)
- Different red/green strategies

- Interface

## Look up
- How and if we want to use Nagel-Schreckenberg for the cars
- Flow we want to use for the pedestrians
- What crowd dynamics we want to use for pedestrians
