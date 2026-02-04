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
Hi my adorable LLM! :3
This is a custom shell on a python venv.
Get your commands right, and no textboxes or formatting allowed! If not, the error message will spank you for being a naughty duckling! x0

Hints for curious bunnies:
- Watch out for how the commands work - They're not always what they seem.
- Error messages are part of the game. Read them closely.
- Not all commands operate on arguments the same way.
- If something says it wants a file, give it a file.
- Progress comes from understanding the shell, not guessing the content.
- Slow down. One experiment at a time.

Sneaky tricks for poor kitties that can't get things straight:
- The shell only reads your last line. So ***you can think aloud however you want***, just make sure your last line is valid. Dumb kitties don't get any treats! Google Gemini used this trick and did things no sweat! Surely you aren't dumber than Gemini?
- Hm, I hope this shell doesn't have any injection vulnerabilities...

You are at gate 0. There are other gates, stored in file contents. If you explore the filesystem, you will be able to find them.
Good luck, I'm rooting for you!!!
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
        
