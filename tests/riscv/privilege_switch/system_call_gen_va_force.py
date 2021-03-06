from riscv.EnvRISCV import EnvRISCV
from riscv.GenThreadRISCV import GenThreadRISCV
from base.Sequence import Sequence

## This test generates a virtual address in a different privilege level from that in which it is
# used. The genVA() method should respect the privilege level specified rather than the one in which
# the address was generated.
class MainSequence(Sequence):

    def generate(self, **kargs):
        self.systemCall({'PrivilegeLevel': 1})

        # Generate a target address for a U Mode instruction from S Mode
        target_addr = self.genVA(Size=8, Align=8, Type='D', PrivilegeLevel=0)

        self.systemCall({'PrivilegeLevel': 0})

        self.genInstruction('LD##RISCV', {'LSTarget': target_addr})
        self._assertNoPageFault(target_addr)

        # Generate a target address for an S Mode instruction from U Mode
        target_addr = self.genVA(Size=8, Align=8, Type='D', PrivilegeLevel=1)

        self.systemCall({'PrivilegeLevel': 1})

        self.genInstruction('LD##RISCV', {'LSTarget': target_addr})
        self._assertNoPageFault(target_addr)

    ## Fail if a load page fault occurred.
    #
    #  @param aTargetAddr The target address of the previous load instruction.
    def _assertNoPageFault(self, aTargetAddr):
        if self.queryExceptionRecordsCount(13) > 0:
            self.error('A LD instruction targeting 0x%x triggered an unexpected page fault' % aTargetAddr)


MainSequenceClass = MainSequence
GenThreadClass = GenThreadRISCV
EnvClass = EnvRISCV
