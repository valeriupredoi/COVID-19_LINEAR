download=True
month=3
countries=Bulgaria,Belgium,Canada,France,Germany,Ireland,Italy,Netherlands,Romania,Slovakia,Spain,US
rm -r country_plots/**
python cov_lin_models.py --countries $countries --download-data $download --month $month
