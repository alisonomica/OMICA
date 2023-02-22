# Running DeepVariant

The following code is used to run DeepVariant image over a BAM exome files located in bam_folder (you can download an example in the following [link](https://storage.googleapis.com/genomics-public-data/ftp-trace.ncbi.nih.gov/1000genomes/ftp/data/HG00126/alignment/HG00126.mapped.ILLUMINA.bwa.GBR.low_coverage.20120522.bam.csra)), which were aligned to the GRCh37 primary reference. The file simple_new_grch37.bed can be found in the repository.

Declare paths
```
BIN_VERSION="1.4.0"
BASE="${HOME}"
INPUT_DIR="${BASE}/BWA_out"
REF="Homo_sapiens.GRCh37.dna.primary_assembly.fa"
BAM="input.sorted.bam"
OUTPUT_DIR="${BASE}/output"
DATA_DIR="${INPUT_DIR}"
OUTPUT_VCF="out.vcf.gz"
```

Region and number of cores can be specified.
```
sudo docker run \
	-v "${DATA_DIR}":"/input" \
	-v "${OUTPUT_DIR}:/output" \
	-v "${HOME}:${HOME}" \
	gcr.io/deepvariant-docker/deepvariant:"${BIN_VERSION}" \
	/opt/deepvariant/bin/run_deepvariant \
	--model_type=WES \
	--ref="${BASE}/${REF}" \
  	--region=chr22 \
	--reads="${DATA_DIR}/${BAM}" \
	--output_vcf=/output/${OUTPUT_VCF} \
	--num_shards=${num_proc}
```
