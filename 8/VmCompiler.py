import os
import sys
import glob

dict = {"jumpCount" : 0}

def push(fileName, segmentName, i):
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


def pop(fileName, segmentName, i):
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

    if "goto" in operation:
        label = operation.split(" ")[1]
        asmCodes.append("@" + label)
        asmCodes.append("0;JMP")
        return [code + "\n" for code in asmCodes]

    asmCodes.append("@SP")
    asmCodes.append("AM=M-1")
    asmCodes.append("D=M")
    asmCodes.append("@R14")
    asmCodes.append("M=D")

    if "if-goto" in operation:
        label = operation.split(" ")[1]
        asmCodes.append("@" + label)
        asmCodes.append("D;JGT")
    else:
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

def label(name):
    asmCodes = []
    asmCodes.append("(" + name + ")")
    return [code + "\n" for code in asmCodes]

def function(name, varsCount):
    asmCodes = []
    asmCodes.append("(" + name + ")")
    for i in range(varsCount):
        asmCodes.append("@" + str(i))
        asmCodes.append("D=A")
        asmCodes.append("@LCL")
        asmCodes.append("A=M+D")
        asmCodes.append("M=0")
    asmCodes.append("@" + str(varsCount))
    asmCodes.append("D=A")
    asmCodes.append("@SP")
    asmCodes.append("M=M+D")

    return [code + "\n" for code in asmCodes]

def function_return():
    asmCodes = []
    asmCodes.append("@LCL")
    asmCodes.append("D=M")
    asmCodes.append("@R14")
    asmCodes.append("M=D")
    asmCodes.append("@5")
    asmCodes.append("A=D-A")
    asmCodes.append("D=M")
    asmCodes.append("@R15")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("AM=M-1")
    asmCodes.append("D=M")
    asmCodes.append("@ARG")
    asmCodes.append("A=M")
    asmCodes.append("M=D")
    asmCodes.append("D=A")
    asmCodes.append("@1")
    asmCodes.append("D=D+A")
    asmCodes.append("@SP")
    asmCodes.append("M=D")

    asmCodes.append("@R14")
    asmCodes.append("D=M")
    asmCodes.append("@1")
    asmCodes.append("A=D-A")
    asmCodes.append("D=M")
    asmCodes.append("@THAT")
    asmCodes.append("M=D")

    asmCodes.append("@R14")
    asmCodes.append("D=M")
    asmCodes.append("@2")
    asmCodes.append("A=D-A")
    asmCodes.append("D=M")
    asmCodes.append("@THIS")
    asmCodes.append("M=D")

    asmCodes.append("@R14")
    asmCodes.append("D=M")
    asmCodes.append("@3")
    asmCodes.append("A=D-A")
    asmCodes.append("D=M")
    asmCodes.append("@ARG")
    asmCodes.append("M=D")

    asmCodes.append("@R14")
    asmCodes.append("D=M")
    asmCodes.append("@4")
    asmCodes.append("A=D-A")
    asmCodes.append("D=M")
    asmCodes.append("@LCL")
    asmCodes.append("M=D")

    asmCodes.append("@R15")
    asmCodes.append("A=M")
    asmCodes.append("0;JMP")
    return [code + "\n" for code in asmCodes]

def call(name, argsCount):
    asmCodes = []
    asmCodes.append("@" + name + "_return")
    asmCodes.append("D=A")
    asmCodes.append("@SP")
    asmCodes.append("A=M")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("M=M+1")

    asmCodes.append("@LCL")
    asmCodes.append("D=M")
    asmCodes.append("@SP")
    asmCodes.append("A=M")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("M=M+1")

    asmCodes.append("@ARG")
    asmCodes.append("D=M")
    asmCodes.append("@SP")
    asmCodes.append("A=M")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("M=M+1")

    asmCodes.append("@THIS")
    asmCodes.append("D=M")
    asmCodes.append("@SP")
    asmCodes.append("A=M")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("M=M+1")

    asmCodes.append("@THAT")
    asmCodes.append("D=M")
    asmCodes.append("@SP")
    asmCodes.append("A=M")
    asmCodes.append("M=D")
    asmCodes.append("@SP")
    asmCodes.append("M=M+1")

    asmCodes.append("@SP")
    asmCodes.append("D=M")
    asmCodes.append("@5")
    asmCodes.append("D=D-A")
    asmCodes.append("@" + str(argsCount))
    asmCodes.append("D=D-A")
    asmCodes.append("@ARG")
    asmCodes.append("M=D")

    asmCodes.append("@SP")
    asmCodes.append("D=M")
    asmCodes.append("@LCL")
    asmCodes.append("M=D")

    asmCodes.append("@" + name)
    asmCodes.append("0;JMP")
    asmCodes.append("(" + name + "_return" + ")")
    return [code + "\n" for code in asmCodes]


def createFilePath(path):
    head, tail = os.path.split(path)
    return head + "/" + tail + "/" + tail + ".asm"

def init():
    asmCodes = []
    asmCodes.append("@256")
    asmCodes.append("D=A")
    asmCodes.append("@0")
    asmCodes.append("M=D")

    asmCodes.append("@0")
    asmCodes.append("D=A")
    
    for address in ['@LCL', '@ARG', '@THIS', '@THAT']:
        asmCodes.append(address)
        asmCodes.append("M=D")
    return [code + "\n" for code in asmCodes]

def callSysInit():
    return call("Sys.init", 0)

def compile(path):
    asmFile = open(createFilePath(path), "w")
    filePaths = glob.glob(path + "/*.vm")

    asmFile.writelines(init())
    asmFile.writelines(callSysInit())
    for filePath in filePaths:
        fileName = os.path.basename(filePath).split(".")[0]
        vmFile = open(filePath, "r")
        lines = vmFile.readlines()
        vmFile.close()
    
        for line in lines:
            line = line.strip()
            line = line.replace("\n", "")
            if "//" in line or len(line) == 0:
                splited = line.split("//")
                if len(splited[0]) == 0:
                    continue
                line = splited[0]

            splited = line.split(" ")
            if "pop" in line:
                asmFile.writelines(pop(fileName, splited[1], splited[2]))
                continue
            if "push" in line:
                asmFile.writelines(push(fileName, splited[1], splited[2]))
                continue
            if "label" in line:
                asmFile.writelines(label(splited[1]))
                continue
            if "function" in line:
                asmFile.writelines(function(splited[1], int(splited[2])))
                continue
            if "call" in line:
                asmFile.writelines(call(splited[1], int(splited[2])))
                continue
            if "return" in line:
                asmFile.writelines(function_return())
                continue
            asmFile.writelines(cal(line))

    asmFile.close()


if len(sys.argv) != 2:
    print("Insufficient arguments")
    sys.exit()

folder_path = sys.argv[1]
compile(folder_path)