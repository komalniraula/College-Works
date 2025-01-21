import os
import argparse
from singlestagedecex import inst_decode, inst_execute
from binaryutils import *
from fivestagedcode import *

MemSize = 1000  # memory size, in reality, the memory size should be 2^32, but for this lab, for the space reason, we keep it as this large number, but the memory is still 32-bit addressable.

class InsMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        
        with open(ioDir + os.sep + "imem.txt") as im:
            self.IMem = [data.replace("\n", "") for data in im.readlines()]

    def readInstr(self, ReadAddress):
        #read instruction memory
        #return 32 bit hex val
        instruction = ''.join(self.IMem[ReadAddress : ReadAddress+4])
        return instruction

class DataMem(object):
    def __init__(self, name, ioDir):
        self.id = name
        self.ioDir = ioDir
        with open(ioDir + os.sep + "dmem.txt") as dm:
            self.DMem = [data.replace("\n", "") for data in dm.readlines()]
            self.DMem.extend(["00000000"]*(1000-len(self.DMem)))

    def readDataMem(self, ReadAddress):
        #read data memory
        #return 32 bit hex val
        data = ''.join(self.DMem[ReadAddress : ReadAddress+4])
        return Twos_Compliment(data)
        
    def writeDataMem(self, Address, WriteData):
        # Ensure binary string (32 bits)
        if isinstance(WriteData, int):
            # Convert integer back to a binary string slong with padding
            WriteData = f"{WriteData:032b}"

        # Write into byte memory (8-bit chunks)
        arr = [WriteData[i:i+8] for i in range(0, len(WriteData), 8)]
        
        for i in range(len(arr)):
            self.DMem[Address+i] = arr[i]
                     
    def outputDataMem(self):
        resPath = self.ioDir + os.sep + self.id + "_DMEMResult.txt"
        with open(resPath, "w") as rp:
            rp.writelines([str(data) + "\n" for data in self.DMem])

class RegisterFile(object):
    def __init__(self, ioDir):
        self.outputFile = ioDir + "RFResult.txt"
        self.Registers = [0x0 for i in range(32)]

    def readRF(self, Reg_addr):
        return self.Registers[Reg_addr]

    def writeRF(self, Reg_addr, Wrt_reg_data):
        if Reg_addr != 0:
            self.Registers[Reg_addr] = Wrt_reg_data

    def outputRF(self, cycle):
        op = ["-"*70+"\n", "State of RF after executing cycle:" + str(cycle) + "\n"]
        # Convert values to strings before concatenating
        op.extend([Decimal_Binary(val) + "\n" for val in self.Registers])

        if cycle == 0:
            perm = "w"
        else:
            perm = "a"
        with open(self.outputFile, perm) as file:
            file.writelines(op)

class State(object):
    def __init__(self):
        self.IF = {"nop": False, "PC": 0}
        self.ID = {"nop": True, "Instr": 0, "is_hazard":False}
        self.EX = {"nop": True, "Read_data1": 0, "Read_data2": 0, "Imm": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "is_I_type": False, "rd_mem": 0, 
                   "wrt_mem": 0, "alu_op": 0, "wrt_enable": 0}
        self.MEM = {"nop": True, "ALUresult": 0, "Store_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "rd_mem": 0, 
                   "wrt_mem": 0, "wrt_enable": 0}
        self.WB = {"nop": True, "Wrt_data": 0, "Rs": 0, "Rt": 0, "Wrt_reg_addr": 0, "wrt_enable": 0}

class Core(object):
    def __init__(self, ioDir, imem, dmem):
        self.myRF = RegisterFile(ioDir)
        self.cycle = 0
        self.halted = False
        self.ioDir = ioDir
        self.state = State()
        self.nextState = State()
        self.ext_imem = imem
        self.ext_dmem = dmem
        self.takeBranch = False
        self.num_ins = 0

class SingleStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(SingleStageCore, self).__init__(ioDir + os.sep + "SS_", imem, dmem)
        self.opFilePath = ioDir + os.sep + "StateResult_SS.txt"

    def step(self):
        if self.state.IF["nop"]:
            self.halted = True

        instr = self.ext_imem.readInstr(self.state.IF["PC"])
        decodedInst = inst_decode(instr) #dict of all operands
        
        if decodedInst is None: 
            self.halted = True
            self.state.IF["nop"] = True
        else: 
            inst_execute(decodedInst, self.myRF, self.ext_dmem, self.takeBranch, self.state)

        self.myRF.outputRF(self.cycle) # dump RF
        self.printState(self.state, self.cycle) # print states after executing cycle 0, cycle 1, cycle 2 ... 

        self.cycle += 1
        self.num_ins += 1

    def printState(self, state, cycle):
        printstate = ["-"*70+"\n", "State after executing cycle: " + str(cycle) + "\n"]
        printstate.append("IF.PC: " + str(state.IF["PC"]) + "\n")
        printstate.append("IF.nop: " + str(state.IF["nop"]) + "\n")

        if cycle == 0: 
            perm = "w"
        else: 
            perm = "a"
        with open(self.opFilePath, perm) as wf:
            wf.writelines(printstate)

