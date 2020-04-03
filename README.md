# COVID-19 Adaptive Linear Fit and Parameter Estimation

## Resources

* Country [tables](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_tables)
* Current country [plots](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots)
* March-2020 [plots](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots_03-2020)
* March-2020 [situation report](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/Situtaion_Report_March-2020.md)

## Software package

* [Package](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/cov_model)
* Usage example: `python cov_model/cov_lin_wrapper.py --month 4`
* Requirements:
- `python2.7` or higher (ok with `python3.x`);
- Package `xlrd` available from PyPi via `pip install xlrd`;
- Package `scipy`: for an easy installation I recommend using `miniconda/anaconda`;
  for a `pip` installation on an older architecture and `python2.7` you will have
  to install the `lapack` and `blas` libraries, a Fortran compiler and `python-dev`:
  - `sudo apt-get install python-dev`
  - `sudo apt-get install gfortran`
  - `sudo apt-get install libblas3 liblapack3 liblapack-dev libblas-dev`
  - `sudo pip install scipy==0.16`

## Data

* UK Data: official data [source](https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases)
* Worldwide Data: Johns Hopkins University CSSE [gitHub repository](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)
