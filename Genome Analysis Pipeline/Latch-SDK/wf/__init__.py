import os
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import Optional
from functools import partial

from flytekit import task
from flytekitplugins.pod import Pod
from kubernetes.client.models import (V1Container, V1PodSpec, V1ResourceRequirements, V1Toleration)
from latch import workflow
from latch.types import LatchDir, LatchFile

print = partial(print, flush=True)

version = open(Path(__file__).parent.joinpath("version").resolve(), "r").read().strip()
print(f"Welcome to GAP by OmicaBio " + version)
"""Read workflow version for intermediate image version."""


def generate_pod_spec_for_task():
    primary_container = V1Container(name="primary")
    resources = V1ResourceRequirements(
        requests={"cpu": "70", "memory": "150Gi"},
        limits={"cpu": "96", "memory": "192Gi"},
    )

    primary_container.resources = resources

    pod_spec = V1PodSpec(
        containers=[primary_container],
        tolerations=[V1Toleration(effect="NoSchedule", key="ng", value="cpu-96-spot")],
    )

    return pod_spec


def _fmt_dir(bucket_path: str) -> str:
    if bucket_path[-1] == "/":
        return bucket_path[:-1]
    return bucket_path


class GenomeBuild(Enum):  # TODO use this class somehow in the tasks
    hg38 = "hg38"
    hg37 = "hg37"


@task(
    task_config=Pod(
        pod_spec=generate_pod_spec_for_task(),
        primary_container_name="primary"
    )
)
def fastq_to_bam(
        fastq1: LatchFile,
        fastq2: LatchFile,
        ref_genome: str,
        preprocess: bool,
        output_dir: LatchDir, # FlyteDirectory = FlyteDirectory("latch:///omica_analysis_output"),
        sample_name: str,
        adapterfile: Optional[LatchFile] = None,
        quality_trim: Optional[int] = None,
        adapter_preset: Optional[str] = None,
) -> LatchFile:
    print("Entered fastq_to_bam")
    output_directory_path = Path("/root/outputs").resolve()

    local_fastq1 = fastq1.local_path
    local_fastq2 = fastq2.local_path

    if preprocess == True:
        optional_parameters = {
            "adapters": adapterfile,
            "qtrim-threshold": quality_trim,
            "adapter-preset": str(adapter_preset),
        }

        _trim_cmd = [
            "flexbar",
            "--reads",
            str(local_fastq1),
            "--reads2",
            str(local_fastq2),
            "-ap",
            "ON",
            "--threads",
            "96",
        ]

        for param_name, value in optional_parameters.items():
            if value is not None:
                if isinstance(value, LatchFile) or isinstance(value, LatchDir):
                    value = Path(value).resolve()
            _trim_cmd.append(f"--{param_name} {value}")

        subprocess.run(_trim_cmd)

        local_fastq1 = Path("flexbarOut_1.fastq").resolve()
        local_fastq2 = Path("flexbarOut_2.fastq").resolve()

    if ref_genome == "hg38":  # TODO CHANGE TO OMICAS GOOGLE BUCKET
        _get_ref_cmd = [
            "aws",
            "s3",
            "cp",
            "--recursive",
            "s3://latch-public/hg38",
            ".",
        ]
        print("Downloading hg38")
        subprocess.run(_get_ref_cmd)

        ref_genome_fa = "GRCh38.primary_assembly.genome.fa"
        ref_dbsnp = "/root/resources_broad_hg38_v0_Homo_sapiens_assembly38.dbsnp138.vcf"
        ref_indels = "/root/resources_broad_hg38_v0_Mills_and_1000G_gold_standard.indels.hg38.vcf"

    elif ref_genome == "hg37":
        _get_ref_cmd = [
            "gsutil",
            "-m",
            "cp",
            "-r",
            "gs://latch-omica-test/hg37/reference_genome/",
            "gs://latch-omica-test/hg37/reference_recalibration/",
            ".",
        ]
        print("Downloading hg37")
        subprocess.run(_get_ref_cmd)

        ref_genome_fa = "/root/reference_genome/GRCh37.dna.primary_assembly"
        ref_dbsnp = "/root/reference_recalibration/Homo_sapiens_assembly19.dbsnp138.vcf"
        ref_indels = "/root/reference_recalibration/Mills_and_1000G_gold_standard.indels.b37.vcf"
        print("Downloaded correctly")

    print("Running BWA MEM")
    pileup_sam = Path("pileup.sam").resolve()
    _mapping_cmd = [
        "bwa",
        "mem",
        "-M",
        "-t",
        "96",
        str(ref_genome_fa),
        str(local_fastq1),
        str(local_fastq2),
    ]
    with open(pileup_sam, "w") as ps:
        subprocess.run(_mapping_cmd, stdout=ps)
    print(_mapping_cmd)

    print("Transforming Sam to Bam")
    pileup_bam = Path("pileup.bam").resolve()
    _sam2bam_cmd = [
        "samtools",
        "view",
        "-S",
        "-b",
        "-@",
        "96",
        "-o",
        "pileup.bam",
        str(pileup_sam),
    ]
    subprocess.run(_sam2bam_cmd)
    print(_sam2bam_cmd)

    print("Sorting and indexing")
    sorted_pileup_bam = Path("pileup_sorted.bam").resolve()
    _sort_cmd = [
        "samtools",
        "sort",
        "-o",
        "pileup_sorted.bam",
        "-O",
        "bam",
        "-@",
        "96",
        str(pileup_bam),
    ]
    subprocess.run(_sort_cmd)
    print(_sort_cmd)

    # Index pileup_sorted.bam file
    subprocess.run(
        [
            "samtools",
            "index",
            str(sorted_pileup_bam),
        ]
    )
    print("indexing bam")
    ref_genome_fa = str(ref_genome_fa) + ".fa"

    print("Indexing reference genome")
    # Index ref.fa
    path_ref_genome_fa = Path(ref_genome_fa).resolve()
    subprocess.run(
        [
            "samtools",
            "faidx",
            str(path_ref_genome_fa),
        ]
    )

    print("Grouping samples")
    assigned_pileup_bam = Path("pileup_sorted_rg1.bam").resolve()
    subprocess.run(
        [
            "java",
            "-jar",
            "picard.jar",
            "AddOrReplaceReadGroups",
            f"I={sorted_pileup_bam}",
            f"O={assigned_pileup_bam}",
            "RGID=1",
            "RGLB=lib2",
            "RGPL=illumina",
            "RGPU=unit1",
            f"RGSM={sample_name}",
        ]
    )

    print("Base recalibration")
    bqsr_pileup_bam = Path("pileup_sorted_bsqr.bam").resolve()
    subprocess.run(
        [
            "/usr/lib/jvm/java-8-openjdk-amd64/bin/java",
            "-jar",
            "/root/gatk-4.2.4.1/gatk-package-4.2.4.1-local.jar",
            "BQSRPipelineSpark",
            "-R",
            str(path_ref_genome_fa),
            "-I",
            str(assigned_pileup_bam),
            "--known-sites",
            str(ref_dbsnp),
            "--known-sites",
            str(ref_indels),
            "-O",
            str(bqsr_pileup_bam),
        ]
    )
    print("fastq_to_bam finished")
    print(bqsr_pileup_bam)

    return LatchFile(str(bqsr_pileup_bam), f"latch://{bqsr_pileup_bam}")
    #return LatchFile(str(bqsr_pileup_bam))


