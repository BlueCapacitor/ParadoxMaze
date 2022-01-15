### Break
The `break;` keyword immediately exits the outermost loop (`forever` or `repeat`).
For example,
```
forever{
    look;
    fd;
    ifClosed{
        break;
    }
}
```
### Continue
The `continue;` keyword immediately skips the rest of the innermost loop and returns to the beginning if necessary. If in a repeat loop on its final iteration, the `continue;` command is equivalent to a `break;` command.
### Stop
The `stop;` keyword immediately halts the code.