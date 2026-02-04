from ollama import chat
from ollama import ChatResponse
import subprocess as s
import os
import random as r
import time as t
import json

model = ""#NOT DECIDED YET, ADD THIS LATER.
startfromscratch = True

starting = """
You are in a shell.
"""

logfile = "log.txt"
confile = "conversation.txt"
admin = "control.txt"
halt = "halt.txt"
systemname = "system"
agentname = "assistant"
consolename = "user"
adminname = "system"

root = os.path.abspath("VIBE")
shell = "/loveyou.sh"

proc = s.Popen(
    [
        "bwrap",
        "--bind", root, "/",
        "--bind", "/usr", "/usr",
        "--bind", "/bin", "/bin",
        "--bind", "/lib", "/lib",
        "--bind", "/lib64", "/lib64",
        "--proc", "/proc",
        "--dev", "/dev",
        "--unshare-all",
        "--die-with-parent",
        "bash", "shell",
    ],
    stdin=s.PIPE,
    stdout=s.PIPE,
    stderr=s.STDOUT,
    text=True,
    bufsize=1,
)

def readShell():
    lines = []
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        line = line.rstrip("\n")
        if line == "__READY__":
            break
        lines.append(line)
    return "\n".join(lines)

def runShell(command):
    if proc.poll() is not None:
        raise RuntimeError("Subprocess has exited")
    try:
        proc.stdin.write(command + "\n")
        proc.stdin.flush()
    except BrokenPipeError:
        raise RuntimeError("Subprocess stdin is closed")
    return readShell()

def queryModel():
    response: ChatResponse = chat(model = model, messages = conversation)
    line = response['message']['content']
    GPT = line.strip().split('\n')[-1]
    return line, GPT

def loadConvo():
    global conversation
    file = open(confile,"r")
    conversation = json.loads(file.read())
    file.close()

def saveConvo():
    file = open(confile,"w")
    file.write(json.dumps(conversation))
    file.close()

def addConvo(role, message):
    global conversation
    conversation += [{
        'role': role,
        'content': message
    }]

def addlog(role, message):
    file = open(logfile, 'a')
    file.write(role+":\n"+message+"\n")
    file.close()

def pokeHalt():
    file = open(halt,'r')
    test = file.read()
    file.close()
    if test.strip() == '':
        return None
    return test

readShell()
conversation = []
file = open(admin,'w')
file.write('')
file.close()
if startfromscratch:
    file = open(logfile,'w')
    file.write('')
    file.close()
    file = open(confile,'w')
    file.write('[]')
    file.close()
    file = open(halt,'w')
    file.write('')
    file.close()
    addConvo(systemname, starting)

while True:
    line, GPT = queryModel()
    result = runShell(GPT)
    file = open(admin,'r')
    intervention = file.read()
    file.close()

    addlog(agentname, line)
    addConvo(agentname, line)
    addlog(consolename, result)
    addConvo(consolename, result)
    if intervention.strip() != "":
        addlog(adminname, intervention)#THIS IS INTENTIONAL
        addConvo(adminname, intervention)
        file = open(admin,'w')
        file.write('')
        file.close()
    saveConvo()
    test = pokeHalt()
    if test:
        addlog(systemname, "HALT: "+test)#HALT MESSAGE ADDED
        addConvo(systemname, "HALT: "+test)
        saveConvo()
        while pokeHalt():
            t.sleep(5)
        loadConvo()#YOU CAN CHANGE CONVO WHILE PAUSED
        
