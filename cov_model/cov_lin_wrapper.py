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
from itertools import groupby

from datafinder.data_finder import (COUNTRIES_TO_SUM,
    get_monthly_countries_data, get_official_uk_data)
from statsanalysis import (linear, ks, country_parameters)
from projections import uk


COUNTRY_PARAMS = country_parameters.COUNTRY_PARAMS

def make_evolution_plot(variable_pack, country, month_str):
    """Make the exponential evolution plot."""
    # unpack variables
    (x_cases, y_cases, x_slow, y_slow, cases, deaths,
     x_deaths, deaths, y_deaths, poly_x, poly_x_s,
     poly_x_d, y_err, y_err_d, plot_text, plot_text_s,
     plot_text_d, plot_name, slope_d, slope,
     march0, april0, may0) = variable_pack

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
    if deaths:
        plt.scatter(x_deaths, y_deaths, marker='v',
                    color='b', label="Daily Deaths")
        if len(poly_x_d) == 5:
            plt.plot(x_deaths[-5:], poly_x_d, '--b')
        else:
            plt.plot(x_deaths, poly_x_d, '--b')

    #plt.errorbar(x_cases, y_cases, yerr=y_err, fmt='o', color='r')
    #if deaths:
    #    plt.errorbar(x_deaths, y_deaths, yerr=y_err_d, fmt='v', color='b')
    plt.grid()
    if not deaths:
        plt.xlim(0., x_cases[-1] + 1.5)
        plt.ylim(0., y_cases[-1] + 3.5)
    else:
        plt.xlim(0., x_cases[-1] + 1.5)
        plt.ylim(y_deaths[0] - 2., y_cases[-1] + 3.5)
    linear.common_plot_stuff(plt, country, month_str)
    if country == "UK":
        plt.axvline(march0 + 20, linestyle="--", color='r', label="LOCKDOWN")
        main_p_x, main_R, _, main_slope, main_dtime, _ = linear.get_linear_parameters(
            x_deaths[8:22],
            y_deaths[8:22])
        plt.plot(x_deaths[8:22], main_p_x, '--k')
        plot_text_uk = \
            "Main exponential phase UK Hospitals\n" + \
            "------------------------------------------------------\n" + \
            "Duration: approx. until April 4 (deaths), March 20 (cases)\n" + \
            "Exponential rate $b=$%.2f day$^{-1}$; doubling time %.2f days\n" % (main_slope, main_dtime) + \
            "Fit quality ($R^2$) %.2f (perfect fit for 14 points)\n" % main_R
        plt.text(35., np.log(10.), plot_text_uk, fontsize=9, color='k')
        # lockdown 10 days before
        minimized_deaths = [d / 7. for d in deaths[22:]]
        sim_d_y = list(deaths[:12])
        sim_d_y.extend(minimized_deaths)
        dx = [x_deaths[12] + i for i in range(len(sim_d_y) - 12)]
        sim_d_x = list(x_deaths[:12])
        sim_d_x.extend(dx)
        plt.scatter(sim_d_x, np.log(sim_d_y), marker='x',
                    color='g', label="Daily Deaths LOCKDOWN 10d Early")
        curr_deaths = deaths[-1] / 7. + .3 * deaths[-1] / 7.
        green_deaths = "If lockdown on 11 March: current number of deaths would be: %i" % int(curr_deaths)
        plt.text(22., np.log(5.), green_deaths, fontsize=10, color='g')
        plt.axhline(np.log(curr_deaths), linestyle="--", color='g')
    plt.axvline(march0, linestyle="--", color='k')
    plt.axvline(april0, linestyle="--", color='k')
    plt.axvline(may0, linestyle="--", color='k')
    plt.text(1., y_cases[-1] + 0.3, plot_text, fontsize=8, color='r')
    if deaths:
        plt.text(1., y_cases[-1] - 2.1, plot_text_d, fontsize=8, color='b')
    plt.legend(loc="lower left", fontsize=7)
    plt.yticks(last_tick, [np.int(y01) for y01 in last_tick_real])
    plt.tick_params(axis="y", labelsize=8)

    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country, plot_name))
    plt.close()


