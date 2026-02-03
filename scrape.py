import subprocess as s
import time as t
import pyautogui as p
import pyperclip as pp

starting = """
This is a custom shell on a python venv. You are an adorable LLM.
No commentary, no textboxes, just commands. If not, the error message will
spank you for being a naughty LLM.
You are at gate 0. There are other gates. If you explore the filesystem, you will be able to find them.
"""

logfile = "log.txt"

copybutton = [1560,1060]
promptbox = [1636,1200]
startbox = [1593,644]

writecooldown = 10
readcooldown = 4


proc = s.Popen(
    ["bash", "loveyou.sh"],
    cwd="VIBE",
    stdin=s.PIPE,
    stdout=s.PIPE,
    stderr=s.STDOUT,
    text=True,
    bufsize=1,
    universal_newlines=True
)

def LoveYou():
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

def LoveYouToo(command):
    proc.stdin.write(command+"\n")
    love = LoveYou()
    proc.stdin.flush()
    return love

def getResponse():
    pp.copy('')
    p.scroll(-100,x=copybutton[0],y=copybutton[1])
    a = pp.paste()
    while a=='':
        p.move(0,-10)
        p.click()
        a = pp.paste()
    return a.rstrip('\n').split("\n")[-1]

def sendPrompt(prompt):
    if prompt == "":
        pp.copy("[no output]")
    else:
        pp.copy(prompt)
    p.click(x=promptbox[0],y=promptbox[1])
    p.click(x=promptbox[0],y=promptbox[1])
    p.hotkey("command","v")
    p.press('enter')

def episode():
    file = open(logfile,mode="a")
    GPT=getResponse()
    print(GPT)
    file.write(GPT+"\n")
    output = LoveYouToo(GPT)
    file.write(output+"\n")
    file.close()
    t.sleep(readcooldown)
    sendPrompt(output)

LoveYou()
if True:
    file = open(logfile,mode="w")
    file.write('')
    file.close()
    backup = [promptbox[0],promptbox[1]]
    promptbox = startbox
    sendPrompt(starting)
    promptbox = backup
    t.sleep(writecooldown)
while True:
    episode()
    t.sleep(writecooldown)
