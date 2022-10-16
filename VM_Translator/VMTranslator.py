import os
import sys
import glob
from Parser import Parser
from CodeWriter import CodeWriter

# This module drives the overall translation process
class VMTranslator:
    # This constructor initializes a VMTranslator instance and translates a VM-file or all VM-files in a folder
    def __init__(self):
        # Get input argument and check if it is a directory
        userInput = sys.argv[1]
        #isFile = os.path.isfile(userInput)
        isDirectory = os.path.isdir(userInput)
        # Create a CodeWriter instance
        codewriter = CodeWriter(userInput)
        # Put all files in a list called "files" and loop through
        files = []
        if isDirectory: 
            files = glob.glob(userInput + '/*.vm')
        else:
            files = [userInput]
        # Loop through all VM-files in the list and translate them into assembly code
        for i in range(len(files)):
            # Create a parser instance for the current VM-file
            parser = Parser(files[i])
            # Inform the CodeWriter instance about the current VM-file name
            if isDirectory:
                codewriter.setFileName(files[i].split('.')[0].split('/')[1])
            else:
                codewriter.setFileName(files[i].split('.')[0])
            # Translate the VM-file line by line
            while parser.hasMoreLines() == True:
                # Move to next line
                parser.advance()
                # Write current VM command to ASM-file for tracking purposes
                codewriter.asmfile.write('// ' + parser.current_command + '\n')
                # Determine command type and translate it
                if parser.commandType() in ['C_PUSH', 'C_POP']:
                    codewriter.writePushPop(parser.commandType(), parser.arg1(), int(parser.arg2()))
                elif parser.commandType() == 'C_ARITHMETIC':
                    codewriter.writeArithmetic(parser.arg1())
                elif parser.commandType() == 'C_LABEL':
                    codewriter.writeLabel(parser.arg1())
                elif parser.commandType() == 'C_IF':
                    codewriter.writeIf(parser.arg1())
                elif parser.commandType() == 'C_GOTO':
                    codewriter.writeGoTo(parser.arg1())
                elif parser.commandType() == 'C_FUNCTION':
                    codewriter.writeFunction(parser.arg1(), int(parser.arg2()))
                elif parser.commandType() == 'C_CALL':
                    codewriter.writeCall(parser.arg1(), parser.arg2())
                elif parser.commandType() == 'C_RETURN':
                    codewriter.writeReturn()  
        # After all VM-files have been translated, create an infinite loop at the end of the ASM-file and close it
        codewriter.asmfile.write('(END)\n')
        codewriter.asmfile.write('@END\n')
        codewriter.asmfile.write('0;JMP')
        codewriter.close()

# Create a VMTranslator instance which kicks off the translation process       
translate = VMTranslator()