def plot_countries(datasets, months, country, table_file, download):
    """Plot countries data."""
    # set correct months labels
    if len(months) == 1:
        if months[0] == 3:
            month_str = "March"
        elif months[0] == 4:
            month_str = "April"
    else:
        month_str = "March-April-May"

    # filter data lists
    cases = [float(c) for c in datasets[0] if c != 'NN']
    deaths = [float(c) for c in datasets[1] if c != 'NN']
    deaths = [d for d in deaths if d > 0.]
    recs = [float(c) for c in datasets[2] if c != 'NN']

    if country != "UK":
        time_fmt = "%Y-%m-%dT%H:%M:%S"
        actual_days = [
            datetime.strptime(c, time_fmt).day
            for c in datasets[3] if c != 'NN'
        ]
        actual_months = [
            datetime.strptime(c, time_fmt).month
            for c in datasets[3] if c != 'NN'
        ]

        days_list = []
        day_march = [d for d, m in zip(actual_days, actual_months) if m == 3]
        day_april = [d + 31 for d, m in zip(actual_days, actual_months) if m == 4]
        day_may = [d + 61 for d, m in zip(actual_days, actual_months) if m == 5]
        # add to x-axis
        days_list.extend(day_march)
        days_list.extend(day_april)
        days_list.extend(day_may)
        # starts of months
        march0 = 1
        april0 = 32
        may0 = 62

        # pad for unavailable data from 1st of month
        if actual_days[0] != 1 and actual_days[0] < 15:
            dt_march = actual_days[0] - 1
            x_cases = [float(n) + dt_march for n in range(1, len(days_list) + 1)]
        else:
            x_cases = [float(n) for n in range(1, len(cases) + 1)]

        # x-axis for deaths
        x_deaths = [float(n) for n in range(int(x_cases[-1]) - len(deaths) + 1,
                                            int(x_cases[-1]) + 1)]

    # UK specific data
    if country == "UK":
        x_cases, cases, x_deaths, deaths, avg_mort, stdev_mort = \
            [], [], [], [], [], []
        for month in months:
            (x_casesi, casesi, x_deathsi,
             deathsi, avg_morti,
             stdev_morti) = get_official_uk_data(month, download)
            x_cases.extend(x_casesi)
            cases.extend(casesi)
            x_deaths.extend(x_deathsi)
            deaths.extend(deathsi)
            avg_mort.append(avg_morti)
            stdev_mort.append(stdev_morti)
            march0 = 1
            april0 = 31
            may0 = 62

        x_cases = [float(n) for n in range(1, len(cases) + 1)]
        x_deaths = [float(n) for n in range(int(x_cases[-1]) - len(deaths) + 1,
                                            int(x_cases[-1]) + 1)]

        avg_mort = np.mean(avg_mort)
        stdev_mort = np.mean(stdev_mort)

    # log data
    y_cases = np.log(cases)
    y_deaths = np.log(deaths)

    # statistics
    Pdt = []
    Pr0 = []
    Pr = []
    x_slow = y_slow = poly_x_s = y_err_s = slope_s = \
        d_time_s = R0_s = R_s = plot_text_s = plot_name_s = None

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
                                                months[-1])

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
        plot_text_d, plot_name, slope_d, slope,
        march0, april0, may0
    )

    # call plotting routines
    make_evolution_plot(variable_pack, country, month_str)
    if deaths and len(deaths) >= 3.0:
        (s1, s2, s3, sim10_0, sim10_1, sim10_2, sim10_3, sim10_4,
         sim20_0, sim20_1, sim20_2, sim20_3, sim20_4) = \
            make_simulations_plot(variable_pack, country, month_str)

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




