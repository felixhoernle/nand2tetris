# Writes VM code
class VMWriter:

    # Dictionary to translate Jack-language operator signs to virtual machine language symbols
    OP_TO_VM_SYMBOLS = {'+': 'add', '-': 'sub', '&': 'and', '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq', '*': 'call Math.multiply 2', '/': 'call Math.divide 2', '~': 'not', 'unary-': 'neg'}

    # This constructor creates a new output vm-file and prepares it for writing
    def __init__(self, filename):
        self.vmfile = open(filename, 'w')
    
    # Writes a VM push command
    def writePush(self, segment, index):
        self.vmfile.write('push ' + segment + ' ' + str(index) + '\n')
    
    # Writes a VM pop command
    def writePop(self, segment, index):
        self.vmfile.write('pop ' + segment + ' ' + str(index) + '\n')
    
    # Writes a VM arithmetic-logical command (translates operators into virtual machine symbols)
    def writeArithmetic(self, command):
        self.vmfile.write(self.OP_TO_VM_SYMBOLS[command.lower()] + '\n')
    
    # Writes a VM label command (uppercase)
    def writeLabel(self, label):
        self.vmfile.write('label ' + label.upper() + '\n')
    
    # Writes a VM goto command (uppercase)
    def writeGoto(self, label):
        self.vmfile.write('goto ' + label.upper() + '\n')
    
    # Writes a VM if-goto command (uppercase)
    def writeIf(self, label):
        self.vmfile.write('if-goto ' + label.upper() + '\n')
    
    # Writes a VM call command
    def writeCall(self, name, nArgs):
        self.vmfile.write('call ' + name + ' ' + str(nArgs) + '\n')
    
    # Writes a VM function command
    def writeFunction(self, name, nVars):
        self.vmfile.write('function ' + name + ' ' + str(nVars) + '\n')
    
    # Writes a VM return command
    def writeReturn(self):
        self.vmfile.write('return\n')
    
    # Closes the output vm-file
    def close(self):
        self.vmfile.close()
