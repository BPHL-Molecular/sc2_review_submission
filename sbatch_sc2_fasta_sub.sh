#!/bin/bash
#SBATCH --account=bphl-umbrella
#SBATCH --qos=bphl-umbrella
#SBATCH --job-name=fasta_format
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=ENTER EMAIL
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --time=1-00
#SBATCH --output=fasta_format.%j.out
#SBATCH --error=fasta_format.%j.err

module load apptainer

#Run script/command and use $SLURM_CPUS_ON_NODE 
python sc2_fasta_for_sub.py --assem_dir assemblies/ --meta <file_name> --state_name FL_BPHL
