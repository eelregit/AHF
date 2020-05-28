#!/usr/bin/env python3

import glob
import numpy as np


def reduce_halo_masses(job_dir='.'):
    hfiles = glob.glob(f'{job_dir}/*.AHF_halos')

    hcat = np.concatenate([
        np.genfromtxt(f, dtype=[('hostHalo', 'i8'), ('Mvir', 'f8')], usecols=(1, 3))
            for f in hfiles
    ])

    hcat = hcat[hcat['hostHalo'] == 0]

    hmasses = hcat['Mvir']

    np.savetxt(f'{job_dir}/AHF_halos.txt', hmasses)


if __name__ == '__main__':
    reduce_halo_masses()
