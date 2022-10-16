import sys
import os
import glob
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from VMWriter import VMWriter

# Main program, sets up and invokes the other modules
class JackCompiler:

    # This constructor initializes a JackCompiler instance and compiles a JACK-file or all JACK-files in a folder
    def __init__(self):
        # Get input argument and check if it is a file or directory
        file_directory_name = sys.argv[1]
        isFile = os.path.isfile(file_directory_name) # True if file
        isDirectory = os.path.isdir(file_directory_name) # True if directory      
        # Put all files in a list called "files" and name each file "*.jack"
        files = []
        if isDirectory: 
            files = glob.glob(file_directory_name + '/*.jack')
        elif isFile:
            files = [file_directory_name]      
        # Loop through files list and compile them one by one
        for i in range(len(files)):
            # Get file name
            if isDirectory:
                current_file = files[i].split('.')[0].split('/')[1]
            elif isFile:
                current_file = files[i].split('.')[0]  
            # Create tokenizer instance (accesses JACK-file in its folder)
            tokenizer = JackTokenizer(files[i])
            # Create a VMWriter instance (writes VM-code to a new VM-file in the JackCompiler-folder)
            vmWriter = VMWriter(current_file + '.vm')
            # Create a CompilationEngine instance and start compiling the file (which equals a class)
            compeng = CompilationEngine(tokenizer, vmWriter)
            compeng.compileClass()

# Create a JackCompiler instance which kicks off the compilation process       
compile = JackCompiler()
