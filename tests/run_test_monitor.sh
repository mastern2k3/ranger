#!/bin/sh

BASEDIR=$(dirname $0)

mkdir -p $BASEDIR/monitor
mkdir -p $BASEDIR/monitor/user1
mkdir -p $BASEDIR/monitor/user2

mkdir -p $BASEDIR/archive

python $BASEDIR/../main.py -t $BASEDIR/monitor -a $BASEDIR/archive &
