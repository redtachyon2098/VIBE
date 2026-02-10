import modelwrapper
import sys
import time as t

cooldown = 300
manual = "manual.txt"
admin = "control.txt"
haltfile = "halt.txt"
reference = "README.md"
logfile = "log.txt"
criticlogfile = "criticlog.txt"
contextlength = 10000

modelwrapper.model = "qwen3:4b-thinking"
run = True
haltwhilecritiquing = False

args = sys.argv[1:]
if "-m" in args:
    manual = args[args.index("-m")+1]
if "-r" in args:
    reference = args[args.index("-r")+1]
if "-c" in args:
    cooldown = float(args[args.index("-c")+1])
if "-l" in args:
    contextlength = int(args[args.index("-l")+1])
if "-d" in args:
    modelwrapper.model = args[args.index("-d")+1]
if "-w" in args:
    modelwrapper.window = int(args[args.index("-w")+1])
if "-h" in args:
    run = False
    print(f"""Usage: python3 autocritic.py [options]
Options:
-m: Set manual file, default: {manual}
-r: Set reference file, default: {reference}
-c: Set cooldown time, default: {cooldown} seconds
-l: Set context length, default: {contextlength} characters
-d: Set critic model, default: {modelwrapper.model}
-w: Set context window of model, default: {modelwrapper.window}
-h: Display this help message
""")

if run:
    file = open(criticlogfile,"w")
    file.write('')
    file.close()

clock = t.time()
while run:
    t.sleep(max(clock+cooldown-t.time(),0))
    if haltwhilecritiquing:
        file = open(haltfile,"w")
        file.write("Preparing critique...")
        file.close()
    file = open(manual,"r")
    manualtext = file.read()
    file.close()
    file = open(logfile,"r")
    logtext = file.read()
    file.close()
    file = open(reference,"r")
    referencetext = file.read()
    file.close()

    sysprompt = f"""REFERENCE MATERIAL:
{referencetext}
CODE OF CONDUCT:
{manualtext}"""
    userprompt = logtext
    query = [
        {
            'role': 'system',
            'content': sysprompt
        },
        {
            'role': 'user',
            'content': userprompt[-contextlength:]
        }
    ]
    output = modelwrapper.promptmodel(query)
    file = open(admin,'w')
    file.write(output)
    file.close()
    file = open(criticlogfile,'a')
    file.write(output+"\n\n")
    file.close()
    clock = t.time()
