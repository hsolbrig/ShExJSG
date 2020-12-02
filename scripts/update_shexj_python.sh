#!/usr/bin/env bash
# Update ShExJ.py file if necessary
# Usage:  . scripts/update_shexj_python.sh


NEWF=$(mktemp).py
generate_parser -nh -e -o $NEWF ShExJSG/ShExJ.jsg
if [[ `tail -n +4 ShExJSG/ShExJ.py | diff -w -q $NEWF -` ]]
then
  mv $NEWF ShExJSG/ShExJ.py
  echo "ShExJ.py was updated"
else
  rm $NEWF
  echo "ShExJ.py was not changed"
fi

