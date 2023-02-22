# Extracting variable positions in the reference panel (run just once per reference panel)

#for i in {2..22}
#do
		#bcftools view -G -m 2 -M 2 -v snps reference_panel/1000GP.chr$i.bcf -Oz -o reference_panel/1000GP.chr$i.sites.vcf.gz
		#bcftools index -f reference_panel/1000GP.chr$i.sites.vcf.gz
		#bcftools query -f'%CHROM\t%POS\t%REF,%ALT\n' reference_panel/1000GP.chr$i.sites.vcf.gz | bgzip -c > reference_panel/1000GP.chr$i.sites.tsv.gz
		#tabix -s1 -b2 -e2 reference_panel/1000GP.chr$i.sites.tsv.gz

		#echo "Reference panel sites for chromosome $i ready"
#done

# Only for each new individual
# mkdir HG00152_chunks
# Just once
# mkdir GLIMPSE_allchrs
i=$1
#for i in {$a..$a}
#do
	echo "Computing genotype likelihoods for a single individual at specific positions in chromosome $i"

	BAM=HG00152_bam/HG00152_BWA_sort_recal.bam
	VCF=reference_panel/1000GP.chr$i.sites.vcf.gz
	TSV=reference_panel/1000GP.chr$i.sites.tsv.gz
	REFGEN=reference_genome/chr$i.fa.gz
	OUT=HG00152_vcf/HG00152.chr$i.vcf.gz

	bcftools mpileup -f ${REFGEN} -I -E -a 'FORMAT/DP' -T ${VCF} -r chr$i ${BAM} -Ou | 
	bcftools call -Aim -C alleles -T ${TSV} -Oz -o ${OUT}
	bcftools index -f ${OUT}

	#echo "Split chromosome $i into chunks"

	#bin/GLIMPSE_chunk --input reference_panel/1000GP.chr$i.sites.vcf.gz --region chr$i --window-size 2000000 --buffer-size 200000 --output HG00152_chunks/chunks.chr$i.txt

	echo "Impute and phase a whole chromosome $i"

	VCF=HG00152_vcf/HG00152.chr$i.vcf.gz
	REF=reference_panel/1000GP.chr$i.bcf
	MAP=../maps/genetic_maps.b38/chr$i.b38.gmap.gz

	while IFS="" read -r LINE || [ -n "$LINE" ];
	do
	   printf -v ID "%02d" $(echo $LINE | cut -d" " -f1)
	   IRG=$(echo $LINE | cut -d" " -f3)
	   ORG=$(echo $LINE | cut -d" " -f4)
	   OUT=GLIMPSE_imputed/HG00152.chr$i.${ID}.bcf
	   bin/GLIMPSE_phase --input ${VCF} --reference ${REF} --map ${MAP} --input-region ${IRG} --output-region ${ORG} --output ${OUT}
	   bcftools index -f ${OUT}
	done < HG00152_chunks/chunks.chr$i.txt
	 
	echo "Ligate multiple chunks together from chromosome $i"

	LST=GLIMPSE_ligated/list.chr$i.txt
	ls GLIMPSE_imputed/HG00152.chr$i.*.bcf > ${LST}
	OUT=GLIMPSE_ligated/HG00152.chr$i.merged.bcf
	
	bin/GLIMPSE_ligate --input ${LST} --output $OUT
	bcftools index -f ${OUT}

	#Optional steps
	echo "Sample haplotypes from chromosome $i"

	VCF=GLIMPSE_ligated/HG00152.chr$i.merged.bcf
	OUT=GLIMPSE_phased/HG00152.chr$i.phased.bcf
	bin/GLIMPSE_sample --input ${VCF} --solve --output ${OUT}
	bcftools index -f ${OUT}

	echo "Check imputation accuracy for chromosome $i"

	./bin/GLIMPSE_concordance --input concordance.lst --minDP 8 --output GLIMPSE_concordance/output_chr$i --minPROB 0.9999 \
	--bins 0.00000 0.00100 0.00200 0.00500 0.01000 0.05000 0.10000 0.20000 --af-tag AF_nfe --thread 8

#done

echo "Concatenating chromosomes into one VCF file"

#bcftools concat -o GLIMPSE_allchrs/HG00125.vcf.gz -Oz GLIMPSE_phased/HG00152.*.phased.bcf
