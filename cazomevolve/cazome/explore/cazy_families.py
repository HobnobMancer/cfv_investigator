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
"""Explore the sizes of CAZy family populations per genome"""


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from matplotlib.patches import Patch

from tqdm import tqdm


def build_fam_freq_df(gfp_df, tax_ranks):
    """Build matrix of fam freq per genome
    
    Each row represents a genome, each column a CAZy family
    
    :param gfp_df: pandas df - tab delimit list of ['Family', 'Genome', 'Protein', 'tax1', 'tax2'...]
    :param tax_ranks: list of tax ranks to include the matrix, one column generated per rank
        Must match columns names in gfp_df, e.g. ['Genus', 'Species']
    
    Return matrix as pandas df
    """
    # identify all families present in the dataset
    all_families = set(gfp_df['Family'])
    all_families = list(all_families)
    all_families.sort()
    print(f"The dataset contains {len(all_families)} CAZy families")
    
    # identify all genomes i the dataset
    all_genomes = set(gfp_df['Genome'])
    
    # define column names
    col_names = ['Genome']
    
    for rank in tax_ranks:
        col_names.append(rank)
        
    for fam in all_families:
        col_names.append(fam)
        
    # gather fam freq data per genome
    fam_df_data = []

    for genome in tqdm(all_genomes, desc="Counting fam frequencies"):
        row_data = [genome]

        # get tax data
        for rank in tax_ranks:
            row_data.append(gfp_df[gfp_df['Genome'] == genome].iloc[0][rank])

        # gather all genome rows
        g_rows = gfp_df[gfp_df['Genome'] == genome]

        # count number of proteins in the family
        for fam in all_families:
            fam_rows = g_rows[g_rows['Family'] == fam]
            fam_freq = len(set(fam_rows['Protein']))
            row_data.append(fam_freq)

        fam_df_data.append(row_data)

    fam_freq_df = pd.DataFrame(fam_df_data, columns=col_names)
    
    return fam_freq_df


def build_row_colours(df, grp, palette):
    """Build map of colour to member of grp (e.g. genus)

    The dataframe that is parsed to `build_row_colours()` must be the dataframe that is used to 
    generate a clustermap, otherwise Seaborn will not be able to map the row oclours correctly 
    and no row colours will be produced.

    The dataframe used to generate the clustermap when passed to the function, must include the 
    column to be used to define the row colours, e.g. a 'Genus' column. This column (named by `grp`)
    is removed within the function.
    
    :param df: matrix of genome x fam, with fam freq
    :param grp: str, name of col to map colour scheme onto, e.g. 'Genus' or 'Species'
    :param palette: str, name of seaborn colour scheme to use, e.g. Set1
    
    Return map and lut
    """
    series = df.pop(grp)
    lut = dict(zip(
        series.unique(),
        sns.color_palette(palette, n_colors=len(list(series.unique())))
    ))
    row_colours = series.map(lut)
    
    return row_colours, lut


def build_family_clustermap(
    df,
    row_colours=None,
    fig_size=None,
    file_path=None,
    file_format='png',
    font_scale=1,
    dpi=300,
    dendrogram_ratio=None,
    lut=None,
    legend_title='',
    title_fontsize='2',
    legend_fontsize='2',
    bbox_to_anchor=(1,1),
    cmap=sns.cubehelix_palette(dark=1, light=0, reverse=True, as_cmap=True),
):
    """Build a clustermap of the CAZy family frequencies per genome
    
    :param df: df of CAZy family frequencies per genome
    :param row_colours: pandas map - used to define additional row colours. or list of maps for 
        multiple sets of row colours. If None, additional row colours are not plotted
    :param fig_size: tuple (width, height) of final figure. If None, decided by Seaborn
    :param file_path: path to save image to. If None, the figure is not written to a file
    :param file_format: str, file format to save figure to. Default 'png'
    :param font_scale: int, scale text - use if text is overlapping. <1 to reduce 
        text size
    :param dpi: dpi of saved figure
    :param dendrogram_ratio: Proportion of the figure size devoted to the dendrograms.
        If a pair is given, they correspond to (row, col) ratios.
    :param lut: lut from generating colour scheme, add to include legend in the plot7
    :param legend_title: str, title of legend for row colours
    :title_fontsize: int or {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}
        The font size of the legend's title.
    :legend_fontsize: int or {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}
    :param bbox_to_anchor: tuple, coordinates to place legend
    :param cmap: Seaborn cmap to be used for colour scheme of the heat/clustermap
    
    Return nothing
    """
    sns.set(font_scale=font_scale)
    
    fam_clustermap = sns.clustermap(
        df,
        cmap=cmap,
        figsize=fig_size,
        row_colors=row_colours,
        dendrogram_ratio=dendrogram_ratio,
        yticklabels=True,
    );
    
    if lut is not None:
        handles = [Patch(facecolor=lut[name]) for name in lut]
        plt.legend(
            handles,
            lut,
            title=legend_title,
            bbox_to_anchor=bbox_to_anchor,
            bbox_transform=plt.gcf().transFigure,
            loc='upper center',
            title_fontsize=title_fontsize,
            fontsize=legend_fontsize,
        )
        
    if file_path is not None:
        fam_clustermap.savefig(
            file_path,
            dpi=dpi,
            bbox_inches='tight',
        )
