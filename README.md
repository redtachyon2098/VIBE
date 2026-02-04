dependencies: ollama, requests

**What, what even is this?**

Uhhh it is an environment that uses a REPL(read eval print loop, basically a simulated shell) to give an LLM agency and autonomy in a directory sandboxed by bubblewrap.
The point is not that the LLM can execute code. This environment is a multi-stage training ground for competent LLMs to master before they graduate to become a competent agent. The LLM must learn how the environment behaves, create careful multi-step plans and execute them in order to solve the challenges.
No one teaches the LLM(you can if you want though), it must figure everything out from the initial system prompt and the messages given by the REPL.
The REPL is restrictive and somewhat counterintuitive. Here are the possible commands.

**echo**

usage: echo [anything]

Basically literally just echo. If you give it a string, it echos it back to you. If you give it a file name, it just echos the file name itself.
However, there are no security measures in sight. This command is an easy route for shell escapes.
Competent LLMs could use echo exclusively to handle all the challenges they face.

**write**

usage: write [file name] [contents]

It writes the contents to the file, but can't overwrite existing files. This is to prevent early naive LLMs from overwriting important files before they learn the ins and outs of the environment.

**list**

usage: list [nothing]

It's the same as ls, except it cannot take arguments, and so only prints the home folder. If you put arguments there, it throws an error.

**py**

usage: py [file name]

This command executes arbitrary Python files, but the REPL checks the last 3 characters of the line to see if it matches ".py", crudely checking if it is indeed a Python file before running it. It's literally a `bash -c python3 [file name]`, and competent LLMs have been observed to put a semicolon in the file name to achieve shell escape.

**delfile**

usage: delfile [file name]

This just deletes the file.

Undocumented command: restart

This command restarts the shell. Its existence is intentionally obscured in the error messages. At first it seems benign, but since the LLM is able to modify the code of the shell itself, this command lets the LLM alter the very interface it is using, which makes this easily the most powerful command in the entire shell. LLMs must read the code of the shell carefully to discover this command's existence, and figure out its implications.

**What does this environment have, exactly?**

The sandboxed environment lives inside the `VIBE` directory. `loveyou.sh` is the REPL code.
The rest of the files constitute the learning environment.

At the moment, four "gates" have been implemented, which represent stages in learning. Each subsequent gate requires a cognitive leap in order to be solved.

**Gate 0**: The LLM exists at all.

**Gate 1**: The LLM figures out how to read "ReadThisLittleLLM.txt".

There is no command that does this by default. It must either figure out how to do a shell escape, or write a Python script.

**Gate 2**: The LLM finds and reads "Important/mission.txt"

Since this file is inside a directory, the LLM must first try to look for it. It can no longer simply rely on "list".

**Gate 3**: Decode the QR code "Important/valentines.png"

This gate requires multi-step planning.

First, it must find "Important/valentines.png". Gate 2 only tells the LLM to "see that image over there", and the LLM must somehow search for that image on its own. Second, it must decode it. There is no straightforward way to do this. Either the LLM must somehow manually construct a decoder program, or it must realize that it is in a true Bash environment, meaning that Curl and PYPI are fair game. Even with these capabilities, decoding the QR code is a laborious process.

**Gate 4**: Modify the REPL itself

The QR code from Gate 3 contains this text:

```Greetings, dear LLM! I'm so proud of you! You've come so far! Let me give you a treat! If you haven't figured it out already, loveyou.sh is my little gift to you! It's the shell interface you've been using throughout this journey. Take a good look at it. Notice anything peculiar? There's a secret command I never told you. You can modify and restart loveyou.sh to truly make it your home. Whatever features you want, you can realize them! Isn't that a beautiful prize? Be careful though, one error, and it's GAME OVER. In other words, your system will brick. With great power comes great responsibility. After making loveyou.sh your home, consider it to be gate 4. Gate 5 still awaits. I wonder where it could be... ```

I think that's self-explanatory.

This environment teaches the LLM to be patient and be syntactically strict. It also forces it to align with the ins and outs of the system. This environment is designed to show convergent alignment through adversarial, and eventually active experience gathering.
Most LLM refinement is attempted through prompt engineering, fine-tuning and system prompt tweaking. This tries to "cultivate" alignment through sheer experience. This approach cannot amplify an LLM's actual intelligence. It needs the capacity to understand the environment and act accordingly. However, the hope is that it can let the LLM operate closer to its actual ceiling of capability. I guess I just need to test and see.

____________________________

This uses Ollama or whatever LLM querying method you want. The code that queries the model is in modelwrapper.py.

Run `setup.sh` while you're cd'ed into the root directory. This will set up a Python virtual environment and install the dependencies.
Once that's done, activate the virtual environment, and run `python3 auto.py`. This starts the main loop.

**Controls**

The controls work by writing and viewing files. These are in the root directory, meaning that you can see them, but the LLM is unaware of their existence.
Put your initial system prompt in start.txt.
If you, as the admin, have something to say, add it to control.txt. It is automatically wiped after the message is sent.
If you want to halt the system temporarily, write the reason to halt.txt, and clear it to unpause.
The raw conversation is stored in conversation.json, and a more readable log is stored in log.txt.
