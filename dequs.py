from __future__ import print_function
import sys
import os
import math
import random
import argparse
import re
from smt2 import convert_to_smt
from dqdimacs import convert_to_qdimacs 


def convert_sl_to_dqbf(file):
	filename = file.split(".sl")[0]
	convert_to_smt(file,filename+".smt2")
	convert_to_qdimacs(filename+".smt2", filename+".dqdimacs")

	print("please find corresponding dqdimacs file:", filename+".dqdimacs")




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help="sl file", dest='file')
    args = parser.parse_args()
    convert_sl_to_dqbf(args.file)