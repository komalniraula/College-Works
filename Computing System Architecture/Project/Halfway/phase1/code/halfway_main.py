import os
import argparse

#Student name: Komal Niraula
#Net id: kn2505

MemSize = 1000  # memory size, in reality, the memory size should be 2^32, but for this lab, for the space resaon, we keep it as this large number, but the memory is still 32-bit addressable.

class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        with open(os.path.join(ioDir, "imem.txt")) as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]
        # Fill the rest of memory with zeros
        self.IMem += ['00000000'] * (MemSize - len(self.IMem))

    def readInstr(self, ReadAddress):
        # Read instruction memory
        # Return 32-bit hex value
        instr_bin = ''.join(self.IMem[ReadAddress : ReadAddress + 4])
        instr_int = int(instr_bin, 2)
        instr_hex = format(instr_int, '08x')
        return instr_hex
              
class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(os.path.join(ioDir, "dmem.txt")) as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]
        # Fill the rest of memory with zeros
        self.DMem += ['00000000'] * (MemSize - len(self.DMem))

    def readDataMem(self, ReadAddress):
        # Read data memory
        # Return 32-bit hex value
        data_bin = ''.join(self.DMem[ReadAddress : ReadAddress + 4])
        data_int = int(data_bin, 2)
        data_hex = format(data_int, '08x')
        return data_hex
        
    def writeDataMem(self, Address, WriteData):
        # Write data into byte-addressable memory
        WriteData_int = WriteData & 0xFFFFFFFF
        WriteData_bin = format(WriteData_int, '032b')
        bytes_list = [WriteData_bin[i*8 : (i+1)*8] for i in range(4)]
        for i in range(4):
            self.DMem[Address + i] = bytes_list[i]
                     
    def outputDataMem(self):
        resPath = os.path.join(self.ioDir, f"{self.id}_DMEMResult.txt")

        os.makedirs(os.path.dirname(resPath), exist_ok=True)

        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])

class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = [0x0 for i in range(32)]

    def readRF(self, Reg_addr):
        return self.Registers[Reg_addr]  # Read register
    
    def writeRF(self, Reg_addr, Wrt_reg_data):
        if Reg_addr != 0:
            self.Registers[Reg_addr] = Wrt_reg_data & 0xFFFFFFFF  # Write into register if Reg_addr is not zero
         
    def outputRF(self, cycle):
        op = ["-" * 70 + "\n", "State of RF after executing cycle:" + str(cycle) + "\n"]
        # Format each register as a 32-bit binary string
        op.extend([format(val, '032b') + "\n" for val in self.Registers])
        
        # Determine write mode based on cycle number
        perm = "w" if cycle == 0 else "a"
        
        with open(self.outputFile, perm) as file:
            file.writelines(op)

class State(object):
    def __init__(self):
        self.IF = {"nop": bool(False), "PC": int(0), "taken": bool(False)}
        self.ID = {"nop": bool(False), "instr": str("0"*32), "PC": int(0), "hazard_nop": bool(False)}
        self.EX = {"nop": bool(False), "instr": str("0"*32), "Read_data1": str("0"*32), "Read_data2": str("0"*32), "Imm": str("0"*32), "Rs": str("0"*5), "Rt": str("0"*5), "Wrt_reg_addr": str("0"*5), "is_I_type": bool(False), "rd_mem": bool(False), 
                   "wrt_mem": bool(False), "alu_op": str("00"), "wrt_enable": bool(False)} # alu_op 00 -> add, 01 -> and, 10 -> or, 11 -> xor
        self.MEM = {"nop": bool(False), "ALUresult": str("0"*32), "Store_data": str("0"*32), "Rs": str("0"*5), "Rt": str("0"*5), "Wrt_reg_addr": str("0"*5), "rd_mem": bool(False), 
                   "wrt_mem": bool(False), "wrt_enable": bool(False)}
        self.WB = {"nop": bool(False), "Wrt_data": str("0"*32), "Rs": str("0"*5), "Rt": str("0"*5), "Wrt_reg_addr": str("0"*5), "wrt_enable": bool(False)}

