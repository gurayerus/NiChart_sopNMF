# opNMF Calculation

**opNMF Calculation** is a package designed to calculate RAVENS maps from T1w MRI scans and extract opNMF coefficient values from pre-calculated atlases

## Features
- Calculate RAVENS maps for different tissue types (segmentation labels)
- Calculate RAVENS maps using different methods (ANTs, SynthMorph)
- Post-processing steps to calculate opNMF coeff.s from GM RAVENS maps

## Installation

- You can install the package using:

```bash
# create environment
mamba create -n sopnmf python=3.10.18     
mamba activate sopnmf

# install NiChart_sopNMF (FIXME: needs work!)
git clone https://github.com/gurayerus/NiChart_sopNMF
cd NiChart_sopNMF
# install dependencies: ANTs 2.3.1, fireants nibabel (see conda_env_list_short.txt)
```

- Or use the docker container (FIXME: needs work!): 
    
    cbica/nichart_opnmf:initialdemo (https://hub.docker.com/r/cbica/nichart_opnmf)
  
## Application

- See the test scripts to apply calculation on the test image

 
```bash
mamba activate sopnmf
cd ./test/scripts
./run_test_opnmf.sh
```

Check the results:
```bash
cd ../output/fireants_default/subj1
cat subj1_MUSIC_C64.csv
```
 

  
  


