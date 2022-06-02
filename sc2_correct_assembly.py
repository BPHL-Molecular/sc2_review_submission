#!/usr/bin/env python

#Author: Sarah Schmedes
#Email: sarah.schmedes@flhealth.gov

'''
This program is designed to mask designated sites in a fasta file. This was developed to mask
sites of PCR/sequencing errors in SARS-CoV-2 consensus assemblies generated using ivar after review with NCBI's VADR prior
to submission.
'''

import os
import sys
import subprocess
import argparse
import os.path

#Parse arguments, get path for fastqs, primer version
parser = argparse.ArgumentParser(usage='sc2_correct_assembly.py [options]')
parser.add_argument('--sample', help='sample ID')
parser.add_argument('--bam', help='path to bam used as mpileup input')
parser.add_argument('--ref', help='path to reference genome')
parser.add_argument('--ref_accession', help='reference accession that appears in mpilup file')
parser.add_argument('--sites_to_mask', help='comma separated list of sites to mask, ref:num_of_bases (e.g., 28250:1,29475:4)')

if len(sys.argv[1:]) == 0:
    parser.print_help()
    parser.exit()

args = parser.parse_args()
sample = args.sample
bam = os.path.abspath(args.bam)
ref = os.path.abspath(args.ref) 
mask_input = args.sites_to_mask
cwd = os.getcwd() + '/'

#Construct mask_site variable for grep
mask_site = ''
mask_list = mask_input.split(',')
for m in mask_list:
    mask_pos = m.split(':')
    mask_start = int(mask_pos[0])
    num_mask_sites = int(mask_pos[1])
    for n in range(mask_start,(mask_start + num_mask_sites)):
        mask_site = mask_site + args.ref_accession + '[[:space:]]' + str(n) + '\|'
mask_site = mask_site[:-2]
    

#Generate corrected consensus assembly
subprocess.run('mkdir corrected_assembly', shell=True, check=True)
subprocess.run('cd corrected_assembly && singularity exec -B $(pwd):/data /apps/staphb-toolkit/containers/samtools_1.12.sif samtools mpileup -A -d 1000000 --reference ' + ref  + ' -B -Q 0 ' + bam + ' | grep -v "' + mask_site + '" | singularity exec -B $(pwd):/data /apps/staphb-toolkit/containers/ivar_1.3.1.sif ivar consensus -t 0 -m 10 -n N -p ' + sample + '.consensus', shell=True, check=True)
subprocess.run('cd corrected_assembly && sed -i \'s/^>.*/>' + sample + '/\' ' + sample + '.consensus.fa', shell=True, check=True)

#Run minimap2 on corrected consensus assembly
subprocess.run('mkdir corrected_assembly/minimap2', shell=True, check=True)
subprocess.run('cd corrected_assembly/minimap2 && singularity exec -B $(pwd):/data /apps/staphb-toolkit/containers/minimap2_2.18.sif minimap2 -cx asm20 -t1 --cs ' + ref + ' ' + cwd + 'corrected_assembly/' + sample + '.consensus.fa > ' + sample + '.paf', shell=True, check=True)
subprocess.run('cd corrected_assembly/minimap2 && singularity exec -B $(pwd):/data /apps/staphb-toolkit/containers/minimap2_2.18.sif sort -k6,6 -k8,8n ' + sample + '.paf > ' + sample + '.srt.paf', shell=True, check=True)
subprocess.run('cd corrected_assembly/minimap2 && singularity exec -B $(pwd):/data /apps/staphb-toolkit/containers/minimap2_2.18.sif paftools.js call -l 200 -L 200 -q 30 ' + sample + '.srt.paf > ' + sample + '.var.txt', shell=True, check=True)
