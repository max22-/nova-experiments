import sys
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

def uxnify_identifier(identifier):
    chunks = []
    chunk = ""
    for c in identifier:
        if c in [' ', '"']:
            if chunk != '':
                chunks.append(chunk)
                chunk = ""
            chunks.append(f"{ord(c):02x}")
        else:
            if chunk == '':
                chunk = '"'
            chunk += c
    if chunk != '':
        chunks.append(chunk)
    return ' '.join(chunks)


if len(sys.argv) != 3:
    print(f"usage: python {sys.argv[0]} file.nv output.tal")
    sys.exit(1)

bag, rules = vera.parse(sys.argv[1])

f = open(sys.argv[2], "w")

emit("|10 @Console    &vector $2 &read     $1 &pad    $5 &write  $1 &error  $1")
emit("|0100")
emit("@loop")

for i, (lhs, rhs) in enumerate(rules):
    emit(f"@rule{i}")
    emit("    #ffff")
    for r in lhs:
        emit(f"    ;{slug(r)} LDA2 LTH2k ?{{ SWP2 }} POP2")
    label = f"rule{i+1}" if i < len(rules) - 1 else "end"
    emit(f"    ORAk ?{{ POP2 ;{label} JMP2 }}")
    emit("    ( -- min )")
    emit("    STH2")
    for r in lhs:
        emit(f"    ;{slug(r)} LDA2k STH2kr SUB2 SWP2 STA2")
    for r in rhs.items.keys():
        emit(f"    ;{slug(r)} LDA2k #{rhs.items[r]:04x} STH2kr MUL2 ADD2 SWP2 STA2")
    emit("    POP2r !loop")

emit(f"@end")

registers = set()
for item in bag.items.keys():
    registers.add(item)
for (lhs, rhs) in rules:
    for item in lhs:
        registers.add(item)
    for item in rhs.items.keys():
        registers.add(item)


for r in registers:
    emit(f"    ;{slug(r)} LDA2 #0000 EQU2 ?{{")
    emit("    #7c7c #18 DEO #18 DEO #2018 DEO")
    emit(f"    ;str_{slug(r)} print-string #203a #18 DEO #18 DEO")
    emit(f"    ;{slug(r)} LDA2 print-short-decimal #0a18 DEO }}")

emit("BRK")

f.write("""

@print-string ( string* -- )
	LDAk ,&not-end JCN
	POP2 JMP2r
	&not-end
	LDAk .Console/write DEO
	INC2
	,print-string JMP

@print-short-decimal ( short* -- )
	#03e8 DIV2k
		DUP ,print-byte-decimal/second JSR
		MUL2 SUB2
	#0064 DIV2k
		DUP ,print-byte-decimal/third JSR
		MUL2 SUB2
	NIP ,print-byte-decimal/second JMP

@print-byte-decimal ( byte -- )
	#64 DIVk DUP #30 ADD .Console/write DEO MUL SUB
	&second
	#0a DIVk DUP #30 ADD .Console/write DEO MUL SUB
	&third
	             #30 ADD .Console/write DEO
	JMP2r
""")

emit("")
emit("( registers )")

for r in registers:
    count = bag.items[r] if r in bag.items.keys() else 0
    emit(f"@{slug(r)} {count:04x}")

for r in registers:
    emit(f"@str_{slug(r)} {uxnify_identifier(r)} $1")

f.close()