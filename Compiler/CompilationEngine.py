from SymbolTable import SymbolTable

# Recursive top-down compilation engine
class CompilationEngine:

    # Dictionary to translate variable kinds to corresponding memory segment names
    VARKIND_TO_MEMSEG = {'STATIC': 'static', 'FIELD': 'this', 'ARG': 'argument', 'VAR': 'local'}

    # Initializes a CompilationEngine instance
    def __init__(self, tokenizer, vmWriter):
        # Set up tokenizer and VM-writer variables
        self.tokenizer = tokenizer
        self.vmWriter = vmWriter
        # Create two SymbolTable instances, a class-level one and a subroutine-level one
        self.classTable = SymbolTable()
        self.subrTable = SymbolTable()
        # Define variables to store a class name, a subroutine name, a subroutine type and subr. return value type
        self.className = ''
        self.subrName = ''
        self.subrType = ''
        self.subrRetValType = ''        
        # Initialize a counter for labels, to ensure uniqueness of each label
        self.label_counter = 1

    # This method compiles a complete class
    def compileClass(self):
        # Advance tokenizer to start compilation process
        self.tokenizer.advance()
        # Advance tokenizer over 'class', then store and advance over className as well as over '{'
        self.tokenizer.advance()
        self.className = self.tokenizer.identifier()
        self.tokenizer.advance()
        self.tokenizer.advance()
        # If class variables are declared, compile them
        while (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() in ['static', 'field']):
            self.compileClassVarDec()
        # Compile all subroutine declarations (constructor/function/method)
        while (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() in ['constructor', 'function', 'method']):
            self.compileSubroutine()
        # Advance tokenizer over '}' (last token of the class-file)
        self.tokenizer.advance()    
        # Close VM-file
        self.vmWriter.close()

    # This method compiles class variable declaration (static/field)
    def compileClassVarDec(self):
        # Store and advance over class variable kind (static/field)
        varKind = self.tokenizer.keyWord()
        self.tokenizer.advance()
        # Store class variable type, which is either a keyword (int/char/boolean) or an identifier (className)
        if self.tokenizer.tokenType() == 'keyword':
            varType = self.tokenizer.keyWord()
        elif self.tokenizer.tokenType() == 'identifier':
            varType = self.tokenizer.identifier()
        # Advance over class variable type
        self.tokenizer.advance()
        # Store class variable name, and add the variable to the class-level symbol table
        varName = self.tokenizer.identifier()
        self.classTable.define(varName, varType, varKind)
        # Advance over class variable name
        self.tokenizer.advance()
        # If there are additional class variable declarations (of same kind and type), compile all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ','):
            # Advance over ','
            self.tokenizer.advance()
            # Store class variable name, and add the variable to the class-level symbol table
            varName = self.tokenizer.identifier()
            self.classTable.define(varName, varType, varKind)
            # Advance over class variable name
            self.tokenizer.advance() 
        # Advance over ';'
        self.tokenizer.advance()

    # This method compiles a complete subroutine (constructor/method/function)
    def compileSubroutine(self):
        # Reset subroutine-level symbol table and store subroutine type
        self.subrTable.reset()
        self.subrType = self.tokenizer.keyWord()
        # If subroutine is a method, define 'this' as first symbol 
        if self.subrType == 'method':
            self.subrTable.define('this', self.className, 'ARG')
        # Advance over subroutine type (constructor/method/function)
        self.tokenizer.advance()
        # Store subroutine return value type, which is either a keyword (int/char/boolean/void) or an identifier (className)
        if self.tokenizer.tokenType() == 'keyword':
            self.subrRetValType = self.tokenizer.keyWord()
        elif self.tokenizer.tokenType() == 'identifier':
            self.subrRetValType = self.tokenizer.identifier()
        # Advance over subroutine return value type
        self.tokenizer.advance()
        # Store and advance over subroutine name
        self.subrName = self.tokenizer.identifier()
        self.tokenizer.advance()
        # Advance over '('
        self.tokenizer.advance()
        # Compile parameterList (also works for empty list)
        self.compileParameterList()
        # Advance over ')'
        self.tokenizer.advance()
        # Compile subroutineBody
        self.compileSubroutineBody()

    # This method compiles a (possibly empty) list of parameters
    def compileParameterList(self):
        # Store subroutine-level variable type, which is either a keyword (int/char/boolean) or an identifier (className)
        if self.tokenizer.tokenType() == 'keyword':
            varType = self.tokenizer.keyWord()
        elif self.tokenizer.tokenType() == 'identifier':
            varType = self.tokenizer.identifier()
        # If no keyword or identifier was encountered, then the parameter list is empty --> Return to compileSubroutine
        else:
            return
        # Advance over subroutine-level variable type
        self.tokenizer.advance()
        # Add the variable to the subroutine-level symbol table (current token is variable name)
        self.subrTable.define(self.tokenizer.identifier(), varType, 'ARG')
        # Advance over variable name
        self.tokenizer.advance()
        # If there are additional parameters, compile all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ','):
            # Advance over ','
            self.tokenizer.advance()
            # Store variable type, which is either a keyword ('int'/'char'/'boolean') or an identifier (className)
            if self.tokenizer.tokenType() == 'keyword':
                varType = self.tokenizer.keyWord()
            elif self.tokenizer.tokenType() == 'identifier':
                varType = self.tokenizer.identifier()
            # Advance over variable type
            self.tokenizer.advance()
            # Add the variable to the subroutine-level symbol table (current token is variable name)
            self.subrTable.define(self.tokenizer.identifier(), varType, 'ARG')
            # Advance over variable name
            self.tokenizer.advance() 

    # This method compiles a subroutine's body
    def compileSubroutineBody(self):
        # Advance over '{'
        self.tokenizer.advance()
        # If variables are declared, compile all such declarations
        while (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() == 'var'):
            self.compileVarDec()
        # Write "function className.subroutineName nVars" to define subroutine with nVar local variables
        self.vmWriter.writeFunction(self.className + '.' + self.subrName, self.subrTable.varCount('VAR'))
        # If the subroutine is a method:
        # Align the virtual memory segment 'this' with the base address of the object on which the method was called
        # Write "push argument 0, pop pointer 0"
        if self.subrType == 'method':
            self.vmWriter.writePush('argument', 0)
            self.vmWriter.writePop('pointer', 0)
        # Else if the subroutine is a constructor:
        # Allocate a memory block of nFields 16-bit words and then align the virtual memory segment 'this' with the base address of the newly allocated block
        # Write "push constant nFields, call Memory.alloc 1, pop pointer 0"
        elif self.subrType == 'constructor':
            self.vmWriter.writePush('constant', self.classTable.varCount('FIELD'))
            self.vmWriter.writeCall('Memory.alloc', 1)
            self.vmWriter.writePop('pointer', 0)
        # Compile all statements
        self.compileStatements()
        # Advance over '}' (subroutine closing)
        self.tokenizer.advance()

    # This method compiles a var (local variable) declaration
    def compileVarDec(self):
        # Advance over 'var'
        self.tokenizer.advance()
        # Store variable type, which is either a keyword ('int'/'char'/'boolean') or an identifier (className)
        if self.tokenizer.tokenType() == 'keyword':
            varType = self.tokenizer.keyWord()
        elif self.tokenizer.tokenType() == 'identifier':
            varType = self.tokenizer.identifier()
        # Advance over variable type
        self.tokenizer.advance()
        # Store variable name, and add variable to the subroutine-level symbol table
        varName = self.tokenizer.identifier()
        self.subrTable.define(varName, varType, 'VAR')
        # Advance over variable name
        self.tokenizer.advance()
        # If there are additional local variable declarations, compile all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ','):
            # Advance over ','
            self.tokenizer.advance()
            # Store variable name, and add variable to the subroutine-level symbol table
            varName = self.tokenizer.identifier()
            self.subrTable.define(varName, varType, 'VAR')
            # Advance over variable name
            self.tokenizer.advance()
        # Advance over ';'
        self.tokenizer.advance()   

    # This method compiles a (possibly empty) sequence of statements
    def compileStatements(self):
        # Determine statement type of each statement (let/if/while/do/return) and compile them all
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

    # This method compiles a let statement
    def compileLet(self):
        # Advance over 'let'
        self.tokenizer.advance()
        # Store and advance over variable name
        varName = self.tokenizer.identifier()
        self.tokenizer.advance()
        # Find variable kind and index in symbol tables (check subroutine-level first)
        if self.subrTable.kindOf(varName) != 'NONE':
            varKind = self.subrTable.kindOf(varName)
            varIndex = self.subrTable.indexOf(varName)
        else:
            varKind = self.classTable.kindOf(varName)
            varIndex = self.classTable.indexOf(varName)
        # If an index ('[expression]') follows, compile it
        if (self.tokenizer.symbol() == '['):
            # Advance over '['
            self.tokenizer.advance()
            # Push the variable's base address to the virtual stack
            self.vmWriter.writePush(self.VARKIND_TO_MEMSEG[varKind], varIndex)
            # Compile expression, which pushes the expression return value to the virtual stack
            self.compileExpression()
            # Add up the variable and the expression return value to determine memory address
            self.vmWriter.writeArithmetic('+')
            # Advance over ']' and '='
            self.tokenizer.advance()
            self.tokenizer.advance()
            # Compile expression on right-hand side of '=', which pushes the expression return value to the virtual stack
            self.compileExpression()
            # Pop the expression’s return value to the 'temp' memory segment
            self.vmWriter.writePop('temp', 0)
            # Pop the addition result (the memory address) to pointer 1 (to set 'that' to the memory address)
            self.vmWriter.writePop('pointer', 1)
            # Push right-hand side expression’s return value (currently stored at temp 0) back on the stack
            self.vmWriter.writePush('temp', 0)
            # Pop right-hand side expression’s return value to that 0
            self.vmWriter.writePop('that', 0)
        # If no '[expression]' follows, then directly move to compiling right-hand side expression
        else:
            # Advance over '='
            self.tokenizer.advance()
            # Compile expression, which pushes the expression return value to the virtual stack
            self.compileExpression()
            # Pop the right-hand side expression return value to varName's memory location
            self.vmWriter.writePop(self.VARKIND_TO_MEMSEG[varKind], varIndex)
        # Advance over ';'
        self.tokenizer.advance()

    # This method compiles an if statement
    def compileIf(self):
        # Advance over 'if' and '('
        self.tokenizer.advance()
        self.tokenizer.advance()
        # Compile expression
        self.compileExpression()
        # Negate expression's return value (which will be true or false) on stack
        self.vmWriter.writeArithmetic('~')
        # Create two unique labels and increase global label counter
        labelA = 'L' + str(self.label_counter)
        self.label_counter += 1
        labelB = 'L' + str(self.label_counter)
        self.label_counter += 1
        # Set conditional jump to label A
        self.vmWriter.writeIf(labelA)
        # Advance over ')' and '{'
        self.tokenizer.advance()
        self.tokenizer.advance() 
        # Compile statements
        self.compileStatements()
        # Set unconditional jump to label B
        self.vmWriter.writeGoto(labelB)
        # Set label A location
        self.vmWriter.writeLabel(labelA)
        # Advance over '}'
        self.tokenizer.advance()
        # If 'else' is encountered, process the else clause
        if (self.tokenizer.tokenType() == 'keyword' and self.tokenizer.keyWord() == 'else'):
            # Advance over 'else' and '{'
            self.tokenizer.advance()
            self.tokenizer.advance()
            # Compile statements
            self.compileStatements()
            # Advance over '}'
            self.tokenizer.advance()
        # Set label B location
        self.vmWriter.writeLabel(labelB)

    # This method compiles a while statement
    def compileWhile(self):
        # Advance over 'while' and '('
        self.tokenizer.advance()
        self.tokenizer.advance()
        # Create two unique labels and increase global label counter
        labelA = 'L' + str(self.label_counter)
        self.label_counter += 1
        labelB = 'L' + str(self.label_counter)
        self.label_counter += 1
        # Set label A location
        self.vmWriter.writeLabel(labelA)
        # Compile expression
        self.compileExpression()
        # Negate expression's return value (which will be true or false) on stack
        self.vmWriter.writeArithmetic('~')
        # Set conditional jump to label B
        self.vmWriter.writeIf(labelB)
        # Advance over ')' and '{'
        self.tokenizer.advance()
        self.tokenizer.advance()
        # Compile statements
        self.compileStatements()
        # Set unconditional jump to label A
        self.vmWriter.writeGoto(labelA)
        # Set label B location
        self.vmWriter.writeLabel(labelB)
        # Advance over '}'
        self.tokenizer.advance()

    # This method compiles a do statement
    def compileDo(self):
        # Advance over 'do'
        self.tokenizer.advance()
        # Compile subroutine call (method or function) with compileExpression (constructor is usually called with let)
        self.compileExpression()
        # The do abstraction is designed to call a subroutine for its effect, ignoring the return value.
        # Pop function/method return value from stack and dump it (per convention to temp 0)
        self.vmWriter.writePop('temp', 0)
        # Advance over ';'
        self.tokenizer.advance()

    # This method compiles a return statement
    def compileReturn(self):
        # Advance over 'return'
        self.tokenizer.advance()
        # If no ';' follows, then there is an expression which has to be compiled
        if not((self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ';')):
            self.compileExpression()
        # Every VM subroutine is expected to push a value onto the stack before returning.
        # --> Write 'push constant 0' if return value type is 'void' to meet this expectation
        if self.subrRetValType == 'void':
            self.vmWriter.writePush('constant', 0)
        # If subroutine type was a constructor, return to the caller the base address of the new object created by it
        # Write 'push pointer 0'
        if self.subrType == 'constructor':
            self.vmWriter.writePush('pointer', 0)
        # Write return statement
        self.vmWriter.writeReturn()
        # Advance over ';'
        self.tokenizer.advance()

    # This method compiles a (possibly empty) list of expressions and returns the number of expressions in that list
    def compileExpressionList(self):
        # Initialize expression counter to 0
        nExpr = 0
        # Compile all expression, if there are no expressions return 0
        if (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == ')'):
            return nExpr
        else:
            # Compile first expression and increase counter
            self.compileExpression()
            nExpr += 1
            # If there are additional expressions, compile them all
            while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() == ','):
                # Advance over ','
                self.tokenizer.advance()
                # Compile expression and increase counter
                self.compileExpression()
                nExpr += 1
            return nExpr      

    # This method handles an expression by calling the method to compile terms repeatedly
    def compileExpression(self):
        # Compile term
        self.compileTerm()
        # If there are additional terms linked by operators, compile them all
        while (self.tokenizer.tokenType() == 'symbol') and (self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']):
            # Store operator and advance over it
            op = self.tokenizer.symbol()
            self.tokenizer.advance()
            # Compile term
            self.compileTerm()
            # Write operator to stack
            self.vmWriter.writeArithmetic(op)

    # This method compiles a term
    def compileTerm(self):
        # If it is an integer...
        if self.tokenizer.tokenType() == 'integerConstant':
            # Push integer to stack and advance over it
            self.vmWriter.writePush('constant', self.tokenizer.intVal())
            self.tokenizer.advance()
        # If it is a string...
        elif self.tokenizer.tokenType() == 'stringConstant':
            # Push string length to stack and call String constructor
            self.vmWriter.writePush('constant', len(self.tokenizer.stringVal()))
            self.vmWriter.writeCall('String.new', 1)
            # For each character, push character to the stack and call appendChar method
            for char in range(len(self.tokenizer.stringVal())):
                self.vmWriter.writePush('constant', ord(self.tokenizer.stringVal()[char]))
                self.vmWriter.writeCall('String.appendChar', 2)
            # Advance over string constant
            self.tokenizer.advance()
        # If it is a keyword (true/false/null/this)...
        elif self.tokenizer.tokenType() == 'keyword':
            # Check keyword type, push 0/0/-1 for null/false/true and 'pointer 0' for 'this'. 
            # This command pushes the base address of the current object onto the stack.
            if self.tokenizer.keyWord() in ['null', 'false']:
                self.vmWriter.writePush('constant', 0)
            elif self.tokenizer.keyWord() == 'true':
                self.vmWriter.writePush('constant', 1)
                self.vmWriter.writeArithmetic('unary-')
            elif self.tokenizer.keyWord() == 'this':
                self.vmWriter.writePush('pointer', 0)
            # Advance over keyword
            self.tokenizer.advance()
        # If it is a unary operator (arithmetic or boolean negation)...
        elif (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() in ['-', '~']):
            # Store unary operator
            unaryOp = self.tokenizer.symbol()
            # If unary operator is '-' (negation), adjust it to make it distinguishable from '-' (minus)
            if unaryOp == '-':
                unaryOp = 'unary-'
            # Advance over unary operator
            self.tokenizer.advance()
            # Compile term
            self.compileTerm()
            # Push unary operator to stack
            self.vmWriter.writeArithmetic(unaryOp)
        # If it is a nested expression...
        elif (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == '('):
            # Advance over '('
            self.tokenizer.advance()
            # Compile expression
            self.compileExpression()
            # Advance over ')'
            self.tokenizer.advance()
        # If it is an identifier...
        elif self.tokenizer.tokenType() == 'identifier':
            # Store identifier until it can be determined exactly what kind of term it is part of
            identifier_token = self.tokenizer.identifier()
            # Advance over identifier token (look ahead) to find out more about the term
            self.tokenizer.advance()  
            # If the term is of type varName[expression]...
            if (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == '['):
                # Find variable kind and index in symbol tables
                if self.subrTable.kindOf(identifier_token) != 'NONE':
                    varKind = self.subrTable.kindOf(identifier_token)
                    varIndex = self.subrTable.indexOf(identifier_token)
                else:
                    varKind = self.classTable.kindOf(identifier_token)
                    varIndex = self.classTable.indexOf(identifier_token)
                # Push variable to stack
                self.vmWriter.writePush(self.VARKIND_TO_MEMSEG[varKind], varIndex)
                # Advance over '['
                self.tokenizer.advance()
                # Compile expression (which pushes the expression return value to the stack)
                self.compileExpression()
                # Add up variable value and expression return value
                self.vmWriter.writeArithmetic('+')
                # Pop the result to pointer 1 (setting 'that' address), then access 'that' address and push to the stack
                self.vmWriter.writePop('pointer', 1)
                self.vmWriter.writePush('that', 0)   
                # Advance over ']'
                self.tokenizer.advance()
            # If the term is of type subroutineName(expressionList)...
            elif (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == '('):
                # Advance over '('
                self.tokenizer.advance()
                # Now we know that identifier was a subroutine name, store it accordingly
                subrName = identifier_token
                # Push the base address of the current object ('this') onto the stack (as we are operating on the current object)
                self.vmWriter.writePush('pointer', 0)
                # Compile expressionList and store the number of expressions
                nExpr = self.compileExpressionList()
                # Write call command to call method, informing that nExpr + 1 arguments were pushed onto the stack
                self.vmWriter.writeCall(self.className + '.' + subrName, nExpr + 1)
                # Advance over ')'
                self.tokenizer.advance()
            # If the term is of type className.subroutineName(expressionList) or varName.subroutineName(expressionList)...
            elif (self.tokenizer.tokenType() == 'symbol' and self.tokenizer.symbol() == '.'):
                # Advance over '.'
                self.tokenizer.advance()
                # Store and advance over subroutine name
                subrName = self.tokenizer.identifier()
                self.tokenizer.advance()
                # Advance over '('
                self.tokenizer.advance()
                # If the identifier is found in one of the symbol tables, then the term must be of type varName.methodName
                if (isinstance(self.subrTable.indexOf(identifier_token), int) or isinstance(self.classTable.indexOf(identifier_token), int)):
                    # Determine and store kind and index of varName, and class name that the object is an instance of
                    if self.subrTable.kindOf(identifier_token) != 'NONE':
                        varKind = self.subrTable.kindOf(identifier_token)
                        varIndex = self.subrTable.indexOf(identifier_token)
                        className = self.subrTable.typeOf(identifier_token)
                    else:
                        varKind = self.classTable.kindOf(identifier_token)
                        varIndex = self.classTable.indexOf(identifier_token)     
                        className = self.classTable.typeOf(identifier_token)               
                    # Push symbol table mapping of 'varName' to stack
                    self.vmWriter.writePush(self.VARKIND_TO_MEMSEG[varKind], varIndex)
                    # Compile expressionList and store the number of expressions
                    nExpr = self.compileExpressionList()                    
                    # Write call command, informing that nExpr + 1 arguments were pushed onto the stack
                    self.vmWriter.writeCall(className + '.' + subrName, nExpr + 1)
                # Else, it is of type className.functionName / className.constructorName
                else:
                    className = identifier_token
                    # Compile expressionList and store the number of expressions
                    nExpr = self.compileExpressionList()
                    # Write call command, informing that nExpr arguments were pushed onto the stack
                    self.vmWriter.writeCall(className + '.' + subrName, nExpr)             
                # Advance over ')'
                self.tokenizer.advance()
            # Else the identifier was just a varName
            else:
                # Find variable kind and index in symbol tables
                if self.subrTable.kindOf(identifier_token) != 'NONE':
                    varKind = self.subrTable.kindOf(identifier_token)
                    varIndex = self.subrTable.indexOf(identifier_token)
                else:
                    varKind = self.classTable.kindOf(identifier_token)
                    varIndex = self.classTable.indexOf(identifier_token)
                # Push variable to stack
                self.vmWriter.writePush(self.VARKIND_TO_MEMSEG[varKind], varIndex) 
