git status
git pull origin master
python cov_model/cov_lin_wrapper.py --regions US_STATES --month 4 --all-data True
rm cov_model/projections/*pyc
rm cov_model/statsanalysis/*pyc
rm cov_model/datafinder/*pyc
git status
