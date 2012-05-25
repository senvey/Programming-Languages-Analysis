'''
Created on May 23, 2012

@author: William
'''

#===============================================================================
# functional style
#===============================================================================

def readf(filename):
    with open(filename) as f:
        for line in f:
            yield line.strip().strip('.')

def shiftlines(freader):
    for line in freader:
        shifted = []
        words = line.split()
        while len(words) > 0:
            shifted.append(' '.join(words))
            words = words[1:]
        yield shifted

def sort(line_set):
    all_lines = []
    for lines in line_set:
        all_lines.extend(lines)
    all_lines.sort(lambda s1, s2: cmp(s1.lower(), s2.lower()))
    
    for line in all_lines:
        yield line

def pnt(result):
    for line in result:
        print line

def funcstyle():
    pnt(sort(shiftlines(readf('input.txt'))))


#===============================================================================
# event-driven style
#===============================================================================

class Event:
    
    READ_EVENT = 'read'
    SHIFT_EVENT = 'shift'
    SORT_EVENT = 'sort'
    PRINT_EVENT = 'print'
    
    def __init__(self, **argv):
        self.__dict__.update(argv)

class Observer:
    
    def __init__(self, buf):
        self.buf = buf
    
    def update(self, event=None):
        raise NotImplementedError()

class Observable:
    
    def __init__(self):
        self.observers = []
    
    def add(self, observer):
        self.observers.append(observer)
    
    def notify(self, event=None):
        for observer in self.observers:
            observer.update(event)

class Reader(Observer):
    
    def update(self, event):
        if event.type != Event.READ_EVENT:
            return
        
        # fill up the buffer with string read from the given
        # file whose name is passed in with event.data
        with open(event.data) as f:
            for line in f:
                self.buf.append(line.strip().strip('.'))

class Shifter(Observer):
    
    def update(self, event):
        if event.type != Event.SHIFT_EVENT:
            return
        
        # assume there are several lines in the buffer;
        # construct shifted strings with each line and
        # store them back to the buffer
        shifted = []
        while self.buf:
            line = self.buf.pop()
            words = line.split()
            while len(words) > 0:
                shifted.append(' '.join(words))
                words = words[1:]
        self.buf.extend(shifted)

class Sorter(Observer):
    
    def update(self, event):
        if event.type != Event.SORT_EVENT:
            return
        
        # assume there are several lines in the buffer;
        # sort all the lines according to the requirement
        self.buf.sort(lambda s1, s2: cmp(s1.lower(), s2.lower()))

class Printer(Observer):
    
    def update(self, event):
        if event.type != Event.PRINT_EVENT:
            return
        
        # assume there are several lines in the buffer;
        # blindly print them out
        for item in self.buf:
            print item

def eventstyle():
    buf = []
    reader = Reader(buf)
    shifter = Shifter(buf)
    sorter = Sorter(buf)
    printer = Printer(buf)
    
    processor = Observable()
    processor.add(reader)
    processor.add(shifter)
    processor.add(sorter)
    processor.add(printer)
    e = Event()
    
    e.data = 'input.txt'
    e.type = Event.READ_EVENT
    processor.notify(e)
    e.type = Event.SHIFT_EVENT
    processor.notify(e)
    e.type = Event.SORT_EVENT
    processor.notify(e)
    e.type = Event.PRINT_EVENT
    processor.notify(e)
    
#===============================================================================
# entry point
#===============================================================================

if __name__ == '__main__':
    funcstyle()
    eventstyle()

