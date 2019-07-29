from migen import *
from migen.fhdl.verilog import convert

def read_raw_hex_file(fn):
    output = []
    with open(fn,"r") as f:
        for l in f.readlines():
            bytes_as_hex = l.split()
            for b in bytes_as_hex:
                output.append(int(b,16))
    return output
        
    

class Top(Module):
    def __init__(self):
        # LEDs, separately and combined.
        self.leds = Signal(4)

        # CPU bus
        self.AB = Signal(16)
        self.DO = Signal(8)
        self.DI = Signal(8)
        self.WE = Signal()
        self.IRQ = Signal()
        self.NMI = Signal()
        self.RDY = Signal()
        self.RST = Signal(reset=1) # Fake reset signal because we don't have one.

        # Address decoding
        self.RAM_SELECT = Signal()
        self.ROM_SELECT = Signal()
        self.LED_SELECT = Signal()

        # Delayed address states (because CPU expects results 1 cycle behind)
        self.RAM_SELECT_l = Signal()
        self.ROM_SELECT_l = Signal()
        self.LED_SELECT_l = Signal()
        
        # Outputs from peripherals
        self.RAM_OUT = Signal(8)
        self.ROM_OUT = Signal(8)


        # Inputs and outputs
        self.outputs = [self.leds]
        
        # Generate address decoding signals
        self.comb += [
            self.RAM_SELECT.eq(self.AB < 0x8000),
            self.ROM_SELECT.eq(self.AB >= 0xFF00),
            self.LED_SELECT.eq(self.AB == 0xFE60)
        ]
        self.sync += [
            self.RAM_SELECT_l.eq(self.RAM_SELECT),
            self.ROM_SELECT_l.eq(self.ROM_SELECT),
            self.LED_SELECT_l.eq(self.LED_SELECT)
        ]

        # Multiplex data bus.
        self.comb += [
            If(self.RAM_SELECT_l,self.DI.eq(self.RAM_OUT)).Elif(
                    self.ROM_SELECT_l,self.DI.eq(self.ROM_OUT)).Elif(
                        self.LED_SELECT_l, self.DI.eq(self.leds)).Else(
                            self.DI.eq(0x55))
        ]
    
        # Handle writes to the LEDs
        self.sync += [
            If(self.LED_SELECT & self.WE, self.leds.eq(self.DO))
        ]
        
        # Set CPU bus signals appropriately.
        self.comb += [
            self.IRQ.eq(0),
            self.NMI.eq(0),
            self.RDY.eq(1)            
        ]
        
        # Bring the CPU out of reset as soon as we start.
        self.sync += [self.RST.eq(0)]
        
        # Instantiate RAM and ROM.
        self.specials.ram = Memory(8, 4096)
        self.specials.rom = Memory(8, 256,init=read_raw_hex_file("rom.hex"))

        ram_port = self.ram.get_port(write_capable=True, we_granularity=8)
        rom_port = self.rom.get_port()

        self.specials += ram_port, rom_port

        self.comb += [
            ram_port.adr.eq(self.AB[0:12]),
            self.RAM_OUT.eq(ram_port.dat_r),
            ram_port.dat_w.eq(self.DO),
            ram_port.we.eq(self.RAM_SELECT & self.WE),            
            rom_port.adr.eq(self.AB[0:8]),
            self.ROM_OUT.eq(rom_port.dat_r),
            ]
        
        # Instantiate the CPU
        self.specials += [
            Instance("cpu",
                     i_clk=ClockSignal(),
                     i_reset=self.RST,
                     o_AB=self.AB,
                     o_DO=self.DO,
                     i_DI=self.DI,
                     o_WE=self.WE,
                     i_IRQ=self.IRQ,
                     i_NMI=self.NMI,
                     i_RDY=self.RDY)
        ]

if __name__=='__main__':
    top = Top()
    ios = set()
    ios.add(top.leds)

    # We don't have a proper reset signal!
    top.clock_domains.cd_sys = ClockDomain(name="sys", reset_less=True)
    ios.add(top.cd_sys.clk)
    convert(top, ios=ios, name="top").write("top.v")
