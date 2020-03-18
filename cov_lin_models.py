"""
Script to plot the evolution of daily number of cases
of COVID-19 and extract some parameters via a linear fit.

Usage
=====
$ python cov_lin_models.py --countries UK,Italy --download-data [True, False]

If download-data set to True, it will download the official,
most up to date data; currently the only data location is at:

UK_DAILY_CASES_DATA = "https://www.arcgis.com/sharing/rest/content/items/e5fd11150d274bebaaf8fe2a7a2bda11/data"

Source (official): https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases

which is an excel spreadsheet.
"""
import argparse
import csv
from datetime import datetime
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import urllib
from xlrd import open_workbook

# data stores: governemental data
UK_DAILY_CASES_DATA = "https://www.arcgis.com/sharing/rest/content/items/e5fd11150d274bebaaf8fe2a7a2bda11/data"
UK_DAILY_DEATH_DATA = "https://www.arcgis.com/sharing/rest/content/items/bc8ee90225644ef7a6f4dd1b13ea1d67/data"

# data stores: Johns Hopkins data
JOHN_HOPKINS = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports"

def c_of_d(ys_orig, ys_line):
    """Compute the line R squared."""
    y_mean_line = [np.mean(ys_orig) for y in ys_orig]
    squared_error_regr = sum((ys_line - ys_orig) * (ys_line - ys_orig))
    squared_error_y_mean = sum((y_mean_line - ys_orig) * \
                               (y_mean_line - ys_orig))
    return 1 - (squared_error_regr / squared_error_y_mean)


def get_linear_parameters(x, y):
    """Retrive linear parameters."""
    # line parameters
    coef = np.polyfit(x, y, 1)
    poly1d_fn = np.poly1d(coef)

    # statistical parameters first line
    R = c_of_d(y, poly1d_fn(x))  # R squared
    y_err = poly1d_fn(x) - y  # y-error
    slope = coef[0]  # slope
    d_time = np.log(2.) / slope  # doubling time
    R0 = np.exp(slope) - 1.  # basic reproductive number, daily

    return poly1d_fn(x), R, y_err, slope, d_time, R0


def get_plot_text(slope, country, R, d_time, R0, x, month):
    """Set plot title, subtitle, text."""
    plot_text = "Daily Cases (red):" + "\n" + \
                "Date: %s-%s-2020" % (str(int(x[-1])), month) + "\n" + \
                "Line fit $N=Ce^{bt}$ with rate $b=$%.2f" % slope + "\n" + \
                "Coefficient of determination R=%.3f" % R + "\n" + \
                "Cases Doubling time: %.1f days" % d_time + "\n" + \
                "Estimated Daily $R_0=$%.1f" % R0
    plot_name = "COVID-19_LIN_{}.png".format(country)

    return plot_text, plot_name


def get_deaths_plot_text(slope, country, R, d_time, avg_mort, stdev_mort):
    """Set text for deaths."""
    plot_text = "Daily Deaths (blue):" + "\n" + \
                "Line fit $N=Ce^{mt}$ with rate $m=$%.2f" % slope + "\n" + \
                "Coefficient of determination R=%.3f" % R + "\n" + \
                "Deaths Doubling time: %.1f days" % d_time + "\n" + \
                "Average mortality %.2f+/-%.2f (STD)" % (avg_mort, stdev_mort)

    return plot_text


def get_excel_data(url, country_table, table_name, column, download):
    """Retrive Excel sheet and parse."""
    country_xls = "country_data/{}.xls".format(country_table)
    if not os.path.isfile(country_xls) or download:
        urllib.urlretrieve(url, country_xls)
    book = open_workbook(country_xls, on_demand=True)
    sheet = [
        book.sheet_by_name(name) for name in book.sheet_names()
        if name == table_name
    ][0]
    cells = [cell.value for cell in sheet.col(column)]

    return cells


def _common_plot_stuff(country):
    """Add common stuff to plot."""
    plt.xlabel("Time [days, starting March 1st, 2020]")
    plt.ylabel("Cumulative number of confirmed cases and deaths")
    plt.title("COVID-19 in {} starting March 1, 2020".format(country))


