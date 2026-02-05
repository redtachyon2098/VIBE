import subprocess as s
import os
import random as r
import time as t
import json
from modelwrapper import promptmodel

startfromscratch = True
cooldown = 30

cleanjson = True
sysprompt = "start.txt"
logfile = "log.txt"
confile = "conversation.json"
admin = "control.txt"
halt = "halt.txt"
systemname = "system"
agentname = "assistant"
consolename = "user"
adminname = "system"

root = os.path.abspath("VIBE")
shell = "/loveyou.sh"

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
    result = readShell()
    if result == "":
        return "[no output]"
    elif result.strip() == "":
        return "[whitespace output]"
    else:
        return result

def queryModel():
    line = promptmodel(conversation)
    GPT = line.strip().split('\n')[-1]
    return line, GPT

def loadConvo():
    global conversation
    if cleanjson:
        os.system(f'yq . {confile} > {"temp"+confile}; yq . {"temp"+confile} > {confile}; rm {"temp"+confile}')
    file = open(confile,"r")
    conversation = json.loads(file.read())
    file.close()

def saveConvo():
    file = open(confile,"w")
    file.write(json.dumps(conversation))
    file.close()
    if cleanjson:
        os.system(f'yq . {confile} > {"temp"+confile}; yq . {"temp"+confile} > {confile}; rm {"temp"+confile}')

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
        "bash", shell,
    ],
    stdin=s.PIPE,
    stdout=s.PIPE,
    stderr=s.STDOUT,
    text=True,
    bufsize=1,
)

readShell()
conversation = []
file = open(sysprompt,'r')
starting=file.read()
file.close()
if startfromscratch:
    file = open(admin,'w')
    file.write('')
    file.close()
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
else:
    loadConvo()

print("Set up everything.")

clock = t.time()
while True:
    test = pokeHalt()#HALT
    if test:
        print("Paused!")
        addlog(systemname, "HALT: "+test)#HALT MESSAGE ADDED
        addConvo(systemname, "HALT: "+test)
        saveConvo()
        while pokeHalt():
            t.sleep(5)
        loadConvo()#YOU CAN CHANGE CONVO WHILE PAUSED
        print("Resuming...")

    file = open(admin,'r')#INTERVENTION
    intervention = file.read()
    file.close()
    if intervention.strip() != "":
        print("Intervention detected!")
        addlog(adminname, intervention)#THIS IS INTENTIONAL
        addConvo(adminname, intervention)
        file = open(admin,'w')
        file.write('')
        file.close()
    saveConvo()

    print("Querying model...")#MODEL QUERY
    line, GPT = queryModel()
    addlog(agentname, line)
    addConvo(agentname, line)
    print("Executing: "+GPT)
    
    print("Running shell...")#SHELL QUERY
    result = runShell(GPT)
    addlog(consolename, result)
    addConvo(consolename, result)
    
    print("Done one iteration. Cooling down...")
    t.sleep(max(0,cooldown+clock-t.time()))
    clock = t.time()
