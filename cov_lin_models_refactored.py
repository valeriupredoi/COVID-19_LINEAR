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

# slowing countries: countries that show a consistent slowing trend
# slowing down value = date in March that is roughly the start of slowdown
SLOWDOWN = {"Belgium": 13,
            "Denmark": 13, 
            "Finland": 14,
            "Ireland": 15,
            "Netherlands": 13,
            "Norway": 14,
            "Sweden": 13}

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
    plot_text = "Daily Cases:" + "\n" + \
                "Date: %s-%s-2020" % (str(int(x[-1])), month) + "\n" + \
                "Line fit $N=Ce^{bt}$ with rate $b=$%.2f" % slope + "\n" + \
                "Coefficient of determination R=%.3f" % R + "\n" + \
                "Cases Doubling time: %.1f days" % d_time + "\n" + \
                "Estimated Daily $R_0=$%.1f" % R0
    plot_name = "COVID-19_LIN_{}.png".format(country)

    return plot_text, plot_name


def get_deaths_plot_text(slope, country, R, d_time, avg_mort, stdev_mort):
    """Set text for deaths."""
    plot_text = "Daily Deaths:" + "\n" + \
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


def _compute_slowdown(x_cases, y_cases, country, month):
    """Get numbers for slowdown phase."""
    slowdown_index = x_cases.index(SLOWDOWN[country])
    y_slow = y_cases[slowdown_index:]
    x_slow = x_cases[slowdown_index:]
    x_cases = x_cases[0:slowdown_index]
    y_cases = y_cases[0:slowdown_index]

    # get linear params for slowdown
    poly_x_s, R_s, y_err_s, slope_s, d_time_s, R0_s = get_linear_parameters(
         x_slow,
         y_slow)
    plot_text_s, plot_name_s = get_plot_text(slope_s, country,
                                             R_s, d_time_s, R0_s,
                                             x_slow,
                                             month)
    return (x_cases, y_cases, x_slow, y_slow,
        poly_x_s, R_s, y_err_s, slope_s, d_time_s, R0_s,
        plot_text_s, plot_name_s)


def make_evolution_plot(variable_pack, country):
    """Make the exponential evolution plot."""
    # unpack variables
    (x_cases, y_cases, x_slow, y_slow, cases, deaths,
     x_deaths, deaths, y_deaths, poly_x, poly_x_s,
     poly_x_d, y_err, y_err_d, plot_text, plot_text_s,
     plot_text_d, plot_name, slope_d) = variable_pack

    # repack some data
    y_all_real = []
    if deaths:
        y_all_real.extend(deaths)
    y_all_real.extend(cases)
    y_all = np.log(y_all_real)
    last_tick_real = []
    if deaths:
        last_tick_real.append(deaths[-1])
    last_tick_real.append(y_all_real[-1])
    last_tick = np.log(last_tick_real)

    # plot
    plt.scatter(x_cases, y_cases, color='r',
                label="Daily Cases")
    plt.plot(x_cases, poly_x, '--r')
    if country in SLOWDOWN:
        plt.axvline(SLOWDOWN[country], linewidth=2, color='orange')
        plt.scatter(x_slow, y_slow, color='g',
                    label="Daily Cases Slower")
        plt.plot(x_slow, poly_x_s, '-g')
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
    if country in SLOWDOWN:
        plt.xlim(0., x_slow[-1] + 1.5)
        plt.ylim(0., y_slow[-1] + 3.5)
    _common_plot_stuff(country)
    if country in SLOWDOWN:
        plt.text(1., y_slow[-1] + 0.3, plot_text_s, fontsize=8, color='g')
        plt.text(1., y_slow[-1] - 1.5, plot_text, fontsize=8, color='r')
        if deaths:
            plt.text(1., y_slow[-1] - 3.1, plot_text_d, fontsize=8, color='b')
    else:
        plt.text(1., y_cases[-1] + 0.3, plot_text, fontsize=8, color='r')
        if deaths:
            plt.text(1., y_cases[-1] - 2.1, plot_text_d, fontsize=8, color='b')
    plt.legend(loc="lower left")
    plt.yticks(last_tick, [np.int(y01) for y01 in last_tick_real])
    plt.tick_params(axis="y", labelsize=8)
    plt.savefig(os.path.join("country_plots", plot_name))
    plt.close()


