cmd="$1"
args="${@:2}"
shell_id="$PPID"
export SHELL_ID=$shell_id
python $(dirname "$0")/pydockenv/commands/pydockenv.py $cmd $args
