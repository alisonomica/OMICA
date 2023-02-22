FROM 812206152185.dkr.ecr.us-west-2.amazonaws.com/latch-base:6839-main

RUN apt-get update -y &&\
    apt-get install -y wget unzip curl

# sabre
#RUN wget https://github.com/najoshi/sabre/archive/refs/heads/master.zip &&\
#    unzip master.zip &&\
#    apt-get install -y zlib1g-dev &&\
#    cd sabre-master/ &&\
#    make &&\
#    mv sabre /usr/bin
RUN apt-get install -y zlib1g-dev
RUN apt-get install -y fastqc
#RUN python3 -m pip install multiqc

RUN wget https://github.com/seqan/flexbar/releases/download/v3.4.0/flexbar-3.4.0-linux.tar.gz &&\
    tar -xzvf flexbar-3.4.0-linux.tar.gz &&\
    mv flexbar-3.4.0-linux/flexbar /usr/bin

# Tell linker about object file needed for flexbar
ENV LD_LIBRARY_PATH=/root/flexbar-3.4.0-linux:$LD_LIBRARY_PATH

## TODO: validate paired end reads

RUN apt-get install -y bwa

## samtools
RUN apt-get install -y libncurses-dev libbz2-dev liblzma-dev
RUN wget https://github.com/samtools/samtools/releases/download/1.9/samtools-1.9.tar.bz2 &&\
    bunzip2 samtools-1.9.tar.bz2 &&\
    tar -xvf samtools-1.9.tar &&\
    cd samtools-1.9 &&\
    make &&\
    mv samtools /usr/bin

# gsutil
RUN apt-get install apt-transport-https ca-certificates gnupg -y
RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list &&\
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
RUN apt-get update -y && apt-get install google-cloud-cli -y

# index + align bwa mem
# sam to bam
# sort bam
# alignment metrics
# bqsr


RUN apt-get install -y default-jre-headless
RUN curl -L https://github.com/broadinstitute/picard/releases/download/2.26.10/picard.jar -o /root/picard.jar

RUN curl -L https://github.com/broadinstitute/gatk/releases/download/4.2.4.1/gatk-4.2.4.1.zip -o gatk-4.2.4.1.zip &&\
    unzip gatk-4.2.4.1.zip &&\ 
    mv gatk-4.2.4.1/gatk /usr/bin

# library code for glimpse
WORKDIR /root
#RUN wget https://github.com/samtools/htslib/releases/download/1.11/htslib-1.11.tar.bz2 &&\
#    tar -xf /root/htslib-1.11.tar.bz2 &&\
#    mv /root/htslib-1.11 /root/htslib &&\
#    cd /root/htslib &&\
#    ./configure &&\
#    make

#RUN wget https://boostorg.jfrog.io/artifactory/main/release/1.73.0/source/boost_1_73_0.tar.bz2 &&\
#    tar --bzip2 -xf boost_1_73_0.tar.bz2 &&\
#    cd boost_1_73_0 &&\
#    ./bootstrap.sh --with-libraries=iostreams,program_options --prefix=../boost &&\
#    ./b2 install'''


ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y && apt-get install -y software-properties-common
RUN wget -qO - https://adoptopenjdk.jfrog.io/adoptopenjdk/api/gpg/key/public | apt-key add - &&\
    add-apt-repository --yes https://adoptopenjdk.jfrog.io/adoptopenjdk/deb/ &&\
    apt-get update -y && apt-get install -y adoptopenjdk-8-hotspot &&\
    ln -s  /usr/lib/jvm/adoptopenjdk-8-hotspot-amd64 /usr/lib/jvm/java-8-openjdk-amd64

COPY wf /root/wf
#COPY data/GLIMPSE_* /usr/bin/
#COPY data/validator.pl /root/validator.pl
#COPY data/glimpse.sh /root

RUN apt-get install -y bcftools tabix
#RUN mkdir chunks GLIMPSE_imputed GLIMPSE_phased GLIMPSE_ligated

RUN python3 -m pip install --upgrade latch
COPY version /root/wf/version

ARG tag
ENV FLYTE_INTERNAL_IMAGE $tag
ENV BOWTIE2_INDEXES="reference"

WORKDIR /root