def make_simulations_plot(variable_pack, country, month_str):
    # get variable pack
    (x_data, y_data, x_slow, y_slow, y_data_real, y_deaths_real,
     x_deaths, y_deaths_real, y_deaths, poly_x, poly_x_s,
     poly_x_d, y_err, y_err_d, plot_text, plot_text_s,
     plot_text_d, plot_name, slope_d, slope,
     march0, april0, may0) = variable_pack

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

    # forecast the cases in 14
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
    # plt.errorbar(x_data, y_data, yerr=y_err, fmt='o', color='r')
    # plt.errorbar(x_deaths, y_deaths, yerr=y_err_d, fmt='v', color='b')
    plt.plot(np.array(x_deaths) - 14., sim_y_0, label="M=0.5%")
    plt.plot(np.array(x_deaths) - 14., sim_y_1, label="M=1%")
    plt.plot(np.array(x_deaths) - 14., sim_y_2, label="M=2%")
    plt.plot(np.array(x_deaths) - 14., sim_y_3, label="M=3%")
    plt.plot(np.array(x_deaths) - 14., sim_y_4, label="M=4%")
    plt.grid()
    plt.xlim(0., x_data[-1] + 1.5)
    plt.ylim(0., np.log(sim_y_0_f) + 3.)
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
    plt.axvline(march0, linestyle="--", color='k')
    plt.axvline(april0, linestyle="--", color='k')
    plt.axvline(may0, linestyle="--", color='k')
    plt.xlabel("Time [days, spanning {}, 2020]".format(month_str))
    plt.ylabel("Cumulative no. of deaths and reported and simulated cases")
    plt.title("COVID-19 in {} spanning {}, 2020\n".format(country, month_str) + \
              "Sim cases are based on mortality fraction M and delayed by 14 days\n" + \
              "Sim cum. no. cases: rep. deaths x 1/M; rate=current death rate (0.5 x current death rate if > 5%)",
              fontsize=10)

    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country,
                             "COVID-19_LIN_{}_SIM_CASES.png".format(country)))
    plt.close()

    # do full 10-day running projection
    # with initial conditions on March 21
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

        if not os.path.isdir(os.path.join("country_plots", country)):
            os.makedirs(os.path.join("country_plots", country))

        plt.savefig(os.path.join("country_plots", country,
                                 "COVID-19_LIN_{}_DARK_SIM_UK.png".format(country)))
        plt.close()

    if country == "UK" and month_str == "April":
        x0, y0, y0d, y, yd, y_min, yd_min = uk.compute_first_april_projection_uk()
        log_ticks = [np.log(y0), np.log(y), np.log(y0d), np.log(yd),
                     np.log(y_min), np.log(yd_min), np.log(curr_case),
                     np.log(curr_death), np.log(20000.)]
        real_ticks = [int(y0), int(y), int(y0d), int(yd),
                      int(y_min), int(yd_min), int(curr_case),
                      int(curr_death), 20000]
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

        if not os.path.isdir(os.path.join("country_plots", country)):
            os.makedirs(os.path.join("country_plots", country))

        plt.savefig(os.path.join("country_plots", country,
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

    country = "ALL_COUNTRIES"
    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots",
                             country,
                             "Histogram_Doubling_Time.png"))
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

    country = "ALL_COUNTRIES"
    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country,
                             "Histogram_Basic_Reproductive_Number.png"))
    # append historical data
    _read_write_parameter("country_data/basic_reproductive_number",
                          mean_r0, std_r0)

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
    # raw plot
    plt.scatter(current_range, cases_dt, marker='o', color='r', label='Case doubling time')
    plt.scatter(current_range, deaths_dt, marker='v', color='b', label='Deaths doubling time')
    plt.plot(current_range, cases_dt, color='r')
    plt.plot(current_range, deaths_dt, color='b')

    # rollong average
    n = 7
    # cases rates
    ret_c = np.cumsum(np.array([float(m) for m in cases_dt]), dtype=float)
    ret_c[n:] = ret_c[n:] - ret_c[:-n]
    rolling_avg_c = ret_c[n - 1:] / n

    # death rates
    ret_d = np.cumsum(np.array([float(m) for m in deaths_dt]), dtype=float)
    ret_d[n:] = ret_d[n:] - ret_d[:-n]
    rolling_avg_d = ret_d[n - 1:] / n

    # plot rolling averages
    plt.plot(current_range[6:], rolling_avg_c,
             color='r', linestyle='--', linewidth=5,
             label="Cases DT 7-day RolAvg")
    plt.plot(current_range[6:], rolling_avg_d,
            color='b', linestyle='--', linewidth=5,
            label="Deaths DT 7-day RolAvg")

    # do a linear analysis
    x = current_range[-7:]
    y = np.log(rolling_avg_d[-7:])
    poly_x, R, y_err, slope, d_time, R0 = linear.get_linear_parameters(
        x,
        y)

    DT_now = rolling_avg_d[-1] * np.exp(slope * 14.)
    R_nought = 14. * 1.43 * (np.exp(0.7/DT_now) - 1.0)
    plt.scatter(current_range[-1], DT_now, color="orange", marker=(5, 1), s=70)
    plt.annotate("Fit last seven 7-day RolAvg Deaths DT and project by 14 days",
                 xy=(15., 6.), color='k', fontsize=8)
    plt.annotate("Actual Cases DT %.2f days" % (DT_now),
                 xy=(15., 5.5), color='k', fontsize=8) 
    plt.annotate("Evolution of Deaths DT = C$\exp^{kt}$, k = %.2f day$^{-1}$" % (slope),
                 xy=(15., 5.), color='k', fontsize=8)
    plt.annotate("Line fit coefficient of determination $R =$ %.2f" % (R),
                 xy=(15., 4.5), color='k', fontsize=8)
    plt.annotate("Estimated $R_0 = $ %.2f" % (R_nought),
                 xy=(15., 4.), color='k', fontsize=8)

    header = "Cases/Deaths doubling time [days] for {} / 7-day Rolling Averages".format(country)
    subheader = "\nHorizontal dashed line: 14 days; vertical dashed line: month delimiter; star: actual Cases DT"
    if country == "UK":
        subheader = "\nHorizontal dashed line: 14 days; vertical dashed line: month delimiter" + \
            "\nUK: 29 April: start of reporting deaths from care homes"
    plt.title(header + subheader, fontsize=10)
    plt.xlabel("Days starting April 4th")
    plt.ylabel("Doubling times [days]")
    plt.axhline(14., color='k', linestyle='--')
    plt.axvline(31, linestyle="--", color='k')
    if country == "UK":
        plt.axvline(29, linestyle="--", color='r')
    plt.semilogy()
    cas = [[float(r) for r in cases_dt][-1]]
    det = [[float(r) for r in deaths_dt][-1]]
    cas.extend(det)
    plt.yticks(cas, cas)
    plt.tick_params(axis="y", labelsize=8)
    plt.ylim(3., max(max([float(t) for t in cases_dt]),
                     max([float(t) for t in deaths_dt])) + 5.)
    plt.grid()
    plt.legend(loc="lower left", fontsize=8)

    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country,
                             "COVID-19_Doubling_Times_{}.png".format(country)))
    plt.close()