class FiveStageCore(Core):
    def __init__(self, ioDir, imem, dmem):
        super(FiveStageCore, self).__init__(ioDir + os.sep + "FS_", imem, dmem)
        self.opFilePath = ioDir + os.sep + "StateResult_FS.txt"

    def step(self):
        # Your implementation
        if self.state.IF["nop"] and self.state.ID["nop"] and self.state.EX["nop"] and self.state.MEM["nop"] and self.state.WB["nop"]:
            self.halted = True

        
        # --------------------- WB stage ---------------------
        
        if not self.state.WB["nop"]:
            
            if (self.state.WB["wrt_enable"]==1):
                self.myRF.writeRF(self.state.WB["Wrt_reg_addr"], self.state.WB["Wrt_data"])
            
            if self.state.MEM["nop"]:
                self.state.WB["nop"] = True
        else:
            if not self.state.MEM["nop"]:
                self.state.WB["nop"] = False
        
        # --------------------- MEM stage --------------------
        if not self.state.MEM["nop"]:
            
            self.state.WB["Rs"] = self.state.MEM["Rs"]
            self.state.WB["Rt"] = self.state.MEM["Rt"]
            self.state.WB["Wrt_reg_addr"] = self.state.MEM["Wrt_reg_addr"]
            self.state.WB["wrt_enable"] = self.state.MEM["wrt_enable"]
    
            if(self.state.MEM["wrt_mem"]==1):
                # writing back to datamem with store
                self.ext_dmem.writeDataMem(self.state.MEM["ALUresult"] , self.state.MEM["Store_data"])
            elif(self.state.MEM["rd_mem"]==1):
                # reading from register with load
                self.state.WB["Wrt_data"] = self.ext_dmem.readDataMem(self.state.MEM["ALUresult"])
            elif(self.state.MEM["wrt_mem"]==0 & self.state.MEM["rd_mem"]==0):
                # any other branch/R-type instruction does not require memory
                self.state.WB["Wrt_data"] = self.state.MEM["ALUresult"]
            
            if self.state.EX["nop"]:
                self.state.MEM["nop"] = True
        else:
            if not self.state.EX["nop"]:
                self.state.MEM["nop"] = False
        
        
        # --------------------- EX stage ---------------------
        if not self.state.EX["nop"]:
            self.state.MEM["wrt_enable"]=self.state.EX["wrt_enable"]
            self.state.MEM["Wrt_reg_addr"]=self.state.EX["Wrt_reg_addr"]
            self.state.MEM["rd_mem"]=self.state.EX["rd_mem"]
            self.state.MEM["wrt_mem"]=self.state.EX["wrt_mem"] 
            self.state.MEM["Rs"]=self.state.EX["Rs"] 
            self.state.MEM["Rt"]=self.state.EX["Rt"] 

            #-------------------- R Type ---------------------
            if (self.state.EX["alu_op"]=='add'):
                self.state.MEM["ALUresult"]=(self.state.EX["Read_data1"]) + (self.state.EX["Read_data2"])

            if (self.state.EX["alu_op"]=='sub'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] - self.state.EX["Read_data2"]

            if (self.state.EX["alu_op"]=='xor'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] ^ self.state.EX["Read_data2"]

            if (self.state.EX["alu_op"]=='or'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] | self.state.EX["Read_data2"]

            if (self.state.EX["alu_op"]=='and'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] & self.state.EX["Read_data2"]
            
            #--------------------- I Type ---------------------
            if (self.state.EX["alu_op"]=='addi'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] + self.state.EX["Imm"]

            if (self.state.EX["alu_op"]=='xori'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] ^ self.state.EX["Imm"]

            if (self.state.EX["alu_op"]=='ori'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] | self.state.EX["Imm"]  

            if (self.state.EX["alu_op"]=='andi'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] & self.state.EX["Imm"] 
            
            #--------------------- Load Type ---------------------
            if (self.state.EX["alu_op"]=='lw'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] + self.state.EX["Imm"]
            
            #--------------------- Store Type ---------------------
            if (self.state.EX["alu_op"]=='sw'):
                self.state.MEM["ALUresult"]=self.state.EX["Read_data1"] + self.state.EX["Imm"] 
                self.state.MEM["Store_data"]=self.state.EX["Read_data2"] 
            
            #--------------------- JAL Type ---------------------
            if (self.state.EX["alu_op"]=='jal'): 
                self.state.MEM["Wrt_reg_addr"]=self.state.EX["Wrt_reg_addr"]
                self.state.MEM["ALUresult"] = self.state.EX["Read_data1"] + self.state.EX["Read_data2"]
            
            self.state.MEM["nop"] = False

            if self.state.ID["nop"]:
                self.state.EX["nop"] = True
        else:
            if not self.state.ID["nop"]:
                self.state.EX["nop"] = False
        
        
        # --------------------- ID stage ---------------------
        if not self.state.ID["nop"]:
            
            self.state.EX["nop"] = False
            self.state.ID["is_hazard"] = False
            Five_Stage_decode(self.state,self.myRF)
            if self.state.IF["nop"]:
                self.state.ID["nop"] = True
        else:
            if not self.state.IF["nop"]:
                self.state.ID["nop"] = False
        
        # --------------------- IF stage ---------------------
        if not self.state.IF["nop"]:
            if self.state.ID["nop"] or (self.state.EX["nop"] and self.state.ID["is_hazard"]):
                pass
            else:
                self.num_ins += 1
                instruction = self.ext_imem.readInstr(self.state.IF["PC"])

                if instruction == "1"*32:
                    self.state.IF["nop"] = True
                    self.state.ID["nop"] = True
                else:
                    self.state.ID["Instr"] = instruction
                    self.state.IF["PC"] += 4

                if not self.state.IF["nop"]: 
                    self.state.ID["nop"] = False
        
        self.myRF.outputRF(self.cycle) 
        self.printState(self.state, self.cycle) 
        
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

