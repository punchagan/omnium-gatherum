#!/bin/bash
found=0

for win in `xdotool search --class $1`;
do
if [ `xdotool get_desktop_for_window $win` -eq `xdotool get_desktop` ];
then found=1; break;
fi;
done

if [ $found -eq 1 ]; then xdotool windowactivate $win; else $1; fi