def plot_countries(datasets, month, country, download):
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
    # pad for unavailable data from 1st of month
    if actual_days[0] != 1 and actual_days[0] < 10:
        x_cases = actual_days
    else:
        x_cases = [float(n) for n in range(1, len(cases) + 1)]

    # x-axis for deaths
    x_deaths = [float(n) for n in range(int(x_cases[-1]) - len(deaths) + 1,
                                        int(x_cases[-1]) + 1)]

    # UK specific data
    if country == "UK":
        (x_cases, cases, x_deaths,
        deaths, avg_mort,
        stdev_mort) = _get_official_uk_data(download)

    # log data
    y_cases = np.log(cases)
    y_deaths = np.log(deaths)

    # statistics: cases: account for slowdown
    d_time_s = []
    R0_s = []
    x_slow = y_slow = poly_x_s = R_s = y_err_s = slope_s = \
        plot_text_s = plot_name_s = None

    if country in SLOWDOWN:
        (x_cases, y_cases, x_slow, y_slow,
        poly_x_s, R_s, y_err_s, slope_s, d_time_s, R0_s,
        plot_text_s, plot_name_s) = _compute_slowdown(x_cases, y_cases,
                                                      country, month)

    # get linear params
    poly_x, R, y_err, slope, d_time, R0 = get_linear_parameters(
        x_cases,
        y_cases)
    if d_time_s and R0_s:
        d_time = np.mean(np.append(d_time, d_time_s))
        R0 = np.mean(np.append(R0, R0_s))

    # plot parameters: cases
    plot_text, plot_name = get_plot_text(slope, country,
                                         R, d_time, R0,
                                         x_cases,
                                         month)

    # compute average mortality
    if country != "UK":
        delta = len(cases) - len(deaths)
        mort = np.array(deaths) / np.array(cases[delta:])
        avg_mort = np.mean(mort)
        stdev_mort = np.std(mort)

    # statistics: deaths
    poly_x_d = R_d = y_err_d = slope_d = \
        d_time_d = R0_d = plot_text_d = None
    if deaths:
        (poly_x_d, R_d, y_err_d,
         slope_d, d_time_d, R0_d) = get_linear_parameters(
            x_deaths,
            y_deaths
        )

        # plot parameters: deaths
        plot_text_d = get_deaths_plot_text(
            slope_d, "bla",
            R_d, d_time_d,
            avg_mort, stdev_mort
        )

    variable_pack = (x_cases, y_cases, x_slow, y_slow,
                     cases, deaths,
                     x_deaths, deaths, y_deaths, poly_x, poly_x_s,
                     poly_x_d, y_err, y_err_d, plot_text,
                     plot_text_s, plot_text_d, plot_name, slope_d)

    make_evolution_plot(variable_pack, country)
    if deaths and len(deaths) > 3.0:
        make_simulations_plot(variable_pack, country)

    return d_time, R0


def _get_official_uk_data(download):
    """Get the official UK data starting March 1st, 2020."""
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

    x_data = [np.float(x) for x in range(1, len(y_data_real) + 1)]
    x_deaths = [np.float(x) for x in range(13, len(y_deaths_real) + 13)]

    # compute average mortality
    mort = np.array(y_deaths_real) / np.array(y_data_real[12:])
    avg_mort = np.mean(mort)
    stdev_mort = np.std(mort)

    return (x_data, y_data_real, x_deaths,
        y_deaths_real, avg_mort, stdev_mort)


