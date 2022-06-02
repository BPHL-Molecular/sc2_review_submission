#!/usr/bin/env python

#Author: Sarah Schmedes
#Email: sarah.schmedes@flhealth.gov

'''
This script will generate a pairwise alignment between SC2 reference and an input consensus assembly
and identify variants.
'''

import os
import sys
import subprocess
import argparse
import os.path

#Parse arguments, get path for fastqs, primer version
parser = argparse.ArgumentParser(usage='sc2_pairwise_align_variant.py [options]')
parser.add_argument('--sample', help='sample ID')
parser.add_argument('--fasta', help='path to consensus assembly')
parser.add_argument('--ref', help='path to reference genome')

if len(sys.argv[1:]) == 0:
    parser.print_help()
    parser.exit()

args = parser.parse_args()
sample = args.sample
fasta = os.path.abspath(args.fasta)
ref = os.path.abspath(args.ref)
cwd = os.getcwd() + '/'

#Run minimap2 on consensus assembly
subprocess.run('mkdir minimap2', shell=True, check=True)
subprocess.run('cd minimap2 && singularity exec -B $(pwd):/data /apps/staphb-toolkit/containers/minimap2_2.18.sif minimap2 -cx asm20 -t1 --cs ' + ref + ' ' + cwd + sample + '.consensus.fa > ' + sample + '.paf', shell=True, check=True)
subprocess.run('cd minimap2 && singularity exec -B $(pwd):/data /apps/staphb-toolkit/containers/minimap2_2.18.sif sort -k6,6 -k8,8n ' + sample + '.paf > ' + sample + '.srt.paf', shell=True, check=True)
subprocess.run('cd minimap2 && singularity exec -B $(pwd):/data /apps/staphb-toolkit/containers/minimap2_2.18.sif paftools.js call -l 200 -L 200 -q 30 ' + sample + '.srt.paf > ' + sample + '.var.txt', shell=True, check=True)
