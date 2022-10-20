# Nand2Tetris Compiler

Compiler from high-level Jack language to binary Hack machine code.

## Description

This is a compiler that translates from a high-level language called Jack all the way down to binary machine code called Hack code, in three consecutive translation steps.

## Getting Started

### Dependencies

Written in Python 3.9, using the following libraries: sys, os, glob

### Installing

No installation needed, just download the whole project and execute it using Python.

### Executing program

To translate a program written in the high-level language Jack, three steps are necessary:

1) Execute the file 'JackCompiler.py' within the 'Compiler' folder to compile the Jack code into an intermediate virtual machine code (VM-code). This will create one VM-file for each Jack-file --> Jack Compiler needs one input argument which is the folder containing your Jack-program. Example:
```
python JackCompiler.py ExampleProgram
```

2) Execute the file 'VMTranslator.py' within the 'VM_Translator' folder to translate the VM-code into human-readable assembly code. This will create one ASM-file combining the code of all VM-files. --> VM Translator needs one input argument which is the folder containing your VM-files. Example:
```
python VMTranslator.py ExampleVMFolder
```

3) Execute the file 'HackAssembler.py' within the 'Assembler' folder to translate the human-readable assembly code into binary machine code called Hack code. This will create one HACK-file for each ASM-file --> Hack Assembler needs one input argument which is the ASM-file. Example:
```
python HackAssembler.py ExampleASMFile
```

The binary machine code (Hack-code) created after this three-step process can be exectuted on a CPU that works based on the Hack instructions set, or in a virtual Hack environment.

## Authors

The code was completely written by myself, in the course of the (excellent) Coursera course "nand2tetris".

## Version History

* 0.1
    * Initial Release

## Acknowledgments

Credits go to Shimon Schocken, Noam Nisan and their team for developing this course and providing it through Coursera.
* [nand2tetris Homepage](https://www.nand2tetris.org/)
* [Coursera Course nand2tetris](https://www.coursera.org/learn/nand2tetris2)