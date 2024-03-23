import re
import os
import sys

p = re.compile(r"\((.*?)\)")
p1 = re.compile(r"^R[0-9]+$")

symbolAddress = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576,
}



staticVariable = {}
staticVariableAddressStart = 16

def parsingSymbol(lines):
    pc = 0
    for line in lines:
        if "//" in line:
            continue
        if "(" in line:
            symbolAddress[p.findall(line)[0]] = pc
            continue
        pc += 1


def transcode(dict):
    compCode = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "D|A": "0010101",
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "D|M": "1010101",
    }

    destCode = {
        "null": "000",
        "M": "001",
        "D": "010",
        "DM": "011",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "AD": "110",
        "ADM": "111",
    }

    jumpCode = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }

    if dict["type"] == "address":
        address = dict["value"]
        if p1.match(address):
            address = address.replace("R", "")
        if address.isdigit():
            b = format(int(address), "b")
        else:
            if address in symbolAddress:
                b = format(symbolAddress[address], "b")
            else:
                if address not in staticVariable:
                    staticVariable[address] = staticVariableAddressStart + len(staticVariable)
                b = format(staticVariable[address], "b")
        return "0" + "".join(["0" for i in range(15 - len(b))]) + b
    if dict["type"] == "cal":
        return "111" + compCode[dict["cal"]] + destCode[dict["dest"]] + jumpCode["null"]
    if dict["type"] == "jmp":
        return (
            "111" + compCode[dict["comp"]] + destCode["null"] + jumpCode[dict["jump"]]
        )


def parser(line):
    if "@" in line:
        return {"type": "address", "value": line.replace("@", "")}
    if "=" in line:
        splited = line.split("=")
        return {"type": "cal", "dest": splited[0], "cal": splited[1]}
    if ";" in line:
        splited = line.split(";")
        return {"type": "jmp", "comp": splited[0], "jump": splited[1]}


def writer(filePath, list):
    with open(filePath, "w") as file:
        file.writelines(list)


def createHackFilePath(path):
    head, tail = os.path.split(path)
    return head + "/" + tail.split(".")[0] + ".hack"


def assembler(path):
    with open(path, "r") as file:
        lines = file.readlines()
        parsingSymbol(lines)
        asmCodes = []
        for line in lines:
            line = line.strip()
            if "(" in line:
                continue
            if "//" in line:
                continue
            if "\n" in line:
                line = line.replace("\n", "")
            if len(line) == 0:
                continue
            asmCodes.append(transcode(parser(line)) + "\n")
        writer(createHackFilePath(path), asmCodes)
    print("done!")


if len(sys.argv) != 2:
    print("Insufficient arguments")
    sys.exit()

file_path = sys.argv[1]
assembler(file_path)
