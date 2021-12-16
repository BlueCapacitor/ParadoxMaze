# Paradox Maze
## This project is currently being completely reworked. A semi-operational and very glitchy version is currently in main, but it is highly unstable and very unfinished.
Among other things, the ingame rules and guide is currently nonexistant. For now, the rules are here.

Hopefully, you have seen and played a "program a robot" game in the past. If you have not, http://robozzle.com/ is a fun one. Paradox Maze is one of these games, but with a twist. In this game, the puzzles involve time travel as well, allong with other related mechanics. Here is the general outline of the gameplay: in each "room", you program a robot to traverse a tile map and reach every target tile (not neccessarily at the same time). Be carful not to run into walls, create paradoxes, or run out of energy (running out of energy does not neccessarely cause you to lose, but the robot stops where it is). Each move consumes one unit of energy for your robot, so economize your moves.

## How to program your robot
You code the robot in a micro-language with the following syntax.
### Program:
```
<Command, loop, or condition>;
<Command, loop, or condition>;
<Command, loop, or condition>;
...
```
### Comments
```
// Comment
```
### Basic commands
```
sleep;  // Wait one tick (still consumes one unit of energy)
fd;  // Move one block forward
lt;  // Rotate 90 degrees left (counter-clockwise)
rt;  // Rotate 90 degrees right (clockwise)
```
### Loops
Loops do not consume any energy or time
```
forever {  // Continue until the robot runs out of energy or the loop is broken out of
  <Command, loop, or condition>;
  <Command, loop, or condition>;
  <Command, loop, or condition>;
  ...
}
repeat(<N>) {  // Repeat N times or until the robot runs out of energy or the loop is broken out of
  <Command, loop, or condition>;
  <Command, loop, or condition>;
  <Command, loop, or condition>;
  ...
}
```
### Control flow
Control flow commands do not consume any energy or time
```
break;  // Breaks out of the innermost
stop;  // Completely halts the program
```
### Sensing
```
look;  // Same effect as sleep, but senses whether the path ahead (just the block infront of the robot) is clear
```
### Conditionals
Conditionals do not consume any energy or time
```
ifOpen {  // Only executes the block if the path ahead appeared safe the most recent time that look was performed (initially safe)
  <Command, loop, or condition>;
  <Command, loop, or condition>;
  <Command, loop, or condition>;
  ...
}
ifClosed {  // Only executes the block if the path ahead appeared blocked the most recent time that look was performed (initially safe)
  <Command, loop, or condition>;
  <Command, loop, or condition>;
  <Command, loop, or condition>;
  ...
}
```

## The tiles
Don't worry, they will be introduced gradually and with demonstrations