class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.instr_executed = 0  # Initialize the instruction executed counter
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem

class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(os.path.join(ioDir, "SS_"), imem, dmem)
        self.opFilePath = os.path.join(ioDir, "StateResult_SS.txt")

    def step(self):
        # Reset halted to False at the beginning of each step
        self.halted = False

        # Fetch the instruction
        fetchedInstr = int(self.ext_imem.readInstr(self.state.IF["PC"]), 16)  # Convert hex to integer
        opcode = fetchedInstr & 0x7F  # Extract the opcode (7 least significant bits)

        # Decode and execute the instruction
        self.decode_execute(opcode, fetchedInstr)

        # Increment instruction count before checking for halt
        self.instr_executed += 1

        # Check if the halt condition (nop) is set
        if self.state.IF["nop"]:
            self.halted = True  # This will stop further execution

        # PC update logic
        if self.state.IF["taken"]:
            self.nextState.IF["PC"] = self.state.IF["PC"]
            self.state.IF["taken"] = False
        else:
            if not self.halted:
                self.nextState.IF["PC"] = self.state.IF["PC"] + 4

        # Output register state and print state
        self.myRF.outputRF(self.cycle)
        self.printState(self.nextState, self.cycle)

        # Update state and increment cycle count
        self.state = self.nextState
        self.cycle += 1

        # Final state capture if halted
        if self.halted:
            self.myRF.outputRF(self.cycle)  # Capture the halted state in RF
            self.printState(self.nextState, self.cycle)
            self.cycle += 1  # Include the halt cycle in the count


    # ALU arithmetic implement
    def calculate_R(self, funct7, funct3, rs1, rs2):
        rd = 0
        
        if funct7 == 0b0000000 and funct3 == 0b000: # ADD
            rd = rs1 + rs2

        if funct7 == 0b0100000 and funct3 == 0b000: # SUB
            rd = rs1 - rs2

        if funct7 == 0b0000000 and funct3 == 0b100: # XOR
            rd = rs1 ^ rs2

        if funct7 == 0b0000000 and funct3 == 0b110: # OR
            rd = rs1 | rs2

        if funct7 == 0b0000000 and funct3 == 0b111: # AND
            rd = rs1 & rs2

        return rd

    # compute sign extended immediate, sign bit:most significant bit location
    def sign_extend(self, val, sign_bit):

        if (val & (1 << sign_bit)) != 0:  # get sign bit, if is set 
            val = val - (1 << (sign_bit + 1))  # negative value complement
        return val  

    def calculate_I(self, funct3, rs1, imm):
        rd = 0

        if funct3 == 0b000: # ADDI
            rd = rs1 + self.sign_extend(imm, 11)

        if funct3 == 0b100: # XORI
            rd = rs1 ^ self.sign_extend(imm, 11)

        if funct3 == 0b110: # ORI
            rd = rs1 | self.sign_extend(imm, 11)

        if funct3 == 0b111: # ANDI
            rd = rs1 & self.sign_extend(imm, 11)

        return rd

    def decode_execute(self, opcode, fetchedInstr):
        
        if opcode == 0b0110011: # R-type

            # get funct7
            funct7 = fetchedInstr >> 25
            # get funct3
            funct3 = (fetchedInstr >> 12) & ((1 << 3) - 1)
            # get rs2
            rs2 = (fetchedInstr >> 20) & ((1 << 5) - 1)
            # get rs1
            rs1 = (fetchedInstr >> 15) & ((1 << 5) - 1)
            # get rd
            rd = (fetchedInstr >> 7) & ((1 << 5) - 1)

            # get data in rs1
            data_rs1 = self.myRF.readRF(rs1)
            # get data in rs2
            data_rs2 = self.myRF.readRF(rs2)
            # get result data
            data_rd = self.calculate_R(funct7, funct3, data_rs1, data_rs2)
            # store all fetched and computed data
            self.myRF.writeRF(rd, data_rd)

        elif opcode == 0b0010011: # I Type

            # get immediate
            imm = fetchedInstr >> 20 & ((1 << 12) - 1)

            # get funct3
            funct3 = (fetchedInstr >> 12) & ((1 << 3) - 1)
            # get rs1
            rs1 = (fetchedInstr >> 15) & ((1 << 5) - 1)
            # get rd
            rd = (fetchedInstr >> 7) & ((1 << 5) - 1)

            # get data in rs1
            data_rs1 = self.myRF.readRF(rs1)
            # get result data
            data_rd = self.calculate_I(funct3, data_rs1, imm)
            # store result data in rd register
            self.myRF.writeRF(rd, data_rd)

        elif opcode == 0b1101111: # J Type Jal

            # get imm
            imm19_12 = (fetchedInstr >> 12) & ((1 << 8) - 1)
            imm11 = (fetchedInstr >> 20) & 1
            imm10_1 = (fetchedInstr >> 21) & ((1 << 10) - 1)
            imm20 = (fetchedInstr >> 31) & 1
            imm = (imm20 << 20) | (imm10_1 << 1) | (imm11 << 11) | (imm19_12 << 12)

            # get rd
            rd = (fetchedInstr >> 7) & ((1 << 5) - 1)

            self.myRF.writeRF(rd, self.state.IF["PC"] + 4)
            self.nextState.IF["PC"] = self.state.IF["PC"] + self.sign_extend(imm, 20)
            self.state.IF["taken"] = True

        elif opcode == 0b1100011:   # B Type

            # get imm
            imm11 = (fetchedInstr >> 7) & 1
            imm4_1 = (fetchedInstr >> 8) & ((1 << 4) - 1)
            imm10_5 = (fetchedInstr >> 25) & ((1 << 6) - 1)
            imm12 = (fetchedInstr >> 31) & 1
            imm = (imm11 << 11) | (imm4_1 << 1) | (imm10_5 << 5) | (imm12 << 12)

            # get rs2
            rs2 = (fetchedInstr >> 20) & ((1 << 5) - 1)
            # get rs1
            rs1 = (fetchedInstr >> 15) & ((1 << 5) - 1)
            # get funct3
            funct3 = (fetchedInstr >> 12) & ((1 << 3) - 1)

            # BEQ
            if funct3 == 0b000:
                data_rs1 = self.myRF.readRF(rs1)
                data_rs2 = self.myRF.readRF(rs2)
                if data_rs1 == data_rs2:
                    self.nextState.IF["PC"] = self.state.IF["PC"] + self.sign_extend(imm, 12)
                    self.state.IF["taken"] = True

            # BNE
            else:
                data_rs1 = self.myRF.readRF(rs1)
                data_rs2 = self.myRF.readRF(rs2)
                if data_rs1 != data_rs2:
                    self.nextState.IF["PC"] = self.state.IF["PC"] + self.sign_extend(imm, 12)
                    self.state.IF["taken"] = True

        elif opcode == 0b0000011: # LW

            # get imm
            imm = fetchedInstr >> 20
            # get rs1
            rs1 = (fetchedInstr >> 15) & ((1 << 5) - 1)
            # get rd
            rd = (fetchedInstr >> 7) & ((1 << 5) - 1)

            self.myRF.writeRF(Reg_addr=rd,
                              Wrt_reg_data=int(self.ext_dmem.readDataMem(
                                  ReadAddress=self.myRF.readRF(rs1) + self.sign_extend(imm, 11)), 16))

        elif opcode == 0b0100011: # SW

            # get imm
            imm11_5 = fetchedInstr >> 25
            imm4_0 = (fetchedInstr >> 7) & ((1 << 5) - 1)
            imm = (imm11_5 << 5) | imm4_0

            # get funct3
            funct3 = fetchedInstr & (((1 << 3) - 1) << 12)
            # get rs1
            rs1 = (fetchedInstr >> 15) & ((1 << 5) - 1)
            # get rd
            rs2 = (fetchedInstr >> 20) & ((1 << 5) - 1)

            self.ext_dmem.writeDataMem(Address=(rs1 + self.sign_extend(imm, 11)) & ((1 << 32) - 1),
                                       WriteData=self.myRF.readRF(rs2))

        elif opcode == 0xFFFFFFFF:  # Halt or NOP condition (assuming all 1s as halt)
            self.state.IF["nop"] = True  # Set the halt signal
        
        # HALT
        else:
            self.state.IF["nop"] = True

    # print StateResult_SS.txt
    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")
        
        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(os.path.join(ioDir, "FS_"), imem, dmem)
        self.opFilePath = os.path.join(ioDir, "StateResult_FS.txt")

    def step(self):
        # Your implementation
        # --------------------- WB stage ---------------------
        
        
        
        # --------------------- MEM stage --------------------
        
        
        
        # --------------------- EX stage ---------------------
        
        
        
        # --------------------- ID stage ---------------------
        
        
        
        # --------------------- IF stage ---------------------
        
        self.halted = True
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and self.state.WB["nop"]:
            self.halted = True
        
        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.nextState, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 
        
        self.state = self.nextState #The end of the cycle and updates the current state with the values calculated in this cycle
        self.cycle += 1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.extend(["IF." + key + ": " + str(val) + "\n" for key, val in state.IF.items()])
        printstate.extend(["ID." + key + ": " + str(val) + "\n" for key, val in state.ID.items()])
        printstate.extend(["EX." + key + ": " + str(val) + "\n" for key, val in state.EX.items()])
        printstate.extend(["MEM." + key + ": " + str(val) + "\n" for key, val in state.MEM.items()])
        printstate.extend(["WB." + key + ": " + str(val) + "\n" for key, val in state.WB.items()])

        if(cycle == 0): perm = "w"
        else: perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

