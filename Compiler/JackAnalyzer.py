import sys
import os
import glob

# Define keywords and symbols
KEYWORD_LIST = (['class', 'constructor', 'function', 'method', 'field', 'static', 
'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 
'do', 'if', 'else', 'while', 'return'])
SYMBOL_LIST = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
xml_symbol_dict = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}

class JackTokenizer:
    def __init__(self, jackfile):
        # Open jack-file and save to string
        with open(jackfile) as file_object:
            self.jackfile = file_object.read()
        self.current_index = 0 # Current index within the jack-file string
        self.current_token = '' # Current token

    # Check if closing token of class is still in remaining jackfile-string
    def hasMoreTokens(self):
        return ("}" in self.jackfile[self.current_index:])

    # Saves next token as current_token, token is empty if comment or whitespace comes next
    def advance(self):
        self.current_token = '' # Reset current token
        # Skip comments/newline/space/tab
        if self.hasMoreTokens():
            while (self.jackfile[self.current_index : self.current_index + 2] in ['//', '/*']) or (self.jackfile[self.current_index] in ['\n', ' ', '\t']):
                # Skip comments by increasing current_index
                if (self.jackfile[self.current_index : self.current_index + 2] in ['//', '/*']):
                    # In case of a full-line comment jump to the byte following new line
                    if (self.jackfile[self.current_index + 1] == '/'):
                        self.current_index = self.jackfile.find('\n', self.current_index + 2) + 1
                    # In case of an in-line comment jump to the byte following "*/"
                    elif (self.jackfile[self.current_index + 1] == '*'):
                        self.current_index = self.jackfile.find('*/', self.current_index + 2) + 2
                # Skip newline/space/tab by increasing current_index
                elif (self.jackfile[self.current_index] in ['\n', ' ', '\t']):
                    self.current_index += 1
        
            # Create a token starting with a length of one byte
            token_length = 1

            # If token starts with a digit then capture all digits in current token and then increase index
            if self.jackfile[self.current_index].isdigit():
                while (self.jackfile[self.current_index + token_length].isdigit()):
                    token_length += 1
                self.current_token = self.jackfile[self.current_index : self.current_index + token_length]
                self.current_index += token_length

            # If token starts with double quotes (") then capture all characters to and incl. closing double quotes
            elif self.jackfile[self.current_index] == '\"':
                end_of_token = self.jackfile.find('\"', self.current_index + 1)
                self.current_token = self.jackfile[self.current_index : end_of_token + 1]
                self.current_index = end_of_token + 1 # Increase index

            # If token starts with a symbol then save this 1-byte symbol and increase index
            elif (self.jackfile[self.current_index] in SYMBOL_LIST):
                self.current_token = self.jackfile[self.current_index]
                self.current_index += 1

            # Else we either have a keyword or an identifier
            else:
                self.current_token = self.jackfile[self.current_index] # Initiate 1-byte token
                # As long as token is not identified as a KEYWORD, add a byte and check if token is complete
                while (self.current_token not in KEYWORD_LIST):
                    # Add byte until encountering a comment/whitespace/symbol and then break out of while-loop
                    if (self.jackfile[self.current_index + token_length] not in ([' ', '/', '\n', '\t'] + SYMBOL_LIST)):
                        token_length += 1
                        self.current_token = self.jackfile[self.current_index : self.current_index + token_length]
                    else:
                        break
                self.current_index += token_length # Increase index

    # Returns token type depending on (non-empty) token content
    def tokenType(self):
        # Check if token is in keyword list
        if self.current_token in KEYWORD_LIST:
            return 'keyword'
        # Check if token is in symbol list
        elif self.current_token in SYMBOL_LIST:
            return 'symbol'
        # Check if token is only digits and inside admissible range
        elif (self.current_token.isdigit()) and (int(self.current_token) in range(32768)):
            return 'integerConstant'
        # Check if token starts with double quotes
        elif self.current_token[0] == '\"': # At this point the token still includes opening and closing double quotes!
            return 'stringConstant'
        # If no check was positive so far it must be an identifier
        else:
            return 'identifier'

    # Return current token as is
    def keyWord(self):
        return self.current_token

    # Return current token as is but adjust for xml-peculiarities
    def symbol(self):
        # If symbol is one of four special symbols it has to be converted to xml-friendly format
        if self.current_token in xml_symbol_dict:
            return xml_symbol_dict[self.current_token]
        else:
            return self.current_token

    # Return current token as is
    def identifier(self):
        return self.current_token

    # Return current token as integer
    def intVal(self):
        return int(self.current_token)

    # Return current token after stripping starting and ending double quotes
    def stringVal(self):
        return self.current_token[1:-1]