def load_daily_deaths_history():
    """Load previously written to disk deaths numbers."""
    return list(np.loadtxt("country_data/UK_deaths_history", dtype='float'))


def plot_countries(datasets, month, country):
    """Plot countries data."""
    # filter data lists
    cases = [float(c) for c in datasets[0] if c != 'NN']
    deaths = [float(c) for c in datasets[1] if c != 'NN']
    deaths = [d for d in deaths if d > 0.]
    recs = [float(c) for c in datasets[2] if c != 'NN']

    actual_days = [
        datetime.strptime(c, "%Y-%m-%dT%H:%M:%S").day
        for c in datasets[3] if c != 'NN'
    ]
    if actual_days[0] != 1 and actual_days[0] < 10:
        x_cases = actual_days
    else:
        x_cases = [float(n) for n in range(1, len(cases) + 1)]

    # logarithimc regression
    y_cases = np.log(cases)
    y_deaths = np.log(deaths)
    x_deaths = [float(n) for n in range(int(x_cases[-1]) - len(deaths) + 1,
                                        int(x_cases[-1]) + 1)]

    # statistics: cases
    poly_x, R, y_err, slope, d_time, R0 = get_linear_parameters(
        x_cases,
        y_cases)

    # plot parameters: cases
    plot_text, plot_name = get_plot_text(slope, country,
                                         R, d_time, R0,
                                         x_cases, month)

    # compute average mortality
    delta = len(cases) - len(deaths)
    mort = np.array(deaths) / np.array(cases[delta:])
    avg_mort = np.mean(mort)
    stdev_mort = np.std(mort)

    # statistics: deaths
    if deaths:
        poly_x_d, R_d, y_err_d, slope_d, d_time_d, R0_d = get_linear_parameters(
            x_deaths,
            y_deaths
        )

        # plot parameters: deaths
        plot_text_d = get_deaths_plot_text(
            slope_d, "UK",
            R_d, d_time_d,
            avg_mort, stdev_mort
        )

    # all in one
    y_all_real = []
    if deaths:
        y_all_real.extend(deaths)
    y_all_real.extend(cases)
    y_all = np.log(y_all_real)

    # plotting cases
    plt.scatter(x_cases, y_cases, color='r',
                label="Daily Cases")
    plt.plot(x_cases, poly_x, '--k')
    if deaths:
        plt.scatter(x_deaths, y_deaths, marker='v',
                    color='b', label="Daily Deaths")
        plt.plot(x_deaths, poly_x_d, '--b')
    plt.errorbar(x_cases, y_cases, yerr=y_err, fmt='o', color='r')
    if deaths:
        plt.errorbar(x_deaths, y_deaths, yerr=y_err_d, fmt='v', color='b')
    plt.grid()
    plt.xlim(0., x_cases[-1] + 1.5)
    plt.ylim(0., y_cases[-1] + 3.5)
    _common_plot_stuff(country)
    plt.text(1., y_cases[-1] + 0.3, plot_text, fontsize=8)
    if deaths:
        plt.text(1., y_cases[-1] - 2.1, plot_text_d, fontsize=8)
    plt.legend(loc="lower left")
    plt.yticks(y_all, [np.int(y01) for y01 in y_all_real])
    plt.tick_params(axis="y", labelsize=8)
    plt.savefig(os.path.join("country_plots", plot_name))
    plt.close()

    return d_time, R0