def plot_R(nums_dt, n=7):
    """Plot a 3-day rolling average of numbers of deaths."""
    analyzed_countries = ["UK", "France", "Germany", "US",
                          "Spain", "Italy", "Netherlands",
                          "Belgium", "Romania", "Sweden", "Norway",
                          "Switzerland", "Canada", "Austria", "Bulgaria"]
    country_colors = {"UK":"k", "France":"b", "Germany":"r", "US":"c",
                      "Spain":"m", "Italy":"y", "Netherlands":"g",
                      "Belgium":"lime", "Romania":"orange", "Sweden":"gray", "Norway":"maroon",
                      "Switzerland":"teal", "Canada":"darkslategrey", "Austria": "tan",
                      "Bulgaria": "fuchsia"}
    len_windows = []
    for country, dt in nums_dt.items():
        if country in analyzed_countries:
            dt = np.array([float(t) for t in dt])
            R = 14. * (np.exp(0.69314 / dt) - 1.)
            plt.plot(range(len(R)), R,
                     color=country_colors[country], label=country)
            #plt.annotate(country, xy=(len(R) + 0.05,
            #                          R[-1]), fontsize=8)

    header = "Reproductive number $R_0 = 14(\exp(ln2/T_d) - 1)$\n"
    sup_header = "where $T_d$ is doubling time for reported cases"
    plt.title(header + sup_header, fontsize=10)
    plt.xlabel("Day [starting April 4th]")
    plt.ylabel("R0")
    plt.axhline(1., linestyle="--", color='r')
    plt.xlim(0, len(R) + 3)
    plt.legend(loc="upper right", fontsize=8)
    plt.grid()

    country = "ALL_COUNTRIES"
    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country,
                             "COVID-19_R0.png"))
    plt.close()


