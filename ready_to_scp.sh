#!/bin/bash
mkdir scp_files
cp -vr arch/arch_inst scp_files/
mv scp_files/arch_inst scp_files/paper_work
mv config.txt scp_files/
scp -r -P 22 -o ProxyJump llwang@10.134.141.161 -p 22 scp_files llwang@172.16.10.11:~/yhshen/upload
