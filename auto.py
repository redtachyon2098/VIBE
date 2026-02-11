import subprocess as s
import os
import random as r
import time as t
import json
from modelwrapper import promptmodel
import modelwrapper
import sys

startfromscratch = True
cooldown = 0

cleanjson = True
sysprompt = "start.txt"
logfile = "log.txt"
confile = "conversation.json"
admin = "control.txt"
halt = "halt.txt"
systemname = "system"
agentname = "assistant"
consolename = "user"
adminname = "user"

root = os.path.abspath("VIBE")
shell = "/loveyou.sh"

run = True
arguments = sys.argv[1:]
if "-h" in arguments or "--help" in arguments:
    run = False
    print(f"""Usage: python3 auto.py [options]
Supported Options:
-h or --help: Display this help message
-m or --model: Specify Ollama model name, default: {modelwrapper.model}
-r or --resume: Resume instead of starting from scratch
-p or --prompt: Specify initial system prompt file, default: {sysprompt}
-c or --cooldown: Specify minimum cooldown time per generation, default: {cooldown}
-w or --window: Specify context window
""")
if "-m" in arguments or "--model" in arguments:
    modelwrapper.model = arguments[[x for x,y in enumerate(arguments) if y in ["-m", "--model"]][0]+1]
    print(f"Model set: {modelwrapper.model}")
if "-r" in arguments or "--resume" in arguments:
    startfromscratch = False
    print("Resuming conversation instead of restarting")
if "-p" in arguments or "--prompt" in arguments:
    sysprompt = arguments[[x for x,y in enumerate(arguments) if y in ["-p", "--prompt"]][0]+1]
    print(f"System prompt path changed to: {sysprompt}")
if "-c" in arguments or "--cooldown" in arguments:
    cooldown = float(arguments[[x for x,y in enumerate(arguments) if y in ["-c", "--cooldown"]][0]+1])
    print(f"Cooldown time specified: {cooldown} seconds")
if "-w" in arguments or "--window" in arguments:
    modelwrapper.window = int(arguments[[x for x,y in enumerate(arguments) if y in ["-w", "--window"]][0]+1])
    print(f"Context window specified: {modelwrapper.window} tokens")

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

if __name__ == "__main__" and run:
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
            "--unshare-user",
            "--unshare-pid",
            "--unshare-ipc",
            "--unshare-uts",
            "--share-net", #THE LLM HAS NETWORK ACCESS
            "--ro-bind", "/etc/ssl", "/etc/ssl",
            "--ro-bind", "/etc/resolv.conf", "/etc/resolv.conf",
            "--die-with-parent",
            "bash", shell,
        ],
        stdin=s.PIPE,
        stdout=s.PIPE,
        stderr=s.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace"
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
            addlog(adminname, intervention)
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
