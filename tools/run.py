#!/usr/bin/env python3

import multiprocessing

from itaxotools.DNAconvert import main

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
