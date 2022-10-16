import sys

# Define constants
C_ARITHMETIC = 'C_ARITHMETIC'
C_PUSH = 'C_PUSH'
C_POP = 'C_POP'
C_LABEL = 'C_LABEL'
C_GOTO = 'C_GOTO'
C_IF = 'C_IF'
C_FUNCTION = 'C_FUNCTION'
C_RETURN = 'C_RETURN'
C_CALL = 'C_CALL'
ARITHMETIC_CLIST = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

# Use first call argument as filename
filename = sys.argv[1]

# Parser class
class Parser:
    def __init__(self, vmfile):
        # Open file as list of single lines
        with open(vmfile) as file_object:
            self.vmfile = file_object.readlines()
        #Remove comments (leaves empty lines for full-line comments)
        for j in range(len(self.vmfile)):
            if self.vmfile[j].find("//") >= 0:
                self.vmfile[j] = self.vmfile[j].split('//')[0]
        #Remove empty lines
        for i in range(self.vmfile.count('\n')):
            self.vmfile.remove('\n')
        for p in range(self.vmfile.count('')):
            self.vmfile.remove('')
        #Remove white space
        for k in range(len(self.vmfile)):
            self.vmfile[k] = self.vmfile[k].strip()

        self.current_command = ''
        self.commands_left = (len(self.vmfile) > 0)

    def hasMoreCommands(self):
        self.commands_left = (len(self.vmfile) > 0)
        return self.commands_left

    def advance(self):
        self.current_command = self.vmfile.pop(0)

    def commandType(self):
        if self.current_command.split()[0].casefold() == 'push':
            return C_PUSH
        elif self.current_command.split()[0].casefold() == 'pop':
            return C_POP
        elif self.current_command.split()[0].casefold() in ARITHMETIC_CLIST:
            return C_ARITHMETIC

    def arg1(self):
        if self.commandType() == C_ARITHMETIC:
            return self.current_command.split()[0].casefold()
        elif self.commandType() != C_RETURN:
            return self.current_command.split()[1].casefold()
        else:
            return 'C_RETURN has no arg1'

    def arg2(self):
        if self.commandType() in [C_PUSH, C_POP, C_FUNCTION, C_CALL]:
            return self.current_command.split()[2].casefold()
        else:
            return 'Only PUSH/POP/FUNCTION/CALL arguments have arg2'

