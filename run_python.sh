#!/bin/bash
#SBATCH --account=project_2010938
#SBATCH --time=00:10:00
#SBATCH --mem=2G

module load python-data

python3 recoding.py