if __name__ == "__main__":
     
    #parse arguments for input file location
    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    ioDir = os.path.abspath(args.iodir)
    print("IO Directory:", ioDir)

    imem = InsMem("Imem", ioDir)
    dmem_ss = DataMem("SS", ioDir)
    #dmem_fs = DataMem("FS", ioDir)
    
    ssCore = SingleStageCore(ioDir, imem, dmem_ss)
    #fsCore = FiveStageCore(ioDir, imem, dmem_fs)

    while(True):
        if not ssCore.halted:
            ssCore.step()
        
        #if not fsCore.halted:
            #fsCore.step()

        if ssCore.halted: #and fsCore.halted:
            break
    
    # Dump SS and FS data mem.
    dmem_ss.outputDataMem()
    #dmem_fs.outputDataMem()

    #Performance metrics
    performance_metrics_path = os.path.join(ioDir, "PerformanceMetrics_Result.txt")
    with open(performance_metrics_path, "w") as pm_file:
        pm_file.write("-"*29 + "Single Stage Core Performance Metrics" + "-"*29 + "\n")
        pm_file.write("Number of cycles taken: {}\n".format(ssCore.cycle))
        pm_file.write("Total Number of Instructions: {}\n".format(ssCore.instr_executed))
        
        # Calculate CPI and IPC
        cpi = ssCore.cycle / ssCore.instr_executed if ssCore.instr_executed != 0 else 0
        ipc = ssCore.instr_executed / ssCore.cycle if ssCore.cycle != 0 else 0
        
        pm_file.write("Cycles per instruction: {:.5f}\n".format(cpi))
        pm_file.write("Instructions per cycle: {:.6f}\n".format(ipc))