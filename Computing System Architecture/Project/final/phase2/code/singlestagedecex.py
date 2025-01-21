from binaryutils import *

def inst_decode(instruction):
    # Dictionary to store the decoded instruction fields
    decoded_instruction = {}
    source_reg1, source_reg2, dest_reg, immediate_val = None, None, None, None

    # Extract opcode and function fields from the instruction
    opcode = instruction[-7:]
    funct3 = instruction[-15:-12]
    funct7 = instruction[:7]

    # Helper functions to calculate immediate values for specific instruction types
    def calculate_b_type_imm(inst):
        # Computes B-type immediate value using specific instruction bits
        return "".join((inst[-32], inst[-8], inst[-31:-25], inst[-12:-8], "0"))

    def calculate_j_type_imm(inst):
        # Computes J-type immediate value using specific instruction bits
        return "".join((inst[-32], inst[-20:-12], inst[-21], inst[-31:-21]))

    # Decoding map to associate opcodes with instruction types and operations
    decode_map = {
        "0110011": (  # R-type instructions
            "R",
            {
                "0000000": {"000": "add", "100": "xor", "110": "or", "111": "and"},
                "0100000": {"000": "sub"},
            },
        ),
        "0010011": ("I", {"000": "addi", "100": "xori", "110": "ori", "111": "andi"}),  # I-type
        "1100011": ("B", {"000": "beq", "001": "bne"}),  # B-type
        "0000011": ("load", "lw"),  # Load
        "0100011": ("store", "sw"),  # Store
        "1101111": ("JAL", "jal"),  # Jump and Link
        "1111111": ("HALT", "halt"),  # Halt
    }

    # Determine instruction type and decode fields
    if opcode in decode_map:
        instruction_type, operation_info = decode_map[opcode]
        if instruction_type == "R":  # R-type
            source_reg1, source_reg2, dest_reg = (
                instruction[-20:-15],
                instruction[-25:-20],
                instruction[-12:-7],
            )
            if isinstance(operation_info, dict) and funct7 in operation_info:
                decoded_instruction["type"] = operation_info[funct7].get(funct3, "unknown")

        elif instruction_type == "I":  # I-type
            source_reg1, dest_reg = instruction[-20:-15], instruction[-12:-7]
            immediate_val = instruction[:12]
            decoded_instruction["type"] = operation_info.get(funct3, "unknown")

        elif instruction_type == "B":  # B-type
            source_reg1, source_reg2 = instruction[-20:-15], instruction[-25:-20]
            immediate_val = calculate_b_type_imm(instruction)
            decoded_instruction["type"] = operation_info.get(funct3, "unknown")

        elif instruction_type == "load":  # Load
            source_reg1, dest_reg, immediate_val = (
                instruction[-20:-15],
                instruction[-12:-7],
                instruction[:12],
            )
            decoded_instruction["type"] = operation_info  # lw

        elif instruction_type == "store":  # Store
            source_reg1, source_reg2, immediate_val = (
                instruction[-20:-15],
                instruction[-25:-20],
                "".join((instruction[:7], instruction[-12:-7])),
            )
            decoded_instruction["type"] = operation_info  # sw

        elif instruction_type == "JAL":  # Jump and Link
            dest_reg, immediate_val = instruction[-12:-7], calculate_j_type_imm(instruction)
            decoded_instruction["type"] = operation_info  # jal

        elif instruction_type == "HALT":  # Halt
            decoded_instruction["type"] = operation_info  # halt
            return None

    # Add decoded fields to the dictionary
    decoded_instruction.update({"rs1": source_reg1, "rs2": source_reg2, "rd": dest_reg, "imm": immediate_val})

    return decoded_instruction


def inst_execute(decoded_instruction, register, data_memory, branch_taken, program_counter):
    # Retrieve values from the decoded instruction
    rs1_index = Binary_Decimal(decoded_instruction.get('rs1')) if decoded_instruction.get('rs1') else None
    rs2_index = Binary_Decimal(decoded_instruction.get('rs2')) if decoded_instruction.get('rs2') else None
    rd_index = Binary_Decimal(decoded_instruction.get('rd')) if decoded_instruction.get('rd') else None
    immediate_value = Twos_Compliment(decoded_instruction.get('imm')) if decoded_instruction.get('imm') else None

    # Handle R-type instructions
    if decoded_instruction['type'] in ('add', 'sub', 'or', 'and', 'xor'):
        operand1 = register.readRF(rs1_index)
        operand2 = register.readRF(rs2_index)
        
        # Perform ALU operation based on the instruction type
        alu_operations = {
            'add': lambda x, y: x + y,
            'sub': lambda x, y: x - y,
            'or': lambda x, y: x | y,
            'and': lambda x, y: x & y,
            'xor': lambda x, y: x ^ y
        }
        
        result = alu_operations[decoded_instruction['type']](operand1, operand2)
        register.writeRF(rd_index, result)

    # Handle I-type instructions
    elif decoded_instruction['type'] in ('addi', 'subi', 'ori', 'andi', 'xori'):
        operand1 = register.readRF(rs1_index)
        
        # Perform ALU operation with immediate value
        alu_operations = {
            'addi': lambda x, y: x + y,
            'subi': lambda x, y: x - y,
            'ori': lambda x, y: x | y,
            'andi': lambda x, y: x & y,
            'xori': lambda x, y: x ^ y
        }
        
        result = alu_operations[decoded_instruction['type']](operand1, immediate_value)
        register.writeRF(rd_index, result)

    # Handle Load instruction
    elif decoded_instruction['type'] == 'lw':
        memory_address = register.readRF(rs1_index) + immediate_value
        result = data_memory.readDataMem(memory_address)
        register.writeRF(rd_index, result)

    # Handle Store instruction
    elif decoded_instruction['type'] == 'sw':
        memory_address = register.readRF(rs1_index) + immediate_value
        data_to_store = register.readRF(rs2_index)
        data_memory.writeDataMem(memory_address, data_to_store)

    # Handle Branch instructions
    elif decoded_instruction['type'] == 'beq':
        operand1 = register.readRF(rs1_index)
        operand2 = register.readRF(rs2_index)
        if operand1 == operand2:
            branch_taken = True
            program_counter.IF["PC"] += immediate_value

    elif decoded_instruction['type'] == 'bne':
        operand1 = register.readRF(rs1_index)
        operand2 = register.readRF(rs2_index)
        if operand1 != operand2:
            branch_taken = True
            program_counter.IF["PC"] += immediate_value

    # Handle JAL instruction
    elif decoded_instruction['type'] == 'jal':
        register.writeRF(rd_index, program_counter.IF["PC"] + 4)
        branch_taken = True
        program_counter.IF["PC"] += immediate_value << 1

    # Handle HALT instruction
    elif decoded_instruction['type'] == 'HALT':
        branch_taken = True
        program_counter.IF["nop"] = True

    # Increment program counter if branch is not taken
    if not branch_taken:
        program_counter.IF["PC"] += 4
