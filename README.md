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

borg 1.1
--------

Borg 1.1 introduced a new option to produce output in JSON format. Besides
providing a stable interface, this also finally provides byte-accurate
information about the size of archives and repositories (which is useful to see
small differences in compression ratio on large repositories, which would have
been lost to rounding until now).

Borgbench has been adapted to support both the old "human-readable" and the new
JSON format.  
To keep things simple, it checks whether `borg help create` mentions the
`--json` option (once, at launch), then selects the borg invocation options and
parser method accordingly.  
If the JSON format is not supported, a warning is printed to stderr (which
shouldn't be a problem since the actual CSV results are printed to stdout, so
they can be easily separated from any error messages).

Borg 1.1 also introduced a lower boundary for the chunker max_size based on the
configured min_size, so two chunker configurations had to be dropped from the
benchmark (though they were rather exotic anyway).

Attribution
-----------

[Original idea and implementation][1] by Michael Gajda (dragetd), [improved and
modularised][2] for general use by Nils Steinger (n-st).

Test results (in the `chunking` and `compression` subdirectories) provided by
Michael Gajda.

[1]: https://github.com/dragetd/borgbench
[2]: https://github.com/n-st/borgbench