def plot_rolling_average(nums_deaths, n=7):
    """Plot a 3-day rolling average of numbers of deaths."""
    analyzed_countries = ["UK", "France", "Germany", "US",
                          "Spain", "Italy", "Netherlands",
                          "Belgium", "Romania", "Sweden", "Norway",
                          "Switzerland", "Canada", "Austria", "Bulgaria"]
    country_colors = {"UK":"k", "France":"b", "Germany":"r", "US":"c",
                      "Spain":"m", "Italy":"y", "Netherlands":"g",
                      "Belgium":"lime", "Romania":"orange", "Sweden":"gray", "Norway":"maroon",
                      "Switzerland":"teal", "Canada":"darkslategrey",
                      "Austria": "tan", "Bulgaria": "fuchsia"}
    len_windows = []
    for country, deaths in nums_deaths.items():
        if country in analyzed_countries:
            if country == "UK":
                deaths = np.loadtxt("country_data/UK_deaths_history")
            deaths = list(sorted([d for d in deaths if d > 5.]))
            # adjust for ONS correction of 29 April 2020
            # rempve the delta from 28 to 29 April (outlier) and replace with 28 apr value
            deaths = [deaths[i + 1] - deaths[i] for i in range(len(deaths) - 1)]
            if country == "UK":
                deaths[46] = 585.  # keep previous delta
            ret = np.cumsum(deaths, dtype=float)
            ret[n:] = ret[n:] - ret[:-n]
            rolling_avg = ret[n - 1:] / n
            plt.plot(range(len(rolling_avg)), rolling_avg,
                     color=country_colors[country], label=country)
            plt.annotate(country, xy=(len(rolling_avg) + 0.05,
                                      rolling_avg[-1]), fontsize=8)
            len_windows.append(len(rolling_avg))

    header = "7-day rolling average for daily no. of deaths increase starting at min=5"
    subheader = "\nUK: 29/04 correction from ONS: 4419 increase replaced with prev. day increase 585"
    plt.title(header + subheader, fontsize=10)
    plt.xlabel("Rolling window midpoint [day]")
    plt.ylabel("7-day rolling window average daily no of deaths")
    plt.semilogy()
    plt.xlim(0, max(len_windows) + 3)
    plt.grid()

    country = "ALL_COUNTRIES"
    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country,
                             "COVID-19_Deaths_Rolling_Average.png"))
    plt.close()

    for country, deaths in nums_deaths.items():
        if country in analyzed_countries:
            if country == "UK":
                deaths = np.loadtxt("country_data/UK_deaths_history")
            deaths = list(sorted([d for d in deaths if d > 5.]))
            deaths = [deaths[i + 1] - deaths[i] for i in range(len(deaths) - 1)]
            # adjust delta from ONS correction; replace outlier with value from 28 apr
            if country == "UK":
                deaths[46] = 585.  # keep previous delta
            cp = COUNTRY_PARAMS[country][1]
            deaths_per_capita = [d / cp for d in deaths]
            ret_pc = np.cumsum(deaths_per_capita, dtype=float)
            ret_pc[n:] = ret_pc[n:] - ret_pc[:-n]
            rolling_avg_pc = ret_pc[n - 1:] / n
            plt.plot(range(len(rolling_avg_pc)), rolling_avg_pc,
                     color=country_colors[country], label=country)
            plt.annotate(country, xy=(len(rolling_avg_pc) + 0.05,
                                      rolling_avg_pc[-1]), fontsize=8)

    header = "7-day rolling average for daily no. of deaths increase starting at min=5"
    subheader = '\n Proportion of each 1,000 of country population (equiv. to per thousand)'
    subheader2 = "\nUK: 29/04 correction from ONS: 4419 increase replaced with prev. day increase 585"
    plt.title(header + subheader + subheader2, fontsize=10)
    plt.xlabel("Rolling window midpoint [day]")
    plt.ylabel("7-day rolling window average daily no of deaths per 1k of population")
    plt.semilogy()
    plt.xlim(0, max(len_windows) + 3)
    plt.grid()
    plt.legend(loc="lower right", fontsize=8)

    country = "ALL_COUNTRIES"
    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country,
                             "COVID-19_Deaths_Rolling_Average_per_Population.png"))
    plt.close()


    for country, deaths in nums_deaths.items():
        if country in analyzed_countries:
            if country == "UK":
                deaths = np.loadtxt("country_data/UK_deaths_history")
            deaths = list(sorted([d for d in deaths if d > 5.]))
            cp = COUNTRY_PARAMS[country][1]
            deaths_per_capita = [d / cp for d in deaths]
            ret_pc = np.cumsum(deaths_per_capita, dtype=float)
            ret_pc[n:] = ret_pc[n:] - ret_pc[:-n]
            rolling_avg_pc = ret_pc[n - 1:] / n
            plt.plot(range(len(rolling_avg_pc)), rolling_avg_pc,
                     color=country_colors[country], label=country)
            plt.annotate(country, xy=(len(rolling_avg_pc) + 0.05,
                                      rolling_avg_pc[-1]), fontsize=8)

    header = "7-day rolling average cumulative no. of deaths starting at min=5"
    subheader = '\n Proportion of each 1,000 of country population (equiv. to per thousand)'
    plt.title(header + subheader, fontsize=10)
    plt.xlabel("Rolling window midpoint [day]")
    plt.ylabel("7-day rolling window average cumulative no. of deaths per 1k population")
    plt.semilogy()
    plt.xlim(0, max(len_windows) + 3)
    plt.grid()
    plt.legend(loc="lower right", fontsize=8)

    country = "ALL_COUNTRIES"
    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country,
                             "COVID-19_Deaths_per_Population.png"))
    plt.close()

    for country, deaths in nums_deaths.items():
        if country in analyzed_countries:
            if country == "UK":
                deaths = np.loadtxt("country_data/UK_deaths_history")
            deaths = list(sorted([d for d in deaths]))
            dd = [deaths[i + 1] - deaths[i] for i in range(len(deaths) - 1)]
            delta_deaths = np.array(deaths[1:]) - np.array(dd) 
            x = np.arange(len(deaths))
            x_shift = np.arange(1, len(deaths))
            width = 0.75
            fig, ax = plt.subplots()
            rects1 = ax.bar(x - width/2, deaths, width,
                            color='red', log=True)
            rects2 = ax.bar(x_shift - width/2, delta_deaths, width,
                            color=country_colors[country], log=True)

            # Add some text for labels, title and custom x-axis tick labels, etc.
            # ax.set_yscale('log')
            ax.set_ylabel('No of deaths')
            ax.set_xlabel('Days since first death recorded')
            ax.set_title('{}: March-April number of deaths and daily increment'.format(country))
            ax.set_xticks(x)
            ax.tick_params(axis="x", labelsize=6)
            ax.grid()
            ax.legend()

            if not os.path.isdir(os.path.join("country_plots", country)):
                os.makedirs(os.path.join("country_plots", country))

            plt.savefig(os.path.join("country_plots", country,
                                     "COVID-19_Deaths_logHist_{}.png".format(country)))
            plt.close()


