# Try it out

### Setup Environment
`uv sync`

### Run tests
`uv run pytest`

### See parser tree for specific file
`uv run python -m decom tests/scripts/<path>.decom`

# Examples

## Example 1: simple.decom

Input:
```
B1 = [1];
B2 = [2]
B3 = [3:1-4 + 4];
B4 = [5+6R];2c
B5 = [7+8];2c;EUC[1,2,3]
B6 = [7+8];2c;[1.0e2,2e+3,3e-4]
B7 = [(5+6)R]
```
Output:
```
start
  value
    measurand
      name      B1
      parameter 1
  value
    measurand
      name      B2
      parameter 2
  value
    measurand
      name      B3
      parameter
        3:1-4
        4
  value
    measurand
      name      B4
      parameter
        5
        6R
      interp    2c
  value
    measurand
      name      B5
      parameter
        7
        8
      interp    2c
      euc
        1
        2
        3
  value
    measurand
      name      B6
      parameter
        7
        8
      interp    2c
      euc
        1.0e2
        2e+3
        3e-4
  value
    measurand
      name      B7
      parameter
        5
        6
        group_operator
```

## Example 2: Incldudes
```
INCLUDE=/absolute/path.decom
INCLUDE = ./relative/path.decom

parent1 = function_a(-arg val -arg val)
parent2.parent1 = function_b(args args)

B1 = [1];

parent.B7 = [7];
parent.USELIST = {
    Ch4 = [4:1-4];
}
```

```
start
  value
    include     /absolute/path.decom
  value
    include      ./relative/path.decom
  value
    function
      name      parent1
      function_a
      -arg
      val
      -arg
      val
  value
    function
      name
        parent2
        parent1
      function_b
      args
      args
  value
    measurand
      name      B1
      parameter 1
  value
    measurand
      name
        parent
        B7
      parameter 7
  value
    uselist
      parent
      measurand
        name    Ch4
        parameter       4:1-4
```