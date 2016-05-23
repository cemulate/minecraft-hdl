> # Status: Archived
> This repository should be considered archived and legacy. Code may be mostly functional, but may be rendered broken or obsolete by external changes since it was last maintained. This project has not and will not be further maintained barring a rewrite.

MinecraftHDL
============

This project attempts to be a basic "HDL" for minecraft redstone. As of now, it can compile all combinational logic, but the combinational logic must be specified with a list of equations in strictly sum-of-products form.

The output is generated in the form of a .schematic, which can be imported into any world using standard tools such as WorldEdit.

Due to the necessarily generic nature of the script, the output is surely not as compressed as it could be, but the script does generate fairly compact logic. 



`/tests` contains some sample input JSON files for the compiler:

* test1 is a test of the size and girth ability of the compiler. The equation for Y has a significantly wide input array, and a significantly long set of prime implicants.

* test2 is the logic for a seven segment display. The compiled schematic can be directly hooked up to a compatible seven segment display and work (using the convention described below in the remainder of this document)

* test3 is a trivial, simple example.



The convention used for the seven segment display outputs:

```
    SA  
SF       SB
    SG
SE       SC
    SD
```


##Input and Output conventions

Right now, input is specified in a `.json` file that contains the following entries:

* `inputs` -- a list of variable names

* `outputs` -- a list of variable names

* `equations` -- a list of strings containing boolean equations in sum-of-products form that give a single output in terms of any of the inputs

Equations can contain `&` for and, `|` for or, and `~` for not. Parenthesis must be around each minterm. A valid equation looks like:

```
Y = (A & ~B & ~C & ~D & ~E & ~F & G) | (A & B & G) | (A & F) | (F & G) | (G & ~E) | (A & B & C & D) | (D & E & F & G)
```

Both the inputs and the outputs on the physical structure will be ordered in the same way that the 'inputs' and 'outputs' lists are ordered in the input file.

Left to right in the input file corresponds to "from the inside of the logic rail" outward:

If your input file specifies:

```
"inputs": ["A", "B", "C"],
"outputs": ["X", "Y", "Z"],
```

your schematic (from the side), will appear as:

```
Y-axis
^
|
|
|
-------> Z-axis

 ___________
|            | ----X----Y----Z----   <== Output rail
|            |
|            |
|            |
|   LOGIC    |
|            |
|            |
|            | ----A----B----C----   <== Input rail
 -----------
 ```
