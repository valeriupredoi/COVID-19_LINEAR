Simple script that plots the evolution of COVID-19
==================================================

This is a simple and easily adaptible script that plots the
log number of daily cases of COVID-19 vs time. It does the
following automated tasks:

- downloads the data (if prompted) for the required countries;
- extracts the daily number of cases from the original data;
- plots log(number of cases) vs time;
- fits a line through and computes the line parameters and least
  squares errors;
- computes the coefficient of determination (how good the linear fit is);
- computes the estimated population doubling time;
- computes the daily basic reproductive number (how many new infections
  result daily from one infected individual).

Usage
=====

Requirements:

- `python2.7` or higher (ok with `python3.x`);
- Package `xlrd` available from PyPi via `pip install xlrd`;

Command line use:

`python cov_lin_models.py --countries COUNTRIES --download-data BOOL`

where `COUNTRIES` is a list of countries to study (currently UK only
implemented); `BOOL`: `True` for doewnloading the data to the `country_data`
directory or `False` to use an older copy from the said directory.
