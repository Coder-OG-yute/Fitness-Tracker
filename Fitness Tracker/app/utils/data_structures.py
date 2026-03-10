# custom data structures: Stack (LIFO) used in workout presets; Queue (FIFO) used in tips search


class Stack: # simple stack using a Python list; push adds to top, pop removes last, is_empty checks if empty
    """
    a simple stack using a Python list underneath. operations: push (add to top), pop (remove last), is_empty (check if no items).
    """

    def __init__(self):
        self.dataList = [] # creates an empty list to store the stack items

    def push(self, item):
        self.dataList.append(item) # adds the item to the top of the stack. uses list operations

    def pop(self):
        if self.is_empty():
            return None # if the stack is empty, return None
        return self.dataList.pop() # removes and returns the last item. uses Stack/Queue Operations

    def is_empty(self):
        return len(self.dataList) == 0 # returns True if there are no items

    def __len__(self):
        return len(self.dataList) # so len(stack) can work and be used easily

    def __iter__(self):
        return iter(self.dataList) # so "for item in stack" can work and be used easily (like when saving preset to JSON)

    def remove_at(self, index):
        """Remove and return the item at an index (would delete one exercise by position)."""
        if index < 0 or index >= len(self.dataList): # checks if the index is out of bounds
            return None # if the index is out of bounds, return None
        return self.dataList.pop(index)


class Queue: # simple queue (FIFO); can be used to process time-ordered data in order
    """
    a simple queue (first in, first out). can be used to process time-ordered data (e.g. log entries) in the order they were recorded.
    """

    def __init__(self):
        self.dataList = [] # creates an empty list to store the queue items

    def enqueue(self, item):
        self.dataList.append(item) # adds the item to the back of the queue

    def dequeue(self):
        if self.is_empty():
            return None
        return self.dataList.pop(0) # removes and returns the first item (O(n) for list, fine for small data). uses Stack/Queue Operations

    def is_empty(self):
        return len(self.dataList) == 0 # returns True if there are no items

