# Model Calibration with Process Variables depending on Environmental Parameters
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jonaspleyer/Paper-ode-integrate/Build%20LaTeX%20document?style=flat-square)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/jonaspleyer/Paper-ode-integrate?style=flat-square)

# Compilation
We assume a working Texlive installation.
Compile with from within the src folder or use the provided makefile if cloning from the [git repository](https://github.com/jonaspleyer/2022-02-Agent-based-Modeling-and-Spatial-Turing-Pattern-Analysis)
```bash
latexmk -pdf
```
or simply use
```bash
make
```
# More Functionalities
## Bibexport
Export all bibliography items into a single file.
```bash
make bibexport
```
## Citecound
Counts the number of citations currently used in the document.
```bash
make citecount
```
## Examine Errors
Examines errors of the `main.log` file (can only be used after `make` or `make fresh`).
```bash
make examine
```
## Latexpand
Create a single large LaTeX file.
```bash
make latexpand
```
## Wordcount
See how many words are in the LaTeX document text at the moment.
```bash
make wordcount
```

# Licensing
This work is licensed under a
[Creative Commons Attribution 4.0 International License](http://creativecommons.org/licenses/by/4.0/).
