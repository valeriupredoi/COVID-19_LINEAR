Obtaining the software
----------------------
Clone the github gitball:
`https://github.com/valeriupredoi/COVID-19_LINEAR.git`


Installation
------------
No installation required: it is a stand-alone script that can be
run from the terminal.

Requirements
------------
- `python2.7` or higher (ok with `python3.x`);
- Package `xlrd` available from PyPi via `pip install xlrd`;

Command line use
----------------
`python cov_lin_models_refactored.py --countries COUNTRIES --regions REGIONS --month 3 --download True`

where `--countries` is a list of countries to study
or `file: COUNTRIES` (just add your country there);
`--regions` is a list of countries to study
or `file: REGIONS` (just add your region or US state there)
`download-data`: `True` (default) for downloading the
data to the `country_data` directory or `False` to use
an older copy from the said directory;
`--month`: numeral of the month to plot.

Contributing
------------
You can contribute to this repository with data, code, images etc.
as long as they are relevant. Just open an issue and ask to be added
as contributing author, I will add you and then you can create a branch
to hold your changes and open a pull request.

Cheers!
