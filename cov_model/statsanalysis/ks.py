"""
Module that runs a Kolmogorov Smirnoff test.
"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


def kstest(nums_cases, nums_deaths):
    """Run a simple Kolmogorov-Sminroff test on populations."""
    # first compare UK to a few representative countries
    uk_france_cases = stats.ks_2samp(nums_cases["UK"],
                                     nums_cases["France"])
    uk_france_deaths = stats.ks_2samp(nums_deaths["UK"],
                                      nums_deaths["France"])
    uk_spain_cases = stats.ks_2samp(nums_cases["UK"],
                                    nums_cases["Spain"])
    uk_spain_deaths = stats.ks_2samp(nums_deaths["UK"],
                                     nums_deaths["Spain"])
    uk_italy_cases = stats.ks_2samp(nums_cases["UK"],
                                    nums_cases["Italy"])
    uk_italy_deaths = stats.ks_2samp(nums_deaths["UK"],
                                     nums_deaths["Italy"])
    uk_germany_cases = stats.ks_2samp(nums_cases["UK"],
                                      nums_cases["Germany"])
    uk_germany_deaths = stats.ks_2samp(nums_deaths["UK"],
                                       nums_deaths["Germany"])
    print("KS Statistic Results comparing UK to other European Countries")
    print("=============================================================")
    print("\n")
    print("cases: KS statistic  |  cases: KS p-value")
    print(":-------------------:|:------------------:")
    print("France: %.2f | France: %.2f" % (uk_france_cases[0], uk_france_cases[1]))
    print("Spain: %.2f | Spain: %.2f" % (uk_spain_cases[0], uk_spain_cases[1]))
    print("Italy: %.2f | Italy: %.2f" % (uk_italy_cases[0], uk_italy_cases[1]))
    print("Germany: %.2f | Germany: %.2f" % (uk_germany_cases[0], uk_germany_cases[1]))
    print("\n")
    print("\n")
    print("deaths: KS statistic  |  deaths: KS p-value")
    print(":-------------------:|:------------------:")
    print("France: %.2f | France: %.2f" % (uk_france_deaths[0], uk_france_deaths[1]))
    print("Spain: %.2f | Spain: %.2f" % (uk_spain_deaths[0], uk_spain_deaths[1]))
    print("Italy: %.2f | Italy: %.2f" % (uk_italy_deaths[0], uk_italy_deaths[1]))
    print("Germany: %.2f | Germany: %.2f" % (uk_germany_deaths[0], uk_germany_deaths[1]))
    print("\n")

    # get ad hoc metrics
    uk_france_metric = uk_france_cases[1] - uk_france_cases[0]
    uk_france_deaths_metric = uk_france_deaths[1] - uk_france_deaths[0]
    uk_spain_metric = uk_spain_cases[1] - uk_spain_cases[0]
    uk_spain_deaths_metric = uk_spain_deaths[1] - uk_spain_deaths[0]
    uk_italy_metric = uk_italy_cases[1] - uk_italy_cases[0]
    uk_italy_deaths_metric = uk_italy_deaths[1] - uk_italy_deaths[0]
    uk_germany_metric = uk_germany_cases[1] - uk_germany_cases[0]
    uk_germany_deaths_metric = uk_germany_deaths[1] - uk_germany_deaths[0]

    # plot the metrics
    labels = ['France', 'Spain', 'Italy', 'Germany']
    men_means = [uk_france_metric, uk_spain_metric, uk_italy_metric,
                 uk_germany_metric]
    women_means = [uk_france_deaths_metric, uk_spain_deaths_metric,
                   uk_italy_deaths_metric, uk_germany_deaths_metric]
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, men_means, width, color='red', label='Cases Score')
    rects2 = ax.bar(x + width/2, women_means, width, label='Deaths Score')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('KS Scores')
    ax.set_title('Kolmogorov-Smirnoff Scores by no. of cases and no. of deaths')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.grid()
    ax.legend()
    plt.savefig("country_plots/UK-KS.png")
    plt.close()
