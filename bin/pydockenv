cmd="$1"
([[ -n $ZSH_EVAL_CONTEXT && $ZSH_EVAL_CONTEXT =~ :file$ ]] ||
 [[ -n $KSH_VERSION && $(cd "$(dirname -- "$0")" &&
    printf '%s' "${PWD%/}/")$(basename -- "$0") != "${.sh.file}" ]] ||
 [[ -n $BASH_VERSION ]] && (return 0 2>/dev/null)) && sourced=1 || sourced=0
if [ $sourced -eq 0 ] && ([ "$cmd" = "activate" ] || [ "$cmd" = "deactivate" ])
then
    echo "$cmd command must be called using 'source'"
    exit 1
fi

shell_id="$PPID"
export SHELL_ID=$shell_id
pydockenv_entry_point=$(python -c 'from pydockenv.commands import pydockenv; print(pydockenv.__file__)')
python $pydockenv_entry_point $@

if [ $? -eq 0 ]
then
    if [ "$cmd" = "activate" ]
    then
        export PYDOCKENV=$2
    elif [ "$cmd" = "deactivate" ]
    then
        export PYDOCKENV=""
    fi
fi
