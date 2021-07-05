## Program Synthesis as Dependency Quantified Formula Modulo Theory
DeQuS takes a SyGuS instance in bit vector theory and convert it to DQBF instance. 

To read more about DeQuS, have a look at [IJCAI-21 paper](https://arxiv.org/pdf/2105.09221.pdf)

## Requiremnents to run

* Python 2.7+

To install the required libraries, run:

```
python -m pip install -r requirements.txt
```
DeQuS depends on:
[z3](https://github.com/Z3Prover/z3) to convert to DQBF.

## Installation

``` 
git clone https://github.com/meelgroup/DeQuS
```
Install specific version of z3 in trace generating mode and have z3 binding in python
```
git clone https://github.com/Z3Prover/z3.git
cd z3
git checkout a97bc65af460e6b796b925dbbe667904c3fa431c
git apply ../DeQuS/z3-tactic-mapping.patch
python scripts/mk_make.py -t --python
cd build
make
sudo make install
```
```
cd ../../DeQuS
python dequs.py --file <input sl file>
```
## Example of use

```
python dequs.py --file find_inv_bvsge_bvadd_4bit.sl
```
It should generate following output:

```
There are/is 1 functions/function to synthesis
details as follow:
-----------------------
function name:  inv-0
Arguments ['2', '7', '14', '19', '4', '10', '16', '22']
Output ['1', '8', '13', '20']
--------------------------------
  Generated 61 clauses
Writing header
please find corresponding dqdimacs file: find_inv_bvsge_bvadd_4bit.dqdimacs

```

## Benchmarks

A single benchmark ` ` is provide. We used SyGuS bit vector theroy benchmarks, avaiable [here] (https://github.com/SyGuS-Org/benchmarks/tree/master/lib/General_Track)

## Issues, questions, bugs, etc.
Please click on "issues" at the top and [create a new issue](https://github.com/meelgroup/manthan/issues). All issues are responded to promptly.

## How to Cite
```
@inproceedings{GRM21,
author={Golia, Priyanka and  Roy, Subhajit and  Meel, Kuldeep S.},
title={Program Synthesis as Dependency Quantified Formula Modulo Theory},
booktitle={Proceedings of International Joint Conference on Artificial Intelligence (IJCAI)},
month={7},
year={2021}
}
```
## Contributors
* Priyanka Golia (pgoila@cse.iitk.ac.in)
* Subhajit Roy (subhajit@cse.iitk.ac.in)
* Kuldeep Meel (meel@comp.nus.edu.sg)