def plot_official_uk_data(download):
    """Plot the UK data starting March 1st, 2020."""
    uk_cases_url = UK_DAILY_CASES_DATA
    cases_cells = get_excel_data(uk_cases_url, "UK_cases",
                                 "DailyConfirmedCases", 2,
                                 download=download)
    uk_deaths_url = UK_DAILY_DEATH_DATA
    # TODO check for possible future book.name == DailyIndicators
    death_cells = get_excel_data(uk_deaths_url, "UK_deaths",
                                 "Sheet1", 3,
                                 download=download)

    # data cells: cases and deaths
    y_data_real = cases_cells[31:]
    y_deaths_real = load_daily_deaths_history()

    # append to file if new data
    if death_cells[1:] not in y_deaths_real:
        y_deaths_real.extend(death_cells[1:])
        with open("country_data/UK_deaths_history", "a") as file:
            file.write(str(death_cells[1:][0]) + "\n")

    # compute avergae mortality
    mort = np.array(y_deaths_real) / np.array(y_data_real[12:])
    avg_mort = np.mean(mort)
    stdev_mort = np.std(mort)

    # all in one
    y_all_real = []
    y_all_real.extend(y_deaths_real)
    y_all_real.extend(y_data_real)
    y_all = np.log(y_all_real)

    # logarithimc regression
    y_data = np.log(y_data_real)
    y_deaths = np.log(y_deaths_real)

    # x-time series, days: cases start 1st March
    # deths start 13th March
    x_data = [np.float(x) for x in range(1, len(y_data) + 1)]
    x_deaths = [np.float(x) for x in range(13, len(y_deaths) + 13)]

    # statistics: cases
    poly_x, R, y_err, slope, d_time, R0 = get_linear_parameters(x_data,
                                                                y_data)

    # plot parameters: cases
    plot_text, plot_name = get_plot_text(slope, "UK-GOV",
                                         R, d_time, R0,
                                         x_data, month="03")

    # statistics: deaths
    poly_x_d, R_d, y_err_d, slope_d, d_time_d, R0_d = get_linear_parameters(
        x_deaths,
        y_deaths
    )

    # plot parameters: deaths
    plot_text_d = get_deaths_plot_text(
        slope_d, "UK",
        R_d, d_time_d,
        avg_mort, stdev_mort
    )

    # plotting cases
    plt.scatter(x_data, y_data, color='r',
                label="Daily Cases")
    plt.plot(x_data, poly_x, '--k')
    plt.scatter(x_deaths, y_deaths, marker='v',
                color='b', label="Daily Deaths")
    plt.plot(x_deaths, poly_x_d, '--b')
    plt.errorbar(x_data, y_data, yerr=y_err, fmt='o', color='r')
    plt.errorbar(x_deaths, y_deaths, yerr=y_err_d, fmt='v', color='b')
    plt.grid()
    plt.xlim(0., x_data[-1] + 1.5)
    plt.ylim(0., y_data[-1] + 2.5)
    _common_plot_stuff("UK")
    plt.text(2., y_data[-1] + 0.5, plot_text, fontsize=8)
    plt.text(2., y_data[-1] - 1.2, plot_text_d, fontsize=8)
    plt.legend(loc="lower left")
    plt.yticks(y_all, [np.int(y01) for y01 in y_all_real])
    plt.tick_params(axis="y", labelsize=8)
    plt.savefig(os.path.join("country_plots", plot_name))
    plt.close()


def _get_daily_countries_data(date, country):
    """Get all countries data via csv file reading."""
    # date[0] = DAY(DD), date[1] = MONTH(MM)
    file_name = "{}-{}-2020.csv".format(date[1], date[0])
    data_dir = os.path.join("country_data",
                            "{}_monthly_{}".format(country, date[1]))
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    fullpath_file = os.path.join(data_dir, file_name)
    if not os.path.isfile(fullpath_file):
        url = os.path.join(JOHN_HOPKINS, file_name)
        urllib.urlretrieve(url, fullpath_file)

    # file reading
    with open(fullpath_file, "r") as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        data_read = [row for row in reader]
        # country data
        exp_dates = [tab[2] for tab in data_read if tab[1] == country]
        if exp_dates:
            exp_dates = exp_dates[0]
        else:
            exp_dates = 'NN'
        count_cases = [float(tab[3]) for tab in data_read if tab[1] == country]
        if count_cases:
            if country != "US":
                count_cases = count_cases[0]
            else:
                count_cases = sum(count_cases)
        else:
            count_cases = 'NN'
        count_deaths = [float(tab[4]) for tab in data_read if tab[1] == country]
        if count_deaths:
            if country != "US":
                count_deaths = count_deaths[0]
            else:
                count_deaths = sum(count_deaths)
        else:
            count_deaths = 'NN'
        count_rec = [float(tab[5]) for tab in data_read if tab[1] == country]
        if count_rec:
            if country != "US":
                count_rec = count_rec[0]
            else:
                count_rec = sum(count_rec)
        else:
            count_rec = 'NN'

    return count_cases, count_deaths, count_rec, exp_dates


