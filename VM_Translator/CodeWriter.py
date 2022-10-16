# This module translates a parsed VM command into Hack assembly code
class CodeWriter:
    
    # This constructor opens an .asm-output file, prepares it for writing and writes some bootstrap code
    def __init__(self, filename):
        self.asmfile = open(filename.split('.')[0] + '.asm', 'w')
        # This dictionary translates between VM language and Hack assembly code arithmetic-logical commands
        self.ops_VM_to_As = {"eq": "JEQ", "lt": "JLT", "gt": "JGT", "add": "+", "sub": "-", "neg": "-", "not": "!", "and": "&", "or": "|"}
        # This dictionary translates between VM language memory segments and corresponding Hack assembly code pointers
        self.pointer_name = {"constant": "SP", "local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": "5", "pointer": "3"}
        # Initialize a label counter to ensure unique labels for jumps
        self.labelCounter = 0
        # Initialize a variable to store the current function name
        self.current_function = ''
        # Initialize a counter to keep track of the number of times a function generates a call
        self.call_counter   = 0
        # Write the assembly instructions that effect the bootstrap code that starts the program's execution
        self.asmfile.write('// Bootstrap code\n')
        # Set SP (stack pointer) to 256
        self.asmfile.write('@256\n')
        self.asmfile.write('D=A\n')
        self.asmfile.write('@SP\n')
        self.asmfile.write('M=D\n')
        # Call OS-function 'Sys.init', which in turn per convention should then call the VM function 'Main.main'
        self.current_function = 'Sys.init'
        self.writeCall('Sys.init', '0')

    # Updates the file name when the translation of a new VM file has started
    def setFileName(self, fileName):
        self.fileNameVM = fileName

    # Writes assembly code that effects the label command
    def writeLabel(self, label):
        # Set label of form '(functionName$label)'
        self.asmfile.write('(' + self.current_function + '$' + label + ')\n')

    # Writes assembly code that effects the if-goto command
    def writeIf(self, label):
        # Decrement stack pointer and store register value to D
        self.asmfile.write('@SP\n')
        self.asmfile.write('AM=M-1\n')
        self.asmfile.write('D=M\n')
        # Set A-register to mapped location of 'functionName$label' and write a conditional jump to address A if D != 0
        self.asmfile.write('@' + self.current_function + '$' + label + '\n')
        self.asmfile.write('D;JNE\n')

    # Writes assembly code that effects the goto command
    def writeGoTo(self, label):
        # Set A-register to mapped location of 'functionName$label' and write an unconditional jump to address A
        self.asmfile.write('@' + self.current_function + '$' + label + '\n')
        self.asmfile.write('0;JMP\n')

    # Writes assembly code that effects the function command
    def writeFunction(self, fname, nvars):
        # Reset call counter to 0 as we are now writing a new function
        self.call_counter   = 0
        # Store function name and set a function entry label of form '(functionName)'
        self.current_function = fname
        self.asmfile.write('(' + fname + ')\n')
        # Set A-register to stack pointer base address (M)
        self.asmfile.write('@SP\n')
        self.asmfile.write('A=M\n')
        # For each of the nvars function variables, set (initialize) the variable to 0 and increment stack pointer
        for i in range(nvars):
            self.asmfile.write('M=0\n')
            self.asmfile.write('@SP\n')
            self.asmfile.write('AM=M+1\n')

    # Writes assembly code that effects the call command
    def writeCall(self, fname, nargs):
        # Push return address to stack by using a pointer to the return address label 'functionName$ret.i'
        # Set A-register to function return address label 'functionName$ret.i', store address to D and push D to the stack
        self.asmfile.write('@' + self.current_function + '$ret.' + str(self.call_counter) + '\n')
        self.asmfile.write('D=A\n')
        self.pushD_to_stack()
        # Get pointer base addresses for local/argument/this/that and push these base addresses to the stack
        for pointer in ['LCL', 'ARG', 'THIS', 'THAT']:
            self.asmfile.write('@' + pointer + '\n')
            self.asmfile.write('D=M\n')
            self.pushD_to_stack()
        # Reposition ARG
        # Store number of arguments (nargs) to D
        self.asmfile.write('@' + nargs + '\n')
        self.asmfile.write('D=A\n')
        # Add 5 to D, because return label/local/argument/this/that have been pushed on stack --> nargs + 5
        self.asmfile.write('@5\n')
        self.asmfile.write('D=D+A\n')
        # Deduct (nargs+5) from current stack pointer base address and store to D
        self.asmfile.write('@SP\n')
        self.asmfile.write('D=M-D\n')
        # Locate ARG pointer and set ARG base address to (stack pointer base address - nargs - 5)
        self.asmfile.write('@ARG\n')
        self.asmfile.write('M=D\n')
        # Reposition LCL
        # Locate stack pointer and store stack pointer base address to D
        self.asmfile.write('@SP\n')
        self.asmfile.write('D=M\n')
        # Locate LCL pointer and set local base address to D (stack pointer base address)
        self.asmfile.write('@LCL\n')
        self.asmfile.write('M=D\n')
        # Set A-register to functionName and execute and unconditional jump to this address (i.e. call the function)
        self.asmfile.write('@' + fname + '\n')
        self.asmfile.write('0;JMP\n')
        # Set return address label ('functionName$ret.i') and increase call counter by 1
        # After the called function finishes it will return to this label
        self.asmfile.write('(' + self.current_function + '$ret.' + str(self.call_counter) + ')\n')
        self.call_counter += 1

    # Writes assembly code that effects the return command
    def writeReturn(self):
        # Set A-register to 'local base address - 5', which is the address containing the function return address
        self.asmfile.write('@LCL\n')
        self.asmfile.write('D=M\n')
        self.asmfile.write('@5\n')
        self.asmfile.write('A=D-A\n')
        # Get register value at that address (value is the function return address), and store it to RAM[13]
        self.asmfile.write('D=M\n')
        self.asmfile.write('@R13\n')
        self.asmfile.write('M=D\n')
        # Pop function return address to ARG0 (i.e. overwrite ARG0)
        self.writePushPop('C_POP', 'argument', 0)
        # Set stack pointer base address to ARG1
        self.asmfile.write('D=A+1\n')
        self.asmfile.write('@SP\n')
        self.asmfile.write('M=D\n') 
        # Restore the 4 pointer base addresses which are located at LCL - 1/2/3/4
        for pointer, reverse in zip(['THAT', 'THIS', 'ARG', 'LCL'], ['1', '2', '3', '4']):
            # Set address to 'LCL base address-reverse' (e.g. LCL-2)
            self.asmfile.write('@' + reverse + '\n')
            self.asmfile.write('D=A\n')
            self.asmfile.write('@LCL\n')
            self.asmfile.write('A=M-D\n')
            # Store value at that address (which is one of the pointer addresses to be restored) to D
            self.asmfile.write('D=M\n') 
            # Update the pointer with the pointer base address just retrieved
            self.asmfile.write('@' + pointer + '\n')
            self.asmfile.write('M=D\n')
        # Fetch function return address from RAM[13] and unconditionally jump to it
        self.asmfile.write('@R13\n')
        self.asmfile.write('A=M\n')
        self.asmfile.write('0;JMP\n')

    # Writes to the output file the assembly code that implements the given push/pop command
    def writePushPop(self, command, segment, index):
        # Pushes the register value at 'segment index' (e.g. 'argument 0') to the stack
        if command == 'C_PUSH':
            # Ensure segment is a valid segment
            if segment in ['constant', 'local', 'argument', 'this', 'that', 'temp', 'pointer', 'static']:
                # If segment is 'static', set address to the unique assembly symbol "FileName.i"
                # The Hack assembler maps this symbolic variable on the host RAM, starting at address 16.
                # Access this mapped address register value and store it to D
                if segment == 'static':
                    self.asmfile.write('@' + self.fileNameVM + '.' + str(index) + '\n')
                    self.asmfile.write('D=M\n')
                # Else find index address within segment and store that adresses' register value to D
                else:
                    # Store index value to D-register (for a 'constant' this is all that has to be done)
                    self.asmfile.write('@' + str(index) + '\n')
                    self.asmfile.write('D=A\n')
                    # For all other segments...
                    if segment in ['local', 'argument', 'this', 'that', 'temp', 'pointer']:
                        # Set A-register to segment pointer location
                        self.asmfile.write('@' + self.pointer_name[segment] + '\n')
                        # For temp/pointer segments, add index value (D) to to segment pointer location (A) and update A-register
                        if segment in ['temp', 'pointer']:
                            self.asmfile.write('A=D+A\n')
                        # For local/argument/this/that segments, update A-register to pointer base address (M) + index value (D)
                        else:
                            self.asmfile.write('A=D+M\n')
                        # Store register value of that address to D
                        self.asmfile.write('D=M\n')
                # Push D to stack
                self.pushD_to_stack()
        # Pops the top-most stack value and saves it into the register at 'segment index' (e.g. 'argument 0')
        elif command == 'C_POP':
            # Ensure segment is a valid segment
            if segment in ['local', 'argument', 'this', 'that', 'temp', 'pointer', 'static']:
                # If segment is 'static', set address to the unique assembly symbol "FileName.i"
                # The Hack assembler maps this symbolic variable on the host RAM, starting at address 16.
                # Set A-register to this mapped address and store the address (the pop-target address) to D
                if segment == 'static':
                    self.asmfile.write('@' + self.fileNameVM + '.' + str(index) + '\n')
                    self.asmfile.write('D=A\n')
                # Else store index to D and locate pointer of respective segment
                else:
                    self.asmfile.write('@' + str(index) + '\n')
                    self.asmfile.write('D=A\n')
                    self.asmfile.write('@' + self.pointer_name[segment] + '\n')
                # For temp/pointer segments, add up pointer location (A) and index value (D), then store to D
                if segment in ['temp', 'pointer']:
                    self.asmfile.write('D=A+D\n')
                # For local/argument/this/that segments, add up pointer base address (M) and index value (D), then store to D
                elif segment in ['local', 'argument', 'this', 'that']:
                    self.asmfile.write('D=M+D\n')
                # We now have the pop target address stored in D, though still need the value to be popped
                # Decrement stack pointer and add register value (the value to be popped) to D
                self.asmfile.write('@SP\n')
                self.asmfile.write('AM=M-1\n')
                self.asmfile.write('D=D+M\n')
                # Locate target address (which was D earlier, but is now D-M because we just added M)
                self.asmfile.write('A=D-M\n')
                # Save popped value (which is now D-A) to target address register
                self.asmfile.write('M=D-A\n')

    # Writes to the output file the assembly code that implements the given arithmetic-logical command
    def writeArithmetic(self, command):
        # If it is an addition or subtraction...
        if command in ['add', 'sub']:
                # Decrement stack pointer and save register value to D
                self.asmfile.write('@SP\n')
                self.asmfile.write('AM=M-1\n')
                self.asmfile.write('D=M\n')
                # Decrement stack pointer again and add D to RAM-value
                self.asmfile.write('AM=M-1\n')
                self.asmfile.write('M=M' + self.ops_VM_to_As[command] + 'D\n')
                # increment stack pointer
                self.asmfile.write('AM=M+1\n')
        # If it is an arithmetic comparison...
        elif command in ['eq', 'gt', 'lt']:
                # Decrement stack pointer and save register value to D
                self.asmfile.write('@SP\n')
                self.asmfile.write('AM=M-1\n')
                self.asmfile.write('D=M\n')
                # Decrement stack pointer and update D=M-D
                self.asmfile.write('AM=M-1\n')
                self.asmfile.write('D=M-D\n')
                # Jump to (TRUE) if arithmetic comparison of D with 0 yields true
                self.asmfile.write('@TRUE' + str(self.labelCounter) + '\n')
                self.asmfile.write('D;' + self.ops_VM_to_As[command] + '\n')
                # Else store 0 (false) to D and unconditionally jump to (STORE)
                self.asmfile.write('D=0\n')
                self.asmfile.write('@STORE' + str(self.labelCounter) + '\n')
                self.asmfile.write('0;JMP\n')
                # Set (TRUE) label
                self.asmfile.write('(TRUE' + str(self.labelCounter) + ')\n')
                # Store -1 (true) to D
                self.asmfile.write('D=-1\n')
                # Set (STORE) label and increase counter
                self.asmfile.write('(STORE' + str(self.labelCounter) + ')\n')
                self.labelCounter += 1
                # Push truth value to stack
                self.pushD_to_stack()
        # If it is an arithmetic or logical negation...
        elif command in ['neg', 'not']:
            # Decrement stack pointer, update (negate) register value and increment stack pointer again
            self.asmfile.write('@SP\n')
            self.asmfile.write('AM=M-1\n')
            self.asmfile.write('M=' + self.ops_VM_to_As[command] + 'M\n')
            #self.asmfile.write('@SP\n')
            self.asmfile.write('AM=M+1\n')
        # If it is a boolean and/or...
        elif command in ['and', 'or']:
            # Decrement stack pointer and save register value to D
            self.asmfile.write('@SP\n')
            self.asmfile.write('AM=M-1\n')
            self.asmfile.write('D=M\n')
            # Decrement stack pointer and compare register value to D, store boolean result to register
            self.asmfile.write('AM=M-1\n')
            self.asmfile.write('M=M' + self.ops_VM_to_As[command] + 'D\n')
            # Increment stack pointer
            self.asmfile.write('AM=M+1\n')

    # Closes the output file
    def close(self):
        self.asmfile.close()

    # This method pushes the value of the D-register to the top of the stack
    def pushD_to_stack(self):
        # Set address to top of stack
        self.asmfile.write('@SP\n')
        self.asmfile.write('A=M\n')
        # Push D to top of stack and increment stack pointer
        self.asmfile.write('M=D\n')
        self.asmfile.write('@SP\n')
        self.asmfile.write('AM=M+1\n')

