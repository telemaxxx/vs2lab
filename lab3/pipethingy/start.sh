#!/bin/bash

echo "starting vs2lab A3"

if ! command -v tmuxp
then
	sudo apt update; sudo apt install -y tmux tmuxp neovim
fi

tmuxp load session.yaml


