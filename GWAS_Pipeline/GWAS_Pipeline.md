# GWAS pipeline for admixed population v0.0.1

Admixed populations, such as Hispanic/Latinos, are known to have complex population structure, and may bias results when employing common analytical methods. Specifically, in GWAS, admixed populations may result in false positive hits due to different allele frequencies across populations. Tractor is a tool which generates ancestry-specific effect size estimates, boosts GWAS power, and improves the resolution of association signals.

Reference URL https://github.com/Atkinson-Lab/Tractor/wiki

## Requirements  
* [ShapeIt](https://mathgen.stats.ox.ac.uk/genetics_software/shapeit/shapeit.html#home)
* [Plink](https://www.cog-genomics.org/plink/)
* Python 3
* R
* [RFmix](https://github.com/slowkoni/rfmix)

## Installation
### RFmix

```
git clone https://github.com/slowkoni/rfmix.git
cd rfmix/
autoreconf --force --install
./configure
make
```

### Tractor

```
git clone https://github.com/Atkinson-Lab/Tractor.git
```

## Step one: Quality Control

Transform imputed, phased multi-genome VCF to Plink binary files.

```
plink --vcf $DATA.vcf --make-bed --out $DATA
```

Keep only autosomes.

```
plink --bfile $DATA --chr 1-22 --make-bed --out $DATA.auto
```

Perform standard GWAS SNP filtering, MAF threshold is given by

MAF = 1.5 / (2 x #ind)

Hence, this threshold will vary depending on the number of individuals in the sample set.

```
plink \
    --bfile $DATA.auto \
    --maf 0.01 \
    --hwe 1e-6 \
    --geno 0.01 \
    --mind 0.01 \
    --qual-threshold 0.3 \
    --write-snplist \
    --make-just-fam \
    --out $DATA.auto.QC
```

Remove duplicated SNPs.

```
cut -f2,4 $DATA.auto.QC.bim | uniq -f1 > $DATA.NonDupSNPs
cut -f2,4 $DATA.auto.QC.bim | uniq -D -f1 > $DATA.DuplicateSNPs
cat $DATA.DuplicateSNPs | uniq -f1 > $DATA.FirstDup
cat $DATA.NonDupSNPs $DATA.FirstDup > $DATA.SNPstoKeep
plink --bfile $DATA.auto.QC --extract $DATA.SNPstoKeep --make-bed --out $DATA.auto.QC.nodup
```

Orient to 1000GP data to correct mismatching alleles. Use python script to make this process.

```
python match_against_1000g_v2.py --bim $DATA.auto.QC.nodup.bim --legend ref-panel-legend-1000GP --out $DATA.1kg
cat $DATA.1kg.Indel.txt $DATA.1kg.NonMatching.txt > $DATA.1kg.badsites.txt
plink --bfile $DATA.auto.QC.nodup --exclude $DATA.1kg.badsites.txt --make-bed --out $DATA.auto.QC.nodup.1ksites
plink --bfile $DATA.auto.1ksites --flip $DATA.1kg.FlipStrand.txt --make-bed --out $DATA.auto.QC.nodup.1ksites.flip
```

Remove A/T C/G loci using the following python script.

```
python find_cg_at_snps.py $DATA.auto.QC.nodup.1ksites.flip.bim > $DATA.ATCGsites
plink --bfile $DATA.auto.QC.nodup.1ksites.flip --exclude $DATA.ATCGsites --make-bed --out $DATA.QCed
```

Return to VCF files split by chromosome.

```
for i in {1..22}; do plink --bfile $DATA.QCed --recode vcf --chr ${i} --out $DATA.QCed.chr${i} ;done
for i in {1..22}; do bgzip $DATA.QCed.chr${i}.recode.vcf ;done
```

## Step two: Local Ancestry Deconvolution

This step is done by chromosome.

```
for i in {1..22}; do \
rfmix -f $DATA.QCed.chr${i}.recode.vcf.gz -r 1000GP.chr$i.vcf.gz --chromosome=${i} -m 1kg_order.indivs.pops.txt \
-g chr${i}.rfimx.b38.gmap -e 1 -n 5 --reanalyze-reference --n-threads=8 -o $DATA.QCed.rfmix.chr${i} ;done
```

## Step three: Correct Switch Errors (optional)

Identifying and correcting switch errors in local ancestry calls. A switch error is defined as a swap in ancestries within a 1 cM window to opposite strands conditioned on heterozygous ancestral dosage. Currently, the tract recovery step is only implemented for a 2-way admixed setting.

VCF files need to be phased, bgzipped, indexed, and annotated.

```
python UnkinkMSPfile.py --msp $DATA.QCed.rfmix.chr${i}
tabix -p $DATA.QCed.chr${i}.recode.vcf.gz
bcftools annotate -x INFO,FORMAT $DATA.QCed.chr${i}.recode.vcf.gz > $DATA.QCed.chr${i}.stripped_file.vcf
python UnkinkGenofile.py --switches $DATA.QCed.rfmix.chr${i}.switches --genofile $DATA.QCed.chr${i}
```

## Step four:  Extracting Tracts and Ancestral Dosages

You can input the unkinked files from the previous step if you chose to correct switch errors, or go straight from the original data. The number of ancestries must be the same as in the msp file.

```
python ExtractTracts.py --msp $DATA.QCed.rfmix.chr${i} --vcf $DATA.QCed.chr${i} --num-ancs 26
```

## Step five: Tractor GWAS

To run Tractor it is rquired to have the following packages: numpy, pandas, sklearn, and statsmodels.

The hapdose input data is the stem name of the ExtractTracts output. Phenotype input data must is a table which contains the samples ID (same as in VCF) in the first column named "IID", the second column "y" contains the phenotype to be analyzed, and the rest of the columns are treated as covariates "COV". The method can be linear for a continuous phenotype or logistic for binary phenotypes. NOTE: All files must be uncompressed.

```
python RunTractor.py --hapdose $DATA.QCed.chr${i} --phe Phenotype.txt --method linear --out sumstats.txt
```
