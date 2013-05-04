.PHONY: help translations

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  translations to make mo files from po files in translations/"

translations:
	find translations/ -name '*.po' | sed -e 's/\(.*\)\.po/\1/' | xargs -I{} msgfmt '{}.po' -o '{}.mo'
	@echo
	@echo "Compiled po files into mo files in translations/"
