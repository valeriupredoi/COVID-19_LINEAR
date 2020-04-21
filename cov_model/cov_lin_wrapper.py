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
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from datetime import datetime

from datafinder.data_finder import (COUNTRIES_TO_SUM,
    get_monthly_countries_data, get_official_uk_data)
from statsanalysis import (linear, ks, country_parameters)
from projections import uk


COUNTRY_PARAMS = country_parameters.COUNTRY_PARAMS

def make_evolution_plot(variable_pack, country,
                        SLOWDOWN, SLOWDOWN_DEATHS,
                        month_str, slowdown_deaths=None):
    """Make the exponential evolution plot."""
    # unpack variables
    (x_cases, y_cases, x_slow, y_slow, cases, deaths,
     x_deaths, deaths, y_deaths, poly_x, poly_x_s,
     poly_x_d, y_err, y_err_d, plot_text, plot_text_s,
     plot_text_d, plot_name, slope_d, slope) = variable_pack

    if slowdown_deaths is not None:
        (x_deaths, y_deaths, x_deaths_slow, y_deaths_slow,
         poly_x_d_s, R_d_s, y_err_d_s,
         slope_d_s, d_time_d_s, R0_d_s,
         plot_text_d_s, plot_name_d_s) = slowdown_deaths

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
    if len(poly_x) == 5: 
        plt.plot(x_cases[-5:], poly_x, '--r')
    else:
        plt.plot(x_cases, poly_x, '--r')
    if country in SLOWDOWN:
        plt.axvline(SLOWDOWN[country], linewidth=2, color='orange')
        plt.scatter(x_slow, y_slow, color='g',
                    label="Daily Cases Slower")
        plt.plot(x_slow, poly_x_s, '-g')
    if deaths:
        plt.scatter(x_deaths, y_deaths, marker='v',
                    color='b', label="Daily Deaths")
        if len(poly_x_d) == 5:
            plt.plot(x_deaths[-5:], poly_x_d, '--b')
        else:
            plt.plot(x_deaths, poly_x_d, '--b')
        if country in SLOWDOWN_DEATHS:
            plt.scatter(x_deaths_slow, y_deaths_slow, marker='v',
                        color='g', label="Daily Deaths Slower")
            plt.plot(x_deaths_slow, poly_x_d_s, '--g')
            plt.errorbar(x_deaths_slow, y_deaths_slow, yerr=y_err_d_s,
                         fmt='v', color='g')

    plt.errorbar(x_cases, y_cases, yerr=y_err, fmt='o', color='r')
    if deaths:
        plt.errorbar(x_deaths, y_deaths, yerr=y_err_d, fmt='v', color='b')
    plt.grid()
    if not deaths:
        plt.xlim(0., x_cases[-1] + 1.5)
        plt.ylim(0., y_cases[-1] + 3.5)
    else:
        plt.xlim(0., x_cases[-1] + 1.5)
        plt.ylim(y_deaths[0] - 2., y_cases[-1] + 3.5)
    if country in SLOWDOWN:
        plt.xlim(0., x_slow[-1] + 1.5)
        plt.ylim(0., y_slow[-1] + 3.5)
    linear.common_plot_stuff(plt, country, month_str)
    if country in SLOWDOWN:
        plt.text(1., y_slow[-1] + 0.3, plot_text_s, fontsize=8, color='g')
        plt.text(1., y_slow[-1] - 1.5, plot_text, fontsize=8, color='r')
        if deaths:
            plt.text(1., y_slow[-1] - 3.1, plot_text_d, fontsize=8, color='b')
            if country in SLOWDOWN_DEATHS:
                plt.text(1., y_deaths_slow[-1] - 3.7, plot_text_d_s, fontsize=8,
                         color='g')
    else:
        plt.text(1., y_cases[-1] + 0.3, plot_text, fontsize=8, color='r')
        if deaths:
            plt.text(1., y_cases[-1] - 2.1, plot_text_d, fontsize=8, color='b')
            if country in SLOWDOWN_DEATHS:
                plt.text(1., y_deaths_slow[-1] - 3.3, plot_text_d_s, fontsize=8,
                         color='g')
    plt.legend(loc="lower left", fontsize=7)
    plt.yticks(last_tick, [np.int(y01) for y01 in last_tick_real])
    plt.tick_params(axis="y", labelsize=8)
    plt.savefig(os.path.join("country_plots", plot_name))
    plt.close()


