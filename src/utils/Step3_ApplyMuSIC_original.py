#!/usr/bin/env python

## adapted from Junhao's MuSIC original git code : https://github.com/anbai106/SOPNMF/tree/master/sopnmf
## in utils function: extract atlas signal

import pandas as pd
import numpy as np
import os,math
import nibabel as nib

PRJ='/cbica/projects/BLSA/Pipelines/MRI/BLSA_MuSIC_2022'

subList = '/cbica/projects/BLSA/Pipelines/MRI/BLSA_MuSIC_2022/Lists/MasterList_ALL_WithBLFlag_withExc_MPRAGE_BL.lst'

df_participant = pd.read_csv(subList,names=['ID'])

subs = list(df_participant['ID'])

atlas_path = os.path.join(PRJ,'Software/nifti/MuSIC_C64.nii.gz')

atlas = nib.load(atlas_path)

atlas_data = np.nan_to_num(atlas.get_data(caching='unchanged'))

num_component=64

for i in range(1,num_component + 1):
  values_mean = []
  values_sum = []

  # create mask
  
  data_mask = np.ma.make_mask(atlas_data == i)

  # read original image

  for sub in subs:
    data = nib.load(os.path.join(PRJ,'Protocols/RAVENS',str(sub),str(sub)+'_T1_LPS_N4_brain_muse-ss_Mean_fastbc_muse_seg_dramms-0.3_RAVENS_150_s2_DS.nii.gz'))
    data = np.nan_to_num(data.get_data(caching='unchanged'))
    data[~data_mask] = 0
    mean_value = np.sum(data) / np.sum(data_mask)  ## RAVENS maps has been scaled by 1000, thus should be divided by 1000 if input is RAVENS maps 
    sum_value = np.sum(data)
    if math.isnan(mean_value) or math.isnan(sum_value):
      break
    else:
      values_mean.append(mean_value)
      values_sum.append(sum_value)
  if len(values_mean) == df_participant.shape[0]:
    df_participant['component_' + str(i) + '_mean'] = values_mean
    df_participant['component_' + str(i) + '_sum'] = values_sum

## write to csv

df_participant.to_csv(os.path.join(PRJ,'Results/BLSA_MuSIC_C64.csv'), index=False, sep=',', encoding='utf-8')
