#!/bin/bash
mkdir scp_files
rm -rf scp_files/*
tar zcvf paper_work.tar.gz arch/arch_inst/*
mv paper_work.tar.gz scp_files/
mv config.txt scp_files/
# scp -r -P 22 -o ProxyJump llwang@10.134.141.161 -p 22 scp_files llwang@172.16.10.11:~/yhshen/upload
