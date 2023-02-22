threads=4

while getopts :p:t: aflag; do
    case $aflag in
        p) path=$OPTARG;;
        t) threads=$OPTARG;;
        
    esac
done


time seq 1 22|parallel -j$threads bash ./GLIMPSE-all-chrs-parallel.sh {};bcftools concat -o GLIMPSE_allchrs/HG00125.vcf.gz -Oz GLIMPSE_phased/HG00152.*.phased.bcf
