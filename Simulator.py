import sys

r_type_instructions = {
     "0110011": { 
        "000": {"0000000": "add", "0100000": "sub"},
        "001": {"0000000": "sll"},
        "010": {"0000000": "slt"},
        "011": {"0000000": "sltu"},
        "100": {"0000000": "xor"},
        "101": {"0000000": "srl", "0100000": "sra"},
        "110": {"0000000": "or"},
        "111": {"0000000": "and"}
    }
}

i_type_instructions = {
    "0000011": {"010": "lw"},
    "0010011": {"000": "addi"},
    "1100111": {"000": "jalr"}
}

s_type_instructions = {
    "0100011": {"010": "sw"}
}

b_type_instructions = {
    "1100011": {
        "000": "beq",
        "001": "bne",
    }
}

j_type_instructions = {
    "1101111": "jal"
}

def bianry_deciaml(n):
    i=0
    sum=0
    while n>0:
        a= n%10
        n=n//10
        a= a*2**i
        sum+=a
        i+=1
    return sum
def decimal_binary(n):
    sum=0
    pow=1
    while n>0:
        a= n%2
        q=n//2
        sum+=pow*a
        n=q
        pow=pow*10
    return sum
