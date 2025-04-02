import sys

# Define instruction formats
r_type_instructions = {
    "0110011": {
        "000": {"0000000": "add", "0100000": "sub"},
        "010": {"0000000": "slt"},
        "101": {"0000000": "srl"},
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

# Initialize registers and memory
registers = [0] * 32
registers[2] = 380
memory = {i: 0 for i in range(32)}  
program_counter = 0

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

def parse_instruction(instruction):

    return {
        "opcode": instruction[25:32],
        "rd": int(instruction[20:25], 2),
        "func3": instruction[17:20],
        "rs1": int(instruction[12:17], 2),
        "rs2": int(instruction[7:12], 2),
        "func7": instruction[0:7],
        "imm": int(instruction[0:12], 2) if instruction[0] == '0' else -((1 << 12) - int(instruction[0:12], 2))
    }

def execute_instruction(instruction):
    global program_counter
    fields = parse_instruction(instruction)
    opcode = fields["opcode"]

    if opcode in r_type_instructions:
        func3 = fields["func3"]
        func7 = fields["func7"]
        if func3 in r_type_instructions[opcode] and func7 in r_type_instructions[opcode][func3]:
            operation = r_type_instructions[opcode][func3][func7]
            if operation == "add":
                registers[fields["rd"]] = registers[fields["rs1"]] + registers[fields["rs2"]]
            elif operation == "sub":
                registers[fields["rd"]] = registers[fields["rs1"]] - registers[fields["rs2"]]
            elif operation == "slt":
                registers[fields["rd"]] = 1 if registers[fields["rs1"]] < registers[fields["rs2"]] else 0
            elif operation == "srl":
                registers[fields["rd"]] = registers[fields["rs1"]] >> registers[fields["rs2"]]
            elif operation == "or":
                registers[fields["rd"]] = registers[fields["rs1"]] | registers[fields["rs2"]]
            elif operation == "and":
                registers[fields["rd"]] = registers[fields["rs1"]] & registers[fields["rs2"]]

    elif opcode in i_type_instructions:
        func3 = fields["func3"]
        if func3 in i_type_instructions[opcode]:
            operation = i_type_instructions[opcode][func3]
            if operation == "addi":
                registers[fields["rd"]] = registers[fields["rs1"]] + fields["imm"]
            elif operation == "lw":
                address = registers[fields["rs1"]] + fields["imm"]
                registers[fields["rd"]] = memory.get(address // 4, 0)
            elif operation == "jalr":
                temp = program_counter + 4
                program_counter = (registers[fields["rs1"]] + fields["imm"]) & ~1
                registers[fields["rd"]] = temp
                return  # Skip the default PC increment

    elif opcode in s_type_instructions:
        func3 = fields["func3"]
        if func3 in s_type_instructions[opcode]:
            operation = s_type_instructions[opcode][func3]
            if operation == "sw":
                address = registers[fields["rs1"]] + fields["imm"]
                memory[address // 4] = registers[fields["rs2"]]

    elif opcode in b_type_instructions:
        func3 = fields["func3"]
        if func3 in b_type_instructions[opcode]:
            operation = b_type_instructions[opcode][func3]
            if operation == "beq":
                if registers[fields["rs1"]] == registers[fields["rs2"]]:
                    program_counter += fields["imm"]
                    return  # Skip the default PC increment
            elif operation == "bne":
                if registers[fields["rs1"]] != registers[fields["rs2"]]:
                    program_counter += fields["imm"]
                    return  # Skip the default PC increment

    elif opcode in j_type_instructions:
        operation = j_type_instructions[opcode]
        if operation == "jal":
            registers[fields["rd"]] = program_counter + 4
            program_counter += fields["imm"]
            return  # Skip the default PC increment

    program_counter += 4  # Increment program counter by 4 (default behavior)

def decode_instruction(instruction):
    opcode = instruction[25:32]
    if opcode in r_type_instructions:
        func3 = instruction[17:20]
        func7 = instruction[0:7]
        if func3 in r_type_instructions[opcode]:
            if func7 in r_type_instructions[opcode][func3]:
                return r_type_instructions[opcode][func3][func7]
    elif opcode in i_type_instructions:
        func3 = instruction[17:20]
        if func3 in i_type_instructions[opcode]:
            return i_type_instructions[opcode][func3]
    elif opcode in s_type_instructions:
        func3 = instruction[17:20]
        if func3 in s_type_instructions[opcode]:
            return s_type_instructions[opcode][func3]
    elif opcode in b_type_instructions:
        func3 = instruction[17:20]
        if func3 in b_type_instructions[opcode]:
            return b_type_instructions[opcode][func3]
    elif opcode in j_type_instructions:
        return j_type_instructions[opcode]
    return "unknown"

def write_registers(outfile):
    outfile.write(f"0b{format(program_counter, '032b')} ")
    outfile.write(" ".join(f"0b{format(reg, '032b')}" for reg in registers) + "\n")


def write_memory(outfile):
    address = 0x00010000
    for i in range(32):
        outfile.write(f"0x{format(address, '08X')}:0b{format(memory[i], '032b')}\n")
        address += 4

def main():

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            for line in infile:
                binary_instruction = line.strip()
                decode_instruction(binary_instruction)  # Decode the instruction
                execute_instruction(binary_instruction)  # Update registers and memory
                write_registers(outfile)
            
            # Write memory contents after Virtual Halt
            write_memory(outfile)

    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

main()
