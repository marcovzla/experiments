#!/bin/sh
sed 's/[^0-9\. OX]//g' < train.txt > processed_data/train_con.txt
sed 's/[^0-9\. OX]//g' < test.txt > processed_data/test_con.txt
