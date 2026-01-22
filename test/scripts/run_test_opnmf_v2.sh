#! /bin/bash
#SBATCH --job-name=ravens_test
#SBATCH --partition=ai
#SBATCH --gres=gpu:a40:2
#SBATCH --mem=16G
#SBATCH --time=02:00:00
#SBATCH --output=slurm-%j.out

echo '----------------------------------------------------'
echo "Running $0 $@"
echo '----------------------------------------------------'

## Test subject
mrid='subj3'

## Set registration mode (profile)
regmode='quick2'
regmode='quick'         # Default mode (~10 minutes)
regmode='test'          # For a quick test (~1 minutes)
regmode='default'          # For a quick test (~1 minutes)

## Registration backend: ants (default) or fireants
reg_backend='fireants'
# reg_backend='ants'

# Allow overriding backend via first CLI argument, e.g.:
#   ./run_test_installed.sh fireants
if [ $# -ge 1 ]; then
    reg_backend="$1"
fi

## Mounting path for the container app
app_dir=$(realpath ../..)
input_dir="${app_dir}/test/input/${mrid}"
output_dir="${app_dir}/test/output/${reg_backend}_${regmode}/${mrid}"

## Input files
t1="${input_dir}/${mrid}_T1.nii.gz"
t1seg="${input_dir}/${mrid}_T1_seg.nii.gz"

## Reference files
template="${app_dir}/resources/templates/istaging/BLSA_SPGR+MPRAGE_averagetemplate.nii.gz"
label_dict="${app_dir}/resources/dictionaries/list_FAST.csv"
music_dir="${app_dir}/resources/music_rois/nifti"

## Create out dir for subject
mkdir -pv ${output_dir}

## Go to scripts
cd ${app_dir}/src

# conda activate fireants
source $(conda info --base)/etc/profile.d/conda.sh
conda activate fireants

echo '----------------------'
echo $CUDA_VISIBLE_DEVICES
nvidia-smi
echo '----------------------'

## Run abn map creation
CMD="./nichart_opnmf.sh \
        --in_img ${t1} \
        --in_seg ${t1seg} \
        --labels GM \
        --out_dir ${output_dir} \
        --out_prefix ${mrid}_ \
        --reg_mode ${regmode} \
        --reg_backend ${reg_backend} \
        --icv_mask ${t1seg} \
        --flag_del_tmp no \
        --template ${template} \
        --label_dict ${label_dict} \
        --music_dir ${music_dir}"

echo "--- COMMAND TO BE EXECUTED ---"
echo "$CMD"
echo "------------------------------"

eval "$CMD"