### Empty tile
Safe for your robot to occupy\
<img width="46" alt="Screen Shot 2021-09-21 at 8 04 52 PM" src="https://user-images.githubusercontent.com/32907199/134264186-92cbccaf-92e3-443f-89df-504614474703.png">
### Wall tile
Don't run into it\
<img width="46" alt="Screen Shot 2021-09-21 at 8 05 26 PM" src="https://user-images.githubusercontent.com/32907199/134264219-c7e2bac2-4963-4cac-8e8b-849c7c08a8a1.png">
### Target tile
Safely press each of these tiles to win the level\
<img width="46" alt="Screen Shot 2021-09-21 at 8 05 42 PM" src="https://user-images.githubusercontent.com/32907199/134264378-b10cbc50-52a4-4cab-9dbc-d05940e298ac.png">
### Portal tile
Enter this tile to be telleported to the matching destination tile (same color/letter)\
<img width="46" alt="Screen Shot 2021-09-21 at 8 06 36 PM" src="https://user-images.githubusercontent.com/32907199/134264496-039f75ed-a6bc-4b06-9336-d76f9760cbb5.png">
### Destination tile
Does nothing, but is the destenation for portal tiles\
<img width="46" alt="Screen Shot 2021-09-21 at 8 06 52 PM" src="https://user-images.githubusercontent.com/32907199/134264553-04ca10bb-11fb-46c5-8c59-ae2f0ef0b9bb.png">
### Hologram tile
Same thing as an empty tile, but it appears to be a wall to the `look` command\
<img width="46" alt="Screen Shot 2021-09-21 at 8 07 55 PM" src="https://user-images.githubusercontent.com/32907199/134264701-203f961c-1c63-4275-9ef4-60d3a0715000.png">
### Lava pit tile
Same thing as a wall, but it appears to be an empty tile to the `look` command\
<img width="46" alt="Screen Shot 2021-09-21 at 8 08 09 PM" src="https://user-images.githubusercontent.com/32907199/134264783-f3fd63c9-9c91-41e7-baf9-14cbcd568e93.png">
### Opening timed door tile
Opens when the timer runs out (counts as an empty tile at 0)\
<img width="46" alt="Screen Shot 2021-09-21 at 8 08 53 PM" src="https://user-images.githubusercontent.com/32907199/134264881-2f34b9f2-ae81-4c0f-9972-59863e23fc15.png">
### Closing timed door tile
Closes when the timer runs out (counts as a wall at 0)\
<img width="46" alt="Screen Shot 2021-09-21 at 8 09 21 PM" src="https://user-images.githubusercontent.com/32907199/134264899-75736fbb-7330-40a1-a97e-746b197f4201.png">
### Time portal tile
Sends the robot forward or backward in time (a -2 time portal only sends the robot to one tick before it entered the portal as one tick elapses to move onto it)\
<img width="46" alt="Screen Shot 2021-09-21 at 8 09 58 PM" src="https://user-images.githubusercontent.com/32907199/134265080-1195bf5a-6906-475b-8283-de7ff6e82446.png">
<img width="46" alt="Screen Shot 2021-09-21 at 8 10 24 PM" src="https://user-images.githubusercontent.com/32907199/134265093-eb9fbd37-67bb-4765-8cfa-c2f90a940855.png">
### Time gate tile
Sends the robot to a specific time\
<img width="46" alt="Screen Shot 2021-09-21 at 8 11 02 PM" src="https://user-images.githubusercontent.com/32907199/134265128-8e8262f7-8de1-4702-bb7f-baf412d5ac9d.png">
### Button tile
Triggers any connected doors\
<img width="46" alt="Screen Shot 2021-09-21 at 8 12 22 PM" src="https://user-images.githubusercontent.com/32907199/134265168-1837b137-3861-4048-bcbd-6be09e7ce281.png">
### Opening logical door tile
Opens when any connected button tiles are triggered (a button is connected if it has the same color/number)\
<img width="46" alt="Screen Shot 2021-09-21 at 8 12 36 PM" src="https://user-images.githubusercontent.com/32907199/134265210-25c979ea-75a4-4d97-b4bb-f00c012f604e.png">
### Closeing logical door tile
Closes when any connected button tiles are triggered (a button is connected if it has the same color/number)\
<img width="46" alt="Screen Shot 2021-09-21 at 8 14 01 PM" src="https://user-images.githubusercontent.com/32907199/134265298-4671389d-4890-4b6c-b5f6-898506aa056a.png">

## The time travel system
The time travel system is centered around the idea that **there are no paradoxes. Any event that had occured in a timeline will be caused and any effect that a robot causes will have already happened.** There is complete (if potentially circular) cause and effect. There is no spliting of timelines. You may have noticed, however, that there could sometimes be multiple possible and valid timelines. All of them will be tested and **all valid timelines must result in a success for you to win**. Also, it can occur that there are no valid timelines (ie. all possibilities are paradoxical such as if the robot triggers a button that causes a door to close on it in the past and never reach the button). In this case, you lose.

This may be confusing. Here is an example that will hopfully clear things up:\
<img width="320" alt="Screen Shot 2021-09-21 at 8 48 39 PM" src="https://user-images.githubusercontent.com/32907199/134266327-67aa99a9-fc15-4b62-bcfd-589c1c311fa2.png">\
In this case the robot must trigger one of the two button tiles to open the door and win. However, one of the buttons is after the door and if the robot presses the other, it will be trapped and unable to reach the door. This puzzle might seem unsolvable at first but the solution is like this. The robot must move forward and look at the door. If the door is closed, then it should immediately go right and push the button. This will cause the door to have been opened. The robot would then be trapped after pushing the button, but it does not matter as **this will never happen!** Beause of this code, the door could not have been closed as that would cause your robot to have pushed the button and oppened it. That would be contradictory, so that timeline does not occur. The door must be open. Now, if the door is open, you might be tempted to head directly for the target tile. The path is clear, you just have to go forward, right? No! If you head staight for the target tile, then nothing would have caused the door to be open which is imposible! The situation of the door being open would be paradoxical as well, so there would be no possible timelines. To avoid this, you must turn right and press the button immediately after passing the door. This will be the cause for the effect of the door being open. Then you can proceed to the target tile.\
There are two important things to note about this situation. First, though the door will never be closed, the code dealing with if it were is still neccessary though it will never be run. Second, it is neccessary to push the button after crossing the door, even though you have already crossed and it is not neccessary by that point. For anyone interested in philosophy, this has **everything** to do with [Newcombs Paradox](https://en.wikipedia.org/wiki/Newcomb%27s_paradox).\
Here is the solution code:
'''
fd;
look;
ifClosed {
	rt;
	repeat(3) {fd;}
}
ifOpen {
	fd; fd;
	rt;
	repeat(3) {fd;}
	rt; rt;
	repeat(3) {fd;}
	rt;
	fd;
}
'''

https://user-images.githubusercontent.com/32907199/134340340-d9c19de4-bdae-41df-877e-e511f6dc0b15.mov
