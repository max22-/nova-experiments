import sys
import os
import vera

def emit(s):
    f.write(s + "\n")

# shamefully copied from Wryl's vera -> C compiler
def slug(identifier):
    res = 'r_'
    for c in identifier:
        if c in ['\r', '\n', '\t', ' ']:
            res += '_'
        elif c in ['`', ':', '|', '>', '<', '$', '#', '@', '*', '!', '?', ';', '&', '%', '^', '|', '/', '(', ')', '[', ']', '{', '}', '\\', '"', '\'', '+', '-', '*', '=', '.', ',', '~']:
            res += str(ord(c))
        else:
            res += c
    return res

if len(sys.argv) != 2:
    print(f"usage: python {sys.argv[0]} file.nv")
    sys.exit(1)

bag, rules = vera.parse(sys.argv[1])

base_filename = sys.argv[1].split('.')[0:-1]

c_file = '.'.join(base_filename + ['c'])
h_file = '.'.join(base_filename + ['h'])

f = open(c_file, "w")

registers = set()
ports = set()

for item in bag.items.keys():
    if item.startswith('@'):
        ports.add(item)
    else:
        registers.add(item)
for (lhs, rhs) in rules:
    for item in lhs:
        if item.startswith('@'):
            ports.add(item)
        else:
            registers.add(item)
    for item in rhs.items.keys():
        if item.startswith('@'):
            ports.add(item)
        else:
            registers.add(item)

emit("#include <stddef.h>")
emit(f'#include "{os.path.basename(h_file)}"')
emit("")
emit("#define MIN(a, b) ((a) < (b) ? (a) : (b))")
emit("")
emit("/* Ports */")
for p in ports:
    emit(f"uint32_t {slug(p)};")
emit("")

emit("int vera(void) {")
for r in registers:
    count = bag.items[r] if r in bag.items.keys() else 0
    emit(f"    static uint32_t {slug(r)} = {count};")
emit("    uint32_t m; /* min */")
emit("")

for i, (lhs, rhs) in enumerate(rules):
    if i == 0:
        emit(f"    /* rule {i} */")
    else:
        emit(f"rule{i}:")
    emit("    m = UINT32_MAX;")
    for r in lhs:
        emit(f"    m = MIN(m, {slug(r)});")
        if i < len(rules) - 1:
            emit(f"    if(m == 0) goto rule{i+1};")
        else:
            emit(f"    if(m == 0) return 0;")
    for r in lhs:
        emit(f"    {slug(r)} -= m;")
    for r in rhs.items.keys():
        mult = f"{rhs.items[r]} *" if rhs.items[r] != 1 else ""
        emit(f"    {slug(r)} +={mult} m;")
    emit("    return 1;")
    emit("")
emit('}')

f.close()

with open(h_file, 'w') as f:
    emit('#ifdef __cplusplus')
    emit('extern "C" {')
    emit('#endif')
    emit('#include <stdint.h>')
    emit('')
    emit('/* Ports */')
    for p in ports:
        emit(f'extern uint32_t {slug(p)};')
    emit('')
    emit('int vera(void);')
    emit('')
    emit('#ifdef __cplusplus')
    emit('}')
    emit('#endif')