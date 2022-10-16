# Tokenizer for the Jack language
class JackTokenizer:

    # Lists of Jack-language keywords and symbols
    KEYWORD_LIST = (['class ', 'constructor ', 'function ', 'method ', 'field ', 'static ', 
    'var ', 'int ', 'char ', 'boolean ', 'void ', 'true ', 'false ', 'null ', 'this ', 'let ', 
    'do ', 'if ', 'else ', 'while ', 'return '])
    SYMBOL_LIST = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

    # This constructor initializes a tockenizer instance and prepares a JACK-file for reading
    def __init__(self, jackfile):
        # Open jack-file and save to string
        with open(jackfile) as file_object:
            self.jackfile = file_object.read()
        self.current_index = 0 # Current index to parse through the jack-file string
        self.current_token = '' # Current token

    # Check for class-closing token (or at least one '}'-token) which per definition is the last token
    def hasMoreTokens(self):
        return ("}" in self.jackfile[self.current_index:])

    # Advances one token and stores it as current_token, token will be empty if comment or whitespace comes next
    def advance(self):
        self.current_token = '' # Reset current token
        if self.hasMoreTokens():
            # Skip comments/newline/space/tab by advancing index over them
            while (self.jackfile[self.current_index : self.current_index + 2] in ['//', '/*']) or (self.jackfile[self.current_index] in ['\n', ' ', '\t']):
                # Skip comments
                if (self.jackfile[self.current_index : self.current_index + 2] in ['//', '/*']):
                    # In case of a full-line comment jump to the byte following new line
                    if (self.jackfile[self.current_index + 1] == '/'):
                        self.current_index = self.jackfile.find('\n', self.current_index + 2) + 1
                    # In case of an in-line comment jump to the byte following the closing "*/"
                    elif (self.jackfile[self.current_index + 1] == '*'):
                        self.current_index = self.jackfile.find('*/', self.current_index + 2) + 2
                # Skip newline/space/tab
                elif (self.jackfile[self.current_index] in ['\n', ' ', '\t']):
                    self.current_index += 1    
            # Create a token starting with a length of one byte
            token_length = 1
            # If token starts with a digit then capture all digits and store to current_token
            if self.jackfile[self.current_index].isdigit():
                while (self.jackfile[self.current_index + token_length].isdigit()):
                    token_length += 1
                self.current_token = self.jackfile[self.current_index : self.current_index + token_length]
                self.current_index += token_length # Advance index
            # If token starts with double quotes (") then capture all characters until incl. closing-double quotes
            elif self.jackfile[self.current_index] == '\"':
                end_of_token = self.jackfile.find('\"', self.current_index + 1)
                self.current_token = self.jackfile[self.current_index : end_of_token + 1]
                self.current_index = end_of_token + 1 # Advance index
            # If token is a symbol then store symbol to current_token and advance index
            elif (self.jackfile[self.current_index] in self.SYMBOL_LIST):
                self.current_token = self.jackfile[self.current_index]
                self.current_index += 1
            # Else the token is either a keyword or an identifier
            else:
                self.current_token = self.jackfile[self.current_index] # Initiate 1-byte token
                # As long as token is not identified as a KEYWORD, add a byte and check if token is complete
                while (self.current_token not in self.KEYWORD_LIST):
                    # As long as no comment/whitespace/symbol comes next, increase token length by one byte
                    if (self.jackfile[self.current_index + token_length] not in ([' ', '/', '\n', '\t'] + self.SYMBOL_LIST)):
                        token_length += 1
                        self.current_token = self.jackfile[self.current_index : self.current_index + token_length]
                    # In case of a comment/space/symbol/tab/newline, stop extending current_token
                    else:
                        break
                # Advance index
                self.current_index += token_length

    # Returns token type depending on (non-empty) token content
    def tokenType(self):
        # Check if token is in keyword list (space is added to avoid detecting keywords prematurly when parsing)
        if (self.current_token + ' ') in self.KEYWORD_LIST:
            return 'keyword'
        # Check if token is in symbol list
        elif self.current_token in self.SYMBOL_LIST:
            return 'symbol'
        # Check if token is only digits and inside admissible range
        elif (self.current_token.isdigit()) and (int(self.current_token) in range(32768)):
            return 'integerConstant'
        # Check if token starts with double quotes
        elif self.current_token[0] == '\"': # At this point the token still includes opening and closing double quotes
            return 'stringConstant'
        # If no check was positive so far it must be an identifier
        else:
            return 'identifier'

    # Return keyword token as is
    def keyWord(self):
        return self.current_token

    # Return symbol token as is
    def symbol(self):
        return self.current_token

    # Return identifier token as is
    def identifier(self):
        return self.current_token

    # Return integer token (as type integer)
    def intVal(self):
        return int(self.current_token)

    # Return string token after stripping double quotes
    def stringVal(self):
        return self.current_token[1:-1]
