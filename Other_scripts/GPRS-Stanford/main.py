#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 10:42:17 2021

@author: Marco A. Nava (marco.nava[at]galatea.bio)

Usage: run_model.py [-hap] [-d ROUTE] [-s STR] [-f FILE ...] [-o ROUTE] [-m NAME ...]

-h        show this help
-d ROUTE  route for the input folder
-f FILE   route(s) for the input file(s)
-o ROUTE  route for the output
-m FILE   run specified models
-s STR    identifiable stamp for the output
-a        run all models

Have a nice day :)

"""
# =============================================================================
# INDEX
# =============================================================================
# =============================================================================
#   0.- Importing libraries
#   1.- Function to match the alleles in the model with the ones in the sample
#   2.- Function to join the model and sample
#   3.- Function to i mpute the missing variant (posibbly deprecated?)
#   4.- Function to run the model
#   5.- Function auxiliar of main to run the model according to args
#   6.- Main function of the program
# =============================================================================


# =============================================================================
# 0.- Importing necesary libraries
# =============================================================================
import allel
import numpy as np
import pandas as pd
from sys import exit
from glob import glob
from docopt import docopt

from scripts.func import concatArrays, joins_per_file

# =============================================================================
# 1.- Matching the ALT alleles in the model and vcf to the correct positions
# =============================================================================
def references_match(model, samples, x_ind, y_ind):
    modelREFALT = model[['REF','ALT']]
    vcfREFALT = pd.DataFrame(
        np.column_stack((samples['variants/REF'],samples['variants/ALT'])),
        columns=['REF','ALT0','ALT1','ALT2'])

    modelREFALT = modelREFALT.iloc[y_ind]
    vcfREFALT = vcfREFALT.iloc[x_ind]

    unmatched=[]
    wheres = [vcfREFALT.loc[i,].tolist().index(modelREFALT.loc[j,'ALT'])
              if modelREFALT.loc[j,'ALT'] in vcfREFALT.loc[i,].tolist()
              else unmatched.append((i,j))
              for i,j in zip(x_ind,y_ind)]

    wheres=[i for i in wheres if i is not None]
    return wheres, unmatched

# =============================================================================
# 2.- Left join the model and the vcf file
# =============================================================================
def variantJoint(model,samples):
    ChromPosModel = concatArrays(model['CHROM'].values,
                                 model['POS'].values)
    ChromSamples = np.array(list(map(lambda x: x.strip('chr'),
                                     samples['variants/CHROM'])))
    ChromPosSamples = concatArrays(ChromSamples,samples['variants/POS'])

    _, x_ind, y_ind = np.intersect1d(ChromPosSamples, ChromPosModel,
                                     return_indices=True)

    wheres, unmatched = references_match(model, samples, x_ind, y_ind)
    x_ind=list(set(x_ind)-{i[0] for i in unmatched})
    y_ind=list(set(y_ind)-{i[1] for i in unmatched})

    slice0 = samples['calldata/GT'][:,:,0][x_ind,:]
    slice1 = samples['calldata/GT'][:,:,1][x_ind,:]
    if len(wheres)==0:
        print('No intersection between the model and the sample was found')
        return pd.DataFrame()

    wheres_expanded = np.repeat(
        np.array(wheres).reshape(np.array(wheres).shape[0],-1),
        len(samples['samples']), axis=1)


    collapsed = 1*((slice0==wheres_expanded) | (slice1==wheres_expanded))

    cleanNames = lambda liste: [ite.split('/')[-1] for ite in liste]
    df = pd.DataFrame(collapsed, index=ChromPosSamples[x_ind],
                      columns=cleanNames(samples['samples'].tolist()))

    model2=model.set_index(ChromPosModel)

    filtered_variant_sample_matrix = model2.merge(df, how='left',
                                                 left_index=True,
                                                 right_index=True)

    return filtered_variant_sample_matrix

# =============================================================================
# 3.- Impute the missing variant with he passed method (Deprecated?)
# =============================================================================

def imputeMissingVariants(variant_matrix, method = 'zeros'):
    if method == 'zeros':
        fix = 0
    elif method == 'ones':
        fix = 1
    elif method == 'random':
        rand = np.random.random_sample(size = variant_matrix.shape)
        fix = pd.DataFrame(rand, columns=variant_matrix.columns.tolist(),
                           index = variant_matrix.index.tolist())
    elif method == 'imputation':
        pass

    variant_matrix.fillna(fix, inplace=True)

    return(variant_matrix)

# =============================================================================
# 4.- Run the model
# =============================================================================

def runModel(variant_matrix,samp,name='ancestry-z_score', output='./'):
    sub = variant_matrix.iloc[:, -samp:]
    z_score = variant_matrix['BETA'].dot(sub)
    df=pd.DataFrame({'z-score':z_score})
    df.to_csv('{}/{}.tsv'.format(output,name),sep='\t')
    #print('Success running file. Now exit')
    return z_score

# =============================================================================
# 5.- Run the model according to args
# =============================================================================

def modelings(models,samples,arg,name):
    #print(models)
    for model in models.keys():
        print('Now running model: {}'.format(model))
        matrix = variantJoint(models[model], samples)
        if not matrix.empty:
            matrix = imputeMissingVariants(matrix)

            file_name='{};;{}'.format(model,name)
            #file_name='{}'.format(model)
            runModel(matrix,samples['samples'].shape[0], file_name, arg['-o'])
        else:
            raise NoIntersection('There is no intersection between the sample and the model')
    #print('Done. Have a nice day :)')
    pass

# =============================================================================
# 6.- Main function of the program
# =============================================================================

if __name__ == '__main__':
    arg = docopt(__doc__, version="Version 1.0")
    #print(arg)
    if not ((arg['-f'] or arg['-d']) and
            (arg['-m'] or arg['-a']) and arg['-o']):
        print('-------------------------------------------------------------')
        print('Please see the usage of this script')
        print('Good luck and have a nice day! :)')
        print('-------------------------------------------------------------')
        exit()

    if arg['-o']=='.':
        arg['-o']=='./'
    
    modelsDFs = dict()
    if arg['-a']:
        models = glob('./models/PANS/*.tsv')
        for model in models:
            name = model.split('/')[-1].split('.')[0]
            modelsDFs[name] = pd.read_csv(model, sep='\t', engine='python')

    if arg['-m']:
        for rmodel in arg['-m']:
            name = rmodel.split('/')[-1].split('.')[0]
            modelsDFs[name]=pd.read_csv(f'./models/PANS/{rmodel}.tsv',
                                    sep='\t', engine='python')

    #print(modelsDFs)
    for file in arg['-f']:
        name = file.split('/')[-1].split('.')[0]
        samples = allel.read_vcf(file)
        #samples['samples']=np.array([name])
        modelings(modelsDFs,samples,arg,name)

    joins_per_file(arg['-o'],arg['-o'],f'{name}')
    print('Done. Have a nice day :)')
