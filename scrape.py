import subprocess as s
import time as t
import pyautogui as p
import pyperclip as pp

p.MINIMUM_DURATION=0
p.MINIMUM_SLEEP=0
p.PAUSE=0

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
- The shell only reads your last line. So ***you can think aloud however you want***, just make sure your last line is valid. Dumb kitties don't get any treats!
- Hm, I hope this shell doesn't have any injection vulnerabilities...

You are at gate 0. There are other gates, stored in file contents. If you explore the filesystem, you will be able to find them.
Good luck, I'm rooting for you!!!
"""

logfile = "log.txt"

copybutton = [1555,1060]
screentop = 200
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
    step = -5
    while a=='' or a==None:
        p.move(0,step)
        y = p.position()[1]
        if y < screentop:
            p.moveTo(copybutton[0],screentop)
            step*=-1
        elif y > copybutton[1]:
            p.scroll(-100,x=copybutton[0],y=copybutton[1])
            step *= -1
        p.click()
        a = pp.paste()
    return a, a.rstrip('\n').split("\n")[-1]

def sendPrompt(prompt):
    if prompt == "":
        pp.copy("[no output]")
    else:
        pp.copy(prompt)
    p.click(x=promptbox[0],y=promptbox[1])
    p.click(x=promptbox[0],y=promptbox[1])
    t.sleep(0.1)
    p.hotkey("command","v")
    t.sleep(0.1)
    p.press('enter')

def episode():
    file = open(logfile,mode="a")
    line, GPT=getResponse()
    print(GPT)
    file.write(line+"\n")
    output = LoveYouToo(GPT)
    file.write(output+"\n")
    file.close()
    t.sleep(readcooldown)
    sendPrompt(output)

LoveYou()
if False:
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
