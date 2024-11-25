import sys
import vera

def emit(s):
    f.write(s + "\n")

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
print(f"bag = {bag}")
print(f"rules = {rules}")

f = open("out.asm", "w")


emit(".text")
emit(".global _start")
emit("_start:")
for i, (lhs, rhs) in enumerate(rules):
    emit(f"rule{i}:")
    for r in lhs.items.keys():
        emit(f"    lw t0, {slug(r)}")
        emit(f"    li t1, {lhs.items[r]}")
        emit(f"    blt t0, t1, rule{i+1}")
    emit("")
    for r in lhs.items.keys():
        emit(f"    lw t0, {slug(r)}")
        emit(f"    addi t0, t0, -{lhs.items[r]}")
        emit(f"    la t1, {slug(r)}")
        emit("    sw t0, 0(t1)")
    for r in rhs.items.keys():
        emit(f"    lw t0, {slug(r)}")
        emit(f"    addi t0, t0, {rhs.items[r]}")
        emit(f"    la t1, {slug(r)}")
        emit("    sw t0, 0(t1)")
    emit("    j _start")
    emit("")

emit(f"rule{len(rules)}:")

emit("")
emit("")
emit("    # exit")
emit("    li a7, 10")
emit("    ecall")

emit(".data")
registers = set()
for item in bag.items.keys():
    registers.add(item)
for rule in rules:
    (lhs, rhs) = rule
    for item in lhs.items.keys():
        registers.add(item)
    for item in rhs.items.keys():
        registers.add(item)
for r in registers:
    count = bag.items[r] if r in bag.items.keys() else 0
    emit(f"{slug(r)}: .word {count}")

f.close()