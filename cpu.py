"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
CMP = 0b10100111
HLT = 0b00000001
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100

SP = 7

L = 5
G = 6
E = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.fl = [0] * 8
        self.ram = [0] * 256   
        self.pc = 0
        self.dispatch_table = {
            LDI: self.LDI_op,
            PRN: self.PRN_op,
            ADD: self.ADD_op,
            MUL: self.MUL_op,
            CMP: self.CMP_op,
            HLT: self.HLT_op,
            PUSH: self.PUSH_op,
            POP: self.POP_op,
            CALL: self.CALL_op,
            RET: self.RET_op,
            JEQ: self.JEQ_op,
            JNE: self.JNE_op,
            JMP: self.JMP_op
        }

    def LDI_op(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3

    def PRN_op(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 2

    def ADD_op(self, operand_a, operand_b):
        self.alu('ADD', operand_a, operand_b)
        self.pc += 3

    def MUL_op(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
        self.pc += 3

    def CMP_op(self, operand_a, operand_b):
        self.alu("CMP", operand_a, operand_b)
        self.pc += 3

    def HLT_op(self, operand_a, operand_b):
        sys.exit(0)

    def PUSH_op(self, operand_a, operand_b):
        self.push(self.reg[operand_a])
        self.pc += 2

    def POP_op(self, operand_a, operand_b):
        self.reg[operand_a] = self.pop()
        self.pc += 2

    def CALL_op(self, operand_a, operand_b):
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + 2
        reg_call = self.ram[self.pc + 1]
        self.pc = self.reg[reg_call]

    def RET_op(self, operand_a, operand_b):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def JMP_op(self, operand_a, operand_b):
        reg_jump = self.ram[self.pc + 1]
        self.pc = self.reg[reg_jump]

    def JEQ_op(self, operand_a, operand_b):
        if self.fl[E] == 1:
            reg_jump = self.ram[self.pc + 1]
            self.pc = self.reg[reg_jump]
        else:
            self.pc += 2

    def JNE_op(self, operand_a, operand_b):
        if self.fl[E] == 0:
            reg_jump = self.ram[self.pc + 1]
            self.pc = self.reg[reg_jump]
        else:
            self.pc += 2

    def push(self, value):
        self.reg[SP] -= 1
        self.ram_write(self.reg[SP], value)
        print(f"PUSH reg[SP]: {self.reg[SP]}")

    def pop(self):
        value = self.ram_read(self.reg[SP])
        self.reg[SP] += 1
        print(f"POP reg[SP]: {self.reg[SP]}")
        return value

    def ram_read(self, mar):
        mdr = self.ram[mar]
        return mdr

    def ram_write(self, mar, value):
        self.ram[mar] = value

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        with open(sys.argv[1]) as f:
            for line in f:
                comment_split = line.split("#")
                num = comment_split[0].strip()

                if num == "":
                    continue

                instruction = int(num, 2)
                self.ram[address] = instruction
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl[E] = 1
            else:
                self.fl[E] = 0
                
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            op = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if int(bin(op), 2) in self.dispatch_table:
                self.dispatch_table[op](operand_a, operand_b)
            else:
                print("Unrecognized operation.")
                sys.exit(1)