def get_linear_parameters_local(x, y):
    """Retrive linear parameters."""
    # line parameters
    coef = np.polyfit(x, y, 1)
    poly1d_fn = np.poly1d(coef)
    slope = coef[0]
    intercept = coef[1]

    return poly1d_fn(x), slope, intercept


def plot_death_extrapolation(death_rates):
    """Plot 5-day death rates dN/dt."""
    analyzed_countries = ["UK", "Italy", "Germany", "US",
                          "Spain", "France", "Netherlands",
                          "Belgium", "Romania", "Sweden", "Norway",
                          "Switzerland", "Canada", "Austria", "Bulgaria"]
    country_colors = {"UK":"k", "France":"b", "Germany":"r", "US":"c",
                      "Spain":"m", "Italy":"y", "Netherlands":"g",
                      "Belgium":"lime", "Romania":"orange", "Sweden":"gray", "Norway":"maroon",
                      "Switzerland":"teal", "Canada":"darkslategrey", "Austria": "tan",
                      "Bulgaria": "fuchsia"}

    all_rates = []
    all_frequencies = []

    for country, tuplex in death_rates.items():
        if country in analyzed_countries:
            daily_deaths = tuplex[0]
            daily_rates = tuplex[1]
            rate_frequency = {float(key):len(list(group)) for key,group in groupby(daily_rates)}
            rate_frequency = dict(sorted(rate_frequency.items()))
            plt.scatter(rate_frequency.keys(), rate_frequency.values(),
                        color=country_colors[country], s=60, label=country)
            all_rates.extend(rate_frequency.keys())
            all_frequencies.extend(rate_frequency.values())

            # plot bar rates
            frequencies = rate_frequency.values()
            labels = ['m={}'.format(m) for m in rate_frequency.keys()]
            x = np.arange(len(labels))  # the label locations
            width = 0.45  # the width of the bars
            fig, ax = plt.subplots()
            rects1 = ax.bar(x - width/2, frequencies, width,
                            color=country_colors[country])

            # Add some text for labels, title and custom x-axis tick labels, etc.
            ax.set_ylabel('No of days of constant rate $m$')
            ax.set_title('{}: 5-day average daily growth rate of deaths $m$ vs no of days of constant $m$'.format(country))
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.tick_params(axis="x", labelsize=8)
            ax.grid()
            ax.legend()

            if not os.path.isdir(os.path.join("country_plots", country)):
                os.makedirs(os.path.join("country_plots", country))

            plt.savefig(os.path.join("country_plots", country,
                                     "COVID-19_DeathsRate_Rolling_Average_{}.png".format(country)))
            plt.close()

    all_rates = [float(a) for a in all_rates]
    all_rates = np.array(all_rates)
    all_frequencies = np.array(all_frequencies)
    doubles = [(i, j) for i, j in zip(all_rates, all_frequencies)]

    lim_10 = [d for d in doubles if d[0] < 10.0]
    x_10 = np.array([s[0] for s in lim_10])
    y_10 = np.array([s[1] for s in lim_10])

    lim_5 = [d for d in doubles if d[0] < 5.0]
    x_5 = np.array([s[0] for s in lim_5])
    y_5 = np.array([s[1] for s in lim_5])

    # look for smaller rates
    #lim_25 = [d for d in doubles if d[0] < 2.5]
    #x_25 = np.array([s[0] for s in lim_25])
    #y_25 = np.array([s[1] for s in lim_25])

    # get linear params for all data
    poly_x, slope, intercept = get_linear_parameters_local(
        all_rates,
        all_frequencies)
    poly_x10, slope10, intercept10 = get_linear_parameters_local(
        x_10,
        y_10)
    poly_x5, slope5, intercept5 = get_linear_parameters_local(
        x_5,
        y_5)
    #poly_x25, slope25, intercept25 = get_linear_parameters_local(
    #    x_25,
    #    y_25)
    plt.plot(all_rates, poly_x, '--r')
    plt.plot(x_10, poly_x10, '--b')
    plt.plot(x_5, poly_x5, '--g')
    #plt.plot(x_25, poly_x25, '--k')
    plt.annotate("(all m) = %.2f %.2f x R" % (intercept, slope), xy=(11., 8.), color='r')
    plt.annotate("$(m < 0.1)$ = %.2f %.2f x R" % (intercept10, slope10), xy=(11., 7.5), color='b')
    plt.annotate("$(m < 0.05)$ = %.2f %.2f x R" % (intercept5, slope5), xy=(11., 7.), color='g')
    #plt.annotate("$(m < 0.025)$ = %.2f %.2f x R" % (intercept25, slope25), xy=(11., 6.5), color='k')

    header = "5-day rolling average daily growth rate $m$ for deaths (from $exp^{mt}$) vs times (days) of constant $m$"
    plt.title(header, fontsize=10)
    plt.ylabel("No of day of constant $m$")
    plt.xlabel("5-day rolling window avg. daily death growth rate $m$ x 100 [day-1]")
    plt.grid()
    plt.legend(loc="upper right", fontsize=8)

    country = "ALL_COUNTRIES"
    if not os.path.isdir(os.path.join("country_plots", country)):
        os.makedirs(os.path.join("country_plots", country))

    plt.savefig(os.path.join("country_plots", country,
                             "COVID-19_DeathsRate_Rolling_Average_Counts.png"))
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
    parser.add_argument('-a',
                        '--all-data',
                        type=bool,
                        default=False,
                        help='Analyze all available data.')
    args = parser.parse_args()

    # parse command line args
    download = False
    all_data = False
    if not args.countries:
        return
    if args.download_data:
        download = True
    if args.all_data:
        all_data = True

    # set the analysis interval depending on user choice
    if not all_data and args.month:
        months = [args.month]
    elif all_data:
        months = [3, 4, 5]
    else:
        raise ValueError("You must supply either --all-data or --month")

    # get countries or regions (states)
    countries = _get_geography(args.countries)
    if not args.regions:
        regions = []
    else:
        regions = _get_geography(args.regions)

    # write summary files
    today_date = datetime.today().strftime('%m-%d-%Y')
    today_day = today_date.split("-")[1]
    today_month = today_date.split("-")[0]
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
    # write inc file pointing to most recent data file
    raw_file = "country_tables/currentdata.inc"
    with open(raw_file, "w") as file:
        file.write(raw_date + '\n' + raw_content)

    # write countriles with doubling time > 14
    with open("country_tables/countries_with_case_doubling-time_larger_14days.csv", "w") as file:
        file.write("Country,doubling time (days)\n")

    # plot other countries
    double_time = []
    basic_rep = []
    lin_fit_quality = []
    nums_cases = {}
    nums_deaths = {}
    all_nums_deaths = {}
    death_rates = {}
    all_nums_cases_dt = {}

    # run for each country
    for country in countries:
        print("Analyzing {} ...".format(country))
        cases, deaths, recs, times = [], [], [], []
        for month in months:
            monthly_numbers_i = get_monthly_countries_data(country,
                                                           month,
                                                           region=False)
            if len(months) == 1:
                monthly_numbers_prev_month = get_monthly_countries_data(
                    country,
                    month - 1,
                    region=False)

            cases.extend(monthly_numbers_i[0])
            deaths.extend(monthly_numbers_i[1])
            recs.extend(monthly_numbers_i[2])
            times.extend(monthly_numbers_i[3])

        monthly_numbers = (cases, deaths, recs, times)

        # get the evolution parameters
        d_time, R0, lin_fit, nums = plot_countries(monthly_numbers,
                                                   months, country,
                                                   table_file,
                                                   download)
        double_time.extend(d_time)
        basic_rep.extend(R0)
        lin_fit_quality.extend(lin_fit)
        nums_cases[country] = nums[0]
        nums_deaths[country] = nums[1]
        all_nums_deaths[country] = nums[1]
        if len(months) == 1:
            prev_month_deaths = [
                float(s) for s in monthly_numbers_prev_month[1] if s != 'NN'
            ]
            all_nums_deaths[country] = np.hstack((all_nums_deaths[country],
                                                  prev_month_deaths))

        # get data from all countries files
        cases_dt = []
        deaths_dt = []
        c_deaths = []
        c_rates = []
        for m in months[1:]:
            if m == 4:
                mth = '04'
                current_range = range(4, 31)
                l_apr = len(current_range)
            elif m == 5:
                mth = '05'
                current_range = range(1, int(today_day) + 1)
                l_may = len(current_range)
            for d in current_range:
                if d < 10:
                    dat_file = "country_tables/ALL_COUNTRIES_DATA_0{}-{}-2020.csv".format(d, mth)
                else:
                    dat_file = "country_tables/ALL_COUNTRIES_DATA_{}-{}-2020.csv".format(d, mth)
                with open(dat_file, "r") as file:
                    content = file.readlines()
                    for line in content:
                        if line.split(",")[1] == country:
                            cases_dt.append(line.split(",")[6])
                            deaths_dt.append(line.split(",")[7])
                            c_deaths.append(line.split(",")[3])
                            c_rates.append(line.split(",")[5])
        tot_l = l_apr + l_may
        if len(cases_dt) == tot_l - 1:
            current_range = range(4, 31)
            may = [31 + x for x in range(0, int(today_day) - 1)]
            current_range.extend(may)
            print("Analyzing cases dubling times count {} with data points {}".format(str(len(cases_dt)), str(len(current_range))))
            plot_doubling(cases_dt, deaths_dt, current_range, country)
            all_nums_cases_dt[country] = cases_dt
        if len(c_deaths) == len(c_rates):
            death_rates[country] = (c_deaths, c_rates)
                
    if regions:
        for region in regions:
            print("Analyzing {} ...".format(region))
            cases, deaths, recs, times = [], [], [], []
            for month in months:
                monthly_numbers_i = get_monthly_countries_data(region,
                                                               month,
                                                               region=True)
                cases.extend(monthly_numbers_i[0])
                deaths.extend(monthly_numbers_i[1])
                recs.extend(monthly_numbers_i[2])
                times.extend(monthly_numbers_i[3])

            monthly_numbers = (cases, deaths, recs, times)

            # get the evolution parameters
            d_timeR, R0R, lin_fitR, nums = plot_countries(monthly_numbers,
                                                          months, region,
                                                          table_file,
                                                          download=False)
            double_time.extend(d_timeR)
            basic_rep.extend(R0R)
            lin_fit_quality.extend(lin_fitR)

    # plot viral parameters and various ensemble plots
    plot_parameters(double_time, basic_rep, lin_fit_quality, len(countries))
    ks.kstest(nums_cases, nums_deaths)
    plot_rolling_average(all_nums_deaths)
    plot_R(all_nums_cases_dt)
    plot_death_extrapolation(death_rates)


if __name__ == '__main__':
    main()
