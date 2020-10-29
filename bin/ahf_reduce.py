#!/usr/bin/env python3

import glob
import numpy as np


def reduce_halos(job_dir='.'):
    hfiles = glob.glob(f'{job_dir}/*.AHF_halos')

    hcat = []
    for f in hfiles:
        hcat.append(np.genfromtxt(
            f,
            dtype=[('hostHalo', 'i8'), ('Mvir', 'f8'), ('npart', 'i8'),
                   ('Eax', 'f8'), ('Eay', 'f8'), ('Eaz', 'f8'),
                   ('Ebx', 'f8'), ('Eby', 'f8'), ('Ebz', 'f8'),
                   ('Ecx', 'f8'), ('Ecy', 'f8'), ('Ecz', 'f8'),
                   ('cNFW', 'f8')],
            usecols=(1, 3, 4) + tuple(range(26, 35)) + (42,),
        ))
    hcat = np.concatenate(hcat)

    hcat = hcat[hcat['hostHalo'] == 0]  # remove subhalos

    hcat = hcat[list(hcat.dtype.names[1:])]  # remove hostHalo column

    hcat = np.sort(hcat, order='Mvir')[::-1]  # decreasing order in mass

    np.savetxt(f'{job_dir}/AHF_halos.txt', hcat)


if __name__ == '__main__':
    reduce_halos()
