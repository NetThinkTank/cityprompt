#! /bin/bash

if [ "$1" == "" ]; then
	echo "argument needed"
	exit
fi

rm -rf .installed.cfg .mr.developer.cfg bin/ develop-eggs/ eggs/ parts/ src/
/usr/local/python/bin/python ./bootstrap.py -c ./buildout_$1.cfg
bin/buildout -c ./buildout_$1.cfg

