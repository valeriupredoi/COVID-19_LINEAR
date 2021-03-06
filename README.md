
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

**Website** https://valeriupredoi.github.io/

![protectnhs](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/stay-home-protect-nhs.png)

Table of Contents
-----------------
* [Model](#Model)
* [Results](#Results)
* [Conclusions](#Conclusions)
* [Resources](#Resources)
* [Software](#Software)
* [Data](#Data)

# Model
## Linear Fit

We assume the following model for the cumulative number of reported cases and deaths:
at any given time `t` (measured in days), the cumulative number of cases will be:

```math
N(t) = N0exp(bt)
```

where `N0` is an initial number of cases, rate `b` is the growth rate (in units
1/day or day-1), and `exp` is the exponential number = 2.72. Similarily, deaths
have the distribution:
```
D(t) = D0exp(mt)
```
where `m` is the growth rate for deaths and `D0` is an initial number.

## Doubling times and daily increments

Line-fitting `ln(N) = f(t)` and `ln(D) = f(t)` will give us rates `b` and `m`, and
will allow us to estimate the doubling times for reported cases and deaths:
```
double_time_cases = ln(2)/b
```
and
```
double_time_deaths = ln(2)/m
```

With these, we can rewrite the evolution of both reported number of cases and reported deaths:
```
N(days) = N0 x 2^(days/double_time_cases)
```
and
```
D(days) = D0 x 2^(days/double_time_deaths)
```
where `days` is the number of days the evolution is measured on; the larger `double_time_cases`
and `double_time_deaths` the smaller `N(t)` and `D(t)` are and for large enough
`double_time_cases >> days` and `double_time_deaths >> days`, the exponential evolution
can be approximated to:
```
N(days) = N0 x (1 + days/double_time_cases)
```
and
```
D(days) = D0 x (1 + days/double_time_deaths)
```
that is a linear evolution with time, which much slower than the exponential one.

We can also estimate a local, daily basic reproductive number:
for a daily evolution, starting from N cases the previous day,
the total number of cases would be
```
dN + N = Nexp(b)
```
where `dN` is the daily increase in cases, so the relative variation
in number of cases in one day will be:
```
dN/N = exp(b) - 1
```
this is a rough estimate of a daily basic reproductive number, which is < 1,
but over an infectious period of X days (I assume 10 in this case) will be > 1.
It somewhat resembles the definition of `R0` as a basic reproductive number since
it measures how fast the number of cases changes over the infectious period,
but it is not a rigorous computation of `R0`. We can rewrite the formula for the
daily increase as
```
b = ln(1 + P)
```
where `P = dN/N` represents the daily measured relative increase in reported number of cases;
this is in fact a function of time `b(t) = ln(1 + P(t))` since both `b` and `P` will decrease
over time (see next section).

We can now express the basic reproductive number R in terms of reported cases doubling time:
```
R = exp(ln2/double_time_cases) - 1
```

## Time evolution of rates

Growth rates `b` and `m` do not stay constant over longer (>10-12 days) periods of time,
it is noticed they are gradually decreasing with time (observed decrease by 50% every 10 days).
Therefore, the linear fits are not performed on all data points from the start of the epidemic,
but are, in fact, performed on subsets of data points to maximize the quality of fit.
This generates a set of rates `b` and `m` over time.

We perform two types of fits: one for all available data and another for the last 5 days. If the
fit for the last 5 days is better than the overall data fit (compare coefficient of determination
R) and if the coefficient of determination for the last 5 days fit is > 0.98 then we chose
the linear parameters for the last 5 days fir (most of the cases show that the last 5 days fit
is generally better; 0.98 means a very high quality fit).

## Estimating the actual number of cases

The reported number of cases is unreliable data, so it is desired to estimate the actual number
of existing cases at any given day (the analysis performed daily, so the actual number of cases
is given at the **today** day).

For this purpose we use the deaths data `D(t)` and its growth rate `m` and a set of plausible
mortality fractions of the virus `M = [0.5, 1, 2, 3 and 4]%`: we construct the plausible actual
number of cases
```
C(t) = D(t) x 1/M
```
and shift `C(t)` in time by a **fixed** delay of 14 days (assumed as average duration between
time of infection and time of death) and compute the number of cases on the day when the deaths
reported today were cases right after infection `C(t - 14)`. To get the number of actual cases of
today, `C(t - 14)` needs to be extrapolated 14 days
(14: as of April 9, previous results with 20 days have been redone)
later (today): for that we use the rate of
growth for deaths, `m`, and construct a function `f(m)` to best represent the evolution of `m = m(t)`
for the next 14 days. Note that we are not using the rate of growth for reported cases `b` since we
consider it to be unreliable. The reason why we need to construct `f(m)` is to best represent the
growth rate of the actual cases, which we assume to be close to the evolution over the next 14 or so
days of `m` (case evolution is well mirrored by the deaths evolution after 14+ days).

A lot of the deaths rates `m` have been noticed to drop to half after ~10 days, so we
chose `f(m) = m/2` and thresholding `m` at 0.05 and apply the 0.5 factor only
for `m > 0.05` since those rates < 0.05 are very stable and have not been observed to
change over longer periods of time. This way we can estimate the actual number of cases today as:
```
C(today) = 1/M x D(today) x exp(m x delay=14)
```
for `m < 0.05` and
```
C(today) = 1/M x D(today) x exp(0.5 x m x delay=14)
```
for `m >= 0.05`.

`C(today)` is a function of observables `D(today)` and two free parameters `M` and `delay` and
may have the same value for two different combinations of `(M, delay)` but for the realistic
set of `M = [0.5, 1, 2, 3 and 4]%` only delays of >= 14 days are a realistic parameter value, that
excludes unrealistic delays of < 2 days.

Further we compute country current cases population percentages as `C(today)/POP` and testing percentages as
`Reported cases/C(today)`.

# Results

## Visualization

Maps are courtesy of [datawrapper](https://github.com/werner17/Covis?fbclid=IwAR19xnSaq57hdbWOX0ab-G1FVf2ScgFUd-iRla-1kfASwwhFZTF9k5KEnCQ) and use data from this daily updated [tables](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_tables). Map source can be found [here](https://github.com/werner17/Covis/blob/master/datawrapper/README.md?fbclid=IwAR3lIkoSgOFhVhSJYFd01FToppwhDvcHpVb87Tvl4vQaeaTJXmFS1TeEfgQ)

* Reported cases doubling time
  ![map](https://github.com/werner17/Covis/blob/master/datawrapper/kdAj6.png)
  [Interactive Map](https://datawrapper.dwcdn.net/kdAj6)
* Reported deaths doubling time
  ![map](https://github.com/werner17/Covis/blob/master/datawrapper/WQXRP.png)
  [Interactive Map](https://datawrapper.dwcdn.net/WQXRP)
* Actual infections percentages of country populations
  ![map](https://github.com/werner17/Covis/blob/master/datawrapper/foNWt.png)
  [Interactive Map](https://datawrapper.dwcdn.net/foNWt)
* Estimated underreporting:
  ![map](https://github.com/werner17/Covis/blob/master/datawrapper/dUzze.png)
  [Interactive Map](https://datawrapper.dwcdn.net/dUzze)

## Rolling averages

We plot the 7-day rolling averages for absolute numbers of daily increases for deaths
and the same but country population weighted (in units of 1000 inhabitants).

![7dayavg](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots/ALL_COUNTRIES/COVID-19_Deaths_Rolling_Average.png)

7-day rolling window averages for daily increases in numbers of deaths (absolute numbers)

![7dayavg](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots/ALL_COUNTRIES/COVID-19_Deaths_Rolling_Average_per_Population.png)

7-day rolling window averages for daily increases in numbers of deaths (weighted by country population in units of
1000 inhabitants; note that Belgium's numbers are very high due to their reporting *all* deaths, see
[article](https://www.rtl.be/info/belgique/societe/la-belgique-pointee-du-doigt-dans-le-monde-entier-pour-son-nombre-de-victimes-du-coronavirus-pourtant-notre-systeme-de-comptage-est-de-plus-en-plus-1212924.aspx?fbclid=IwAR18cKoaeUCZzR6WoyIsEaHSq4DCX5XbMhdKeyPMSMh1D4sLLw_55NTlXiw))

## Upper bound on mortality: Israel

Israel is the only country that has solid testing results (16,000+ TpM as of April 10)
and has sufficiently good data for us to place an upper limit on the mortality mortality there: M=2%

Actual and simulated cases in Israel         |  Doubling times in Israel
:-------------------------------------------:|:---------------------------:
![IsraelSim](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots/Israel/COVID-19_LIN_Israel_SIM_CASES.png) | ![DoublIsrael](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots/Israel/COVID-19_Doubling_Times_Israel.png)

## Representative countries

We compare results obtained from simulating the actual number of cases for different countries giving
percentages of infect out of total country population for different mortality fraction scenarios
(0.5, 1 and 2% respecitively). Comparison is made with the Imperial College London report from 30/03/2020,
different in-country studies and a [study](http://www.uni-goettingen.de/en/606540.html)
from Georg-August University, Germany.

Comparison labels:
- Numbers labelled IC for 30-03-2020 from the Imperial College
  London [report](https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-Europe-estimates-and-NPI-impact-30-03-2020.pdf).
- Numbers labelled GA for 31-03-2020 from the Georg August University, Germany [study](http://www.uni-goettingen.de/en/606540.html).

**There is very good overlap with these results suggesting a consistent mortality
fraction per country of M=0.5-1%.**

**Tables header:**
- Date: date for data
- C: number of reported cases
- D: number of reported deaths
- DayR C %: daily increase rate for reported cases in percentage
- DayR D %: daily increase rate for reported deaths in percentage
- DoubT C (d): doubling time for entire reported cases population in days
- DoubT D (d): doubling time for entire reported deaths population in days
- %pop M=0.5%: percentage of country population infected for mortality M=0.5%
- %pop M=1%: percentage of country population infected for mortality M=1%
- %pop M=2%: percentage of country population infected for mortality M=2%
- Test% M=0.5%: country testing efficiency in percent for mortality M=0.5%
- Test% M=1%: country testing efficiency in percent for mortality M=1%
- Test% M=2%: country testing efficiency in percent for mortality M=2%
- Square brackets for 31 March data: values obtained for a 10-day and 20-day delay (equivalent
  to a 95% confidence interval) for each mortality M.

**Key parameters:**
- Parameter space for simulations: 14 day delay between deaths and simulated cases
  and projected rate 0.5 x current death rate or current death rate if current death rate < 0.05 (or 5%)
- For 31 March data we give in `[ ]` the values obtained for a 10-day and 20-day delay

### Spain
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
12/03 | 2277 | 54 | 40 | 50 | 1.8 | 1.4 | 0.79 | 0.39 | 0.20 | 0.6 | 1.2 | 2.5
21/02 | 25374 | 1375 | 19 | 24 | 3.6 | 2.9 | 3.18 | 1.59 | 0.80 | 1.7 | 3.4 | 6.8
31/03 | 95923 | 8464 | 9 | 13 | 7.4 | 5.5 | 8.71[6.8-12.7] | 4.36[3.4-6.4] | 2.18[1.7-3.2] | 2.4 | 4.7 | 9.4
11/04 | 158273 | 16081 | 4 | 5 | 18.7 | 14.8 | 13.28 | 6.64 | 3.32 | 2.6 | 5.1 | 10.2

- Population percentage %pop IC: 15% ci=[3.7%-41%] implies underestimation vs IC, probably M=0.5[-1]% best overlap.
- Population percentage %pop GA: 12.24% implies slight underestimation vs GA, probably M=0.5% for longer delays 14-20 days.

## Israel
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
31/03 | 5358 | 20 | 23 | 34 | 3.0 | 2.0 | 0.53 | 0.27 | 0.13 | 12.1 | 24.1 | 48.2
11/04 | 10408 | 95 | 6 | 13 | 12.5 | 5.3 | 0.56 | 0.28 | 0.14 | 22.0 | 44.0 | 88.1

### Austria
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
31/03 | 10180 | 128 | 7 | 20 | 9.6 | 3.4 | 1.21[0.8-2.2] | 0.60[0.4-1.1] | 0.30[0.2-0.6] | 9.5 | 19.0 | 38.0
11/04 | 13555 | 319 | 2 | 9 | 28.7 | 7.8 | 1.34 | 0.67 | 0.33 | 11.4 | 22.8 | 45.5

- Population percentage %pop IC: 1.1% ci=[0.36%-3.1%] implies M=0.5[-1]%.
- Population percentage %pop GA: 0.94% implies M=0.5% and longer delays ~16 days.
- Austrian [study](https://www.bloomberg.com/news/articles/2020-04-10/austrian-study-shows-coronavirus-cases-more-than-3-times-higher?fbclid=IwAR0sUvTL38gYPHWMn0fqHkZRfrs9WnK7On0uH8hLA-dVs3qXhAd1bcOSq7g) suggests 0.32% of total population infected around April 4-5, meaning exactly M=2%

### France
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
12/03 | 2281 | 48 | 29 | 31 | 2.4 | 2.3 | 0.13 | 0.06 | 0.03 | 2.8 | 5.5 | 11.0
21/03 | 14282 | 562 | 16 | 27 | 4.4 | 2.6 | 1.16 | 0.58 | 0.29 | 1.9 | 3.8 | 7.6
31/03 | 52827 | 3532 | 11 | 14 | 6.4 | 4.9 | 2.91[2.2-4.5] | 1.46[1.1-2.2] | 0.73[0.6-1.1] | 2.8 | 5.6 | 11.2
11/04 | 125931 | 13215 | 9 | 10 | 7.5 | 7.3 | 7.92 | 3.96 | 1.98 | 2.4 | 4.9 | 9.8

- Population percentage %pop IC: 3% ci=[1.1%-7.4%] implies M=0.5[-1]%.
- Population percentage %pop GA: 3.09% implies M=0.5% and longer delays ~16 days.

### Germany
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
21/03 | 22213 | 84 | 26 | 33 | 2.7 | 2.1 | 0.21 | 0.10 | 0.05 | 12.9 | 25.8 | 51.6
31/03 | 71808 | 775 | 8 | 20 | 8.3 | 3.4 | 0.77[0.5-1.4] | 0.39[0.3-0.7] | 0.19[0.1-0.4] | 11.2 | 22.3 | 44.6
11/04 | 122171 | 2767 | 4 | 12 | 16.2 | 5.7 | 1.56 | 0.78 | 0.39 | 9.4 | 18.8 | 37.6

- Population percentage %pop IC: 0.72% ci=[0.28%-1.8%] implies M=0.5[-1]%.
- Population percentage %pop GA: 0.55% implies M=0.5% for shorter dealys or M=1% for longer delays.
- Heinsberg [study](https://www.tagesschau.de/regional/nordrheinwestfalen/corona-studie-heinsberg-101.html) suggests a mortality M=0.37%, in line with my estimate and IC (if M=0.5%)

### Denmark
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
21/03 | 1326 | 13 | 8 | 33 | 8.9 | 2.1 | 0.45 | 0.22 | 0.11 | 5.1 | 10.3 | 20.5
31/03 | 3039 | 90 | 8 | 26 | 8.7 | 2.7 | 1.90[1.1-4.1] | 0.95[0.6-2] | 0.48[0.3-1] | 2.8 | 5.6 | 11.1
11/04 | 6014 | 247 | 7 | 7 | 10.1 | 9.7 | 1.41 | 0.71 | 0.35 | 7.4 | 14.8 | 29.6

- Population percentage %pop IC: 1.1% ci=[0.40%-3.1%] implies M=1[-2]%.
- Population percentage %pop GA: 0.41% implies M=2%.

### Italy
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
12/03 | 12462 | 827 | 20 | 31 | 3.4 | 2.2 | 2.40 | 1.20 | 0.60 | 0.9 | 1.7 | 3.4
21/03 | 53578 | 4825 | 13 | 16 | 5.2 | 4.3 | 4.93 | 2.47 | 1.23 | 1.8 | 3.6 | 7.2
31/03 | 105792 | 12428 | 5 | 8 | 13.9 | 9.1 | 6.99[6-8.8] | 3.49[3-4.4] | 1.75[1.5-2.2] | 2.5 | 5.0 | 10.0
11/04 | 147577 | 18849 | 3 | 3 | 25.4 | 21.1 | 9.85 | 4.92 | 2.46 | 2.5 | 4.9 | 9.9

- Population percentage %pop IC: 9.8% ci=[3.2%-26%] implies underestimation vs IC and M=0.5[-1]%.
- Population percentage %pop GA: 5% implies M=0.5% or understimated M=1%.

### Switzerland
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
21/03 | 6575 | 75 | 23 | 29 | 3.0 | 2.4 | 1.30 | 0.65 | 0.33 | 5.9 | 11.8 | 23.7
31/03 | 16605 | 433 | 6 | 16 | 11.1 | 4.4 | 3.04[2.2-4.9] | 1.52[1.1-2.4] | 0.76[0.6-1.2] | 6.4 | 12.8 | 25.7
11/04 | 24551 | 1002 | 3 | 7 | 19.9 | 10.1 | 3.79 | 1.90 | 0.95 | 7.6 | 15.2 | 30.4
17/04 | 26732 | 1281 | 1 | 4 | 55.0 | 18.3 | 5.11 | 2.55 | 1.28 | 6.1 | 12.3 | 24.6

- Population percentage %pop IC: 3.1% ci=[1.3%-7.6%] implies M=0.5[-1]%.
- Population percentage %pop GA: 2.72% implies M=0.5%.
- Wide antibody testing results [published](https://www.swissinfo.ch/eng/serological-test_antibody-test-results-suggest-6x-more-covid-19-infections-in-geneva/45712418) on April 25 quotes a total population infection of 5.5% which corresponds to M=0.5% from our model (5.1%
  population infected).

### Norway
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
31/03 | 4641 | 39 | 5 | 18 | 13.2 | 3.9 | 0.50[0.4-0.9] | 0.25[0.2-0.4] | 0.13[0.1-0.2] | 17.3 | 34.5 | 69.0
11/04 | 6314 | 113 | 3 | 11 | 24.9 | 6.5 | 0.90 | 0.45 | 0.22 | 13.2 | 26.3 | 52.7

- Population percentage %pop IC: 0.41% ci=[0.09%-1.2%] implies M=0.5[-1-2]%.
- Population percentage %pop GA: 0.23% implies M=1%.

### Belgium
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
21/03 | 2815 | 67 | 21 | 48 | 3.4 | 1.5 | 3.30 | 1.65 | 0.83 | 0.7 | 1.5 | 3.0
31/03 | 12775 | 705 | 24 | 22 | 2.9 | 3.2 | 5.56[3.6-10.6] | 2.78[1.8-5.3] | 1.39[0.9-2.7] | 2.0 | 4.0 | 8.0
11/04 | 26667 | 3019 | 6 | 14 | 11.3 | 5.0 | 13.90 | 6.95 | 3.48 | 1.7 | 3.3 | 6.7

- Population percentage %pop IC: 3.7%i ci=[1.3%-9.7%] implies M=0.5[-1-2]%.
- Population percentage %pop GA: 5.5% implies M=0.5%.

### Sweden
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
21/03 | 1763 | 20 | 10 | 34 | 6.7 | 2.0 | 0.43 | 0.22 | 0.11 | 4.1 | 8.2 | 16.4
31/03 | 4435 | 180 | 9 | 27 | 7.8 | 2.5 | 2.45[1.4-5.6] | 1.23[0.7-2.8] | 0.61[0.4-1.4] | 1.8 | 3.6 | 7.3
11/04 | 9685 | 870 | 8 | 14 | 9.1 | 5.0 | 4.64 | 2.32 | 1.16 | 2.1 | 4.2 | 8.4

- Population percentage %pop IC: 3.1% ci=[0.85%-8.4%] implies underestimation vs IC and M=0.5[-1]%.
- Population percentage %pop GA: 0.58% implies M=2%.

### United Kingdom
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
31/03 | 25150 | 1789 | 14 | 20 | 5.1 | 3.4 | 2.22[1.5-4.1] | 1.11[0.7-2.1] | 0.55[0.4-1] | 1.7 | 3.4 | 6.8
11/04 | 70272 | 8958 | 8 | 13 | 8.9 | 5.4 | 6.54 | 3.27 | 1.64 | 1.6 | 3.2 | 6.4

- Population percentage %pop IC: 2.7% ci=[1.2%-5.4%] implies M=0.5[-1]%.
- Population percentage %pop GA: 3.15% implies M=0.5% for longer delays ~17 days.

### Romania
Date  | C | D | DayR C % | DayR D % | DoubT C (d) | DoubT D (d) | %pop M=0.5% | %pop M=1% | %pop M=2% | Test% M=0.5% | Test% M=1% | Test% M=2%
:----:|:-:|:-:|:--------:|:--------:|:-----------:|:-----------:|:-----------:|:---------:|:---------:|:------------:|:----------:|:----------:
31/03 | 2245 | 82 | 24 | 29 | 2.9 | 2.4 | 0.62[0.4-1.5] | 0.31[0.2-0.7] | 0.16[0.1-0.4] | 1.8 | 3.7 | 7.4
11/04 | 5467 | 270 | 8 | 11 | 9.1 | 6.4 | 0.59 | 0.30 | 0.15 | 4.7 | 9.5 | 18.9

- Population percentage %pop GA: 0.48% implies M=0.5% for short ~10 days delays or M=1% for ~16day days delays.

## Evolution of doubling time with time

Here we compute an `R0` that is obtained from the doubling time and multiplied by 10 days
(the average infectious period).

Date  | Mean DoublT (days) | `R0` (10 days) | Figure
:----:|:------------------:|:--------------:|:--------:
16/03 | 3.1+/-1.9 | 3.3+/-1.4 | ![d0](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/anciliaries/country_plots_03-2020/frozen_plots_03-2020/16-3-2020/Histogram_Doubling_Time.png)
27/03 | 3.4+/-2 | 2.9+/-1.4 | ![d1](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/anciliaries/country_plots_03-2020/frozen_plots_03-2020/27-3-2020/Histogram_Doubling_Time.png)
31/03 | 4.2+/-2.4 | 2.6+/-1.5 | ![d2](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/anciliaries/country_plots_03-2020/frozen_plots_03-2020/31-3-2020/Histogram_Doubling_Time.png)
05/04 | 8.9+/-4.3 | 1.0+/-0.4 | ![d3](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots/frozen_plots_04-2020/05-04-2020/Histogram_Doubling_Time.png)
12/04 | 12.6+/-7.3 | 0.7+/-0.3 | ![d4](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots/frozen_plots_04-2020/12-04-2020/Histogram_Doubling_Time.png)
Current | - | - | ![d4](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots/ALL_COUNTRIES/Histogram_Doubling_Time.png)

# Conclusions

- Viral transmission is very high: `R0` of up to 5-6 in mid-March (considering an infectious phase of 10 days,
  could be even higher if infectious phase is longer); definite decrease in transmission due to social distancing,
  of ~70% in the three weeks between 16/03/2020 and 05/04/2020
- Countries underreport cases in very high proportions; underreporting decreases with
  the increase of number of tests per million; the average reporting for the 13 representative countries
  we looked at is 13.6% (std.dev. 11.6%) for April 11, for a reference mortality M=1%; that means, on
  average, that 86% of actual infections may go unreported;
- Average mortality of 0.5-1% (possibly higher to 2% in certain countries, defintely not higher than 2%,
  considering reference countries we looked at).

# Resources

Current repository resources:

* Country [tables](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_tables)
* Current country [plots](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/country_plots)
* March-2020 [plots](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/anciliaries/country_plots_03-2020)
* March-2020 [situation report](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/anciliaries/Situtaion_Report_March-2020.md)

# Software

- [Package](https://github.com/valeriupredoi/COVID-19_LINEAR/blob/master/cov_model)
- Usage example: `python cov_model/cov_lin_wrapper.py --countries COUNTRIES --regions REGIONS --month MONTH`
- Command line args:
  - `--countries`: list of comma-sep strings or file (example: Italy,Germany)
  - `--regions`: list of comma-sep strings or file (example: California,Georgia)
  - `--month`: int (example: 3 (for March))
- Requirements:
- `python2.7` or higher (ok with `python3.x`);
- Package `xlrd` available from PyPi via `pip install xlrd`;
- Package `scipy`: for an easy installation I recommend using `miniconda/anaconda`;
  for a `pip` installation on an older architecture and `python2.7` you will have
  to install the `lapack` and `blas` libraries, a Fortran compiler and `python-dev`:
  - `sudo apt-get install python-dev`
  - `sudo apt-get install gfortran`
  - `sudo apt-get install libblas3 liblapack3 liblapack-dev libblas-dev`
  - `sudo pip install scipy==0.16`

# Data

- UK Data: official data [source](https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases)
- Worldwide Data: Johns Hopkins University CSSE [gitHub repository](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)
- Testing efficiency [numbers](https://en.wikipedia.org/wiki/COVID-19_testing#Virus_testing_by_country)
- Heinsberg [study](https://www.tagesschau.de/regional/nordrheinwestfalen/corona-studie-heinsberg-101.html)
- Imperial College London, UK [report](https://www.imperial.ac.uk/media/imperial-college/medicine/sph/ide/gida-fellowships/Imperial-College-COVID19-Europe-estimates-and-NPI-impact-30-03-2020.pdf)
- Georg August University, Germany [study](http://www.uni-goettingen.de/en/606540.html)
- Austrian large scale testing [study](https://www.bloomberg.com/news/articles/2020-04-10/austrian-study-shows-coronavirus-cases-more-than-3-times-higher?fbclid=IwAR0sUvTL38gYPHWMn0fqHkZRfrs9WnK7On0uH8hLA-dVs3qXhAd1bcOSq7g)
