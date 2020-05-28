#!/usr/bin/env python3

import itertools
import pathlib
import os
import numpy as np
from scipy.interpolate import CubicSpline


# See AHF.input-example and user's guide for documentations
ahf_param_template = \
"""[AHF]
anifac_x = {anifac_x}
anifac_y = {anifac_y}
anifac_z = {anifac_z}
ic_filename       = {snapshot_path}
ic_filetype       = 61
outfile_prefix    = ahf_output
LgridDomain       = 64
LgridMax          = 16777216
NperDomCell       = 2.0
NperRefCell       = 2.5
VescTune          = 1.5
NminPerHalo       = 20
RhoVir            = 1
Dvir              = 200
MaxGatherRad      = 5.0
LevelDomainDecomp = 6
NcpuReading       = 8

[GADGET]
GADGET_LUNIT      = 1.
GADGET_MUNIT      = 1e10
"""


ahf_slurm_script = \
"""#!/bin/bash

#SBATCH --job-name=ahf
#SBATCH --output=%x-%j.out
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=kazuyuki.akitsu@ipmu.jp

#SBATCH --partition=general

#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --time=02:00:00

hostname; pwd; date

module purge
module load slurm
module load gcc openmpi

srun --mpi=pmi2 -n $SLURM_CPUS_ON_NODE ~/AHF/bin/AHF ahf.input

~/AHF/bin/ahf_reduce.py

date
"""


snapshots_to_scale_factors = {
    '006': 1,
    '005': 0.666667,
    '004': 0.5,
    '003': 0.333333,
    '002': 0.25,
    '001': 0.125,
    '000': 0.0625,
}


def get_anifac(a, dc_type):
    """ a_i / a
    """
    path = f'/home/yinli/csit/analysis/Aniss/Aniss_planck2015_{dc_type}_z200'
    aniss = np.loadtxt(path, unpack=True)

    anifac = {}
    for dim, key in zip(range(1, 4), ['anifac_x', 'anifac_y', 'anifac_z']):
        spline = CubicSpline(aniss[0], aniss[dim])
        anifac[key] = 1 + spline(a)

    return anifac  # dict with keys: anifac_{x, y, z}


if __name__ == '__main__':
    root = '/mnt/sdceph/users/yinli/csit/planck2015'

    boxsize = 1000

    sim_type = 'ASMTH6'  # or use empty string '' to skip this level in dir hierarchy

    dc_types = ['iso', 'mmp003', 'ppm003']

    #seeds = range(1991, 2020)  # all seeds
    seeds = [1991]        # or select some

    #snapshots = ['{:03d}'.format(i) for i in range(7)]  # all snapshots
    snapshots = ['006']                           # or select some

    for dc_type, seed, snapshot in itertools.product(dc_types, seeds, snapshots):
        a = snapshots_to_scale_factors[snapshot]

        anifac = get_anifac(a, dc_type)

        sim_dir = f'{root}/{boxsize}/{seed}/{dc_type}/{sim_type}'
        snapshot_path = f'{sim_dir}/nbody/snapdir_{snapshot}/snap_{snapshot}.'
        job_dir = f'{sim_dir}/halos'
        pathlib.Path(job_dir).mkdir(exist_ok=True)

        with open(f'{job_dir}/ahf.input', 'w') as f:
            f.write(ahf_param_template.format(**anifac, snapshot_path=snapshot_path))

        with open(f'{job_dir}/ahf.slurm', 'w') as f:
            f.write(ahf_slurm_script)

        os.chdir(job_dir)
        os.system('sbatch ahf.slurm')
