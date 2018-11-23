# author: LK


# P77 __getitem__
class AtoZ:
    def __getitem__(self, index):
        if 0 <= index < 26:
            return chr(index + ord("A"))
        raise IndexError()  # This error is not raised in for


for letter in AtoZ():
    print(letter, end='')  # output: ABCDEFGHIJKLMNOPQRSTUVWXYZ


# P78 iter(callable, stop_mark)
# one parameter iter()
lst = [1, 2, 3]
for i in iter(lst):
    print(i)

# two parameters iter(): regular class's def in iter()
class counter:

    def __init__(self, _start, _end):
        self.start = _start
        self.end = _end

    def get_next(self):
        s = self.start
        if self.start < self.end:
            self.start += 1
        else:
            raise StopIteration
        return s

c = counter(1, 5)
iterator = iter(c.get_next, 3)
print(type(iterator))
for i in iterator:
    print(i)

# two parameters iter(): class with __call__ in iter() case refer to book P78 the presidents case

# P80: __iter__ __next__
# refer to Bag1.py Bag2.py Bag3.py