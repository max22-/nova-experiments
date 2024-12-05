import sys
from copy import copy

class Bag:
    def __init__(self, items = None):
        if isinstance(items, dict):
            self.items = items
        elif isinstance(items, list) or isinstance(items, set):
            self.items = {}
            for item in items:
                self.add_item(item)
        elif items is None:
            self.items = {}
        else:
            raise RuntimeError(f"can't create a bag from a `{type(items).__name__}`")

    def add_item(self, item, count = 1):
        if item in self.items.keys():
            self.items[item] += count
        else:
            self.items[item] = count

    def remove_item(self, item, count = 1):
        assert(item in self.items.keys() and self.items[item] >= count)
        self.items[item] -= count

    def __add__(self, other):
        new_bag = Bag(copy(self.items))
        for item, count in other.items.items():
            new_bag.add_item(item, count)
        return new_bag
    
    def __sub__(self, other):
        new_bag = Bag(copy(self.items))
        for item, count in other.items.items():
            new_bag.remove_item(item, count)
        return new_bag
    
    def __mul__(self, constant):
        new_bag = Bag()
        for item, count in self.items.items():
            new_bag.add_item(item, count * constant)
        return new_bag
    
    def contains_items(self, items_set):
        return all([item in self.items.keys() and self.items[item] > 0 for item in items_set])
    
    def remove_zeros(self):
        new_items = {}
        for item, count in self.items.items():
            if count > 0:
                new_items[item] = count
        return Bag(new_items)

    def __str__(self):
        return str(self.items)
    
    def __repr__(self):
        return str(self.items)

class ParseError(Exception):
    pass

def parse(file):
    with open(file, 'r') as f:
        data = f.read().lstrip()
    separator = data[0]
    sep_counter = 0
    lines = []
    for c in data:
        if c == separator:
            if sep_counter % 2 == 0:
                lines.append("")
            sep_counter += 1
        lines[-1] += c
    lines = [line.strip().split(separator)[1:] for line in lines]
    lines = [line for line in lines if len(line) > 0]
    for i, line in enumerate(lines):
        if len(line) != 2:
            raise ParseError(f"at line {i}")
    def chop(x):
        return [item.strip() for item in x.split(',') if item != '']
    lines = [(chop(a), chop(b)) for [a, b] in lines]
    bag = Bag({})
    rules = []
    for (lhs, rhs) in lines:
        rhs_bag = Bag()
        for item in rhs:
            if ':' in item:
                try:
                    [a, b] = item.split(':')
                except ValueError:
                    raise ParseError("too many `:`")
                try:
                    b = int(b)
                except ValueError:
                    raise ParseError("expected an integer after `:`")
                rhs_bag.add_item(a, b)
            else:
                rhs_bag.add_item(item)
                    
        if len(lhs) == 0:
            bag += rhs_bag
        else:
            rules.append((set(lhs), rhs_bag))
    return (bag, rules)

def apply_rule(bag, rule):
    lhs, rhs = rule
    if bag.contains_items(lhs):
        _min = min([bag.items[x] for x in lhs])
        print(f"applying rule {rule} (min = {_min})")
        bag -= Bag(lhs) * _min
        bag += rhs * _min
        return bag, True
    else:
        return bag, False
    
def run(bag, rules):
    while True:
        rule_applied = False
        for r in rules:
            bag, result = apply_rule(bag, r)
            if result:
                rule_applied = True
                print(bag)
                break
        if not rule_applied:
            return bag


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} file.nv")
        sys.exit(1)

    (bag, rules) = parse(sys.argv[1])
    print(bag)
    bag = run(bag, rules)
    print("\nResult:")
    print(bag.remove_zeros())