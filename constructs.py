from capstone import *

class Function(object):
    NORMAL_FUNC = 0
    DYNAMIC_FUNC = 1

    def __init__(self, address, size, name, type=NORMAL_FUNC):
        self.address = address
        self.size = size
        self.name = name
        self.type = type

        # BELOW: Helpers used to explore the binary.
        # NOTE: These should *not* be directly modified at this time.
        # Instead, executable.replace_instruction should be used.
        self.instructions = [] # Sequential list of instructions
        self.bbs = [] # Sequential list of basic blocks. BB instructions are auto-populated from our instructions
    
    def __repr__(self):
        return '<Function \'{}\' at {}>'.format(self.name, hex(self.address))
    
    def contains_address(self, address):
        return self.address <= address < self.address + self.size

    def iter_bbs(self):
        for bb in self.bbs:
            yield bb

    def print_disassembly(self):
        for i in self.instructions:
            print hex(i.address) + ' ' + str(i)


class BasicBlock(object):
    def __init__(self, parent_func, address, size):
        self.parent = parent_func
        self.address = address
        self.size = size
        self.offset = self.parent.address - self.address
        self.instructions = [i for i in self.parent.instructions if self.address <= i.address < self.address + self.size]
    
    def __repr__(self):
        return '<Basic block at {}>'.format(hex(self.address))
    
    def print_disassembly(self):
        for i in self.instructions:
            print hex(i.address) + ' ' + str(i)

class Instruction(object):
    def __init__(self, capstone_inst, executable):
        self.capstone_inst = capstone_inst
        self.address = int(self.capstone_inst.address)
        self.op_str = self.capstone_inst.op_str
        self.mnemonic = self.capstone_inst.mnemonic
        self.size = int(self.capstone_inst.size)
        self.groups = self.capstone_inst.groups
        self.bytes = self.capstone_inst.bytes

        self._executable = executable

    def __repr__(self):
        return '<Instruction at {}>'.format(hex(self.address))

    def __str__(self):
        return self.mnemonic + ' ' + self.nice_op_str()

    def nice_op_str(self):
        '''
        Returns the operand string "nicely formatted." I.e. replaces addresses with function names (and function
        relative offsets) if appropriate.
        :return: The nicely formatted operand string
        '''
        s = self.op_str.split(', ')

        # If this is an immediate call or jump, try to put a name to where we're calling/jumping to
        if CS_GRP_CALL in self.capstone_inst.groups or CS_GRP_JUMP in self.capstone_inst.groups:
            # jump/call destination will always be the last operand (even with conditional ARM branch instructions)
            operand = self.capstone_inst.operands[-1]
            if operand.imm in self._executable.functions:
                s[-1] = self._executable.functions[operand.imm].name
            elif self._executable.vaddr_is_executable(operand.imm):
                func_addrs = self._executable.functions.keys()
                func_addrs.sort(reverse=True)
                for func_addr in func_addrs:
                    if func_addr < operand.imm:
                        break
                diff = operand.imm - func_addr
                s[-1] = self._executable.functions[func_addr].name+'+'+hex(diff)


        return ', '.join(s)