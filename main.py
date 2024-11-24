import sys
from copy import copy

class Bag:
    def __init__(self, items = {}):
        if isinstance(items, dict):
            self.items = items
        elif isinstance(items, list):
            self.items = {}
            for item in items:
                self.add_item(item)
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
    
    def contains(self, other):
        for item, count in other.items.items():
            if not item in self.items.keys() or self.items[item] < count:
                return False
        return True

    def __str__(self):
        return str(self.items)
    
    def __repr__(self):
        return str(self.items)

class ParseError(Exception):
    pass

def parse(file):
    with open(file, 'r') as f:
        lines = f.readlines()
    lines = [line.strip().split('|')[1:] for line in lines]
    lines = [line for line in lines if len(line) > 0]
    for i, line in enumerate(lines):
        if len(line) != 2:
            raise ParseError(f"at line {i}")
    def chop(x):
        return [item.strip() for item in x.split(',') if item != '']
    lines = [(chop(a), chop(b)) for [a, b] in lines]
    bag = Bag()
    rules = []
    for (lhs, rhs) in lines:
        if len(lhs) == 0:
            for item in rhs:
                bag.add_item(item)
        else:
            rules.append((Bag(lhs), Bag(rhs)))
    return (bag, rules)

def apply_rule(bag, rule):
    lhs, rhs = rule
    if bag.contains(lhs):
        print(f"applying rule {rule}")
        bag -= lhs
        bag += rhs
        return bag, True
    else:
        return bag, False
    
def run(bag, rules):
    while True:
        rule_applied = False
        for r in rules:
            bag, result = apply_rule(bag, r)
            rule_applied = rule_applied or result
            if result:
                print(bag)
        if not rule_applied:
            return bag

if len(sys.argv) != 2:
    print(f"usage: python {sys.argv[0]} file")
    sys.exit(1)



(bag, rules) = parse(sys.argv[1])
print(bag)
bag = run(bag, rules)
print("\nResult:")
print(bag)