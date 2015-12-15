# NLP_PL

## Contents

### CorpusPopulate
Contains script to retrieve Python Files from /git_dl

### Data
Files containing extracted data

### Java
Our corpus

### LM
The main code:

ExtractCode.py - CodeUnit / Code analysis
ExtractSequences.py - Generate sequences from CodeUnits
LM.py - The Language Model
ProcessData.py - Gets info for LM
TestModel.py - The actual test
TypeUtils.py - misc.
WriteData.py - Processes CodeUnits
results.csv - THE LL's

### git_dl
Store zip files here

## Process

### Build Corpus
DL .zip files to git_dl
CorpusPopulate/GetJavaFiles.py

### Build LM
mode = {levels, cfs}
WriteData.py mode
ProcessData.py mode

### Run LM
TestModel.py
