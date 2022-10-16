# Keeps track of all the variables found in the Jack code
class SymbolTable:
    
    # This constructor initializes a symbol table and the indices for addressing it
    def __init__(self):
        # Initialize a dictionary with four lists, and an index dictionary, to keep track and access the four lists
        self.indices = {'STATIC': 0, 'FIELD': 0, 'ARG': 0, 'VAR': 0}
        self.lists = {'STATIC': [], 'FIELD': [], 'ARG': [], 'VAR': []}

    # This method resets the symbol table to its initial state
    def reset(self):
        # Empty symbol table (4 lists) and reset list indices
        for kind, sym_list in self.lists.items():
            self.lists[kind].clear()
        for kind, index in self.indices.items():
            self.indices[kind] = 0

    # This method defines a new variable and adds it to the symbol table of the given kind
    def define(self, name, type, kind):
        kind = kind.upper() # Ensure that kind is uppercase
        # Save symbol information in dictionary and append it to the symbol list of the respective symbol kind
        symbol = {'name': name, 'type': type, 'kind': kind}
        self.lists[kind].append(symbol)
        # Increase index of symbol kind by 1
        self.indices[kind] += 1

    # This method returns the number of defined variables for a given kind
    def varCount(self, kind):
        kind = kind.upper() # Ensure that kind is uppercase
        return self.indices[kind]

    # This method returns the kind of a symbol with the given name
    def kindOf(self, name):
        # Loop through symbol kinds
        for kind, sym_list in self.lists.items():
            # Loop through all symbols of a kind
            for symbol in self.lists[kind]:
                # If a symbol name matches the given name, return the respective symbol kind
                if symbol['name'] == name:
                    return symbol['kind']
        # If nothing has been returned yet, return 'NONE'
        return 'NONE'

    # This method returns the index of a symbol with the given name
    def indexOf(self, name):
        # Loop through symbol kinds
        for kind, sym_list in self.lists.items():
            # Loop through all symbols of a kind
            for symbol in self.lists[kind]:
                # If a symbol name matches the given name, return the respective list index
                if symbol['name'] == name:
                    return self.lists[kind].index(symbol)
        # If nothing has been returned yet, return 'NONE'
        return 'NONE'

    # This method returns the type of a symbol with the given name
    def typeOf(self, name):
        # Loop through symbol kinds
        for kind, sym_list in self.lists.items():
            # Loop through all symbols of a kind
            for symbol in self.lists[kind]:
                # If a symbol name matches the given name, return the respective index
                if symbol['name'] == name:
                    return symbol['type']
        # If nothing has been returned yet, return 'NONE'
        return 'NONE'