def make_simulations_plot(variable_pack, country):
    # get variable pack
    (x_data, y_data, x_slow, y_slow, y_data_real, y_deaths_real,
     x_deaths, y_deaths_real, y_deaths, poly_x, poly_x_s,
     poly_x_d, y_err, y_err_d, plot_text, plot_text_s,
     plot_text_d, plot_name, slope_d) = variable_pack

    # simulate by death rate scenario
    sim_y_0_real = np.array(y_deaths_real) * 200.  # mrate=0.005
    sim_y_1_real = np.array(y_deaths_real) * 100.  # mrate=0.01
    sim_y_2_real = np.array(y_deaths_real) * 50.  # mrate=0.02
    sim_y_3_real = np.array(y_deaths_real) * 33.3  # mrate=0.03
    sim_y_4_real = np.array(y_deaths_real) * 25.  # mrate=0.04

    # all in one for sims
    y_sim_real = []
    y_sim_real.extend(y_deaths_real)
    y_sim_real.extend(y_data_real)
    y_sim_real.extend(sim_y_0_real)
    y_sim_real.extend(sim_y_1_real)
    y_sim_real.extend(sim_y_2_real)
    y_sim_real.extend(sim_y_3_real)
    y_sim_real.extend(sim_y_4_real)
    y_sim = np.log(y_sim_real)

    # log the simulations too
    sim_y_0 = list(np.log(sim_y_0_real))
    sim_y_1 = list(np.log(sim_y_1_real))
    sim_y_2 = list(np.log(sim_y_2_real))
    sim_y_3 = list(np.log(sim_y_3_real))
    sim_y_4 = list(np.log(sim_y_4_real))

    # forecast the cases in 10 days
    sim_y_0_f = sim_y_0_real[-1] * np.exp(10. * slope_d)
    sim_y_1_f = sim_y_1_real[-1] * np.exp(10. * slope_d)
    sim_y_2_f = sim_y_2_real[-1] * np.exp(10. * slope_d)
    sim_y_3_f = sim_y_3_real[-1] * np.exp(10. * slope_d)
    sim_y_4_f = sim_y_4_real[-1] * np.exp(10. * slope_d)

    # estimate time for 65M total infection
    full_time_0 = (np.log(65 * 1e6) - np.log(sim_y_0_real[-1])) / slope_d
    full_time_1 = (np.log(65 * 1e6) - np.log(sim_y_1_real[-1])) / slope_d
    full_time_2 = (np.log(65 * 1e6) - np.log(sim_y_2_real[-1])) / slope_d
    full_time_3 = (np.log(65 * 1e6) - np.log(sim_y_3_real[-1])) / slope_d

    y_all_real = []
    y_all_real.extend(y_deaths_real)
    y_all_real.extend(y_data_real)
    y_all = np.log(y_all_real)
    last_tick_real = []
    last_tick_real.append(y_deaths_real[-1])
    last_tick_real.append(y_data_real[-1])
    last_tick = np.log(last_tick_real)

    # plot simulated cases
    plt.scatter(x_data, y_data, color='r',
                label="Cum. Cases")
    plt.plot(x_data, poly_x, '--r')
    plt.scatter(x_deaths, y_deaths, marker='v',
                color='b', label="Cum. Deaths")
    if country in SLOWDOWN:
        plt.axvline(SLOWDOWN[country], linewidth=2, color='orange')
        plt.scatter(x_slow, y_slow, color='g',
                    label="Daily Cases Slower")
        plt.plot(x_slow, poly_x_s, '-g')
    plt.scatter(x_deaths[-1], np.log(sim_y_0_f), marker='x', color='b')
    plt.scatter(x_deaths[-1], np.log(sim_y_1_f), marker='x', color='g')
    plt.scatter(x_deaths[-1], np.log(sim_y_2_f), marker='x', color='r')
    plt.scatter(x_deaths[-1], np.log(sim_y_3_f), marker='x', color='c')
    plt.scatter(x_deaths[-1], np.log(sim_y_4_f), marker='x', color='m')
    plt.plot([list(np.array(x_deaths) - 10.)[-1], x_deaths[-1]], [sim_y_0[-1], np.log(sim_y_0_f)], '--b')
    plt.plot([list(np.array(x_deaths) - 10.)[-1], x_deaths[-1]], [sim_y_1[-1], np.log(sim_y_1_f)], '--g')
    plt.plot([list(np.array(x_deaths) - 10.)[-1], x_deaths[-1]], [sim_y_2[-1], np.log(sim_y_2_f)], '--r')
    plt.plot([list(np.array(x_deaths) - 10.)[-1], x_deaths[-1]], [sim_y_3[-1], np.log(sim_y_3_f)], '--c')
    plt.plot([list(np.array(x_deaths) - 10.)[-1], x_deaths[-1]], [sim_y_4[-1], np.log(sim_y_4_f)], '--m')
    plt.plot(x_deaths, poly_x_d, '--b')
    plt.errorbar(x_data, y_data, yerr=y_err, fmt='o', color='r')
    plt.errorbar(x_deaths, y_deaths, yerr=y_err_d, fmt='v', color='b')
    plt.plot(np.array(x_deaths) - 10., sim_y_0, label="M=0.5%")
    plt.plot(np.array(x_deaths) - 10., sim_y_1, label="M=1%")
    plt.plot(np.array(x_deaths) - 10., sim_y_2, label="M=2%")
    plt.plot(np.array(x_deaths) - 10., sim_y_3, label="M=3%")
    plt.plot(np.array(x_deaths) - 10., sim_y_4, label="M=4%")
    plt.grid()
    plt.xlim(0., x_data[-1] + 1.5)
    plt.ylim(0., np.log(sim_y_0_f) + 3.)
    if country in SLOWDOWN:
        plt.xlim(0., x_slow[-1] + 1.5)
    # plt.text(2., sim_y_0[-1] + 4., plot_text_d, fontsize=8, color="blue")
    plt.legend(loc="lower left", fontsize=9)
    last_tick = list(last_tick)
    last_tick.append(np.log(sim_y_0_f))
    last_tick.append(np.log(sim_y_1_f))
    last_tick.append(np.log(sim_y_2_f))
    last_tick.append(np.log(sim_y_3_f))
    last_tick.append(np.log(sim_y_4_f))
    last_tick_real.append(sim_y_0_f)
    last_tick_real.append(sim_y_1_f)
    last_tick_real.append(sim_y_2_f)
    last_tick_real.append(sim_y_3_f)
    last_tick_real.append(sim_y_4_f)
    plt.yticks(last_tick, [np.int(y01) for y01 in last_tick_real])
    plt.tick_params(axis="y", labelsize=8)
    plt.annotate(str(int(sim_y_4_real[-1])),xy=(x_deaths[-1]-10,sim_y_4[-1]))
    plt.annotate(str(int(sim_y_0_real[-1])),xy=(x_deaths[-1]-10,sim_y_0[-1]))
    plt.annotate(str(int(sim_y_1_real[-1])),xy=(x_deaths[-1]-10,sim_y_1[-1]))
    plt.annotate(str(int(sim_y_2_real[-1])),xy=(x_deaths[-1]-10,sim_y_2[-1]))
    plt.annotate(str(int(sim_y_3_real[-1])),xy=(x_deaths[-1]-10,sim_y_3[-1]))
    plt.xlabel("Time [days, starting March 1st, 2020]")
    plt.ylabel("Cumulative no. of deaths and reported and simulated cases")
    plt.title("COVID-19 in {} starting March 1, 2020\n".format(country) + \
              "Sim cases are based on mortality fraction M and delayed by 10 days\n" + \
              "Sim cumulative no. cases: measured deaths x 1/M\n" + \
              "Est. time for total infection: %i days (M=0.03); %i days (M=0.02); %i days (M=0.01); %i days (M=0.005)" % (int(full_time_3), int(full_time_2), int(full_time_1), int(full_time_0)),
              fontsize=10)
    plt.savefig(os.path.join("country_plots",
                             "COVID-19_LIN_{}_SIM_CASES.png".format(country)))
    plt.close()


