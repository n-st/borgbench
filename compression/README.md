# borgbench

This repository will host a script to test the different chunking settings of borgbackup and document any conclusion in this README

The script borgbench.py is a very simple hack that you can pass the string for the '--compression' setting as the first argument. It will output the chunking-settings, original size, compressed size, deduplicated size, unique and total chunks.
