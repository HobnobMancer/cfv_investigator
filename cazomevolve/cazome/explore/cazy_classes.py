#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# (c) University of St Andrews 2022
# (c) University of Strathclyde 2022
# (c) James Hutton Institute 2022
# Author:
# Emma E. M. Hobbs

# Contact
# eemh1@st-andrews.ac.uk

# Emma E. M. Hobbs,
# Biomolecular Sciences Building,
# University of St Andrews,
# North Haugh Campus,
# St Andrews,
# KY16 9ST
# Scotland,
# UK

# The MIT License
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Explore the sizes od CAZy class populations per genus"""


import pandas as pd
import numpy as np
import re

from tqdm import tqdm


CAZY_CLASSES = ['GH', 'GT', 'PL', 'CE', 'AA', 'CBM']


def calculate_class_sizes(gfp_df, grp, round_by=None):
    """Calculate the mean (+- SD) of CAZymes per CAZy class per grp.

    Num of CAZymes is the number of unique protein accessions.

    :param gfp_df: pandas df, columns = ['Family', 'Genome', 'Protein', 'Genus', 'Species']
    :param grp: str, tax rank to group genomes by, e.g. 'Genus' or 'Species'
    :param round_by: int, num of dp to round the mean and sd to, if None does not round

    Return
    * df columns ['CAZyClass', grp, 'MeanCazyClass', 'SdCazyClass', 'NumOfGenomes']
    * dict cazy_class_size_dict
    """
    cazy_class_size_dict = {}  # {class: {grp: {genome: {'proteins': set(protein id), 'numOfProteins': int}}}}

    for ri in tqdm(range(len(gfp_df)), desc="Getting CAZy class sizes"):
        protein_acc = gfp_df.iloc[ri]['Protein']
        fam = gfp_df.iloc[ri]['Family']
        grp_name = gfp_df.iloc[ri][grp]
        genome = gfp_df.iloc[ri]['Genome']
        
        cazy_class = re.match('\D{2,3}', fam).group()
        
        try:
            cazy_class_size_dict[cazy_class]
        except KeyError:
            cazy_class_size_dict[cazy_class] = {}
            
        try:
            cazy_class_size_dict[cazy_class][grp_name]
        except KeyError:
            cazy_class_size_dict[cazy_class][grp_name] = {}
            
        try:
            cazy_class_size_dict[cazy_class][grp_name][genome]['proteins'].add(protein_acc)
        except KeyError:
            cazy_class_size_dict[cazy_class][grp_name][genome] = {'proteins': {protein_acc}}
            
    cazy_class_data = []
    grps = set(gfp_df[grp])

    for cazy_class in tqdm(CAZY_CLASSES, desc="Calculating CAZy class sizes"):
        
        for grp_name in grps:
            try:
                cazy_class_size_dict[cazy_class][grp_name]
            except KeyError:
                # cazy class is not in any genomes from the grp_name
                num_genomes = len(set(gfp_df[gfp_df[grp] == grp_name]['Genome']))  # sample size
                cazy_class_data.append(
                    [cazy_class, grp_name, 0, 0, num_genomes]
                )
                continue
                
            # get sample size, i.e. num of genomes
            num_genomes = len(list(cazy_class_size_dict[cazy_class][grp_name].keys()))
            
            cazy_class_sizes = []
            for genome in cazy_class_size_dict[cazy_class][grp_name]:
                num_of_cazymes = len(cazy_class_size_dict[cazy_class][grp_name][genome]['proteins'])
                cazy_class_size_dict[cazy_class][grp_name][genome]['numOfProteins'] = num_of_cazymes
                cazy_class_sizes.append(num_of_cazymes)
                
            mean_cazy_class = np.mean(cazy_class_sizes)
            sd_cazy_class = np.std(cazy_class_sizes)

            if round_by is not None:
                mean_cazy_class = round(mean_cazy_class, round_by)
                sd_cazy_class = round(sd_cazy_class, round_by)

            num_genomes = len(list(cazy_class_size_dict[cazy_class][grp_name].keys()))
            
            cazy_class_data.append(
                [cazy_class, grp_name, mean_cazy_class, sd_cazy_class, num_genomes]
            )

    col_names = ['CAZyClass', grp, 'MeanCazyClass', 'SdCazyClass', 'NumOfGenomes']
    class_df = pd.DataFrame(cazy_class_data, columns=col_names)
    
    return class_df, cazy_class_size_dict
