#!/bin/bash

# */2 * * * * cd $HOME/tx20; ./chkwindpost.sh > $HOME/logs/chkwindpost.log 2>&1

PY_PID=`pgrep -x -u pi -f "python windpost.py"`

if [[ $PY_PID ]]; then
  echo OK
else
  echo NOK!  
  python windpost.py > /dev/null 2>&1 &
fi

