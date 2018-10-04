
class PrintScope(object):
    indentation = 0
    
    @classmethod
    def Print(self, msg):
        print(' ' * self.indentation + msg)

    def __init__(self, msg):
        self.Print(msg)
        
    def __enter__(self):
        PrintScope.indentation += 1
        
    def __exit__(self, type, value, traceback):
        PrintScope.indentation -= 1

Print = PrintScope.Print