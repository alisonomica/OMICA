# PRS-Execution


## Input

- A phased VFC file is expected
- A .tsv file corresponding to the PRS model

## Output

PRS Z-score

## Pre-processing

### Read:
Use python library "Scikit-allel" 1.3.3

### Imputation:
Two options:
- If missing, set to zero
- If missing, use Beagle 5.2 and 1000 genomes as reference

### Filtering:
- Left join RSIDs in the PRS model to the VCF file
- If missing, set everyting to zero  

### Data handling:
Collapse the two haplotypes into one matrix using OR bitwise operation

## Run the model

Dot product between the vector of the model and the haplotype matrix

A two-column .tsv file is generated, where first column is sample ID and the second column corresponds to the calculated PRS Z-score
