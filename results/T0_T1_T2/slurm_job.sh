#!/bin/bash

#SBATCH -p rome,genoa
#SBATCH -t 01:00:00
#SBATCH -c 16

source ~/.bashrc
conda activate geo
export PYTHONUNBUFFERED=TRUE

ROOT1=/projects/0/nwo2021025/archive
ROOT2=/projects/0/uuesm2/archive
OUT=./data

archives=(
  $ROOT1/lres_b.e10.B2000_CAM5.f09_g16.feedforward.001
  $ROOT1/lres_b.e10.B2000_CAM5.f09_g16.feedforward_2050.001
  $ROOT1/mres_b.e10.B2000_CAM5.f05_t12.001
  $ROOT1/B.E.13.B1950TRC5.ne30g16.ihesp24.control2020.01
  $ROOT1/B.E.13.B1950TRC5.ne30g16.ihesp24.sai2020.01
  $ROOT1/B.E.13.B1950TRC5.ne30g16.ihesp24.sai2050.01
  $ROOT1/B.E.13.BRCP85C5.ne30g16.feedback.006
  $ROOT1/B.E.13.BRCP85C5.ne30g16.sai.fb.2020.001
)

for archive in ${archives[@]}
do
  outfile=$OUT/$(basename $archive).nc
  if [ -f $outfile ]; then
    echo "$outfile already exists, skipping."
  else
    echo $(basename $archive)
    python temperaturegradients.py $archive/atm/hist/*.h0.*.nc $outfile
  fi
done
