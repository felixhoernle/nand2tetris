# This module handles the parsing of a single .vm-file
class Parser:

    # List of virtual machine language symbols for arithmetic-logical operations
    ARITHMETIC_CLIST = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']

    # This constructor opens the .vm-file and removes comments/empty lines/white space
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
        #Remove leading and trailing white space
        for k in range(len(self.vmfile)):
            self.vmfile[k] = self.vmfile[k].strip()
        # Initialize a variable to store the currently processed command
        self.current_command = ''

    # Returns a boolean stating wether or not there are any lines left
    def hasMoreLines(self):
        return (len(self.vmfile) > 0)

    # Pops the next command (line) from the list and makes it the current command
    def advance(self):
        self.current_command = self.vmfile.pop(0)

    # Returns a constant representing the type of the current command
    def commandType(self):
        # Check first word in the line to decide type
        if self.current_command.split()[0].casefold() == 'push':
            return 'C_PUSH'
        elif self.current_command.split()[0].casefold() == 'pop':
            return 'C_POP'
        elif self.current_command.split()[0].casefold() in self.ARITHMETIC_CLIST:
            return 'C_ARITHMETIC'
        elif self.current_command.split()[0].casefold() == 'label':
            return 'C_LABEL'
        elif self.current_command.split()[0].casefold() == 'if-goto':
            return 'C_IF'
        elif self.current_command.split()[0].casefold() == 'goto':
            return 'C_GOTO'
        elif self.current_command.split()[0].casefold() == 'function':
            return 'C_FUNCTION'
        elif self.current_command.split()[0].casefold() == 'call':
            return 'C_CALL'
        elif self.current_command.split()[0].casefold() == 'return':
            return 'C_RETURN'

    # Returns the first argument of the current command
    def arg1(self):
        # For arithmetic-logical commands the command itself is returned
        if self.commandType() == 'C_ARITHMETIC':
            return self.current_command.split()[0].casefold()
        # For all other commands, except a return command, the first argument comes after the commandType-keyword
        elif self.commandType() != 'C_RETURN':
            return self.current_command.split()[1]
        # For a return command, return an error message
        else:
            return 'C_RETURN has no arg1'

    # Returns the second argument of the current command
    def arg2(self):
        # Only return a second argument for push/pop/function/call commands
        if self.commandType() in ['C_PUSH', 'C_POP', 'C_FUNCTION', 'C_CALL']:
            return self.current_command.split()[2].casefold()
        # For all other commands, return an error message
        else:
            return 'Only PUSH/POP/FUNCTION/CALL arguments have arg2'
