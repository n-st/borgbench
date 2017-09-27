#!/usr/bin/env python3

import subprocess
import re
from tempfile import TemporaryDirectory
from timeit import default_timer as timer

def print_header():
    info_items = ['Compression setting', 'CHUNK_MIN_EXP', 'CHUNK_MAX_EXP', 'CHUNK_HASH_MASK_BITS', 'Original size', 'Compressed size', 'Deduplicated size', 'Unique chunks', 'Total chunks', 'Duration [seconds]']
    print(';'.join(map(str, info_items)))

# single benchmark run
def runConfig(inputdir, compression="none", chunker_params=None):
    """ If given, chunker_params should be a tuple of (cmin, cmax, cavg). """

    with TemporaryDirectory(prefix='borgbench_') as tempdir:
        subprocess.call(["borg", "init", "-e", "none", tempdir])

        commandline = ["borg"]
        commandline += ["create", tempdir+"::test", "-v", "-s", "-C", compression]
        if chunker_params:
            commandline += ["--chunker-params=%d,%d,%d,4095" % (chunker_params)]
        commandline += [inputdir]

        start = timer()
        proc = subprocess.Popen(commandline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = proc.stderr.read()
        duration = timer() - start

        # parse output
        m = re.match(".*This archive: +(\d+\.?\d+ ..) +(\d+\.?\d+ ..) +(\d+\.?\d+ ..).*Chunk index: +(\d+) +(\d+)", str(output))
        if m:
            original_size, compressed_size, dedup_size, unique_chunks, total_chunks = re.match(1, 2, 3, 4, 5)
            info_items = [compression, cmin, cmax, cavg, original_size, compressed_size, dedup_size, unique_chunks, total_chunks, duration]
            print(';'.join(map(str, info_items)))

        else:
            print("Error")

# Directory with input data that will be added to Borg repos with different
# compression settings.
# For speed reasons, this should be a tmpfs.
testData = "/tmp/borgbench/testdata"

compression_settings = [
    "none",
    "lz4",
    "zlib,0",
    "zlib,1",
    "zlib,2",
    "zlib,3",
    "zlib,4",
    "zlib,5",
    "zlib,6",
    "zlib,7",
    "zlib,8",
    "zlib,9",
    "lzma,0",
    "lzma,1",
    "lzma,2",
    "lzma,3",
    "lzma,4",
    "lzma,5",
    "lzma,6",
    "lzma,7",
    "lzma,8",
    "lzma,9",
]

chunker_settings = [
    (8, 12, 10),
    (9, 14, 10),
    (8, 13, 11),
    (9, 17, 11),
    (9, 14, 12),
    (10, 17, 12),
    (10, 15, 13),
    (11, 18, 13),
    (11, 16, 14),
    (12, 20, 14),
    (12, 19, 15),
    (13, 20, 16),
    (14, 21, 17),
    (14, 20, 18),
    (15, 21, 19),
    (16, 22, 20),
    (20, 23, 21),
    (18, 18, 18),
]

print_header()

for params in chunker_settings:
    # Deduplication is done based on the contents of chunks *before* they are
    # compressed, so we don't need to use any compression during the chunker
    # benchmark.
    runConfig(testData, chunker_params=params)

for comp in compression_settings:
    runConfig(testData, comp)
