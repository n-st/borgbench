# borgbench

A crude python script to benchmark borg (https://github.com/borgbackup/borg/) with different settings for compression and deduplication.
It is a very simple script that creates an archive under /tmp/borgbench/ from /tmp/borgbench/testdata.

* chunking: Test of differenct chunking settings vs compressed and deduplicated reduction ratio
  You can pass the string for the '--compression' setting as the first argument. It will output the chunking-settings, original size, compressed size, deduplicated size, unique and total chunks.
* compression
  Uses default chunking and tries compression level 1-9, also outputting the time the creation of the archive took.
