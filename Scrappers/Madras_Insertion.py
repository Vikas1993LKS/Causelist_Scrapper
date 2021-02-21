# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 17:37:49 2020

@author: Vikas.gupta
"""

with open("Output.txt", "r") as f:
    data = f.read()
    
    
for entry in data:
    print (entry)