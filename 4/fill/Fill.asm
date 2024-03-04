// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//// Replace this comment with your code.
(LOOP)
@KBD
D=M
@KEY_DOWN
D;JGT
@KEY_UP
0;JMP


(KEY_DOWN)
@R4
M=1
@R2
D=M+1
@PRINT_SCREEN
D;JEQ
@R0
M=0
@R2
M=-1
@PRINT_SCREEN
0;JMP

(KEY_UP)
@R2
D=M
@PRINT_SCREEN
D;JEQ
@R0
M=0
@R2
M=0
@PRINT_SCREEN
0;JMP

(PRINT_SCREEN)
@SCREEN
D=A
@R0
D=D+M
@R1
M=D
@R2
D=M
@R1
A=M
M=D
@R0
M=M+1
@LOOP
0;JMP
