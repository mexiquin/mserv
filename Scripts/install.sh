#!/bin/bash

# ONLY WORKS FOR LINUX

# Step 1: Download from git to home dir (~/.mserv)
git clone https://github.com/mexiquin/mserv.git ~/.mserv 

# Step 2: Build executable
cd ~/.mserv && python build.py mserv.py 

# Step 3: link the executable to PATH
printf '\nAdd this line to your .bashrc, .zshrc, etc. file\n'
echo 'export PATH=$PATH:~/.mserv/bin'