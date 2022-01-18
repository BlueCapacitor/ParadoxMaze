Alright, time for subroutines (functions)! You have seen this level before. Let's solve it better this time.

Here is how to define a subroutine:
```
def(subroutine_name){
    code;
    code;
    ...
}
```

And to call it, use:
```
fun(subroutine_name);
```

Note that these subroutines can not have any arguments or return values.

**Also, make sure to define the subroutine *before* you call it.**

The program looks for the subroutine definition as soon as the `fun` command is called (not necessarily as soon as it is parsed).