def _check_for_us(param, country):
    """Get special csv param for US - summing is needed."""
    if country != "US":
        param = param[0]
    else:
        param = sum(param)

    return param


def _extract_from_csv(data_object, country, param_idx,
                      country_idx, special_case=False, numeric=False):
    """Extract and return the needed field from csv file."""
    if not numeric:
        param = [
            tab[param_idx] for tab in data_object if tab[country_idx] == country
        ]
    else:
        param = [
            tab[param_idx] for tab in data_object
            if tab[country_idx] == country
        ]
        param = [float(p) for p in param if p != 'NN']

    if not param:
        param = 'NN'
        return param

    if not special_case:
        param = param[0]
    else:
        # list of specific data checks
        param = _check_for_us(param, country)

    return param


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
        # dates
        exp_dates = _extract_from_csv(data_read, country, 2, 1)
        # cases
        count_cases = _extract_from_csv(data_read, country, 3, 1,
                                        special_case=True, numeric=True)
        # deaths
        count_deaths = _extract_from_csv(data_read, country, 4, 1,
                                         special_case=True, numeric=True)
        # recoveries
        count_rec = _extract_from_csv(data_read, country, 5, 1,
                                      special_case=True, numeric=True)

    country_data = ',' + ','.join([country, exp_dates, str(count_cases),
                                   str(count_deaths), str(count_rec)])

    # overwrite so to optimize disk use
    with open(fullpath_file, "w") as file:
        file.write(country_data)

    return count_cases, count_deaths, count_rec, exp_dates


