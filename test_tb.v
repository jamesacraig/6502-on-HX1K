`timescale 1ns / 1ns
`include "top.v"
`include "../arlet-6502/cpu.v"
`include "../arlet-6502/alu.v"


module tb(LED2, LED3, LED4, LED5);
   output LED2, LED3, LED4, LED5;
   
   reg clk;

   initial
     begin
	$dumpfile("test.vcd");
	$dumpvars(0,top);
	clk = 0;
	
	#1000 $finish;
     end
   
   
   always
     #2 clk = !clk;
   
   top top(.leds({LED5, LED4, LED3, LED2}),
	   .sys_clk(clk));
   
   endmodule
