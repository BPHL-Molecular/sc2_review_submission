# Accessory scripts for SARS-CoV-2 assembly review, assembly correction (N-padding), and submission to GISAID and NCBI Genbank.

FL BPHL submits all passing SARS-CoV-2 consensus assemblies to [NCBI Genbank](https://submit.ncbi.nlm.nih.gov/sarscov2/) and [GISAID](https://gisaid.org/). This repository contains scripts to automate fasta file formatting for submissions and scripts to review and correct assemblies that contain sequencing/pcr artifacts prior to submission.

## sc2_fasta_for_sub.py
### Usage
sc2_fasta_for_sub.py will convert individual SC2 assembly fasta files into a single, properly formatted multi-fasta file that can be used for submission to NCBI Genbank and GISAID. This script will rename all fasta headers to public sample names that meet required SC2 viral naming schemes, as provided by the user in a two-column, tab-separated metadata file containing the original sample name and the new sample name. 

```
cp /path/to/fastas/for/sub/*.fasta 
python sc2_fasta_for_sub.py --assem_dir assemblies/ --meta <metadata_file> --state_name <FL_BPHL>
```

## Scripts for SC2 assembly/variant manual review and correction (N-padding)

The current versions below will run only on [HiPerGator](https://www.rc.ufl.edu/about/hipergator/)(HPG) using local Singularity containers for each process.

## sc2_pairwise_align_variant.py
### Usage
sc2_pairwise_align_variant.py runs [minimap2[(https://github.com/lh3/minimap2) in whole-genome alignment mode to perform a pairwise alignment between the SC2 reference and your generated consensus assembly. The output helps you visualize incorporated variants and/or artifacts when reviewing samples flagged by public repositories.
```
python sc2_pairwise_align_variant.py --sample <sample_id> --fasta <consensus_assembly> --ref <reference.fasta>
```
 
## sc2_correct_assembly.py
### Usage
sc2_correct_assembly.py will regenerate your consenus assembly while masking sites designated by the user to pad with Ns. This allows the user to remove incorporated artifacts from the assembly, so the fasta can be resubmitted to public repositories. Main processes include [iVar](https://github.com/andersen-lab/ivar) and [minimap2[(https://github.com/lh3/minimap2). Outputs include a corrected fasta and a pairwise whole-genome alignment to confirm the correct sites have been masked.
```
python sc2_correct_assembly.py --sample <sample_id> --bam <sample_bam> --ref <reference.fasta> --ref_accession <reference_accession> --sites_to_mask <ref:num_of_bases,ref:num_of_bases> 
```

