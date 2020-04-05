# COVID-19 Adaptive Linear Fit and Parameter Estimation

## Modelling

A description of the simple mathematical model behind these
results can be found [here](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/Mathematical_Model.md)

## Visualization

Maps are courtesy of [datawrapper](https://github.com/werner17/Covis?fbclid=IwAR19xnSaq57hdbWOX0ab-G1FVf2ScgFUd-iRla-1kfASwwhFZTF9k5KEnCQ) and use data from this daily updated [tables](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_tables). Map source can be found[here](https://github.com/werner17/Covis/blob/master/datawrapper/README.md?fbclid=IwAR3lIkoSgOFhVhSJYFd01FToppwhDvcHpVb87Tvl4vQaeaTJXmFS1TeEfgQ)

* Reported cases doubling time
  ![map](https://github.com/werner17/Covis/blob/master/datawrapper/kdAj6.png)
* Reported deaths doubling time
  ![map](https://github.com/werner17/Covis/blob/master/datawrapper/WQXRP.png)
* Actual infections percentages of country populations
  ![map](https://github.com/werner17/Covis/blob/master/datawrapper/foNWt.png)
* Estimated underreporting:
  ![map](https://github.com/werner17/Covis/blob/master/datawrapper/dUzze.png)

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
