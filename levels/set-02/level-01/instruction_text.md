For this level, you could use a repeat loop. Instead, here are a few more commands to help you out.
### The forever loop
Repeats until the robot runs out of charge
```
forever{
    command;
    ...
}
```
### Sensing
Checks if the tile directly in front of the robot is safe and remembers it for later use
(`look;` counts as an action — it consumes time and energy)
```
look;
```
### Conditionals
Only execute the inner code based on the stored value from the previous `look;` command
```
ifOpen{
    command;
    ...
}
ifClosed{
    command;
    ...
}
```