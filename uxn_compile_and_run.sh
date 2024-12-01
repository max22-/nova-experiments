set -xe
python compiler_uxn.py examples/$1.nv $1.tal
uxnasm $1.tal $1.rom
uxncli $1.rom