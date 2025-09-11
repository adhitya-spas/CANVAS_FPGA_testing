@echo off

CALL git pull
REM Activate conda environment
CALL "C:\Users\canmo\miniconda3\Scripts\activate.bat"
CALL conda activate canalg_env

REM Run the Python script with pdb
:: python -m pdb longtermtest_main_final_gain.py
python longtermtest_main_final_gain.py