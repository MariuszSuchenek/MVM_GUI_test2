#!/bin/bash

MVMGUI_BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export MVMGUI="${MVMGUI_BASEDIR}/gui/"

# Test numpy
if ! $(python -c "import numpy" &> /dev/null); then 
  echo "ERROR: can not use the MVM GUI due to missing package numpy."
  return
fi

# Test pyqt5
if ! $(python -c "import PyQt5" &> /dev/null); then 
  echo "ERROR: can not use the MVM GUI due to missing package PyQt5."
  return
fi

# Test pyqtgraph
if ! $(python -c "import pyqtgraph" &> /dev/null); then 
  echo "ERROR: can not use the MVM GUI due to missing package pyqtgraph."
  return
fi

# Test pyserial
if ! $(python -c "import serial" &> /dev/null); then 
  echo "ERROR: can not use the MVM GUI due to missing package pyserial."
  return
fi

# Test pyyaml
if ! $(python -c "import yaml" &> /dev/null); then 
  echo "ERROR: can not use the MVM GUI due to missing package pyyaml."
  return
fi


export PYTHONPATH=$MVMGUI_BASEDIR/gui:$PYTHONPATH
echo $PYTHONPATH
