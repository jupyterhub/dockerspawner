#!/bin/sh

line=$(cat user)
user=`echo $line | cut -f 1 -d':'`
id=`echo $line | cut -f 2 -d':'`
echo "Creating user $user ($id)"
useradd -u $id -s $SHELL $user