def Performance_Metrics(ioDir, cpiSS, ipcSS, cycles_SS, numIns_SS,
                       cpiFS, ipcFS, cycles_FS, numIns_FS):
    opFilePath = ioDir + os.sep + "PerformanceMetrics.txt"
    printstate_SS = ["Performance of Single Stage:" + "\n",
                     "#Cycles -> " + str(cycles_SS) + "\n",
                     "#Instructions -> " + str(numIns_SS) + "\n",
                     "CPI -> " + str(cpiSS) + "\n",
                     "IPC -> " + str(ipcSS) + "\n\n",
                     "Performance of Five Stage:" + "\n",
                     "#Cycles -> " + str(cycles_FS) + "\n",
                     "#Instructions -> " + str(numIns_FS) + "\n",
                     "CPI -> " + str(cpiFS) + "\n",
                     "IPC -> " + str(ipcFS)]

    with open(opFilePath, 'w') as wf:
        wf.writelines(printstate_SS)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='RV32I processor')
    parser.add_argument('--iodir', default="", type=str, help='Directory containing the input files.')
    args = parser.parse_args()

    input_output_dir = os.path.abspath(args.iodir)
    print("IO Directory:", input_output_dir)

    instruct_mem = InsMem("Imem", input_output_dir)
    Dmemory_SS = DataMem("SS", input_output_dir)
    Dmemory_FS = DataMem("FS", input_output_dir)

    SS_core = SingleStageCore(input_output_dir, instruct_mem, Dmemory_SS)
    FS_core = FiveStageCore(input_output_dir, instruct_mem, Dmemory_FS)
    
    while(True):
        if not SS_core.halted:
            SS_core.step()
        if SS_core.halted:
            SS_core.step()
            break

    #Process instruction using FS
    while True:
        if not FS_core.halted:
            FS_core.step()     

        if FS_core.halted:
            break           
    
    Dmemory_SS.outputDataMem()
    Dmemory_FS.outputDataMem()

    cpiSS = SS_core.cycle / (SS_core.cycle - 1)
    ipcSS = 1 / cpiSS    

    insSS = SS_core.num_ins - 1
    insFS = FS_core.num_ins

    cpiFS = FS_core.cycle / FS_core.num_ins
    ipcFS = 1 / cpiFS    

    Performance_Metrics(input_output_dir, cpiSS, ipcSS, SS_core.cycle, insSS, cpiFS, ipcFS, FS_core.cycle, insFS)


    