def _get_monthly_countries_data(country, month):
    """Assemble monthly data per country."""
    m_cases = []
    m_deaths = []
    m_rec = []
    actual_dates = []

    # start date / actual date
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


def _read_write_parameter(filename, parameter, stddev_parameter):
    """Read doubling time from record."""
    # eg filename="country_data/mean_doubling_time", parameter=mean_dt
    # stddev_parameter=np.std(parameter)
    with open(filename, "r") as file:
        data_lines = [c.split(' ')[0] for c in file.readlines()]
    with open(filename, "a") as file:
        if str(parameter) not in data_lines:
            file.write(str(parameter) + ' ' + str(stddev_parameter) + "\n")


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
    header = "Cases doubling time [days] for %i countries\n" % len(doubling_time)
    mean_text = "%.1f+/-%.1f (standard deviation)" % (mean_dt, std_dt)
    title = header + \
            "Vertical line: mean doubling time: " + \
            mean_text
    plt.title(title, fontsize=10)
    plt.savefig(os.path.join("country_plots", "Histogram_Doubling_Time.png"))
    plt.close()

    # append historical data
    _read_write_parameter("country_data/mean_doubling_time", mean_dt, std_dt)

    R_0 = [c * 10. for c in basic_reproductive]
    plt.hist(R_0, bins=len(R_0), histtype='step',
             normed=False, cumulative=False)
    plt.grid()
    plt.xlabel("Basic Reproductive Number")
    plt.ylabel("Number")
    mean_r0 = np.mean(R_0)
    std_r0 = np.std(R_0)
    plt.axvline(mean_r0, color='red', linestyle='--')
    header = "Basic reproductive number $R_0$ for %i countries\n" % len(R_0)
    mean_title = \
        "Vertical line: mean number: %.1f+/-%.1f (standard deviation)\n" % (mean_r0,
                                                                          std_r0)
    title = header + \
            "Vertical line: mean number: %.1f+/-%.1f (standard deviation) " + \
            mean_title + \
            "(assuming an avg infectious phase 10 days)"
    plt.title(title, fontsize=8)
    plt.savefig(os.path.join("country_plots",
                             "Histogram_Basic_Reproductive_Number.png"))
    # append historical data
    _read_write_parameter("country_data/basic_reproductive_number",
                          mean_r0, std_r0)

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
        d_time, R0 = plot_countries(monthly_numbers,
                                    args.month, country, download)
        double_time.append(d_time)
        basic_rep.append(R0)

    # plot viral parameters
    plot_parameters(double_time, basic_rep)


if __name__ == '__main__':
    main()