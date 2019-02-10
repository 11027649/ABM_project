# ABM project: Traffic!
Interactions between pedestrians at crosswalks can have a significant effect on flow rates. Omitting this factor from traffic models could therefore result in poor design of traffic light systems. In order to better understand the extent of these effects, an agent based model was implemented, using the work of Liu et al. to model  pedestrian movement and the work of Nagel Schreckenberg as a base for cars. The flow rates of pedestrians and cars were examined over pedestrian densities ranging from 5 to 160 pedestrians in the field with 3 different traffic light strategies. Local and global sensitivity analyses were then performed on the four most important parameters. 

For the ABM project in our Master, we have implemented an Agent-Based Model for a small conjunction.

![picture of road](https://github.com/11027649/ABM_project/blob/master/vids/abm.PNG)

## Authors
Cormac Berkery, (12288160)
Jordan Earle, (12297127)
Steven Schoenmaker, (10777679),
Natasja Wezel, (11027649),
Linda Wouters (11000139)

### Installation
pip install -r requirements.txt

### To run:
python run.py

The user will be asked whether they want to run the vizualisation or not - answer yes or no.
If answered no, you will be asked how often you want to run the model, and with how many iterations. Answer with integers.
