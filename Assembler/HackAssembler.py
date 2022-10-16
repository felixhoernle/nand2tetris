import sys
from Parser import Parser
from Code import Code
from SymbolTable import SymbolTable

# Coordinates the ASM-file parsing process and assembles code to an output Hack-file
class HackAssembler:

    # Initializes a HackAssembler instance and creates a Hack binary code file
    def __init__(self):
        # Get input argument which is the ASM-file to be assembled into Hack binary code
        filename = sys.argv[1]
        # Create a Parser instance for a first parse to build the symbol table
        preparser = Parser(filename)
        # Create a Symbol Table
        symtable = SymbolTable()
        # Carry out first parse and build up symbol table, initializin the line counter with 0
        lineCounter = 0
        # Parse all commands and add symbols to table while keeping track of the line number
        while preparser.hasMoreCommands() == True:
                # Move ahead one line in the list of ASM-commands
                preparser.advance()
                # In case of an A- or C-instruction, increase line counter by 1
                if (preparser.commandType() == 'A_COMMAND' or preparser.commandType() == 'C_COMMAND'):
                    lineCounter += 1
                # In case of a label declaration, add symbol to the symbol table
                elif preparser.commandType() == 'L_COMMAND':
                    symtable.addEntry(preparser.symbol(), lineCounter)
        # Create a Code instance and a second Parser instance for the main parse of the ASM-file
        decoder = Code()
        parser = Parser(filename)
        # Initialize counter for variables
        varCounter = 0
        # Create hack-file and prepare it for writing
        with open(filename.split('.')[0] + '.hack', 'w') as hack:
            # Parse all commands and write hack binary code to the hack-file
            while parser.hasMoreCommands() == True:
                # Move ahead one line in the list of ASM-commands
                parser.advance()
                # In case of an A-instruction, write 16-bit binary representation of the address to the Hack-file
                if parser.commandType() == 'A_COMMAND':
                    # If address is numeric, write 16-bit binary representation to file (cut leading '0b' after conversion)
                    if parser.symbol().isnumeric() == True:
                        hack.write(str(bin(int(parser.symbol()))[2:]).zfill(16))
                    # If address is a symbol, get address from symbol table and write 16-bit binary representation to file (cut leading '0b' after conversion)
                    elif symtable.contains(parser.symbol()): 
                        hack.write(str(bin(symtable.getAddress(parser.symbol()))[2:]).zfill(16))
                    # Else it's a variable symbol --> Add it to the symbol table and write to hack
                    else:
                        # Add entry to symbol table starting with address 16 (RAM[16])
                        symtable.addEntry(parser.symbol(), varCounter+16)
                        # Write 16-bit binary representation to file (cut leading '0b' after conversion)
                        hack.write(str(bin(varCounter+16)[2:]).zfill(16))
                        # Increase variable counter
                        varCounter += 1
                # In case of a C-instruction, build up 16-bit binary representation and write it to Hack-file
                elif parser.commandType() == 'C_COMMAND':
                    hack.write('111' + decoder.comp(parser.comp()) + decoder.dest(parser.dest()) + decoder.jump(parser.jump()))
                # If there are more ASM-commands and current command was not a label declaration, then write a new line
                if (parser.hasMoreCommands() == True) and (parser.commandType() != 'L_COMMAND'):
                    hack.write('\n')

# Create a HackAssembler instance which kicks off the assembly process 
assemble = HackAssembler()