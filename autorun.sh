#!/usr/bin/env bash
export EDITOR=vim
export PYTHONIOENCODING=utf8

now=$(date +'%T/%m/%d/%Y')
echo "Current time : $now"

/Users/yipengm/miniconda3/envs/soup3/bin/python /Users/yipengm/PycharmProjects/AMZ_LIB/webfront_collect_input.py -d $now -m BH
/Users/yipengm/miniconda3/envs/soup3/bin/python /Users/yipengm/PycharmProjects/AMZ_LIB/webfront_collect_input.py -d $now -m MM
/Users/yipengm/miniconda3/envs/soup3/bin/python /Users/yipengm/PycharmProjects/AMZ_LIB/webfront_collect_input.py -d $now -m PB
/Users/yipengm/miniconda3/envs/soup3/bin/python /Users/yipengm/PycharmProjects/AMZ_LIB/webfront_collect_input.py -d $now -m PS