@task(
    task_config=Pod(
        pod_spec=generate_pod_spec_for_task(), primary_container_name="primary"
    ),
    container_image=f"812206152185.dkr.ecr.us-west-2.amazonaws.com/omica-dv:v0.1.9",
)
def deepvariant(
        bam_file: LatchFile,
        output_dir: LatchDir,
        ref_genome: str,
        DV_model: str,
        out_gvcf: bool,
        regions: Optional[str] = None,
        regionbed: Optional[LatchFile] = None,
) -> (LatchFile, LatchDir):
    print("Variant calling with DeepVariant")
    o_local_bam_file = Path(bam_file).resolve()
    print(o_local_bam_file)
    local_bam_file = Path(f"{o_local_bam_file.name}")
    print(local_bam_file)
    shutil.move(o_local_bam_file, local_bam_file)

    if ref_genome == "hg38":
        subprocess.run(
            [
                "curl",
                "-L",
                "http://hgdownload.soe.ucsc.edu/goldenPath/hg38/bigZips/hg38.fa.gz",
                "-o",
                "hg38.fa.gz",
            ]
        )
        ref_genome_file = "hg38.fa"

    elif ref_genome == "hg37":
        subprocess.run(
            [
                "curl",
                "-L",
                "https://hgdownload.cse.ucsc.edu/goldenPath/hg19/bigZips/hg19.fa.gz",
                "-o",
                "hg19.fa.gz",
            ]
        )
        print("Downloaded hg19")
        ref_genome_file = "hg19.fa"

    subprocess.run(
        [
            "gunzip",
            str(ref_genome_file + ".gz"),
        ]
    )

    subprocess.run(
        [
            "samtools",
            "faidx",
            str(ref_genome_file),
        ],
        check=True,
    )

    subprocess.run(
        [
            "samtools",
            "index",
            str(local_bam_file),
        ]
    )

    optional_parameters = {
        "regions": regions,
        "regionbed": regionbed,
    }
    print(os.listdir("/opt"))

    _dv_cmd = [
        "/opt/deepvariant/bin/run_deepvariant",
        f"--model_type={DV_model}",
        f"--ref={ref_genome_file}",
        f"--reads={local_bam_file}",
        "--output_vcf=/output/output.vcf.gz",
        "--num_shards=96",
    ]

    if out_gvcf == True:
        _dv_cmd.append("--output_gvcf=/output/output.g.vcf.gz")
    for param_name, value in optional_parameters.items():
        if value is not None:
            if isinstance(value, LatchFile) or isinstance(value, LatchDir):
                value = Path(value).resolve()
        _dv_cmd.append(f"--regions={value}")
    subprocess.run(_dv_cmd)

    return (
        LatchFile(
            f"/output/output.{ref_genome}.vcf.gz",
            #remote_path=_fmt_dir(output_dir.remote_source) + f"/output.{ref_genome}.vcf.gz",
            remote_path=output_dir.remote_source + f"/output.{ref_genome}.vcf.gz",
        ),
        #LatchDir("/output/", remote_directory=_fmt_dir(output_dir.remote_source)),
        LatchDir("/output/", remote_directory=output_dir.remote_source),
    )


