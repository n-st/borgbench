borgbench
=========

Compares speed and efficiency of borgbackup compression and chunker settings.

Usage:

    ./borgbench.py /path/to/testdata

To produce accurate results for your use case, you need to provide your own
test data.  
Create a directory with a collection of files resembling what you'll be backing
up with borg later, then run this script with the test data directory as an
argument.

Ideally, you should store the test data on a tmpfs ("RAM disk") so the results
won't be skewed by your disk speed.

The script will copy your test data to the system's temporary storage, so make
sure there's enough space in there to temporarily store your entire set of test
data.

---

Original idea and implementation by Michael Gajda (dragetd), improved and
modularised for general use by Nils Steinger (n-st).

Test results in this repo provided by Michael Gajda.