def plot_countries(datasets, month, country, table_file, download):
    """Plot countries data."""
    if month == 3:
        month_str = "March"
    elif month == 4:
        month_str = "April"
    # filter data lists
    cases = [float(c) for c in datasets[0] if c != 'NN']
    deaths = [float(c) for c in datasets[1] if c != 'NN']
    deaths = [d for d in deaths if d > 0.]
    recs = [float(c) for c in datasets[2] if c != 'NN']

    SLOWDOWN, SLOWDOWN_DEATHS = linear.get_slowdown(month)

    if country != "UK":
        time_fmt = "%Y-%m-%dT%H:%M:%S"
        actual_days = [
            datetime.strptime(c, time_fmt).day
            for c in datasets[3] if c != 'NN'
        ]

        # pad for unavailable data from 1st of month
        if actual_days[0] != 1 and actual_days[0] < 15:
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
        stdev_mort) = get_official_uk_data(month, download)

    # log data
    y_cases = np.log(cases)
    y_deaths = np.log(deaths)

    # statistics: cases: account for slowdown
    Pdt = []
    Pr0 = []
    Pr = []
    x_slow = y_slow = poly_x_s = y_err_s = slope_s = \
        d_time_s = R0_s = R_s = plot_text_s = plot_name_s = None

    if country in SLOWDOWN:
        (x_cases, y_cases, x_slow, y_slow,
        poly_x_s, R_s, y_err_s, slope_s, d_time_s, R0_s,
        plot_text_s, plot_name_s) = linear.compute_slowdown(x_cases, y_cases,
                                                            country, month,
                                                            deaths=False)
        # get data for plotting
        Pdt.append(d_time_s)
        Pr0.append(R0_s)
        Pr.append(R_s)

    # get linear params for all data
    poly_x, R, y_err, slope, d_time, R0 = linear.get_linear_parameters(
        x_cases,
        y_cases)

    # extract the last 5 days only
    x_cases5 = x_cases[-5:]
    y_cases5 = y_cases[-5:]
    poly_x5, R5, y_err5, slope5, d_time5, R05 = linear.get_linear_parameters(
        x_cases5,
        y_cases5)

    # test for goodness of fit and reassign data
    # if R < R5 and R5 > 0.98:  ## switch to last 5 days get flat behaviour (20/04)
    poly_x, R, slope, d_time, R0 = \
        poly_x5, R5, slope5, d_time5, R05
        

    # get data for plotting
    Pdt.append(d_time)
    Pr0.append(R0)
    Pr.append(R)
    double_cases = d_time
    rate_cases = slope

    if d_time_s and R0_s:
        # compute MEAN doublind time for the combined fast&slow
        rate_cases = slope_s
        double_cases = d_time_s
        d_time = np.mean(np.append(d_time, d_time_s))
        R0 = np.mean(np.append(R0, R0_s))

    # plot parameters: cases
    plot_text, plot_name = linear.get_plot_text(slope, country,
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
    rate_deaths = double_deaths = 1e-10
    if deaths:
        d_time_d_s = None
        if country in SLOWDOWN_DEATHS:
            (x_deaths, y_deaths, x_deaths_slow, y_deaths_slow,
             poly_x_d_s, R_d_s, y_err_d_s, slope_d_s, d_time_d_s, R0_d_s,
             plot_text_d_s, plot_name_d_s) = linear.compute_slowdown(x_deaths,
                                                                     y_deaths,
                                                                     country,
                                                                     month,
                                                                     deaths=True)
        (poly_x_d, R_d, y_err_d,
         slope_d, d_time_d, R0_d) = linear.get_linear_parameters(
            x_deaths,
            y_deaths
        )

        # refit for last five days
        x_deaths5 = x_deaths[-5:]
        y_deaths5 = y_deaths[-5:]
        (poly_x_d5, R_d5, y_err_d5,
         slope_d5, d_time_d5, R0_d5) = linear.get_linear_parameters(
            x_deaths5,
            y_deaths5
        )

        # check for goodness of fit and reassign data
        # if R_d < R_d5 and R_d5 > 0.9:  ## switch to last 5 days get flat behaviour (20/04)
        (poly_x_d, R_d,
         slope_d, d_time_d, R0_d) = (poly_x_d5, R_d5,
                                     slope_d5, d_time_d5, R0_d5)

        # plot parameters: deaths
        plot_text_d = linear.get_deaths_plot_text(
            slope_d, "bla",
            R_d, d_time_d,
            avg_mort, stdev_mort
        )
        if not d_time_d_s:
            rate_deaths = slope_d
            double_deaths = d_time_d
        else:
            rate_deaths = slope_d_s
            double_deaths = d_time_d_s

    s1 = s2 = s3 = 1e-20
    variable_pack = (
        x_cases, y_cases, x_slow, y_slow,
        cases, deaths, x_deaths, deaths,
        y_deaths, poly_x, poly_x_s, poly_x_d,
        y_err, y_err_d, plot_text, plot_text_s,
        plot_text_d, plot_name, slope_d, slope
    )
    if country not in SLOWDOWN_DEATHS:
        make_evolution_plot(variable_pack, country, SLOWDOWN,
                            SLOWDOWN_DEATHS, month_str)
        if deaths and len(deaths) >= 3.0:
            (s1, s2, s3, sim10_0, sim10_1, sim10_2, sim10_3, sim10_4,
             sim20_0, sim20_1, sim20_2, sim20_3, sim20_4) = \
                make_simulations_plot(variable_pack, country,
                                      SLOWDOWN, SLOWDOWN_DEATHS,
                                      month_str)
    else:
        slowdown_deaths = (x_deaths, y_deaths, x_deaths_slow, y_deaths_slow,
                           poly_x_d_s, R_d_s, y_err_d_s,
                           slope_d_s, d_time_d_s, R0_d_s,
                           plot_text_d_s, plot_name_d_s)
        make_evolution_plot(variable_pack, country, SLOWDOWN,
                            SLOWDOWN_DEATHS,
                            month_str, slowdown_deaths)
        if deaths and len(deaths) >= 3.0:
            (s1, s2, s3, sim10_0, sim10_1, sim10_2, sim10_3, sim10_4,
             sim20_0, sim20_1, sim20_2, sim20_3, sim20_4) = \
                make_simulations_plot(variable_pack, country, SLOWDOWN,
                                      SLOWDOWN_DEATHS, month_str,
                                      slowdown_deaths)

    # write to table file
    if country in COUNTRY_PARAMS:
        iso_country = COUNTRY_PARAMS[country][0]
        pop = COUNTRY_PARAMS[country][1]
        cs = str(int(cases[-1]))
        if deaths:
            ds = str(int(deaths[-1]))
        else:
            ds = '0'
        br = "%.0f" % (rate_cases * 100.)
        mr = "%.0f" % (rate_deaths * 100.)
        dc = "%.1f" % double_cases
        dd = "%.1f" % double_deaths
        f1 = "%.2f" % (s1 / 1000. / pop * 100.)
        f2 = "%.2f" % (s2 / 1000. / pop * 100.)
        f3 = "%.2f" % (s3 / 1000. / pop * 100.)
        f10_1 = "%.2f" % (sim10_0 / 1000. / pop * 100.)
        f10_2 = "%.2f" % (sim10_1 / 1000. / pop * 100.)
        f10_3 = "%.2f" % (sim10_2 / 1000. / pop * 100.)
        f20_1 = "%.2f" % (sim20_0 / 1000. / pop * 100.)
        f20_2 = "%.2f" % (sim20_1 / 1000. / pop * 100.)
        f20_3 = "%.2f" % (sim20_2 / 1000. / pop * 100.)
        xs1 = str(int(s1))
        xs2 = str(int(s2))
        xs3 = str(int(s3))
        fs1 = "%.1f" % (cases[-1] / s1 * 100.)
        fs2 = "%.1f" % (cases[-1] / s2 * 100.)
        fs3 = "%.1f" % (cases[-1] / s3 * 100.)
        data_line = ",".join([iso_country,
                              country,
                              cs,
                              ds,
                              br,
                              mr,
                              dc,
                              dd,
                              f1, f2, f3,
                              xs1, xs2, xs3,
                              fs1, fs2, fs3,
                              f10_1, f10_2, f10_3,
                              f20_1, f20_2, f20_3]) + '\n'
        with open(table_file, "a") as file:
            file.write(data_line)
        with open("country_tables/countries_with_case_doubling-time_larger_14days.csv", "a") as file:
            if float(dc) >= 14.:
                file.write(country + "," + dc + "\n")


    return Pdt, Pr0, [pr - 0.5 for pr in Pr], (np.array(cases), np.array(deaths))




def make_simulations_plot(variable_pack, country,
                          SLOWDOWN, SLOWDOWN_DEATHS,
                          month_str, slowdown_deaths=None):
    # get variable pack
    (x_data, y_data, x_slow, y_slow, y_data_real, y_deaths_real,
     x_deaths, y_deaths_real, y_deaths, poly_x, poly_x_s,
     poly_x_d, y_err, y_err_d, plot_text, plot_text_s,
     plot_text_d, plot_name, slope_d, slope) = variable_pack

    if slowdown_deaths is not None:
        (x_deaths, y_deaths, x_deaths_slow, y_deaths_slow,
         poly_x_d_s, R_d_s, y_err_d_s,
         slope_d_s, d_time_d_s, R0_d_s,
         plot_text_d_s, plot_name_d_s) = slowdown_deaths
        x_deaths = np.append(x_deaths, x_deaths_slow)
        y_deaths = np.append(y_deaths, y_deaths_slow)
        poly_x_d = np.append(poly_x_d, poly_x_d_s)
        y_err_d = np.append(y_err_d, y_err_d_s)

    # extract last points for dsiplay
    curr_case = y_data_real[-1]
    curr_death = y_deaths_real[-1]

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
    # correction: 20 days is probably more realistic
    if slowdown_deaths is not None:
        slope_sim = slope_d_s  # / 2.0 when rates halfen roughly
        if slope_sim > 0.15:
            slope_sim = slope_sim / 2.0
    else:
        slope_sim = slope_d  # / 2.0 when rates halfen roughly
        if slope_sim > 0.05:
            slope_sim = slope_sim / 2.0
    # 14 day delay between infection and death
    sim_y_0_f = sim_y_0_real[-1] * np.exp(14. * slope_sim)
    sim_y_1_f = sim_y_1_real[-1] * np.exp(14. * slope_sim)
    sim_y_2_f = sim_y_2_real[-1] * np.exp(14. * slope_sim)
    sim_y_3_f = sim_y_3_real[-1] * np.exp(14. * slope_sim)
    sim_y_4_f = sim_y_4_real[-1] * np.exp(14. * slope_sim)

    # 10 day delay between infection and death
    sim10_0 = sim_y_0_real[-1] * np.exp(10. * slope_sim)
    sim10_1 = sim_y_1_real[-1] * np.exp(10. * slope_sim)
    sim10_2 = sim_y_2_real[-1] * np.exp(10. * slope_sim)
    sim10_3 = sim_y_3_real[-1] * np.exp(10. * slope_sim)
    sim10_4 = sim_y_4_real[-1] * np.exp(10. * slope_sim)

    # 20 day delay between infection and death
    sim20_0 = sim_y_0_real[-1] * np.exp(20. * slope_sim)
    sim20_1 = sim_y_1_real[-1] * np.exp(20. * slope_sim)
    sim20_2 = sim_y_2_real[-1] * np.exp(20. * slope_sim)
    sim20_3 = sim_y_3_real[-1] * np.exp(20. * slope_sim)
    sim20_4 = sim_y_4_real[-1] * np.exp(20. * slope_sim)

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
    if len(poly_x) == 5:
        plt.plot(x_data[-5:], poly_x, '--r')
    else:
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
    plt.plot([list(np.array(x_deaths) - 14.)[-1], x_deaths[-1]], [sim_y_0[-1], np.log(sim_y_0_f)], '--b')
    plt.plot([list(np.array(x_deaths) - 14.)[-1], x_deaths[-1]], [sim_y_1[-1], np.log(sim_y_1_f)], '--g')
    plt.plot([list(np.array(x_deaths) - 14.)[-1], x_deaths[-1]], [sim_y_2[-1], np.log(sim_y_2_f)], '--r')
    plt.plot([list(np.array(x_deaths) - 14.)[-1], x_deaths[-1]], [sim_y_3[-1], np.log(sim_y_3_f)], '--c')
    plt.plot([list(np.array(x_deaths) - 14.)[-1], x_deaths[-1]], [sim_y_4[-1], np.log(sim_y_4_f)], '--m')
    if len(poly_x_d) == 5:
        plt.plot(x_deaths[-5:], poly_x_d, '--b')
    else:
        plt.plot(x_deaths, poly_x_d, '--b')
    plt.errorbar(x_data, y_data, yerr=y_err, fmt='o', color='r')
    plt.errorbar(x_deaths, y_deaths, yerr=y_err_d, fmt='v', color='b')
    plt.plot(np.array(x_deaths) - 14., sim_y_0, label="M=0.5%")
    plt.plot(np.array(x_deaths) - 14., sim_y_1, label="M=1%")
    plt.plot(np.array(x_deaths) - 14., sim_y_2, label="M=2%")
    plt.plot(np.array(x_deaths) - 14., sim_y_3, label="M=3%")
    plt.plot(np.array(x_deaths) - 14., sim_y_4, label="M=4%")
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
    plt.annotate(str(int(sim_y_4_real[-1])),xy=(x_deaths[-1]-20,sim_y_4[-1]))
    plt.annotate(str(int(sim_y_0_real[-1])),xy=(x_deaths[-1]-20,sim_y_0[-1]))
    plt.annotate(str(int(sim_y_1_real[-1])),xy=(x_deaths[-1]-20,sim_y_1[-1]))
    plt.annotate(str(int(sim_y_2_real[-1])),xy=(x_deaths[-1]-20,sim_y_2[-1]))
    plt.annotate(str(int(sim_y_3_real[-1])),xy=(x_deaths[-1]-20,sim_y_3[-1]))
    plt.xlabel("Time [days, starting {} 1st, 2020]".format(month_str))
    plt.ylabel("Cumulative no. of deaths and reported and simulated cases")
    plt.title("COVID-19 in {} starting {} 1, 2020\n".format(country, month_str) + \
              "Sim cases are based on mortality fraction M and delayed by 14 days\n" + \
              "Sim cum. no. cases: rep. deaths x 1/M; rate=current death rate (0.5 x current death rate if > 5%)",
              fontsize=10)

    plt.savefig(os.path.join("country_plots",
                             "COVID-19_LIN_{}_SIM_CASES.png".format(country)))
    plt.close()

    # do full 10-day running projection
    # with initial conditions on March 21
    # only for March
    do_plot = False
    if country == "UK" and month_str == 'March' and do_plot:
        # projection data and ticks
        x0, y0, y0d, y, yd, y_min, yd_min = uk.compute_initial_projection_uk()
        log_ticks = [np.log(y0), np.log(y), np.log(y0d), np.log(yd),
                     np.log(y_min), np.log(yd_min), np.log(curr_case),
                     np.log(curr_death)]
        real_ticks = [int(y0), int(y), int(y0d), int(yd),
                      int(y_min), int(yd_min), int(curr_case),
                      int(curr_death)]

        # if slowdown
        if country in SLOWDOWN:
            plt.axvline(SLOWDOWN[country], linewidth=2, color='orange')
            plt.scatter(x_slow, y_slow, color='darkolivegreen', marker='s',
                        label="Daily Cases Slower")
            plt.plot(x_slow, poly_x_s, linestyle='-', color='darkolivegreen')
        plt.scatter((x0, x0 + 10.), (np.log(y0), np.log(y)),
                    color='k', label="Worst Cases Proj")
        plt.scatter((x0, x0 + 10.), (np.log(y0), np.log(y_min)),
                    color='g', label="Best Cases Proj")

        # plot projections
        plt.scatter((x0, x0 + 10.), (np.log(y0d), np.log(yd)), marker='v',
                    color='k', label="Worst Death Proj")
        plt.scatter((x0, x0 + 10.), (np.log(y0d), np.log(yd_min)), marker='v',
                    color='g', label="Best Death Proj")
        plt.plot((x0, x0 + 10.), (np.log(y0), np.log(y)), "--k")
        plt.plot((x0, x0 + 10.), (np.log(y0), np.log(y_min)), "--g")
        plt.plot((x0, x0 + 10.), (np.log(y0d), np.log(yd)), "--k")
        plt.plot((x0, x0 + 10.), (np.log(y0d), np.log(yd_min)), "--g")

        # plot reported evolving numbers
        plt.scatter(x_data, y_data, color='r',
                    label="Cases")  # reported cases
        if len(poly_x) == 5:
            plt.plot(x_data[-5:], poly_x, '--r')
        else:
            plt.plot(x_data, poly_x, '--r')
        plt.scatter(x_deaths, y_deaths, marker='v',
                    color='b', label="Deaths")  # reported deaths
        if len(poly_x_d) == 5:
            plt.plot(x_deaths[-5:], poly_x_d, '--b')
        else:
            plt.plot(x_deaths, poly_x_d, '--b')

        # plot anciliaries
        plt.xlim(0., x0 + 11.5)
        plt.yticks(log_ticks, real_ticks)
        plt.tick_params(axis="y", labelsize=7)
        plt.xlabel("Time [days, starting March 1st, 2020]")
        plt.ylabel("Cumulative no. of deaths and reported and simulated cases")
        plt.grid()
        plt.annotate("Pubs", xy=(20.5, 0.9), color='red')
        plt.annotate("shut", xy=(20.5, 0.6), color='red')
        plt.annotate("Lockdown", xy=(23.5, 3.6), color='red')
        plt.annotate("London:", xy=(20.5, np.log(y0) - 0.25),
                     color='red', fontsize=8)
        plt.annotate("2000", xy=(20.5, np.log(y0) - 0.5),
                     color='red', fontsize=8)
        plt.annotate("London: 2872", xy=(23.5, np.log(y0)),
                     color='red', fontsize=8)
        plt.legend(loc="lower right", fontsize=9)
        plt.text(1., y_slow[-1] + 0.3, plot_text_s, fontsize=8, color='darkolivegreen')
        plt.text(1., y_data[-1] - 0.7, plot_text, fontsize=8, color='r')
        plt.text(1., y_data[-1] - 2.4, plot_text_d, fontsize=8, color='b')
        plt.axvline(20, color="red")
        plt.axvline(23, color="red")
        plt.suptitle("COVID-19 in {} starting {} 1, 2020 spun up 10 days\n".format(country, month_str) + \
                     "Worst case: March 21 rates b=0.25/DT=2.8d (R=0.99) and m=0.37/DT=1.9d (R=0.97)",
                     fontsize=10)
        plt.title("Best case: quarantine rates b=m=0.2", color='green', fontsize=10)
        plt.savefig(os.path.join("country_plots",
                                 "COVID-19_LIN_{}_DARK_SIM_UK.png".format(country)))
        plt.close()

    if country == "UK" and month_str == "April":
        x0, y0, y0d, y, yd, y_min, yd_min = uk.compute_first_april_projection_uk()
        log_ticks = [np.log(y0), np.log(y), np.log(y0d), np.log(yd),
                     np.log(y_min), np.log(yd_min), np.log(curr_case),
                     np.log(curr_death), np.log(20000.)]
        real_ticks = [int(y0), int(y), int(y0d), int(yd),
                      int(y_min), int(yd_min), int(curr_case),
                      int(curr_death), 20000.]
        plt.scatter((x0, x0 + 10.), (np.log(y0), np.log(y)),
                    color='k', label="Worst Cases Proj")
        plt.scatter((x0, x0 + 10.), (np.log(y0), np.log(y_min)),
                    color='g', label="Best Cases Proj")
        # plot projections
        plt.scatter((x0, x0 + 10.), (np.log(y0d), np.log(yd)), marker='v',
                    color='k', label="Worst Death Proj")
        plt.scatter((x0, x0 + 10.), (np.log(y0d), np.log(yd_min)), marker='v',
                    color='g', label="Best Death Proj")
        plt.plot((x0, x0 + 10.), (np.log(y0), np.log(y)), "--k")
        plt.plot((x0, x0 + 10.), (np.log(y0), np.log(y_min)), "--g")
        plt.plot((x0, x0 + 10.), (np.log(y0d), np.log(yd)), "--k")
        plt.plot((x0, x0 + 10.), (np.log(y0d), np.log(yd_min)), "--g")

        # plot reported evolving numbers
        plt.scatter(x_data, y_data, color='r',
                    label="Cases")  # reported cases
        if len(poly_x) == 5:
            plt.plot(x_data[-5:], poly_x, '--r')
        else:
            plt.plot(x_data, poly_x, '--r')
        plt.scatter(x_deaths, y_deaths, marker='v',
                    color='b', label="Deaths")  # reported deaths
        if len(poly_x_d) == 5:
            plt.plot(x_deaths[-5:], poly_x_d, '--b')
        else:
            plt.plot(x_deaths, poly_x_d, '--b')

        # plot anciliaries
        plt.xlim(0., x0 + 21.5)
        plt.yticks(log_ticks, real_ticks)
        plt.tick_params(axis="y", labelsize=7)
        plt.xlabel("Time [days, starting April 1st, 2020]")
        plt.ylabel("Cumulative no. of deaths and reported and simulated cases")
        plt.grid()
        plt.annotate("20 days from Lockdown", xy=(11.1, y_data[0]), color='red')
        plt.annotate("Daily growth rates for deaths April 11-21:",
                     xy=(11.1, np.log(6100.)), color='darkblue', fontsize=8)
        plt.annotate("0.12/0.10/0.09/0.07/0.07/0.06/0.06/0.06/0.06/0.06/0.04",
                     xy=(11.1, np.log(5300.)), color='darkblue', fontsize=8)
        plt.annotate("Daily growth rates for deaths April 04-10:",
                     xy=(11.1, np.log(4700.)), color='royalblue', fontsize=8)
        plt.annotate("0.20/0.19/0.17/0.16/0.15/0.15/0.13",
                     xy=(11.1, np.log(4100.)), color='royalblue', fontsize=8)
        plt.legend(loc="lower right", fontsize=9)
        plt.text(1., y_data[-9] + 0.5, plot_text, fontsize=8, color='r')
        plt.text(1., y_data[-4] - 1.9, plot_text_d, fontsize=8, color='b')
        plt.axvline(11., color="red")
        plt.axvline(19., color='k')
        plt.axhline(np.log(20000.), color='darkred')
        plt.suptitle("COVID-19 in {} starting {} 1, 2020 spun up 10 days\n".format(country, month_str) + \
                     "Worst: April 10 rates b=0.08/DoublTime=8.9d (R=0.99) and m=0.12/DoublTime=5.6d (R=0.99)",
                     fontsize=10)
        plt.title("Best: b=m=0.05 (DoublTime=14 days, R=1)", color='green', fontsize=10)
        plt.savefig(os.path.join("country_plots",
                                 "COVID-19_LIN_{}_DARK_SIM_UK.png".format(country)))
        plt.close()

    return (sim_y_0_f, sim_y_1_f, sim_y_2_f, sim10_0, sim10_1, sim10_2, sim10_3, sim10_4,
            sim20_0, sim20_1, sim20_2, sim20_3, sim20_4)


def _read_write_parameter(filename, parameter, stddev_parameter):
    """Read doubling time from record."""
    # eg filename="country_data/mean_doubling_time", parameter=mean_dt
    # stddev_parameter=np.std(parameter)
    with open(filename, "r") as file:
        data_lines = [c.split(' ')[0] for c in file.readlines()]
    with open(filename, "a") as file:
        if str(parameter) not in data_lines:
            file.write(str(parameter) + ' ' + str(stddev_parameter) + "\n")


def plot_parameters(doubling_time, basic_reproductive,
                    lin_fit_quality, no_countries):
    """Plot simple viral infection parameters."""
    plt.hist(doubling_time, bins=20, color='darkolivegreen',
             normed=True, cumulative=False, weights=lin_fit_quality)
    plt.grid()
    plt.xlabel("Cases doubling time [days]")
    plt.ylabel("Number")
    mean_dt = np.mean(doubling_time)
    std_dt = np.std(doubling_time)
    plt.axvline(np.mean(mean_dt), color='red', linestyle='--')
    header = "Cases doubling time [days] for %i countries\n" % no_countries
    mean_text = "%.1f days (+/-%.1f days, standard deviation)" % (mean_dt, std_dt)
    title = header + \
            "Vertical line: mean doubling time: " + \
            mean_text + '\n' + \
            "weighted by quality of fit $f=R^2-0.5$; incl.some US states"
    plt.title(title, fontsize=10)
    plt.savefig(os.path.join("country_plots", "Histogram_Doubling_Time.png"))
    plt.close()

    # append historical data
    _read_write_parameter("country_data/mean_doubling_time", mean_dt, std_dt)

    R_0 = [c * 10. for c in basic_reproductive]
    plt.hist(R_0, bins=20, color='darkolivegreen',
             normed=True, cumulative=False, weights=lin_fit_quality)
    plt.grid()
    plt.xlabel("Basic Reproductive Number")
    plt.ylabel("Number")
    mean_r0 = np.mean(R_0)
    std_r0 = np.std(R_0)
    plt.axvline(mean_r0, color='red', linestyle='--')
    header = "Basic reproductive number $R_0$ for %i countries\n" % no_countries
    mean_title = \
        "%.1f (+/-%.1f, standard deviation)\n" % (mean_r0, std_r0)
    title = header + \
            "Vertical line: mean $R_0$: " + \
            mean_title + \
            "Avg infectious phase 10 days; weighted by quality of fit $f=R^2-0.5$; incl.some US states"
    plt.title(title, fontsize=8)
    plt.savefig(os.path.join("country_plots",
                             "Histogram_Basic_Reproductive_Number.png"))
    # append historical data
    _read_write_parameter("country_data/basic_reproductive_number",
                          mean_r0, std_r0)

    # record data at fixed 10-day intervals
    # TODO uncomment every 10 days
    with open("country_data/DT_27-03-2020", "w") as file:
        for dt in doubling_time:
            file.write(str(dt) + "\n")
    with open("country_data/R0_27-03-2020", "w") as file:
        for r0 in R_0:
            file.write(str(r0) + "\n")

    plt.close()


def _get_geography(arg):
    """Parse args to get either countries or regions."""
    if not os.path.isfile(arg):
        geographies = arg.split(",")
    else:
        with open(arg, "r") as file:
            geographies = [coun.strip() for coun in file.readlines()]

    return geographies


def plot_doubling(cases_dt, deaths_dt, current_range, country):
    """Plot doubling times for cases and deaths per country."""
    plt.scatter(current_range, cases_dt, marker='o', color='r', label='Case doubling time')
    plt.scatter(current_range, deaths_dt, marker='v', color='b', label='Deaths doubling time')
    plt.plot(current_range, cases_dt, color='r')
    plt.plot(current_range, deaths_dt, color='b')
    header = "Cases/Deaths doubling time [days] for {}".format(country)
    plt.title(header, fontsize=10)
    plt.xlabel("Day in April")
    plt.ylabel("Doubling times [days]")
    plt.axhline(14., color='k', linestyle='--')
    plt.semilogy()
    cas = [float(r) for r in cases_dt]
    det = [float(r) for r in deaths_dt]
    cas.extend(det)
    plt.yticks(cas, cas)
    plt.tick_params(axis="y", labelsize=8)
    plt.ylim(3., 15.)
    plt.grid()
    plt.legend(loc="lower left", fontsize=8)
    plt.savefig(os.path.join("country_plots",
                             "COVID-19_Doubling_Times_{}.png".format(country)))
    plt.close()


def plot_rolling_average(nums_deaths, n=7):
    """Plot a 3-day rolling average of numbers of deaths."""
    analyzed_countries = ["UK", "France", "Germany", "US",
                          "Spain", "Italy", "Netherlands",
                          "Belgium", "Romania", "Sweden", "Norway",
                          "Switzerland", "Canada"]
    country_colors = {"UK":"k", "France":"b", "Germany":"r", "US":"c",
                      "Spain":"m", "Italy":"y", "Netherlands":"g",
                      "Belgium":"lime", "Romania":"orange", "Sweden":"gray", "Norway":"maroon",
                      "Switzerland":"teal", "Canada":"darkslategrey"}
    len_windows = []
    for country, deaths in nums_deaths.items():
        if country in analyzed_countries:
            if country == "UK":
                deaths = np.loadtxt("country_data/UK_deaths_history")
            deaths = list(sorted([d for d in deaths if d > 5.]))
            deaths = [deaths[i + 1] - deaths[i] for i in range(len(deaths) - 1)]
            ret = np.cumsum(deaths, dtype=float)
            ret[n:] = ret[n:] - ret[:-n]
            rolling_avg = ret[n - 1:] / n
            plt.plot(range(len(rolling_avg)), rolling_avg,
                     color=country_colors[country], label=country)
            plt.annotate(country, xy=(len(rolling_avg) + 0.05,
                                      rolling_avg[-1]), fontsize=8)
            len_windows.append(len(rolling_avg))

    header = "7-day rolling average for daily no. of deaths increase (March and April) starting at min=5".format(country)
    plt.title(header, fontsize=10)
    plt.xlabel("Rolling window midpoint [day]")
    plt.ylabel("7-day rolling window average daily no of deaths")
    plt.semilogy()
    plt.xlim(0, max(len_windows) + 3)
    plt.grid()
    plt.savefig(os.path.join("country_plots",
                             "COVID-19_Deaths_Rolling_Average.png"))
    plt.close()

    for country, deaths in nums_deaths.items():
        if country in analyzed_countries:
            if country == "UK":
                deaths = np.loadtxt("country_data/UK_deaths_history")
            deaths = list(sorted([d for d in deaths if d > 5.]))
            deaths = [deaths[i + 1] - deaths[i] for i in range(len(deaths) - 1)]
            cp = COUNTRY_PARAMS[country][1]
            deaths_per_capita = [d / cp for d in deaths]
            ret_pc = np.cumsum(deaths_per_capita, dtype=float)
            ret_pc[n:] = ret_pc[n:] - ret_pc[:-n]
            rolling_avg_pc = ret_pc[n - 1:] / n
            plt.plot(range(len(rolling_avg_pc)), rolling_avg_pc,
                     color=country_colors[country], label=country)
            plt.annotate(country, xy=(len(rolling_avg_pc) + 0.05,
                                      rolling_avg_pc[-1]), fontsize=8)

    header = "7-day rolling average for daily no. of deaths increase (March and April) starting at min=5".format(country)
    subheader = '\n Proportion of each 1,000 of country population (equiv. to per thousand)'
    plt.title(header + subheader, fontsize=10)
    plt.xlabel("Rolling window midpoint [day]")
    plt.ylabel("7-day rolling window average daily no of deaths per 1k of population")
    plt.semilogy()
    plt.xlim(0, max(len_windows) + 3)
    plt.grid()
    plt.legend(loc="lower right", fontsize=8)
    plt.savefig(os.path.join("country_plots",
                             "COVID-19_Deaths_Rolling_Average_per_Population.png"))
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
    parser.add_argument('-r',
                        '--regions',
                        type=str,
                        default=None,
                        help='List OR file with list of regions or US states.')
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

    countries = _get_geography(args.countries)
    if not args.regions:
        regions = []
    else:
        regions = _get_geography(args.regions)

    # write summary files
    today_date = datetime.today().strftime('%m-%d-%Y')
    today_day = today_date.split("-")[1]
    header = "Country,country-name,cases,deaths,case rate,death rate," + \
             "doubling cases (days),doubling deaths (days)," + \
             "pct pop 0.5% mort,prct pop 1% mort,prct pop 2% " +  \
             "mort,0.5% mort sim cases,1% mort sim cases," + \
             "2% mort sim cases," + \
             "prct rep cases 0.5% mort,prct rep cases 1% mort," + \
             "prct rep cases 2% mort," + \
             "pct pop 0.5% mort (10d),prct pop 1% mort (10d),prct pop 2% (10d)," +  \
             "pct pop 0.5% mort (20d),prct pop 1% mort (20d),prct pop 2% (20d) "
    table_file = \
        "country_tables/ALL_COUNTRIES_DATA_{}-0{}-2020.csv".format(today_day,
                                                                   args.month)
    with open(table_file, "w") as file:
        file.write(header + "\n")
    # write pointer file
    raw_date = "date={}-0{}-2020".format(today_day, args.month)
    raw_content = "url=https://raw.githubusercontent.com/" + \
                  "valeriupredoi/" + \
                  "COVID-19_LINEAR/master/country_tables/" + \
                  "ALL_COUNTRIES_DATA_{}-0{}-2020.csv".format(today_day,
                                                              args.month)
    raw_file = "country_tables/currentdata.inc"
    with open(raw_file, "w") as file:
        file.write(raw_date + '\n' + raw_content)

    with open("country_tables/countries_with_case_doubling-time_larger_14days.csv", "w") as file:
        file.write("Country,doubling time (days)\n")

    # plot other countries
    double_time = []
    basic_rep = []
    lin_fit_quality = []
    nums_cases = {}
    nums_deaths = {}
    all_nums_deaths = {}
    for country in countries:
        monthly_numbers = get_monthly_countries_data(country,
                                                     args.month,
                                                     region=False)
        monthly_numbers_prev_month = get_monthly_countries_data(country,
                                                                args.month - 1,
                                                                region=False)
        d_time, R0, lin_fit, nums = plot_countries(monthly_numbers,
                                                   args.month, country,
                                                   table_file,
                                                   download)
        double_time.extend(d_time)
        basic_rep.extend(R0)
        lin_fit_quality.extend(lin_fit)
        nums_cases[country] = nums[0]
        nums_deaths[country] = nums[1]
        all_nums_deaths[country] = nums[1]
        prev_month_deaths = [
            float(s) for s in monthly_numbers_prev_month[1] if s != 'NN'
        ]
        all_nums_deaths[country] = np.hstack((all_nums_deaths[country],
                                              prev_month_deaths))
        current_range = range(4, int(today_day) + 1)
        cases_dt = []
        deaths_dt = []
        for d in current_range:
            if d < 10:
                dat_file = "country_tables/ALL_COUNTRIES_DATA_0{}-04-2020.csv".format(d)
            else:
                dat_file = "country_tables/ALL_COUNTRIES_DATA_{}-04-2020.csv".format(d)
            with open(dat_file, "r") as file:
                content = file.readlines()
                for line in content:
                    if line.split(",")[1] == country:
                        cases_dt.append(line.split(",")[6])
                        deaths_dt.append(line.split(",")[7])
        if len(cases_dt) == len(current_range):
            plot_doubling(cases_dt, deaths_dt, current_range, country)
                
    if regions:
        for region in regions:
            monthly_numbers = get_monthly_countries_data(region,
                                                         args.month,
                                                         region=True)
            d_timeR, R0R, lin_fitR, nums = plot_countries(monthly_numbers,
                                                          args.month, region,
                                                          table_file,
                                                          download=False)
            double_time.extend(d_timeR)
            basic_rep.extend(R0R)
            lin_fit_quality.extend(lin_fitR)

    # plot viral parameters
    plot_parameters(double_time, basic_rep, lin_fit_quality, len(countries))
    ks.kstest(nums_cases, nums_deaths)
    plot_rolling_average(all_nums_deaths)


if __name__ == '__main__':
    main()
