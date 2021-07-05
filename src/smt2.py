#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Copyright (C) 2021 Priyanka Golia, Subhajit Roy, and Kuldeep Meel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''


from __future__ import print_function
import sys
import os
import math
import random
import argparse
import re



def convert_to_smt(slfile,smtfile):
	with open(slfile, 'r') as f:
		lines = f.readlines()
	f.close()
	content=''
	flag=0
	for line in lines:
		if line.startswith("(synth-fun"):
			pattern ="\(synth-fun(.*?)\("
			line = line.replace("(synth-fun","(declare-fun")
			varname_pattern="\(([a-z]*[A-Z]*[0-9]*)\s"
			varname = re.findall(varname_pattern, line)
			for var in varname:
				if var !="":
					line= line.replace("("+var,"")

			line=line.replace("Bool)","Bool")
			line=line.replace("))",")")
			if"(BitVec "in line:
				line = line.replace("(BitVec","(_ BitVec")
			content += line.strip("\n")+")\n"
			flag = 1
			continue
		if flag == 1:
			if "declare" in line or "define" in line or "constraint" in line:
				flag=0
		if flag == 0:
			if"(BitVec "in line:
				line= line.replace("(BitVec","(_ BitVec")
			if"declare-var "in line:
				line= line.replace("declare-var","declare-const")
			if "check-synth" in line:
				line= line.replace("check-synth","check-sat")
			if "constraint" in line:
				line = line.replace("constraint","assert")
			content += line
	f=open(smtfile,"w")
	f.write(content)
	f.close()
