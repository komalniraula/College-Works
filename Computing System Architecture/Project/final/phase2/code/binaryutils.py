def Decimal_Binary(n, n_bits=32):
    # Convert decimal to binary with fixed n_bits length
    return f"{n & (2**n_bits - 1):0{n_bits}b}"

def Binary_Decimal(n): 
    # Handling both binary string inputs and numeric inputs
    if isinstance(n, str):
        return int(n, 2)
    return n  # If n is already a number, just return it

def Twos_Compliment(n):
    # Properly handle both string and numeric types
    if isinstance(n, str):
        return int(n, 2) if n[0] == "0" else -((-int(n, 2)) & 0b11111111111)
    return n

def reset(state):
    if state.EX["nop"]:
        return
    
    # Resetting all fields in the EX dictionary
    defaults = {
        "Read_data1": 0,
        "Read_data2": 0,
        "Imm": 0,
        "Rs": 0,
        "Rt": 0,
        "Wrt_reg_addr": -1,
        "is_I_type": False,
        "rd_mem": 0,
        "wrt_mem": 0,
        "alu_op": 0,
        "wrt_enable": 0,
    }
    state.EX.update(defaults)

def Detect_Hazard(state, rs):
    mem_wrt_addr = state.MEM["Wrt_reg_addr"]
    wb_wrt_addr = state.WB["Wrt_reg_addr"]

    if rs == mem_wrt_addr and not state.MEM["rd_mem"]:
        # EX to 1st (state.MEM["ALUresult"])
        return 1
    elif rs == wb_wrt_addr and state.WB["wrt_enable"]:
        # EX to 2nd or MEM to 2nd (state.WB["Wrt_data"])
        return 2
    elif rs == mem_wrt_addr and state.MEM["rd_mem"]:
        # MEM to 1st (state.WB["Wrt_data"])
        state.EX["nop"] = True
        state.ID["is_hazard"] = True
        return 3
    return 0
