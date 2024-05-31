#/bin/sh

source ~/.venv/bin/activate

export PROTOTYPING_DEVELOP="True"
python train_osero.py -dn -fp
