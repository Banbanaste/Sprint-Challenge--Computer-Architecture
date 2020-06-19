"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    # register stores info according to instruction

    # what top do , where to do it, with what

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xf4
        self.pc = 0
        self.SP = 7
        self.FL = 0b00000000
        self.return_from_call_addr = None
        self.running = True

    def load(self, filename):
        """Load a program into memory."""

        with open(filename) as f:
            address = 0

            for line in f:
                line = line.split("#")

                try:
                    v = int(line[0], 2)
                except ValueError:
                    continue

                self.ram[address] = v
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        def add():
            self.reg[reg_a] += self.reg[reg_b]

        def sub():
            self.reg[reg_a] -= self.reg[reg_b]

        def mul():
            self.reg[reg_a] *= self.reg[reg_b]

        def div():
            self.reg[reg_a] /= self.reg[reg_b]

        def mod():
            if self.reg[reg_b] == 0:
                self.running = False
                raise Exception("Cannot divide by 0")
            self.reg[reg_a] %= self.reg[reg_b]

        def inc():
            self.reg[reg_a] += 1

        def dec():
            self.reg[reg_a] -= 1

        def compare():
            self.reg[reg_a] += self.reg[reg_b]

        def bit_and():
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]

        def bit_not():
            self.reg[reg_a] = ~ self.reg[reg_a]

        def bit_xor():
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]

        def shl():
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]

        def shr():
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]

        def bit_or():
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]

        ADD = 0b10100000
        SUB = 0b10100001
        MUL = 0b10100010
        DIV = 0b10100011
        MOD = 0b10100100
        INC = 0b01100101
        DEC = 0b01100110
        CMP = 0b10100111
        AND = 0b10101000
        NOT = 0b01101001
        XOR = 0b10101011
        SHL = 0b10101100
        SHR = 0b10101101
        OR = 0b10101010

        ops_dict = {
            ADD: add,
            SUB: sub,
            MUL: mul,
            DIV: div,
            INC: inc,
            DEC: dec,
            CMP: compare,
            AND: bit_and,
            NOT: bit_not,
            XOR: bit_xor,
            SHL: shl,
            SHR: shr,
            OR: bit_or
        }

        if op:
            ops_dict[op]()
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, adress):
        return self.ram[adress]

    def ram_write(self, adress, value):
        self.ram[adress] = value

    def run(self):
        """Run the CPU."""
        # PC is the place in ram
        # IR is the command grabed from ram
        # operand is another way to say parameter or argument
        # opcode is what you save in op_a or op_b

        # ALU operations
        ADD = 0b10100000
        SUB = 0b10100001
        MUL = 0b10100010
        DIV = 0b10100011
        MOD = 0b10100100
        INC = 0b01100101
        DEC = 0b01100110
        CMP = 0b10100111
        AND = 0b10101000
        NOT = 0b01101001
        XOR = 0b10101011
        SHL = 0b10101100
        SHR = 0b10101101
        BOR = 0b10101010

        # PC mutators
        CALL = 0b01010000
        RET = 0b00010001
        INT = 0b01010010
        IRET = 0b00010011
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110
        JGT = 0b01010111
        LT = 0b01011000
        JLE = 0b01011001
        JGE = 0b01011010

        # Other operations
        NOP = 0b00000000
        HLT = 0b00000001
        LDI = 0b10000010
        LD = 0b10000011
        ST = 0b10000100
        PUSH = 0b01000101
        POP = 0b01000110
        PRN = 0b01000111
        PRA = 0b01001000

        ir = self.ram_read(self.pc)

        while self.running:
            ir = self.ram_read(self.pc)
            op_a = self.ram_read(self.pc + 1)
            op_b = self.ram_read(self.pc + 2)

            if ir == LDI:
                self.reg[op_a] = op_b
                self.pc += 3

            elif ir == PRN:
                print(self.reg[op_a])
                self.pc += 2

            elif ir == MUL:
                self.alu(MUL, op_a, op_b)
                self.pc += 3

            elif ir == ADD:
                self.alu(ADD, op_a, op_b)
                self.pc += 3

            elif ir == PUSH:
                self.reg[self.SP] -= 1

                value = self.reg[op_a]

                top_of_stack = self.reg[self.SP]

                self.ram[top_of_stack] = value

                self.pc += 2

            elif ir == POP:
                self.reg[op_a] = self.ram[self.reg[self.SP]]

                self.reg[self.SP] += 1

                self.pc += 2

            elif ir == CALL:
                self.return_from_call_addr = self.pc + 2

                self.reg[self.SP] -= 1
                self.ram[self.reg[self.SP]] = self.return_from_call_addr

                reg_num = op_a
                subroutine_addr = self.reg[reg_num]

                self.pc = subroutine_addr

            elif ir == RET:
                self.reg[op_a] = self.ram[self.reg[self.SP]]

                self.reg[self.SP] += 1

                self.pc = self.return_from_call_addr

            elif ir == JMP:
                self.pc = self.reg[op_a]

            elif ir == CMP:

                if self.reg[op_a] < self.reg[op_b]:
                    self.FL = 0b00000100
                elif self.reg[op_a] is self.reg[op_b]:
                    self.FL = 0b00000001
                elif self.reg[op_a] > self.reg[op_b]:
                    self.FL = 0b00000010
                self.pc += 3

            elif ir == JEQ:
                if self.FL == 0b00000001:
                    self.pc = self.reg[op_a]
                else:
                    self.pc += 2

            elif ir == JNE:
                if self.FL != 0b00000001:
                    self.pc = self.reg[op_a]
                else:
                    self.pc += 2

            elif ir == AND or ir == OR or ir == XOR or ir == NOT or ir == NOT or ir == SHL or ir == MOD:
                self.alu(ir, op_a, op_b)
                self.pc += 3

            elif ir == HLT:
                self.running = False
                self.pc += 1