class CompilationEngine:
    # This constructor initializes a CompilationEngine instance, containing a JackTokenizer instance and an open XML-file
    def __init__(self, tokenizer, xmlfile):
        self.tokenizer = tokenizer
        self.xmlfile = open(xmlfile, 'w')
    # This method compiles a class into XML
    def compileClass(self):
        # Write opening "<class>" and advance tokenizer
        self.xmlfile.write('<class>\n')
        self.tokenizer.advance()
        # Write "class", className and "{"
        self.writeToXml('keyword')
        self.writeToXml('identifier')
        self.writeToXml('symbol')      
        # If class variables are declared, process all such declarations
        while (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() in ['static', 'field']):
            self.compileClassVarDec()
        # If subroutines are declared, process all such subroutine declarations
        while (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() in ['constructor', 'function', 'method']):
            self.compileSubroutine()
        # Write closing "}"
        self.writeToXml('symbol')     
        # Write closing "</class>"
        self.xmlfile.write('</class>\n')
    # This method compiles a class variable declaration into XML
    def compileClassVarDec(self):
        # Write opening "<classVarDec>"
        self.xmlfile.write('<classVarDec>\n')
        # Write 'static' or 'field'
        self.writeToXml('keyword')
        # Write type, which is either a keyword ('int'/'char'/'boolean') or an identifier (className)
        if self.tokenizer.tokenType() == 'keyword':
            self.writeToXml('keyword')
        elif self.tokenizer.tokenType() == 'identifier':
            self.writeToXml('identifier')
        # Write varName
        self.writeToXml('identifier')
        # If there are additional varNames, process all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ','):
            self.writeToXml('symbol')
            self.writeToXml('identifier')  
        # Write ';'
        self.writeToXml('symbol')
        # Write closing "</classVarDec>"
        self.xmlfile.write('</classVarDec>\n')
    # This method compiles a subroutine (constructor/method/function) into XML
    def compileSubroutine(self):
        # Write opening "<subroutineDec>"
        self.xmlfile.write('<subroutineDec>\n')
        # Write "constructor", "function" or "method"
        self.writeToXml('keyword')
        # Write "void" or type, where type is either a keyword ('int'/'char'/'boolean') or an identifier (className)
        if self.tokenizer.tokenType() == 'keyword':
            self.writeToXml('keyword')
        elif self.tokenizer.tokenType() == 'identifier':
            self.writeToXml('identifier')
        # Write subroutineName and "("
        self.writeToXml('identifier')
        self.writeToXml('symbol')
        # Process parameterList (also works for empty list)
        self.compileParameterList()
        # Write ")"
        self.writeToXml('symbol')
        # Process subroutineBody
        self.compileSubroutineBody()
        # Write closing "</subroutineDec>"
        self.xmlfile.write('</subroutineDec>\n')
    # This method compiles the body of a subroutine (constructor/method/function) into XML
    def compileSubroutineBody(self):
        # Write opening "<subroutineBody>"
        self.xmlfile.write('<subroutineBody>\n')
        # Write "{"
        self.writeToXml('symbol')
        # If variables are declared, process all such declarations
        while (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() == 'var'):
            self.compileVarDec()
        # If there are statements, process all such statements with compileStatements
        if (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() in ['let', 'if', 'while', 'do', 'return']):
            self.compileStatements()
        # Write "}"
        self.writeToXml('symbol')
        # Write closing "</subroutineBody>"
        self.xmlfile.write('</subroutineBody>\n')
    # This method handles statements by calling the appropriate statment method (let/if/while/do/return)
    def compileStatements(self):
        # Write opening "<statements>"
        self.xmlfile.write('<statements>\n')
        while (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() in ['let', 'if', 'while', 'do', 'return']):
            if self.tokenizer.keyWord() == 'let':
                self.compileLet()
            elif self.tokenizer.keyWord() == 'if':
                self.compileIf()
            elif self.tokenizer.keyWord() == 'while':
                self.compileWhile()
            elif self.tokenizer.keyWord() == 'do':
                self.compileDo()
            elif self.tokenizer.keyWord() == 'return':
                self.compileReturn()
        # Write closing "</statements>" 
        self.xmlfile.write('</statements>\n')
    # This method compiles a let-statement into XML
    def compileLet(self):
        # Write opening "<letStatement>" 
        self.xmlfile.write('<letStatement>\n')
        # Write "let"
        self.writeToXml('keyword')
        # Write varName
        self.writeToXml('identifier')
        # If expression is encountered, process expression
        if (self.tokenizer.symbol() == '['):
            # Write "["
            self.writeToXml('symbol')
            # Process expression
            self.compileExpression()
            # Write "]"
            self.writeToXml('symbol')
        # Write "="
        self.writeToXml('symbol')
        # Process expression
        self.compileExpression()
        # Write ';'
        self.writeToXml('symbol')
        # Write closing "</letStatement>"
        self.xmlfile.write('</letStatement>\n')
    # This method compiles an if-statement into XML
    def compileIf(self):
        # Write opening "<ifStatement>"
        self.xmlfile.write('<ifStatement>\n')
        # Write "if"
        self.writeToXml('keyword')
        # Write '('
        self.writeToXml('symbol')
        # Process expression
        self.compileExpression()
        # Write ')'
        self.writeToXml('symbol')
        # Write '{'
        self.writeToXml('symbol')
        # Process statements
        self.compileStatements()
        # Write '}'
        self.writeToXml('symbol')
        # If 'else' is encountered, process the else clause
        if (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() == 'else'):
            # Write "else"
            self.writeToXml('keyword')
            # Write '{'
            self.writeToXml('symbol')
            # Process statements
            self.compileStatements()
            # Write '}'
            self.writeToXml('symbol')
        # Write closing "</ifStatement>"
        self.xmlfile.write('</ifStatement>\n')
    # This method compiles a while-statement into XML
    def compileWhile(self):
        # Write opening "<whileStatement>"
        self.xmlfile.write('<whileStatement>\n')
        # Write "while"
        self.writeToXml('keyword')
        # Write '('
        self.writeToXml('symbol')
        # Process expression
        self.compileExpression()
        # Write ')'
        self.writeToXml('symbol')
        # Write '{'
        self.writeToXml('symbol')
        # Process statements
        self.compileStatements()
        # Write '}'
        self.writeToXml('symbol')
        # Write closing "</whileStatement>"
        self.xmlfile.write('</whileStatement>\n')
    # This method compiles a do-statement into XML
    def compileDo(self):
        # Write opening "<doStatement>"
        self.xmlfile.write('<doStatement>\n')
        # Write "do"
        self.writeToXml('keyword')
        # Process subroutineCall with compileTerm-method
        self.compileTerm(callerIsDo = True)
        # Write ';'
        self.writeToXml('symbol')
        # Write closing "</doStatement>"
        self.xmlfile.write('</doStatement>\n')
    # This method compiles a return-statement into XML
    def compileReturn(self):
        # Write opening "<returnStatement>"
        self.xmlfile.write('<returnStatement>\n')
        # Write "return"
        self.writeToXml('keyword')
        # If no '; is encountered, there must be an expression
        if not((self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ';')):
            # Process expression
            self.compileExpression()
        # Write ';'
        self.writeToXml('symbol')
        # Write closing "</returnStatement>"
        self.xmlfile.write('</returnStatement>\n')
    # This method handles a list of expressions by calling the method to compile an expression repeatedly
    def compileExpressionList(self):
        # Write opening "<expressionList>"
        self.xmlfile.write('<expressionList>\n')
        # Process expression
        if (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == ')'):
            pass
        else:
            self.compileExpression()
        # If there are additional expressions, process all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ','):
            # Write ","
            self.writeToXml('symbol')
            # Process expression
            self.compileExpression()          
        # Write closing "</expressionList>"
        self.xmlfile.write('</expressionList>\n')
    # This method handles an expression by calling the method to compile terms repeatedly
    def compileExpression(self):
        # Write opening "<expression>"
        self.xmlfile.write('<expression>\n')
        # Process term
        self.compileTerm()
        # If there are additional terms, process all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() in ['+', '-', '*', '/', '&amp;', '|', '&lt;', '&gt;', '=']):
            self.writeToXml('symbol')
            self.compileTerm()
        # Write closing "</expression>"
        self.xmlfile.write('</expression>\n')
    # This method compiles a term
    def compileTerm(self, callerIsDo = False):
        if self.tokenizer.tokenType() == 'integerConstant':
            # Write opening "<term>"
            self.xmlfile.write('<term>\n')
            # Write integerConstant
            self.writeToXml('integerConstant')
            # Write closing "</term>"
            self.xmlfile.write('</term>\n')
        elif self.tokenizer.tokenType() == 'stringConstant':
            # Write opening "<term>"
            self.xmlfile.write('<term>\n')
            # Write stringConstant
            self.writeToXml('stringConstant')
            # Write closing "</term>"
            self.xmlfile.write('</term>\n')
        elif self.tokenizer.tokenType() == 'keyword':
            # Write opening "<term>"
            self.xmlfile.write('<term>\n')
            # Write keywordConstant
            self.writeToXml('keyword')
            # Write closing "</term>"
            self.xmlfile.write('</term>\n')
        elif (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() in ['-', '~']):
            # Write opening "<term>"
            self.xmlfile.write('<term>\n')
            # Write unaryOp
            self.writeToXml('symbol')
            # Process term
            self.compileTerm()
            # Write closing "</term>"
            self.xmlfile.write('</term>\n')
        elif (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == '('):
            # Write opening "<term>"
            self.xmlfile.write('<term>\n')
            # Write '('
            self.writeToXml('symbol')
            # Process expression
            self.compileExpression()
            # Write ')'
            self.writeToXml('symbol')
            # Write closing "</term>"
            self.xmlfile.write('</term>\n')
        elif self.tokenizer.tokenType() == 'identifier':
            # Store (current) identifier token
            identifier_token = self.tokenizer.identifier()
            # Look ahead one token to decide how to proceed
            self.tokenizer.advance()  
            # Check if "[", "(", or "." follows
            if (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == '['):
                # Write opening "<term>"
                self.xmlfile.write('<term>\n')
                # Write stored varName to xml and avoid advance
                self.xmlfile.write('<identifier> ' + str(identifier_token) + ' </identifier>\n')
                # Write '['
                self.writeToXml('symbol')
                # Process expression
                self.compileExpression()
                # Write ']'
                self.writeToXml('symbol')
                # Write closing "</term>"
                self.xmlfile.write('</term>\n')
            elif (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == '('):
                if not(callerIsDo):
                    # Write opening "<term>"
                    self.xmlfile.write('<term>\n')
                # Write stored subroutineName to xml and avoid advance
                self.xmlfile.write('<identifier> ' + str(identifier_token) + ' </identifier>\n')
                # Write '('
                self.writeToXml('symbol')
                # Process expressionList
                self.compileExpressionList()
                # Write ')'
                self.writeToXml('symbol')
                if not(callerIsDo):
                    # Write closing "</term>"
                    self.xmlfile.write('</term>\n')
            elif (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == '.'):
                if not(callerIsDo):
                    # Write opening "<term>"
                    self.xmlfile.write('<term>\n')
                # Write stored className/varName to xml and avoid advance
                self.xmlfile.write('<identifier> ' + str(identifier_token) + ' </identifier>\n')
                # Write '.'
                self.writeToXml('symbol')
                # Write subroutineName
                self.writeToXml('identifier')
                # Write '('
                self.writeToXml('symbol')
                # Process expressionList
                self.compileExpressionList()
                # Write ')'
                self.writeToXml('symbol')
                if not(callerIsDo):
                    # Write closing "</term>"
                    self.xmlfile.write('</term>\n')
            else:
                # Write opening "<term>"
                self.xmlfile.write('<term>\n')
                # Write identifier to xml and avoid advance
                self.xmlfile.write('<identifier> ' + str(identifier_token) + ' </identifier>\n')
                # Write closing "</term>"
                self.xmlfile.write('</term>\n')
    # This method compiles a variable declaration (int/char/boolean/className)
    def compileVarDec(self):
        # Write opening "<varDec>"
        self.xmlfile.write('<varDec>\n')
        # Write 'var'
        self.writeToXml('keyword')
        # Write type, which is either a keyword ('int'/'char'/'boolean') or an identifier (className)
        if self.tokenizer.tokenType() == 'keyword':
            self.writeToXml('keyword')
        elif self.tokenizer.tokenType() == 'identifier':
            self.writeToXml('identifier')
        # Write varName
        self.writeToXml('identifier')
        # If there are additional varNames, process all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ','):
            self.writeToXml('symbol')
            self.writeToXml('identifier')  
        # Write ';'
        self.writeToXml('symbol')
        # Write closing "</varDec>"
        self.xmlfile.write('</varDec>\n')
    # This method compiles a list of parameters
    def compileParameterList(self):
        # Write opening "<parameterList>"
        self.xmlfile.write('<parameterList>\n')
        # Write type, which is either a keyword ('int'/'char'/'boolean') or an identifier (className), then varName
        if self.tokenizer.tokenType() == 'keyword':
            self.writeToXml('keyword')
            self.writeToXml('identifier')
        elif self.tokenizer.tokenType() == 'identifier':
            self.writeToXml('identifier')
            self.writeToXml('identifier')
        # If there are additional parameters, process all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ','):
            # Write ","
            self.writeToXml('symbol')
            # Write type, which is either a keyword ('int'/'char'/'boolean') or an identifier (className), then varName
            if self.tokenizer.tokenType() == 'keyword':
                self.writeToXml('keyword')
                self.writeToXml('identifier')
            elif self.tokenizer.tokenType() == 'identifier':
                self.writeToXml('identifier')
                self.writeToXml('identifier')           
        # Write closing "</parameterList>"
        self.xmlfile.write('</parameterList>\n')
    # This helper method writes code to the XML-file and then advances the tokenizer. Also warns if token type is unexpected.
    def writeToXml(self, expToken):
        tokenType = self.tokenizer.tokenType()
        if tokenType == 'keyword':
            token_content = self.tokenizer.keyWord()
        elif tokenType == 'symbol':
            token_content = self.tokenizer.symbol()
        elif tokenType == 'integerConstant':
            token_content = self.tokenizer.intVal()
        elif tokenType == 'stringConstant':
            token_content = self.tokenizer.stringVal()
        elif tokenType == 'identifier':
            token_content = self.tokenizer.identifier()
        # Inform user if token type does not conform to expectation, then write to xml-file and advance tokenizer
        if (expToken !=  tokenType):
            print('Warning: Expected token type ' + expToken + ', actual type was ' + tokenType + '.')
        self.xmlfile.write('<' + tokenType + '> ' + str(token_content) + ' </' + tokenType + '>\n')
        self.tokenizer.advance()  

class JackAnalyzer:
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

        # Loop through files list
        for i in range(len(files)):
            # Create xml-output file
            if isDirectory:
                current_file = files[i].split('.')[0].split('/')[1]
            elif isFile:
                current_file = files[i].split('.')[0]  
            # Create tokenizer instance
            tokenizer = JackTokenizer(files[i])
            # Create compilation engine instance and start compilation
            compeng = CompilationEngine(tokenizer, current_file + '.xml')
            compeng.compileClass()
        
analyzer = JackAnalyzer()
