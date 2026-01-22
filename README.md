# opNMF Calculation

**opNMF Calculation** is a package designed to calculate RAVENS maps from T1w MRI scans and extract opNMF coefficient values from pre-calculated atlases

## Features
- Calculate RAVENS maps for different tissue types (segmentation labels)
- Calculate RAVENS maps using different methods (ANTs, SynthMorph)
- Post-processing steps to calculate opNMF coeff.s

## Installation

- You can install the package using:

```bash
pip install nichart-opnmf [FIXME: dependencies ANTs 2.3.1, fireants and Python (nibabel))
```

- Or use the docker container: 
    
    cbica/nichart_opnmf:initialdemo (https://hub.docker.com/r/cbica/nichart_opnmf)
  
## Application

- See the test scripts to apply calculation on the test image:
 
```bash
cd ./test/scripts
```

  
  