# CodeWriter Class
class CodeWriter:
    def __init__(self, filename):
        self.asmfile = open(filename.split('.')[0] + '.asm', 'w')
        self.operators = {"eq": "JEQ", "lt": "JLT", "gt": "JGT", "add": "+", "sub": "-", "neg": "-", "not": "!", "and": "&", "or": "|"}
        self.pointer_name = {"constant": "SP", "local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT", "temp": "5", "pointer": "3"}
        self.jump_counter = 0

    def writePushPop(self, command, segment, index):
        if command == C_PUSH:
            if segment in ['constant', 'local', 'argument', 'this', 'that', 'temp', 'pointer', 'static']:
                # Set segment address (or constant value for constant)
                if segment == 'static':
                    self.asmfile.write('@Foo.' + str(index) + '\n')
                    self.asmfile.write('D=M\n')
                else:
                    self.setSegmentAddress(segment, index)
                # Go to RAM[SP]
                self.asmfile.write('@SP\n')
                self.asmfile.write('A=M\n')
                # RAM[SP] = D and increment pointer
                self.asmfile.write('M=D\n')
                self.incrementPointer('SP')
        elif command == C_POP:
            if segment in ['local', 'argument', 'this', 'that', 'temp', 'pointer', 'static']:
                # Get target address and save to D
                if segment == 'static':
                    self.asmfile.write('@Foo.' + str(index) + '\n')
                    self.asmfile.write('D=A\n')
                else:
                    self.asmfile.write('@' + str(index) + '\n')
                    self.asmfile.write('D=A\n')
                    self.asmfile.write('@' + self.pointer_name[segment] + '\n')
                if segment in ['temp', 'pointer']:
                    self.asmfile.write('D=A+D\n')
                elif segment in ['local', 'argument', 'this', 'that']:
                    self.asmfile.write('D=M+D\n')
                # Get last stack element and add to D
                self.decrementPointer('SP')
                self.asmfile.write('D=D+M\n')
                # Change address to target address
                self.asmfile.write('A=D-M\n')
                # Save D-A in target address
                self.asmfile.write('M=D-A\n')

    def writeArithmetic(self, command):
        if command in ['add', 'sub']:
                # D = y
                self.decrementPointer('SP')
                self.asmfile.write('D=M\n')
                # Update RAM to x +/- y at RAM location of x
                self.decrementPointer('SP')
                self.asmfile.write('M=M' + self.operators[command] + 'D\n')
                # Increment pointer
                self.incrementPointer('SP')
        elif command in ['eq', 'gt', 'lt']:
                # Get y into D
                self.decrementPointer('SP')
                self.asmfile.write('D=M\n')
                # Get x, calculate x-y and check in relation to 0, jump to (TRUE) if condition is satisfied
                self.decrementPointer('SP')
                self.asmfile.write('D=M-D\n')
                self.asmfile.write('@TRUE' + str(self.jump_counter) + '\n')
                self.asmfile.write('D;' + self.operators[command] + '\n')
                # Else store 0 (false) to D and unconditionally jump to memory write
                self.asmfile.write('D=0\n')
                self.asmfile.write('@STORE' + str(self.jump_counter) + '\n')
                self.asmfile.write('0;JMP\n')
                # Store -1 (true) to D if condition was satisfied
                self.asmfile.write('(TRUE' + str(self.jump_counter) + ')\n')
                self.asmfile.write('D=-1\n')
                # Store result to stack
                self.asmfile.write('(STORE' + str(self.jump_counter) + ')\n')
                self.asmfile.write('@SP\n')
                self.asmfile.write('A=M\n')
                self.asmfile.write('M=D\n')
                self.incrementPointer('SP')
                self.jump_counter += 1
        elif command in ['neg', 'not']:
            self.decrementPointer('SP')
            self.asmfile.write('M=' + self.operators[command] + 'M\n')
            self.incrementPointer('SP')
        elif command in ['and', 'or']:
            # D = y
            self.decrementPointer('SP')
            self.asmfile.write('D=M\n')
            # Update RAM to x &/| y at RAM location of x
            self.decrementPointer('SP')
            self.asmfile.write('M=M' + self.operators[command] + 'D\n')
            # Increment pointer
            self.incrementPointer('SP')

    def close(self):
        self.asmfile.close()

    # pointer++ incl. A-update
    def incrementPointer(self, pointer):
        self.asmfile.write('@' + pointer + '\n')
        self.asmfile.write('AM=M+1\n')
       
    # pointer-- incl. A-update
    def decrementPointer(self, pointer):
        self.asmfile.write('@' + pointer + '\n')
        self.asmfile.write('AM=M-1\n')

    def setSegmentAddress(self, segment, index):
        # D = arg2 for constant segment
        self.asmfile.write('@' + str(index) + '\n')
        self.asmfile.write('D=A\n')
        # D RAM[base-address + index] for other segments
        if segment in ['local', 'argument', 'this', 'that', 'temp', 'pointer']:
            self.asmfile.write('@' + self.pointer_name[segment] + '\n')
            if segment in ['temp', 'pointer']:
                self.asmfile.write('A=D+A\n')
            else:
                self.asmfile.write('A=D+M\n')
            self.asmfile.write('D=M\n')

# Create a new Parser and CodeWriter instance
parser = Parser(filename)
codewriter = CodeWriter(filename)

while parser.hasMoreCommands() == True:
    parser.advance()
    codewriter.asmfile.write('// ' + parser.current_command + '\n')
    if parser.commandType() in [C_PUSH, C_POP]:
        codewriter.writePushPop(parser.commandType(), parser.arg1(), int(parser.arg2()))
    elif parser.commandType() == C_ARITHMETIC:
        codewriter.writeArithmetic(parser.arg1())
            
# Create an infinite loop at end of ASM-file and close it
codewriter.asmfile.write('(END)\n')
codewriter.asmfile.write('@END\n')
codewriter.asmfile.write('0;JMP')
codewriter.close()