@workflow
def omica_genome_analysis(
        fastq1: LatchFile,
        fastq2: LatchFile,
        sample_name: str,
        ref_genome: str,
        DV_model: str,
        out_gvcf: bool,
        preprocess: bool,
        output_dir: LatchDir,
        regions: Optional[str] = None,
        regionbed: Optional[LatchFile] = None,
        adapterfile: Optional[LatchFile] = None,
        quality_trim: Optional[int] = None,
        adapter_preset: Optional[str] = None,
) -> (LatchFile, LatchDir):
    """omica.bio custom genomic analysis pipeline.

    # Genome Analysis Pipeline

    The genome analysis pipeline is design to discover the genomic variants in Mexican and Latin American populations. This pipeline is optimized to work with low coverage whole genome sequencing (lcWGS), from raw FASTQ files (multiplexed or demultiplexed) to imputed VCF files, leveraging systematized bioinformatic algorithms.

    __metadata__:
        display_name: Omica Genome Analysis
        documentation:
        author:
            name: Constanza Marini
            email: constanza@omica.bio
            github:
        repository:
        license:
            id:

    Args:
        fastq1:
            First read file bgzipped or uncompressed.

            __metadata__:
                display_name: FastQ Read 1

        fastq2:
            Second read file bgzipped or uncompressed.

            __metadata__:
                display_name: FastQ Read 2

        sample_name:
            Sample name or identification.

            __metadata__:
                display_name: Sample ID

        ref_genome:
            The reference genome desired for assembly and variant calling, hg37 or hg38.

            __metadata__:
                display_name: Reference Genome Build
                output: true

        preprocess:
            Preprocess raw FastQ files, such as quality trimming and adapters removal.

            __metadata__:
                display_name: Preprocess FastQ files

        adapterfile:
            Fasta file with adapters sequences.

            __metadata__:
                display_name: Adapters sequences

        adapter_preset:
            Use adapter preset for Illumina libraries: TruSeq, SmallRNA, Methyl, Ribo, Nextera, NexteraMP.

            __metadata__:
                display_name: Adapter preset

        quality_trim:
            Trimming based on phred quality values.

            __metadata__:
                display_name: Quality trimming threshold

        DV_model:
            DeepVariant model for exome or whole genome sequencing: WES, WGS, PacBio, HYBRID_PACBIO_ILLUMINA.

            __metadata__:
                display_name: DeepVariant model type

        regions:
            A space-separated list of chromosome regions to process. Individual elements can be region literals, such as chr20:10-20 or only chr20.

            __metadata__:
                display_name: DeepVariant regions

        regionbed:
            BED file for variant calling in specific regions.

            __metadata__:
                display_name: DeepVariant BED regions

        out_gvcf:
            Output gVCF file?

            __metadata__:
                display_name: DeepVariant gVCF output

        output_dir:
            The location of output results within Latch Data.

            __metadata__:
                display_name: Output Directory
                output: true

    """
    bam_file = fastq_to_bam(
        fastq1=fastq1,
        fastq2=fastq2,
        ref_genome=ref_genome,
        output_dir=output_dir,
        preprocess=preprocess,
        sample_name=sample_name,
        adapterfile=adapterfile,
        quality_trim=quality_trim,
        adapter_preset=adapter_preset,
    )
    return deepvariant(
        bam_file=bam_file,
        output_dir=output_dir,
        DV_model=DV_model,
        ref_genome=ref_genome,
        out_gvcf=out_gvcf,
        regions=regions,
        regionbed=regionbed,
    )


if __name__ == "__main__":
    print("Entered main")
    print(os.listdir())
    omica_genome_analysis(
        fastq1=LatchFile("data/HG00152_1.fastq.gz"),
        fastq2=LatchFile("data/HG00152_2.fastq.gz"),
        sample_name="HG00152",
        ref_genome="hg37",
        DV_model="WGS",
        out_gvcf=False,
        preprocess=False,
        output_dir=LatchDir("."),
        regions="chr22",
        regionbed=None,
        adapterfile=None,
        quality_trim=None,
        adapter_preset=None,
    )
