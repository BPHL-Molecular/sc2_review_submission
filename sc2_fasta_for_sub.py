#!/usr/bin/env python

#Author: Sarah Schmedes
#Email: sarah.schmedes@flhealth.gov

'''
This script will take in SC2 consensus assemblies and output into concatenated fasta files for submission to GISAID and Genbank using an
input metadata file. This script has been tested on assemblies generated from FLAQ-SC2 (ivar) and Dragen pipelines.
'''

import os
import subprocess
import datetime
import sys
import argparse
import pandas as pd
from Bio import SeqIO

#Parse arguments, get path of metadata file
parser = argparse.ArgumentParser(usage='sc2_fasta_for_sub.py <input_meta>')
parser.add_argument('--assem_dir', help='path to assembly directory as input')
parser.add_argument('--concat_fasta', help='path to concatenated fasta as input')
parser.add_argument('--meta', help='path to sample name metadata file')
parser.add_argument('--state_name', help='state and lab acronym. (e.g., FL_BPHL)')

if len(sys.argv[1:]) == 0:
    parser.print_help()
    parser.exit()

args = parser.parse_args()

assem_path = args.assem_dir
cat_fasta = args.concat_fasta
meta = args.meta
state = args.state_name
cwd = os.getcwd() + '/'

output_dir = cwd + datetime.date.today().strftime('%Y%m%d') + '_bulk_submission/'
subprocess.run('mkdir -p ' + output_dir, shell=True, check=True)

#Read in metadata file and create gisaid and ncbi name dictionaries
names = pd.read_table(meta, sep ="\t", header=None)
lab_name = list(names[0])
repo_name = list(names[1])
gisaid_names = ['hCoV-19/' + i for i in repo_name]
genbank_names = ['SARS-CoV-2/Human/' + i for i in repo_name]
gisaid = dict(zip(lab_name, gisaid_names))
genbank = dict(zip(lab_name, genbank_names))

#Make output_dirs for individual fastas
gis_out = output_dir + 'gisaid/'
gen_out = output_dir + 'genbank/'
subprocess.run('mkdir ' + gis_out, shell=True, check=True)
subprocess.run('mkdir ' + gen_out, shell=True, check=True)
subprocess.run('mkdir temp_fastas', shell=True, check=True)

#If individual assemblies as input, find assembly in assembly directory and prepare for submission
if assem_path:
    for n in lab_name:
        #Get fasta file name
        proc_f = subprocess.run('ls ' + assem_path + '/' + n + '*.fa*', shell=True, capture_output=True, text=True, check=True)
        fasta_file = proc_f.stdout.rstrip()
        #Read in each fasta using biopython and print back to file to get one line of sequence.
        for record in SeqIO.parse(fasta_file, "fasta"):
            seq_id = record.id
            sn = seq_id.split("|")
            sn = sn[0]
            assert n == sn, 'File sample name does not match fasta header file name. Sample:' + n + '; header:' + sn
            seq = str(record.seq)
            with open('temp_fastas/' + n + '.fasta', 'w') as temp_fasta:
                temp_fasta.write('>' + seq_id + "\n")
                temp_fasta.write(seq)
        #Write header to new gisaid fasta and then write sequence (removing leading Ns and fold every 75 characters
        subprocess.run('echo ">' + gisaid[n] + '" > ' + gis_out + n + '_gisaid.fasta', shell=True, check=True)
        subprocess.run('grep -v ">" temp_fastas/' + n + '.fasta | sed \'s/^N*N//g\' | fold -w 75 >> ' + gis_out + n + '_gisaid.fasta', shell=True, check=True)
        #Write header to new genbank fasta and then write sequence (removing leading Ns and fold every 75 characters
        subprocess.run('echo ">' + genbank[n] + '" > ' + gen_out + n + '_genbank.fasta', shell=True, check=True)
        subprocess.run('grep -v ">" temp_fastas/' + n + '.fasta | sed \'s/^N*N//g\' | fold -w 75 >> ' + gen_out + n + '_genbank.fasta', shell=True, check=True)

#If concatenated fasta as input
if cat_fasta:
    for record in SeqIO.parse(cat_fasta, "fasta"):
        seq_id = record.id
        sn = seq_id.split("|")
        sn = sn[0]
        seq = str(record.seq)
        with open('temp_fastas/' + sn + '.fasta','w') as temp_fasta:
            temp_fasta.write('>' + seq_id + "\n")
            temp_fasta.write(seq)
    for n in lab_name:
        #Write header to new gisaid fasta and then write sequence (removing leading Ns and fold every 75 characters
        subprocess.run('echo ">' + gisaid[n] + '" > ' + gis_out + n + '_gisaid.fasta', shell=True, check=True)
        subprocess.run('grep -v ">" temp_fastas/*' + n + '*.fasta | sed \'s/^N*N//g\' | fold -w 75 >> ' + gis_out + n + '_gisaid.fasta', shell=True, check=True)
        #Write header to new genbank fasta and then write sequence (removing leading Ns and fold every 75 characters
        subprocess.run('echo ">' + genbank[n] + '" > ' + gen_out + n + '_genbank.fasta', shell=True, check=True)
        subprocess.run('grep -v ">" temp_fastas/*' + n + '*.fasta | sed \'s/^N*N//g\' | fold -w 75 >> ' + gen_out + n + '_genbank.fasta', shell=True, check=True)

    
    

#Concatenate fastas for each submission file
subprocess.run('cat ' + gis_out + '*_gisaid.fasta > ' + output_dir + datetime.date.today().strftime('%Y%m%d') + '_' + state + '_all_sequences_gisaid.fasta', shell=True, check=True)
subprocess.run('cat ' + gen_out + '*_genbank.fasta > ' + output_dir + datetime.date.today().strftime('%Y%m%d') + '_' + state + '_all_sequences_genbank.fasta', shell=True, check=True)

#Remove separated assemblies
subprocess.run('rm -r temp_fastas/', shell=True, check=True)
subprocess.run('rm -r ' + gis_out, shell=True, check=True)
subprocess.run('rm -r ' + gen_out, shell=True, check=True)
