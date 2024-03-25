import os
import sys

fileName = ""
dict = {"jumpCount" : 0}


def push(segmentName, i):
    asmCodes = []
    if segmentName == "constant":
        asmCodes.append("@" + i)
        asmCodes.append("D=A")
    elif segmentName == "static":
        asmCodes.append("@" + fileName + "." + i)
        asmCodes.append("D=M")
    elif segmentName == "pointer":
        if i == "0":
            asmCodes.append("@THIS")
        else:
            asmCodes.append("@THAT")
        asmCodes.append("D=M")

    elif segmentName == "temp":
        asmCodes.append("@" + str(5 + int(i)))
        asmCodes.append("D=M")

    else:
        if segmentName == "local":
            asmCodes.append("@LCL")
        if segmentName == "argument":
            asmCodes.append("@ARG")
        if segmentName == "this":
            asmCodes.append("@THIS")
        if segmentName == "that":
            asmCodes.append("@THAT")
        asmCodes.append("D=M")
        asmCodes.append("@" + i)
        asmCodes.append("D=D+A")
        asmCodes.append("A=D")
        asmCodes.append("D=M")

    asmCodes.append("@SP")
    asmCodes.append("A=M")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("M=M+1")

    return [code + "\n" for code in asmCodes]


def pop(segmentName, i):
    asmCodes = []
    if segmentName == "temp":
        asmCodes.append("@" + str(5 + int(i)))
        asmCodes.append("D=A")
    elif segmentName == "static":
        asmCodes.append("@" + fileName + "." + i)
        asmCodes.append("D=A")
    elif segmentName == "pointer":
        if i == "0":
            asmCodes.append("@THIS")
            asmCodes.append("D=A")
        else:
            asmCodes.append("@THAT")
            asmCodes.append("D=A")
    else:
        if segmentName == "local":
            asmCodes.append("@LCL")
        if segmentName == "argument":
            asmCodes.append("@ARG")
        if segmentName == "this":
            asmCodes.append("@THIS")
        if segmentName == "that":
            asmCodes.append("@THAT")

        asmCodes.append("D=M")
        asmCodes.append("@" + i)
        asmCodes.append("D=D+A")

    asmCodes.append("@R13")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("AM=M-1")
    asmCodes.append("D=M")
    asmCodes.append("@R13")
    asmCodes.append("A=M")
    asmCodes.append("M=D")

    return [code + "\n" for code in asmCodes]


def cal(operation):
    asmCodes = []

    asmCodes.append("@SP")
    asmCodes.append("AM=M-1")
    asmCodes.append("D=M")
    asmCodes.append("@R14")
    asmCodes.append("M=D")

    if operation == "neg":
        asmCodes.append("D=-M")
    elif operation == "not":
        asmCodes.append("D=!M")
    else:
        asmCodes.append("@SP")
        asmCodes.append("AM=M-1")
        asmCodes.append("D=M")
        asmCodes.append("@R15")
        asmCodes.append("M=D")

        if operation == "add":
            asmCodes.append("@R14")
            asmCodes.append("D=M")
            asmCodes.append("@R15")
            asmCodes.append("D=D+M")

        if operation == "sub":
            asmCodes.append("@R15")
            asmCodes.append("D=M")
            asmCodes.append("@R14")
            asmCodes.append("D=D-M")

        if operation == "and":
            asmCodes.append("@R14")
            asmCodes.append("D=M")
            asmCodes.append("@R15")
            asmCodes.append("D=D&M")
        
        if operation == "or":
            asmCodes.append("@R14")
            asmCodes.append("D=M")
            asmCodes.append("@R15")
            asmCodes.append("D=D|M")
        if operation == "eq" or operation == "lt" or operation == "gt":
            asmCodes.append("@R14")
            asmCodes.append("D=M")
            asmCodes.append("@R15")
            asmCodes.append("D=M-D")
            asmCodes.append("@" + "JMP" + str(dict["jumpCount"]))

            if operation == "eq":
                asmCodes.append("D;JEQ")

            if operation == "lt":
                asmCodes.append("D;JLT")

            if operation == "gt":
                asmCodes.append("D;JGT")
            
            asmCodes.append("D=0")
            asmCodes.append("@" + "JMP" + str(dict["jumpCount"] + 1))
            asmCodes.append("0;JMP")
            asmCodes.append("(" + "JMP" + str(dict["jumpCount"]) + ")")
            asmCodes.append("D=-1")
            asmCodes.append("(" + "JMP" + str(dict["jumpCount"] + 1) + ")")
            dict["jumpCount"] += 2
            



    asmCodes.append("@SP")
    asmCodes.append("A=M")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("M=M+1")

    return [code + "\n" for code in asmCodes]

def endLoop():
    asmCodes = []
    asmCodes.append("(END)")
    asmCodes.append("@END")
    asmCodes.append("0;JMP")
    return [code + "\n" for code in asmCodes]



def createFilePath(path):
    head, tail = os.path.split(path)
    fileName = tail.split(".")[0]
    return head + "/" + fileName + ".asm"


def compile(path):
    vmFile = open(path, "r")
    lines = vmFile.readlines()
    vmFile.close()

    asmFile = open(createFilePath(path), "w")
    for line in lines:
        line = line.replace("\n", "")
        if "//" in line or len(line) == 0:
            continue

        splited = line.split(" ")
        if "pop" in line:
            asmFile.writelines(pop(splited[1], splited[2]))
            continue
        if "push" in line:
            asmFile.writelines(push(splited[1], splited[2]))
            continue
        asmFile.writelines(cal(line))
    asmFile.writelines(endLoop())
    asmFile.close()


if len(sys.argv) != 2:
    print("Insufficient arguments")
    sys.exit()

file_path = sys.argv[1]
compile(file_path)
