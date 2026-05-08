// Self-checking testbench for module SB (iverilog / vvp compatible).
`timescale 1ns / 1ps

module tb_sb;
    reg  [5:0] x;
    wire [5:0] y;
    integer i;
    reg [5:0] exp;

    SB dut (.x(x), .y(y));

    task expect_out;
        input [5:0] val;
        begin
            if (y !== val) begin
                $display("FAIL x=%0d got=%h want=%h", x, y, val);
                $fatal(1);
            end
        end
    endtask

    initial begin
        for (i = 0; i < 64; i = i + 1) begin
            x = i[5:0];
            #1;
            case (x)
                6'd0:  exp = 6'h00; 6'd1:  exp = 6'h36; 6'd2:  exp = 6'h30; 6'd3:  exp = 6'h0d;
                6'd4:  exp = 6'h0f; 6'd5:  exp = 6'h12; 6'd6:  exp = 6'h35; 6'd7:  exp = 6'h23;
                6'd8:  exp = 6'h19; 6'd9:  exp = 6'h3f; 6'd10: exp = 6'h2d; 6'd11: exp = 6'h34;
                6'd12: exp = 6'h03; 6'd13: exp = 6'h14; 6'd14: exp = 6'h29; 6'd15: exp = 6'h21;
                6'd16: exp = 6'h3b; 6'd17: exp = 6'h24; 6'd18: exp = 6'h02; 6'd19: exp = 6'h22;
                6'd20: exp = 6'h0a; 6'd21: exp = 6'h08; 6'd22: exp = 6'h39; 6'd23: exp = 6'h25;
                6'd24: exp = 6'h3c; 6'd25: exp = 6'h13; 6'd26: exp = 6'h2a; 6'd27: exp = 6'h0e;
                6'd28: exp = 6'h32; 6'd29: exp = 6'h1a; 6'd30: exp = 6'h3a; 6'd31: exp = 6'h18;
                6'd32: exp = 6'h27; 6'd33: exp = 6'h1b; 6'd34: exp = 6'h15; 6'd35: exp = 6'h11;
                6'd36: exp = 6'h10; 6'd37: exp = 6'h1d; 6'd38: exp = 6'h01; 6'd39: exp = 6'h3e;
                6'd40: exp = 6'h2f; 6'd41: exp = 6'h28; 6'd42: exp = 6'h33; 6'd43: exp = 6'h38;
                6'd44: exp = 6'h07; 6'd45: exp = 6'h2b; 6'd46: exp = 6'h2c; 6'd47: exp = 6'h26;
                6'd48: exp = 6'h1f; 6'd49: exp = 6'h0b; 6'd50: exp = 6'h04; 6'd51: exp = 6'h1c;
                6'd52: exp = 6'h3d; 6'd53: exp = 6'h2e; 6'd54: exp = 6'h05; 6'd55: exp = 6'h31;
                6'd56: exp = 6'h09; 6'd57: exp = 6'h06; 6'd58: exp = 6'h17; 6'd59: exp = 6'h20;
                6'd60: exp = 6'h1e; 6'd61: exp = 6'h0c; 6'd62: exp = 6'h37; 6'd63: exp = 6'h16;
                default: exp = 6'hxx;
            endcase
            expect_out(exp);
        end
        $display("TB OK: 64 vectors");
        $finish;
    end
endmodule
