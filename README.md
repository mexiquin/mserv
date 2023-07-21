# mserv
A simple wrapper for managing your Minecraft servers.

## What is it?
Mserv is a little commandline utility I wrote to help me better
manage my, and my friends' Minecraft servers.  

Mojang offers a DIY *server.jar* file 
which you can execute and host a server on your own PC for free. But, what if I wanted
separate servers? What if I don't care to go to the Minecraft website and download the file myself?
Or, what if I don't care to remember the server execution parameters?  

Mserv serves to simplify many of these processes, and should make efforts to help those who just want to get playing.

## What can it do?
This is a wrapper around the official server.jar from Mojang
As of right now, it can...

- Download and generate files from the official server executable
- Start and shutdown the server
- Displays network connection information (public ip, port number) so others can join your server

## What can it NOT do?
This script can not:
- Port forward for you (You have to do that yourself)
- Execute multiple servers at the same time

# Requirements
1. Java (to run the server)

# TODO - Installation

# Usage

## Setup
To start using mserv, you have to create a new server folder. Do this by running the:
```shell
mserv setup
```
command. This will create a new folder in your current working directory which will hold all of 
the server files.

## Running
To actually start the server you use the command:
```shell
mserv run
```
this will provide some useful networking information (eg. public IP address when playing with others), as well as spin-up the server

# Generated Help Page
```
Usage: mserv.py [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  run
  setup   Create a new server.
  update  Download a fresh server.jar file from Mojang.

```

