# Parser to parse the input assembly code
class Parser:

    # Initializes a Parser instance that opens the input ASM-file and gets ready to parse it
    def __init__(self, asmfile):
        # Open ASM-file as list of lines
        with open(asmfile) as file_object:
            self.asmfile = file_object.readlines()
        #Remove comments
        for j in range(len(self.asmfile)):
            if self.asmfile[j].find("//") >= 0:
                self.asmfile[j] = self.asmfile[j].split('//')[0]
        #Remove empty lines
        for i in range(self.asmfile.count('\n')):
            self.asmfile.remove('\n')
        for p in range(self.asmfile.count('')):
            self.asmfile.remove('')
        #Remove white space
        for k in range(len(self.asmfile)):
            self.asmfile[k] = self.asmfile[k].strip()
        # Initialize current command string to be an empty string
        self.current_command = ''
        # Initialize boolean variable stating if there are any commands in the ASM-file
        self.commands_left = (len(self.asmfile) > 0)

    # This method checks if there are more lines in the ASM-file to be parsed
    def hasMoreCommands(self):
        # Check if there are lines left and return boolean value accordingly
        self.commands_left = (len(self.asmfile) > 0)
        return self.commands_left

    # This method reads the next instruction from the ASM-file and makes it the current instruction
    def advance(self):
        # Pop first value from list of command lines
        self.current_command = self.asmfile.pop(0)

    # This method returns the type of the current command (A/L/C-command)
    def commandType(self):
        # A-instructions start with '@'
        if self.current_command[0] == '@':
            return 'A_COMMAND'
        # If it starts with a '(' it's a label declaration
        elif self.current_command[0] == '(':
            return 'L_COMMAND'
        # In all other cases with have a C-instruction
        else:
            return 'C_COMMAND'

    # This method returns the symbol that is part of the A/L-instruction
    def symbol(self):
        # In case of an A-instruction, remove the '@'
        if self.commandType() == 'A_COMMAND':
            return self.current_command.split('@')[1]
        # In case of an L-command, remove the surrounding '()'
        elif self.commandType() == 'L_COMMAND':
            return self.current_command.strip('()')

    # Returns the symbolic 'dest' part of a C-instruction
    def dest(self):
        # If there are only characters following the '=', then 'dest' is empty --> Return 'null'
        if len(self.current_command.split('=')) == 1:
            return 'null'
        # In all other cases, return the part before the '=' sign
        else:
            return self.current_command.split('=')[0]

    # Returns the symbolic 'comp' part of a C-instruction
    def comp(self):
        # If the instruction contains no '=' then there must be a ';' --> Return part before ';' sign
        if self.current_command.find('=') == -1:
            return self.current_command.split(';')[0]
        # If the instruction contains a '=' but no ';', then return the whole part after the '=' sign
        elif self.current_command.find(';') == -1:
            return self.current_command.split('=')[1]
        # Else the instruction contains both a '=' and ';' --> Return part in between those two signs
        else:
            return self.current_command.split('=')[1].split(';')[0]

    # Returns the symbolic 'jump' part of a C-instruction
    def jump(self):
        # If the instruction contains no ';' then there is no 'jump'
        if self.current_command.find(';') == -1:
            return 'null'
        # In all other cases return the part after the ';' sign
        else:
            return self.current_command.split(';')[1]
