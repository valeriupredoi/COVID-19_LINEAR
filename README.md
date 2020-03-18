Results: Exponential Phase
==========================

Current results for linear fit for logarithmic data of daily number of cases and daily number of
deaths per country. Almost every coutry is undergoing an expoenential infection spread phase,
`exp(bt)`, characterised by the rate `b` and time coordinate `t` (time exponential)
in most cases, the exponential rates `b` are 0.25-0.3 day-1, yieling population (cases, deaths)
doubling times of 2-3 days. The results are affected by poor testing in different areas and countries,
and by **driver** regions (like Lombardia in Italy or London in UK, ultimately assigning a lot of
statistical weight to these parts of the country, given overwheling numbers).

United Kingdom
--------------

![COVID-19 UK Evolution](country_plots/COVID-19_LIN_UK-GOV.png)

Linear fit of the exponential spread in the United Kingdom, starting March 1st, 2020.
Data is piped automatically from the official database
https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases

![COVID-19 France Evolution](country_plots/COVID-19_LIN_France.png)
![COVID-19 Belgium Evolution](country_plots/COVID-19_LIN_Belgium.png)
![COVID-19 Spain Evolution](country_plots/COVID-19_LIN_Spain.png)
![COVID-19 Italy Evolution](country_plots/COVID-19_LIN_Italy.png)
![COVID-19 Romania Evolution](country_plots/COVID-19_LIN_Romania.png)
![COVID-19 Canada Evolution](country_plots/COVID-19_LIN_Canada.png)
![COVID-19 Germany Evolution](country_plots/COVID-19_LIN_Germany.png)
![COVID-19 Netherlands Evolution](country_plots/COVID-19_LIN_Netherlands.png)
![COVID-19 Bulgaria Evolution](country_plots/COVID-19_LIN_Bulgaria.png)
![COVID-19 Ireland Evolution](country_plots/COVID-19_LIN_Ireland.png)
![COVID-19 Slovakia Evolution](country_plots/COVID-19_LIN_Slovakia.png)
![COVID-19 US Evolution](country_plots/COVID-19_LIN_US.png)
![COVID-19 Doubling Time Evolution](country_plots/Histogram_Doubling_Time.png)
![COVID-19 Rzero Evolution](country_plots/Histogram_Basic_Reproductive_Number.png)

Parameters:

- `b`: exponential rate at which daily cases rise (in units `day-1`);
- `m`: exponential rate at which daily deaths rise (in units `day-1`);
- Coefficient of determination: how good the linear fit is: perfect fit R=1;
- Cases/Deaths doubling time: the number of days in which the cases/deaths will double;
- Estimated R0: the number of people a single infected person will infect per day, on average;
- Average Mortality Rate: average percent of number of cases that die.

Simple script that plots the evolution of COVID-19
==================================================

This is a simple and easily adaptible script that plots the
log number of daily cases of COVID-19 and deaths vs time. It does the
following automated tasks:

- downloads the data (if prompted) for the required countries;
- extracts the daily number of cases and daily deaths from the original datasets;
- plots log(number of cases) and log(number of deaths) vs time;
- fits a line through and computes the line parameters and least
  squares errors;
- computes the coefficient of determination (how good the linear fit is);
- computes the estimated infected population doubling time and death toll doubling time;
- computes the daily basic reproductive number (how many new infections
  result daily from one infected individual); note that the actual `R0`
  (basic reproductive number) can be estimated by multiplying by 7 (days, the median
  duration of the infectious phase).

Usage
=====

Requirements:

- `python2.7` or higher (ok with `python3.x`);
- Package `xlrd` available from PyPi via `pip install xlrd`;

Command line use:

`python cov_lin_models.py --countries COUNTRIES --month 3`

where `--countries` is a list of countries to study
or `file: COUNTRIES` (just add your country there);
`download-data`: `True` (default) for downloading the
data to the `country_data` directory or `False` to use
an older copy from the said directory;
`--month`: numeral of the month to plot.

UK Data
=======

Official data source: https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases

Worldwide Data
==============
Johns Hopkins University CSSE gitHub repository: https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports
