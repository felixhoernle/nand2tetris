# Creates and maintains a table as correspondence between symbols and their meaning
class SymbolTable:

    # This constructor creates a symbol table (dictionary) and prefills it with predefined symbols
    def __init__(self):
        self.symbols = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4, "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7, "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15, "SCREEN": 16384, "KBD": 24576}

    # This methods adds <symbol, address> to the symbol table
    def addEntry(self, symbol, address):
        self.symbols[symbol] = address

    # This method checks if the symbol table contains a given symbol and returns a boolean
    def contains(self, symbol):
        if self.symbols.get(symbol) == None:
            return False
        else:
            return True

    # This method returns the address associated with a symbol
    def getAddress(self, symbol):
        return self.symbols.get(symbol)
