from formats import *

import logging, struct, sys

logging.basicConfig(level=logging.DEBUG)

# Load in the executable with read_executable (pass filename)
executable = read_executable(sys.argv[1])

# Invoke the analyzer to find functions
executable.analyze()

logging.debug('Functions found: {}'.format(executable.functions))

# TODO: API so you can do something like this:
# executable.function_named('main').instructions[0] = '\xcc'

"""
instrumentation = '\xcc\xc3' # INT3, RET
instrumentation_vaddr = executable.inject(instrumentation)
logging.debug('Injected instrumentation asm at {}'.format(hex(instrumentation_vaddr)))

for function in [executable.function_named('main')]: #executable.iter_functions():
    for bb in function.iter_bbs():
        replaced_instruction = None
        for instruction in bb.instructions:
            if instruction.size >= 5 \
                    and not executable.analyzer.ins_redirects_flow(instruction) \
                    and 'ip' not in instruction.op_str and 'sp' not in instruction.op_str: # TODO: Proper eip/rip checking
                logging.debug('In {} - Found candidate replacement instruction at {}: {} {}'.format(bb,
                                                                                                   hex(instruction.address),
                                                                                                   instruction.mnemonic,
                                                                                                   instruction.op_str))
                replaced_instruction = instruction
                break

        if not replaced_instruction:
            logging.warning('Could not find instruction to replace in {}'.format(bb))
        else:
            # Given a candidate instruction, replace it with a call to a new "function" that contains just that one
            # instruction and a jmp to the instrumentation code.

            # Compute relative address that the jmp after the instruction should go to
            instrumentation_jmp_offset = instrumentation_vaddr - (executable.next_injection_vaddr + instruction.size + 5)
            ins_and_jump = instruction.bytes + '\xe9' + struct.pack(executable.pack_endianness + 'i',
                                                                    instrumentation_jmp_offset)

            ins_jump_vaddr = executable.inject(ins_and_jump)

            logging.debug('Added instruction ({} {}) and jmp to instrumentation at {}'.format(instruction.mnemonic,
                                                                                              instruction.op_str,
                                                                                              hex(ins_jump_vaddr)))



            # Finally, replace the instruction we lifed with a call to the ins and jump we just put together
            call_ins = '\xe8' + struct.pack(executable.pack_endianness + 'i', ins_jump_vaddr - (instruction.address + instruction.size))

            executable.replace_instruction(instruction, call_ins)

            logging.debug('Replaced instruction at {} with call to {}'.format(hex(instruction.address), hex(ins_jump_vaddr)))

f = open('a.out','wb')
f.write(executable.get_binary())
f.close()"""

cfg = executable.analyzer.cfg()