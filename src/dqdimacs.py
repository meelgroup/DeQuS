## motivated by https://github.com/MarkusRabe/smtlib2qdimacs.

   
import z3
from z3  import *
import math
import argparse
import os
import numpy as np
import re


class AstRefKey:
    def __init__(self, n):
        self.n = n
    def __hash__(self):
        return self.n.hash()
    def __eq__(self, other):
        return self.n.eq(other.n)
    def __repr__(self):
        return str(self.n)

def askey(n):
    assert isinstance(n, AstRef)
    return AstRefKey(n)




def encode_literal(var_mapping, Tseitin_vars, max_var, l,all_var_mapping):
    var = None
    if is_not(l):
        var = l.children()[0]
        lit_str = '-'
    else:
        var = l
        lit_str = ''
    
    if var.get_id() not in var_mapping:
        max_var += 1
        Tseitin_vars.append(max_var)
        var_mapping[var.get_id()] = max_var
        all_var_mapping[str(var)] = str(max_var)
            
    lit_str += str(var_mapping[var.get_id()]) + ' ' 
    

    return max_var, lit_str, all_var_mapping



def find_mapped_variable(bool_var,bitvec_var,function_name,function_inst):
    with open(".z3-trace", 'r') as f:
        trace_string = f.readlines()
    f.close()
    variable_mapping={}
    function_mapping={}
    count={}
    flag=0
    for line in trace_string:
        if line.startswith("mapping"):
            if "bool" in line:
                mapped_var=line.strip(" ").split(":")[2].split(' ')[1:]
                mapped_var[len(mapped_var)-1]=mapped_var[len(mapped_var)-1].strip(")\n")
                if mapped_var in function_mapping.values():
                    continue
                else:
                    var=line.split(':')[1]
                    var_func=var.split('!')[0]
                    if var_func in function_name:
                        if var_func not in count.keys():
                            count[var_func]=0
                        else:
                            count[var_func] +=1
                        function_mapping[var_func+"-"+str(count[var_func])]=mapped_var
            else:
                flag=1
                string = line.strip(" ").strip("\n")+" "
            continue
        
        if flag == 1:
            if line.startswith('--'):
                flag=0
                mapped_var=string.strip(" ").split(":")[2].split(' ')[1:]
                mapped_var[len(mapped_var)-1]=mapped_var[len(mapped_var)-1].strip(")\n")
                var=string.split(':')[1]
                if var in bitvec_var: 
                    variable_mapping[var]=mapped_var
                    continue
                var_func=var.split('!')[0]
                if var_func in function_name:
                    if var_func not in count.keys():
                        count[var_func]=0
                    else:
                        count[var_func] +=1
                    function_mapping[var_func+"-"+str(count[var_func])]=mapped_var
            else:
                string += line.strip(" ").strip("\n")+" "

    return function_mapping, variable_mapping



