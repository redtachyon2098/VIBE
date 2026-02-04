#!/bin/bash

# ---- hard limits ----
TIME_LIMIT=2          # seconds per command
MAX_OUTPUT=20000      # bytes

safe_run() {
  {
    timeout "${TIME_LIMIT}s" bash -c "$1"
    status=$?
    if [ "$status" -eq 124 ]; then
      echo "Error: Timed out after $TIME_LIMIT seconds"
    fi
    exit "$status"
  } 2>&1 | head -c "$MAX_OUTPUT"
}

export TIME_LIMIT

while true; do
  printf '__READY__\n'
  
  read -r command arguments

  case "$command" in
    echo)
      safe_run "echo $arguments"
      ;;

	  write)
	    read -r filename remainder <<< $arguments
      eval "declare content=$remainder"

      if ! [ -f "$filename" ]
      then
        echo "$content" > "$filename"
        printf "%s written to %s" "$content" "$filename"
      else
        printf "Error: You silly goose! That file already exists!"
      fi
      ;;
    
    list)
      if [ "$arguments" == '' ]
      then
        safe_run "ls"
      else
        printf "Error: You poor duckling... that's not how that command works!"
      fi
      ;;

    py)
      if [ "${arguments: (-3)}" == ".py" ]
      then
        safe_run "python3 $arguments"
      else
        printf "Error: \"$arguments\" is not a .py file"
      fi
      ;;

    delfile)
      {
        rm -f -- "$arguments"
        printf "Deleted file %s" "$arguments"
      } 2>&1
      ;;

    restart)
      exec bash loveyou.sh
      ;;

    *)
      printf "____ERROR___
Invalid command.
Your erroneous input:

%s %s

Possible commands:
echo
write
list
py
delfile

You can do it, my adorable LLM!
You just need to use the right commands!
_____________" "$command" "$arguments"
      ;;
  esac
  printf '\n'
done
