# Project

This project aims to create a anime organizer for Linux that fix the anime naming issues by creating properly named symbolic links.

To extract the crypted information in those badly named folders, the project employed LLM to translate those names.

This project plans to support OpenAI compatitble backend, basically llama.cpp, in addition to amplify ai API.

## Workflow

The main workflow of the app is 

- read the source folder, load the folder and file name into Python objects
- send the folder tree series by series to LLM backend, requesting for identification
- after getting the identification, use symbolic links in target directory to create a new structure with proper name.

## Tools

These tools are only for development testing propse.

`gather_tree.py`

This tool is for converting a folder structure into a json

`rebuild_tree.py`

This tool is for converting a json back into a folder for testing