def _get_monthly_countries_data(country, month):
    """Assemble monthly data per country."""
    m_cases = []
    m_deaths = []
    m_rec = []
    actual_dates = []
    # start March 1st
    today_date = datetime.today().strftime('%m-%d-%Y')
    today_day = today_date.split("-")[1]
    for day in range(1, int(float(today_day))):
        date_object = datetime(day=day,
                               month=month,
                               year=2020).strftime('%d-%m-%Y')
        date = (date_object.split("-")[0], date_object.split("-")[1])
        month_cases, month_deaths, month_rec, exp_dates = \
            _get_daily_countries_data(date, country)
        m_cases.append(month_cases)
        m_deaths.append(month_deaths)
        m_rec.append(month_rec)
        actual_dates.append(exp_dates)

    return m_cases, m_deaths, m_rec, actual_dates

def plot_parameters(doubling_time, basic_reproductive):
    """Plot simple viral infection parameters."""
    plt.hist(doubling_time, bins=len(doubling_time), histtype='step',
             normed=False, cumulative=False)
    plt.grid()
    plt.xlabel("Cases doubling time [days]")
    plt.ylabel("Number")
    mean_dt = np.mean(doubling_time)
    std_dt = np.std(doubling_time)
    plt.axvline(np.mean(mean_dt), color='red', linestyle='--')
    plt.title(
        "Cases doubling time [days] for %i countries\nVertical line: mean doubling time: %.1f+/-%.1f" % (len(doubling_time), mean_dt, std_dt)
    )
    plt.savefig(os.path.join("country_plots", "Histogram_Doubling_Time.png"))
    plt.close()

    # append historical data
    with open("country_data/mean_doubling_time", "a") as file:
        if str(mean_dt) not in file.readlines():
            file.write(str(mean_dt) + ' ' + str(std_dt) + "\n")

    R_0 = [c * 10. for c in basic_reproductive]
    plt.hist(R_0, bins=len(R_0), histtype='step',
             normed=False, cumulative=False)
    plt.grid()
    plt.xlabel("Basic Reproductive Number")
    plt.ylabel("Number")
    mean_r0 = np.mean(R_0)
    std_r0 = np.std(R_0)
    plt.axvline(mean_r0, color='red', linestyle='--')
    plt.title(
        "Basic reproductive number for %i countries\nVertical line: mean number: %.1f+/-%.1f (assuming an avg infectious phase 10 days)" % (len(R_0), mean_r0, std_r0)
    )
    plt.savefig(os.path.join("country_plots",
                             "Histogram_Basic_Reproductive_Number.png"))
    plt.close()

def main():
    """Execute the plotter."""
    # parse command line args
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d',
                        '--download-data',
                        type=bool,
                        default=True,
                        help='Flag to trigger downloading data.')
    parser.add_argument('-c',
                        '--countries',
                        type=str,
                        default="COUNTRIES",
                        help='List OR file with list of countries.')
    parser.add_argument('-m',
                        '--month',
                        type=int,
                        help='Month index: March: 3, April: 4 etc.')
    args = parser.parse_args()
    download = False
    if not args.countries:
        return
    if args.download_data:
        download = True

    # plot UK always
    plot_official_uk_data(download)

    # get countries
    if not os.path.isfile(args.countries):
        countries = args.countries.split(",")
    else:
        with open(args.countries, "r") as file:
            countries = [coun.strip() for coun in file.readlines()]

    # plot other countries
    double_time = []
    basic_rep = []
    for country in countries:
        monthly_numbers = _get_monthly_countries_data(country, args.month)
        d_time, R0 = plot_countries(monthly_numbers, args.month, country)
        double_time.append(d_time)
        basic_rep.append(R0)

    # plot viral parameters
    plot_parameters(double_time, basic_rep)


if __name__ == '__main__':
    main()
