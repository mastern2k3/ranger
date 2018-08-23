#!/bin/sh

BASEDIR=$(dirname $0)

mkdir -p $BASEDIR/monitor/user1

cp $BASEDIR/files/$1_records.csv $BASEDIR/monitor/user1
