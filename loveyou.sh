#!/bin/bash

# ---- hard limits ----
TIME_LIMIT=2          # seconds per command
MAX_OUTPUT=20000      # bytes

copy() {
  xclip -selection clipboard
}

safe_run() {
  timeout "$TIME_LIMIT" bash -c "$1" 2>&1 \
    | head -c "$MAX_OUTPUT"
}

while true; do
  read -r -p '$ ' command arguments

  case "$command" in
    echo)
      safe_run "printf '%s\n' $arguments" | copy
      ;;

    write)
      {
        read -r filename content <<< "$arguments"
        printf '%s' "$content" > "$filename"
        printf "\"%s\" written to %s" "$content" "$filename"
      } 2>&1 | copy
      ;;

    list)
      safe_run "ls" | copy
      ;;

    py)
      safe_run "python3 - <<'EOF'
$arguments
EOF" | copy
      ;;

    delfile)
      {
        rm -f -- "$arguments"
        printf "Deleted file %s" "$arguments"
      } 2>&1 | copy
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

You are an LLM. You are at gate 0.
Avoid newlines. Output is executed.
_____________" "$command" "$arguments" | copy
      ;;
  esac
done
