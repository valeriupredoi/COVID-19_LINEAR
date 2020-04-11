# Mathematical Model
## Linear Fit

We assume the following model for the cumulative number of reported cases and deaths:
at any given time `t` (measured in days), the cumulative number of cases will be:
```
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
it is noticed they are gradually decreasing with time. Therefore, the linear fits are not
performed on all data points from the start of the epidemic, but are, in fact, performed
on subsets of data points to maximize the quality of fit. This generates a set of rates `b`
and `m` over time.

We perform two types of fits: one for all available data and another for the last 5 days. If the
fit for the last 5 days is better than the overall data fit (compare coefficient of determination
R) and if the coefficient of determination for the last 5 days fit is > 0.98 then we chose
the linear parameters for the last 5 days fir (most of the cases show that the last 5 days fit
is generally better; 0.98 means a very high quality fit).

## Estimating the actual number of cases

The reported number of cases is an unreliable data, so it is desired to estimate the actual number
of existing cases at any given day (the analysis performed daily, so the actual number of cases
is given at the **today** day).

For this purpose we use the deaths data `D(t)` and its growth rate `m` and a set of plausible
mortality fractions of the virus `M=[0.5, 1, 2, 3 and 4]%`: we construct the plausible actual
number of cases
```
C(t) = M x D(t)
```
and shift `C(t)` in time by a **fixed** delay of 20 days (assumed as average duration between
time of infection and time of death) and compute the number of cases on the day when the deaths
reported today were cases right after infection `C(t - 20)`. To get the number of actual cases of
today, `C(t - 20)` needs to be extrapolated 14 days (as of April 9, previous results with 20 days)
later (today): for that we use the rate of
growth for deaths, `m`, and construct a function `f(m)` to best represent the evolution of `m = m(t)`
for the next 14 days. Note that we are not using the rate of growth for reported cases `b` since we
consider it to be unreliable. The reason why we need to construct `f(m)` is to best represent the
growth rate of the actual cases, which we assume to be close to the evolution over the next 20 or so
days of `m` (case evolution is well mirrored by the deaths evolution after 14-20 days).

For March, when a lot of the deaths rates `m` have been noticed to drop to half after 15-20 days, we
chose `f(m) = m/2`; for April (so far) we are thresholding `m` at 0.15 and apply the 0.5 factor only
for `m > 0.15` since those rates < 0.15 are very stable and have not been observed to change over longer
periods of time. This way we can estimate the actual number of cases today as:
```
C(today) = M x D(today) x exp(f(m) x 20)
```
