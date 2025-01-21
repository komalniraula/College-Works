from binaryutils import *

def Five_Stage_decode(state,register):
    reset(state)
    instruction = state.ID["Instr"]

    # Handles R-type instructions, focusing on decoding and execution setup.

    if instruction[-7:] == "0110011":  
        state.EX["Rs"] = instruction[-20:-15]
        state.EX["Rt"] = instruction[-25:-20]
        state.EX["Wrt_reg_addr"] = instruction[-12:-7]

        rs1 = Binary_Decimal(state.EX["Rs"])
        rs2 = Binary_Decimal(state.EX["Rt"])
        state.EX["Wrt_reg_addr"] = Binary_Decimal(state.EX["Wrt_reg_addr"])

        hazard_rs1 = Detect_Hazard(state, rs1)
        hazard_rs2 = Detect_Hazard(state, rs2)

        if hazard_rs1 == 3 or hazard_rs2 ==3:
            return 

        if hazard_rs1 == 1:
            state.EX["Read_data1"] = state.MEM["ALUresult"]
        elif hazard_rs1 == 2:
            state.EX["Read_data1"] = state.WB["Wrt_data"]
        else:
            state.EX["Read_data1"] = register.readRF(rs1)

        if hazard_rs2 == 1:
            state.EX["Read_data2"] = state.MEM["ALUresult"]
        elif hazard_rs2 == 2:
            state.EX["Read_data2"] = state.WB["Wrt_data"]
        else:
            state.EX["Read_data2"] = register.readRF(rs2)  
        

        state.EX["wrt_enable"] = 1
        state.EX["is_I_type"] = False

        if instruction[-15:-12] == "000" and instruction[-32:-25] == "0000000":
            # Operation for addition.
            state.EX["alu_op"] = "add"

        elif instruction[-15:-12] == "000" and instruction[-32:-25] == "0100000":
            # Operation for subtraction.
            state.EX["alu_op"] = "sub"

        elif instruction[-15:-12] == "100" and instruction[-32:-25] == "0000000":
            # Operation for bitwise XOR.
            state.EX["alu_op"] = "xor"

        elif instruction[-15:-12] == "110" and instruction[-32:-25] == "0000000":
            # Operation for bitwise OR.
            state.EX["alu_op"] = "or"

        elif instruction[-15:-12] == "111" and instruction[-32:-25] == "0000000":
            # Operation for bitwise AND.
            state.EX["alu_op"] = "and"

    # Decoding logic for I-type instructions. ---------------------------------------------------------------------------------


    elif instruction[-7:] == "0010011":  # I-type
        state.EX["Rs"] = instruction[-20:-15]
        state.EX["Imm"] = instruction[-32:-20]
        state.EX["Wrt_reg_addr"] = instruction[-12:-7]
        
        rs1 = Binary_Decimal(state.EX["Rs"])
        state.EX["Wrt_reg_addr"] = Binary_Decimal(state.EX["Wrt_reg_addr"])

        hazard_rs1 = Detect_Hazard(state, rs1)
        
        if hazard_rs1 == 3:
            return 

        if hazard_rs1 == 1:
            state.EX["Read_data1"] = state.MEM["ALUresult"]
        elif hazard_rs1 == 2:
            state.EX["Read_data1"] = state.WB["Wrt_data"]
        else:
            state.EX["Read_data1"] = register.readRF(rs1)

        state.EX["is_I_type"] = True
        state.EX["wrt_enable"] = 1

        if instruction[-15:-12] == "000":
            # Operation for addition with immediate.
            state.EX["alu_op"] = "addi"

        elif instruction[-15:-12] == "100":
            # Operation for bitwise XOR with immediate.
            state.EX["alu_op"] = "xori"

        elif instruction[-15:-12] == "110":
            # Operation for bitwise OR with immediate.
            state.EX["alu_op"] = "ori"

        elif instruction[-15:-12] == "111":
            # Operation for bitwise AND with immediate.
            state.EX["alu_op"] = "andi"
    
    # Processing logic for Load-type instructions. --------------------------------------------------------------------
    
    elif instruction[-7:] == "0000011":  
        state.EX["Rs"] = instruction[-20:-15]
        state.EX["Imm"] = instruction[-32:-20]
        state.EX["Wrt_reg_addr"] = instruction[-12:-7]

        rs1 = Binary_Decimal(state.EX["Rs"])   
        state.EX["Wrt_reg_addr"] = Binary_Decimal(state.EX["Wrt_reg_addr"])

        hazard_rs1 = Detect_Hazard(state, rs1)
        
        if hazard_rs1 == 3:
            return 

        if hazard_rs1 == 1:
            state.EX["Read_data1"] = state.MEM["ALUresult"]
        elif hazard_rs1 == 2:
            state.EX["Read_data1"] = state.WB["Wrt_data"]
        else:
            state.EX["Read_data1"] = register.readRF(rs1)

        state.EX["rd_mem"] = 1
        state.EX["wrt_enable"] = 1
        state.EX["is_I_type"] = True
        state.EX["alu_op"] = "lw"
        
    # Decoding and processing logic for Store-type instructions. ---------------------------------------------------------------------------------------

    elif instruction[-7:] == "0100011": 
        state.EX["Rs"] = instruction[-20:-15]
        state.EX["Imm"] = "".join((instruction[-32:-25], instruction[-12:-7]))
        state.EX["Rt"] = instruction[-25:-20]

        rs1 = Binary_Decimal(state.EX["Rs"])
        rs2 = Binary_Decimal(state.EX["Rt"])

        hazard_rs1 = Detect_Hazard(state, rs1)
        hazard_rs2 = Detect_Hazard(state, rs2)
        
        if hazard_rs1 == 3 or hazard_rs2 ==3:
            return 

        if hazard_rs1 == 1:
            state.EX["Read_data1"] = state.MEM["ALUresult"]
        elif hazard_rs1 == 2:
            state.EX["Read_data1"] = state.WB["Wrt_data"]
        else:
            state.EX["Read_data1"] = register.readRF(rs1)

        if hazard_rs2 == 1:
            state.EX["Read_data2"] = state.MEM["ALUresult"]
        elif hazard_rs2 == 2:
            state.EX["Read_data2"] = state.WB["Wrt_data"]
        else:
            state.EX["Read_data2"] = register.readRF(rs2) 

        state.EX["is_I_type"] = True
        state.EX["wrt_mem"] = 1
        state.EX["alu_op"] = "sw"

    # Handling Branch-type instructions. --------------------------------------------------------------------

    elif instruction[-7:] == "1100011":

        state.EX["Rs"] = instruction[-20:-15]
        state.EX["Imm"] = "".join(
            (
                instruction[-32],
                instruction[-8],
                instruction[-31:-25],
                instruction[-12:-8],
                "0",
            )
        )
        state.EX["Rt"] = instruction[-25:-20]

        rs1 = Binary_Decimal(state.EX["Rs"])
        rs2 = Binary_Decimal(state.EX["Rt"])

        hazard_rs1 = Detect_Hazard(state, rs1)
        hazard_rs2 = Detect_Hazard(state, rs2)

        if hazard_rs1 == 3 or hazard_rs2 ==3:
            return 

        if hazard_rs1 == 1:
            state.EX["Read_data1"] = state.MEM["ALUresult"]
        elif hazard_rs1 == 2:
            state.EX["Read_data1"] = state.WB["Wrt_data"]
        else:
            state.EX["Read_data1"] = register.readRF(rs1)

        if hazard_rs2 == 1:
            state.EX["Read_data2"] = state.MEM["ALUresult"]
        elif hazard_rs2 == 2:
            state.EX["Read_data2"] = state.WB["Wrt_data"]
        else:
            state.EX["Read_data2"] = register.readRF(rs2)        

        if instruction[-15:-12] == "000":
            # Operation for Branch if Equal.
            state.EX["alu_op"] = "beq"

        elif instruction[-15:-12] == "001":
            # Operation for Branch if Not Equal.
            state.EX["alu_op"] = "bne"
        
        result = abs(state.EX["Read_data1"] - state.EX["Read_data2"])
        if bool(result) == (state.EX["alu_op"] == "bne"):
            state.IF["PC"] += Twos_Compliment(state.EX["Imm"]) - 4
            state.ID["nop"] = state.EX["nop"] = True
        else: 
            state.EX["nop"] = True

    # Logic for Jump and Link (JAL) instructions. ---------------------------------------------------------------------------------------------------------
    
    elif instruction[-7:] == "1101111":  
        state.EX["Imm"] = "".join((instruction[-32], instruction[-20:-12], instruction[-21],instruction[-31:-21],"0" ))
        state.EX["Wrt_reg_addr"] = instruction[-12:-7]
        state.EX["Wrt_reg_addr"] = Binary_Decimal(state.EX["Wrt_reg_addr"])
        state.EX["Read_data1"] = state.IF["PC"] - 4
        state.EX["Read_data2"] = 4
        state.EX["wrt_enable"] = 1
        state.EX["alu_op"] = "jal"
        state.IF["PC"] += Twos_Compliment(state.EX["Imm"]) - 4
        state.ID["nop"] = True
    
    else:
        state.IF["nop"] = True

    if state.EX["is_I_type"]:
        state.EX["Imm"] = Twos_Compliment(state.EX["Imm"])
