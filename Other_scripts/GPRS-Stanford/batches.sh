OUTPUT='./'

while getopts ":o:" flag;do
	case "${flag}" in 
	  o) OUTPUT=${OPTARG};;
	  *)
		echo "There are invalid arguments"
		echo "Your arguments are: $@  "
		;;
	esac
done
shift $((OPTIND -1))
mkdir ${OUTPUT}/results

for i in {16..83};
do
	echo "Running GPRS-Genecove in batch "${i}
	python3 main.py -f ../1K-genome/x${i}.vcf.gz -a -o ${OUTPUT} -s batch_${i}
	echo "Done"
done
