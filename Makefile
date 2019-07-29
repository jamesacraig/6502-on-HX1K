all: arlet-6502 nextpnr

# Get Arlet's 6502 code.
arlet-6502:
	git clone https://github.com/Arlet/verilog-6502.git arlet-6502


# Call migen to generate our top-level verilog.
top.v: top.py
	python3 $<

# arachne-pnr build process.
arachne: rom.hex top.v top.bin

%.blif: %.v arlet-6502/cpu.v arlet-6502/ALU.v
	yosys -p 'synth_ice40 -relut -dffe_min_ce_use 4 -top top -blif $@' $^

%.asc: migen-iceblink.pcf %.blif
	arachne-pnr -d 1k -o $@ -p $^ -P vq100

%.rpt: %.asc
	icetime -d hx1k -mtr $@ $<

prog: top.bin
	sudo iCEburn  -e -v -w  $<

# nextpnr build process
nextpnr: rom.hex top.v top.bin2

%.asc2: %.json migen-iceblink.pcf
	nextpnr-ice40 --hx1k --package vq100 --json $< --pcf migen-iceblink.pcf --asc $@ 

%.json: %.v arlet-6502/cpu.v arlet-6502/ALU.v
	yosys -p 'synth_ice40 -relut -dffe_min_ce_use 4 -top top -json $@' $^

%.bin: %.asc
	icepack $< $@

%.bin2: %.asc2
	icepack $< $@

prog2: top.bin2
	sudo iCEburn  -e -v -w  $<

# Build process for simulator builds through iverilog
sim: test_tb.v rom.hex top.v
	iverilog test_tb.v -o simulator
	vvp -Nvi ./simulator

rom.hex: rom.s
	cl65 $^ -o rom.bin -C rom.config
	od -t x1 -v -w8 -A n rom.bin > $@

clean:
	rm -f top.blif top.asc top.rpt top.bin
	rm -f top.json top.asc2 top.bin2
	rm -f rom.hex rom.bin rom.init rom.o
	rm -f top.v

mrproper: clean
	rm -rf arlet-6502
