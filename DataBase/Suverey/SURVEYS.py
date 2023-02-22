#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 11:24:25 2021

@author: felipe
"""
#LOAD LIBRARIES
import pandas as pd
from glob import glob
import re
from sqlalchemy import create_engine
from os import popen

import webbrowser
import os
import time

for i in range(1000000):
    os.system('rm ./*Prisma*')
    #consentimiento
    webbrowser.open('https://docs.google.com/spreadsheets/d/e/2PACX-1vTe_RcoU3dMfzus8yqDB7B5VMjpoAA161ZOTZ9BqlrQYrLRtlDaHSiHCQzEZPWy2-uG7oGAw6GmADTH/pub?gid=1775209806&single=true&output=csv')  # Go to example.com
    #healt
    webbrowser.open('https://docs.google.com/spreadsheets/d/e/2PACX-1vRUqrKnbeE3BPZfR4X4h4PzbOy4Cp-9qg1tnkp9J7nOiNSLe-nKWpnePSLIRAP3_co84WDQ3DblWzjS/pub?gid=852451627&single=true&output=csv')
    #kit
    webbrowser.open('https://docs.google.com/spreadsheets/d/e/2PACX-1vRHCBTy3QvvezFB9Hi5ll-A4ZgFhA2uYFHhZkuXWaBC5M7RHNfnOef_nS4TehduRkq2xA8flpTl_lft/pub?gid=1055847366&single=true&output=csv')
    time.sleep(5.4)
    os.system('mv /home/tet/Downloads/*Prisma* ./ ')
    
    
    #LOAD SURVEYS
    samples=glob('*')
    r = re.compile("Prisma*")
    samples = list(filter(r.match, samples)) # Read Note
    
    #ITERATION GENERATION OF DATABASES FOR EACH ONE
    for i in samples:
        dt=pd.read_csv(f"./{i}",header=None)
        col=dt.shape[1]
        buck=list()
        for e in range(0,col):
            a=e+1
            con=f"QST-{a}"
            buck.append(con)
            
        dt.columns = [buck]
    
        engine = create_engine("mysql+pymysql://{user}:{pw}@localhost/{db}"
                               .format(user="root",
                                       pw="omicamxx",
                                       db="OMICA"))
        
        
        dt.to_sql(con=engine, name=f'{i}', if_exists='replace')   
    hours=24
    time.sleep(60*60*hours)
