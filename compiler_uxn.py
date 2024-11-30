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

if len(sys.argv) != 3:
    print(f"usage: python {sys.argv[0]} file.nv output.tal")
    sys.exit(1)

bag, rules = vera.parse(sys.argv[1])
print(f"bag = {bag}")
print(f"rules = {rules}")

f = open(sys.argv[2], "w")

emit("|0100")
emit("@loop")

for i, (lhs, rhs) in enumerate(rules):
    emit(f"@rule{i}")
    emit("    #ffff")
    for r in lhs:
        emit(f"    ;{slug(r)} LDA2 LTH2k ?{{ SWP2 }} POP2")
    emit(f"    DUP2 #0000 NEQ2 ?{{ POP2 ;rule{i+1} JMP2 }}")
    emit("    ( -- min )")
    emit("    STH2")
    for r in lhs:
        emit(f"    ;{slug(r)} LDA2k STH2kr SUB2 SWP2 STA2")
    for r in rhs.items.keys():
        emit(f"    ;{slug(r)} LDA2k #{rhs.items[r]:04x} STH2kr MUL2 ADD2 SWP2 STA2")
    emit("    POP2r ;loop JMP2")

emit(f"@rule{len(rules)}")

registers = set()
for item in bag.items.keys():
    registers.add(item)
for (lhs, rhs) in rules:
    for item in lhs:
        registers.add(item)
    for item in rhs.items.keys():
        registers.add(item)


for r in registers:
    emit(f"    ;{slug(r)} LDA2 print-short-decimal #0a18 DEO")

emit("BRK")

f.write("""
@print-short-decimal ( short* -- )
	#03e8 DIV2k
		DUP ,print-byte-decimal/second JSR
		MUL2 SUB2
	#0064 DIV2k
		DUP ,print-byte-decimal/third JSR
		MUL2 SUB2
	NIP ,print-byte-decimal/second JMP

@print-byte-decimal ( byte -- )
	#64 DIVk DUP #30 ADD #18 DEO MUL SUB
	&second
	#0a DIVk DUP #30 ADD #18 DEO MUL SUB
	&third
	             #30 ADD #18 DEO
	JMP2r
""")

emit("( registers )")

for r in registers:
    count = bag.items[r] if r in bag.items.keys() else 0
    emit(f"@{slug(r)} {count:04x}")

f.close()