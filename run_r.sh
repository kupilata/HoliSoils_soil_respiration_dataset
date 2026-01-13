#!/bin/bash
#SBATCH --job-name=Rscript_job
#SBATCH --partition=small
#SBATCH --account=project_2010938
#SBATCH --time=00:10:00
#SBATCH --mem=2G
#SBATCH --output=slurm_%x_%A_%a.out

module load r-env/442

SCRATCHDIR=$LOCAL_SCRATCH

time Rscript moisture_joining.R

sacct -j $SLURM_JOB_ID --format=JobID,MaxRSS,Elapsed,ReqMem,State

echo "Job ended at: $(date)"

