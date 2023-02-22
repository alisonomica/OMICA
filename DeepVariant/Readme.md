# DeepVariant

[DeepVariant](https://github.com/google/deepvariant/tree/r1.1/docs) is a deep learning-based variant caller that takes aligned reads in BAM or CRAM, produces [pileup image tensors](https://google.github.io/deepvariant/posts/2020-02-20-looking-through-deepvariants-eyes/) from them, classifies each tensor using CNN, and reports the results in standard VCF or gVCF files.

Supports germline variant-calling in diploid organisms:
- NGS Illumina data for WGS or WES
- PacBio HiFi data
- Oxford Nanopore long-read data by using PEPPER-DeepVariant
- Illumina + HiFi hybrid data

Only works on Unix-like systems and Python 3.6.

Requires at the highest level input:

- Reference genome in FASTA with corresponding .fai index file (samtools faidx)
- Aligned reads in BAM with corresponding .bai index file (same as reference)
- Model checkpoint for DeepVariant

*Files with suffix .gz are treated as compressed with gzip.

DeepVariant v0.7 or higher accepts CRAM files as input, but running time is increased in approximately 20%, although the file size is reduced in around 55%.
DeepVariant is composed of three programs: make_examples, call_variants, and postprocess_variants.