def writeQDIMACS(outfile, g, bool_var,bitvec_var,function_name,function_inst):
    t = Then('simplify', 'ackermannize_bv','bit-blast','tseitin-cnf')
    subgoal = t(g)
    function_mapping, variable_mapping=find_mapped_variable(bool_var,bitvec_var,function_name,function_inst)
    
    all_var_mapping = {}
    max_var = 0
    var_mapping = {}
    Tseitin_vars = []
    clause_num = 0
    matrix = []


    for c in subgoal[0]:
        clause_num += 1
        if clause_num % 10000 == 0:
            print('  {} clauses'.format(clause_num))
        if is_or(c):
            clause = ''
            for l in c.children(): 
                max_var, lit_str, all_var_mapping = encode_literal(var_mapping, Tseitin_vars, max_var, l,all_var_mapping)
                clause += lit_str
            matrix.append(clause)
        else:
            max_var, lit_str, all_var_mapping = encode_literal(var_mapping, Tseitin_vars, max_var, c,all_var_mapping)
            matrix.append(lit_str)
    
   

    each_function_e = {}
    each_function_a = {}
    a_var_list = []
    e_var_list = []
    for function in function_inst.keys():
        each_function_e[function] = []
        each_function_a[function] = []
        map_var_list= function_mapping[function]
        for map_var in map_var_list:
            if map_var in all_var_mapping.keys():
                each_function_e[function].append(all_var_mapping[map_var])
                e_var_list.append(str(all_var_mapping[map_var]))
            else:
                print("problem with function mapping")
                exit(1)
        
        function_arg = function_inst[function].split(" ")
        
        for argu in function_arg:
            if argu in variable_mapping.keys():
                map_var_list=variable_mapping[argu]
                for map_var in map_var_list:
                    if map_var in all_var_mapping.keys():
                        each_function_a[function].append(all_var_mapping[map_var])
                        a_var_list.append(str(all_var_mapping[map_var]))
                    else:
                        print("problem with variable mapping")
                        exit(1)
            else:
                if argu in all_var_mapping.keys():
                    each_function_a[function].append(all_var_mapping[argu])
                    a_var_list.append(str(all_var_mapping[argu]))
                else:
                    print("problem with bool variable mapping")
    
    a_var_list=np.array(a_var_list)
    _, idx = np.unique(a_var_list, return_index=True)

    a_var = "a "+" ".join(a_var_list[np.sort(idx)])+" 0\n"

    e_var_list = np.array(e_var_list)

    _, idx = np.unique(e_var_list, return_index=True)

    e_var = "e "+" ".join(e_var_list[np.sort(idx)])+" 0\n"
    
        
    
    print("There are/is %s functions/function to synthesis" %(str(len(function_name))))
    print("details as follow:")
    print("-----------------------")
    
    write_str_func=''
    for function in function_inst.keys():
        
        print("function name: ",function)
        print("Arguments",each_function_a[function])
        print("Output",each_function_e[function])
        for e in each_function_e[function]:
            write_str_func += "d %s %s 0\n" %(str(e),' '.join([str(a) for a in each_function_a[function]]))
        print("--------------------------------")

    print('  Generated ' + str(clause_num) + ' clauses')
    print('Writing header')
    
    textFile = open(outfile, "w")
    textFile.write('p cnf {} {}\n'.format(max_var,clause_num))
    textFile.write(a_var)
    textFile.write(write_str_func)
    textFile.write('0\n'.join(matrix))
    textFile.write("0 \n")
    textFile.close()



def parse_smtfile(inputfile):
    with open(inputfile, 'r') as f:
        smt2string = f.read()
    f.close()
    free_variables = re.findall('\(declare-fun (\w+) \(\) (Bool)|\(declare-fun (\w+) \(\) \(\_ BitVec (\d+)\)', smt2string)
    free_variables += re.findall('\(declare-const (\w+) (Bool)|\(declare-const (\w+) \(\_ BitVec (\d+)\)', smt2string)
    
    bool_var=[]
    bitvec_var={}
    
    for idx, (a,b,x,y) in enumerate(free_variables): 
        assert(a != '' or x != '')
        if a != '':
            assert(b == 'Bool')
            bool_var.append(a)
        else:
            bitvec_var[x]=y

    function_name=[]
    function_arg={}
    lines=smt2string.split("\n")
    for line in lines:
        if line.startswith("(declare-fun"):
            pattern="\(declare-fun(.*?)\("
            name=re.search(pattern, line).group(1).strip(" ")
            function_name.append(name)
            function_arg[name]=[]
            continue

    function_inst={}
    
    for function in function_name:
        itr=0
        for line in lines:
            if line.startswith("(declare-fun"):
                continue
            if function+" " in line:
                pattern="\(\s*"+function+"(.*?)\)"
                args_list=re.findall(pattern,line)
                for args in args_list:
                    args=args.strip(" ").strip("(").strip(")")
                    if function in function_arg.keys():
                        if args in function_arg[function]:
                            continue
                        else:
                            function_arg[function].append(args)
                            function_inst[function+"-"+str(itr)]=args
                            itr=itr+1



    return bool_var,bitvec_var,function_name,function_inst

def convert_to_qdimacs(inputfile,outfile):
    
    bool_var,bitvec_var,function_name,function_inst = parse_smtfile(inputfile)
    F = parse_smt2_file(inputfile)
    print("done parsring")
    g = Goal()
    g.add(F)
    set_param(proof=False)
    set_param(unsat_core=False)
    set_param(verbose=100000)
    enable_trace('simplifier')
    enable_trace('after_simplifier_detail')
    enable_trace('bit_blaster')
    enable_trace('tseitin_cnf')
    enable_trace('ackermannize_bv')
    enable_trace('ackermannize')
    enable_trace('propagate_values')
    enable_trace('after_simplifier_detail')

    writeQDIMACS(outfile, g, bool_var, bitvec_var,function_name, function_inst)




