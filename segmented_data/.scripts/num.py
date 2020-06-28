import regex
from itertools import zip_longest

from common import bilarasortkey

class Num:
    """
    >>> Num(1)
    Num('1')

    >>> Num('2a')
    Num('2a')

    >>> Num('1-10')
    Num('1-10')

    >>> Num('1') - Num('0')
    Num('1')

    >>> Num('2a') - Num('1')
    Num('1')

    >>> Num('1-10') - Num('0')
    Num('1')

    >>> Num('11-20') - Num('1-10')
    Num('1')

    >>> num = Num('1')
    >>> num + 1
    Num('2')

    >>> Num('1a') > Num('1')
    True

    >>> Num('0a') < Num('1')
    True

    >>> Num('1-10') < Num('11-20')
    True

    >>> Num('0a') < Num('1-10')
    True

    Addition is not allowed if the other value cannot be converted to an int
    >>> Num('1-10') + Num('11-20')
    Traceback (most recent call last):
        ...
    ValueError: Cannot convert to int

    Subtraction is allowed as it has a special meaning in the case of ranges
    >>> Num('11-20') - Num('1-10')
    Num('1')

    """

    def __init__(self, value):
        if isinstance(value, str):
            m = regex.match(r'(\d+)(?:-(\d+))?(\^?[a-z]*)', value)
            
            self.start = int(m[1])
            self.end = int(m[2]) if m[2] else self.start
            self.suffix = m[3]
        else:
            self.start = self.end = int(value)
            self.suffix = ''

    
    def __str__(self):
        if self.start == self.end:
            return str(self.start) + self.suffix
        return f'{self.start}-{self.end}{self.suffix}'

    def __repr__(self):
        return f"Num('{str(self)}')"

    def __eq__(self, other_num):
        if isinstance(other_num, int):
            return self.start == self.end == other_num and not self.suffix
        else:
            return self.start == other_num.start and self.end == other_num.end and self.suffix == other_num.suffix

    def __gt__(self, other):
        return bilarasortkey(str(self)) > bilarasortkey(str(other))
    
    def __lt__(self, other):
        return bilarasortkey(str(self)) < bilarasortkey(str(other))

    def __add__(self, other_num):
        return Num(self.end + int(other_num))
    
    def __sub__(self, other_num):
        if isinstance(other_num, int):
            return Num(self.start - int(other_num))
        else:
            return Num(self.start - other_num.end)

    def __int__(self):
        if self.start != self.end or self.suffix:
            raise ValueError('Cannot convert to int')
        return int(self.start)

    def set_numeric(self, value):
        self.start = self.end = int(value)

    def is_range(self):
        return self.end != self.start
    

class DottedNum:
    """

    >>> DottedNum('1.2')
    DottedNum('1.2')

    >>> DottedNum('2.4.0a')
    DottedNum('2.4.0a')

    >>> DottedNum('1.2')[1]
    Num('2')

    >>> DottedNum('1.2') - DottedNum('1.1')
    DottedNum('0.1')

    >>> DottedNum('1.2') > DottedNum('1.1')
    True

    >>> dnum = DottedNum('1.2')
    >>> dnum.make_one_greater(DottedNum('1.2'))
    >>> dnum
    DottedNum('1.3')

    >>> cases =[
    ...  ['1.2', '1.3'],
    ...  ['1.3', '1.4.1'],
    ...  ['0.1', '1.1.1'],
    ...  ['3.1.4', '4.1.1'],
    ...  ['4.2.1', '5.1'],
    ...  ['1.1', '1.1'],
    ...  ['3.4', '3.3'],
    ...  ['2.9', '2.11']
    ...  ]
    >>> [DottedNum(b).is_logical_progression(DottedNum(a)) for a, b in cases]
    [True, True, True, True, True, False, False, False]
    
    """
    def __init__(self, string=None, nums=None):
        if not string and not nums:
            self.nums = [Num('0')]
        elif string:
            self.nums = [Num(s) for s in string.split('.')]
        elif nums:
            self.nums = list(nums)

    def __eq__(self, other):
        return self.nums == other.nums

    def __gt__(self, other):
        return bilarasortkey(str(self)) > bilarasortkey(str(other))
    
    def __lt__(self, other):
        return bilarasortkey(str(self)) < bilarasortkey(str(other))


    def __getitem__(self, i):
        return self.nums[i]

    def __str__(self):
        return '.'.join(str(num) for num in self)

    def __repr__(self):
        return f"DottedNum('{str(self)}')"

    def __sub__(self, other):
        nums = []
        for num, other_num in zip_longest(self.nums, other.nums, fillvalue=0):
            nums.append(num - other_num)
        return DottedNum(nums=nums)

    def __iter__(self):
       return iter(self.nums)

    def __len__(self):
        return len(self.nums)

    def only_one_one(self):
        one_count = 0
        for num in self.nums:
            if num == 1:
                one_count += 1
            elif num == 0:
                continue
            else:
                return False
        return one_count == 1

    def is_logical_progression(self, previous):
        mode = 0
        for a, b in zip_longest(previous, self, fillvalue=Num(0)):
            if mode == 0:
                diff = b - a
                if diff == 0:
                    continue
                elif diff == 1:
                    mode = 1
                    continue
                else:
                    return False
            else:
                if b == 1 or b == 0:
                    continue
                else:
                    return False
        if mode == 0:
            return False
        return True
                
    def differs_by_last_num(self, other):
        if self.nums[:-1] == other.nums[:-1]:
            if  self[-1] != other[-1]:
                return True
        return False

    def make_one_greater(self, previous):
        if self.nums[-1].is_range():
            raise ValueError(f'Unable to automatically fix range {self}')
        self.nums = previous.nums[::]
        self.nums[-1].set_numeric(previous[-1]+1)


def is_logical_progression(previous_num, num):

    nums = num.split('.')
    previous_nums = previous_num.split('.')

    for i in range(0, min(len(nums), len(previous_nums))):
        a = previous_nums[i]
        b = nums[i]

if __name__ == '__main__':
    import doctest
    doctest.testmod()