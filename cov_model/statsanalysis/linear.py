"""
Line fit via numpy polyfit.
"""
import numpy as np


# slowing countries: countries that show a consistent slowing trend
# slowing down value = date in March that is roughly the start of slowdown
def get_slowdown(month):
    """Set the correct slowdowns depending on month."""
    if month == 3:
        SLOWDOWN = {"Austria": 26,
                    "Belgium": 13,
                    "Bulgaria": 22,
                    "Denmark": 13,
                    "Finland": 14,
                    "France": 16,
                    "Germany": 20,
                    "Ireland": 16,
                    "Italy": 21,
                    "Netherlands": 13,
                    "Norway": 14,
                    "Poland": 16,
                    "Romania": 24,
                    "Slovakia": 21,
                    "Spain": 19,
                    "Sweden": 13,
                    "UK": 21}
        # same for deaths
        SLOWDOWN_DEATHS = {"France": 20,
                           "Germany": 20,
                           "Italy": 21,
                           "Netherlands": 22,
                           "Romania": 27,
                           "Spain": 15,
                           "UK": 21}
    elif month == 4:
        SLOWDOWN = {"Italy": 2}
        SLOWDOWN_DEATHS = {"Italy": 2}

    return SLOWDOWN, SLOWDOWN_DEATHS


def compute_slowdown(x_cases, y_cases, country, month, deaths=False):
    """Get numbers for slowdown phase."""
    SLOWDOWN, SLOWDOWN_DEATHS = get_slowdown(month)
    if not deaths:
        slowdown_index = x_cases.index(SLOWDOWN[country])
    else:
        slowdown_index = x_cases.index(SLOWDOWN_DEATHS[country])
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
                                             month,
                                             deaths_label=deaths)
    return (x_cases, y_cases, x_slow, y_slow,
        poly_x_s, R_s, y_err_s, slope_s, d_time_s, R0_s,
        plot_text_s, plot_name_s)


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


def common_plot_stuff(plt, country):
    """Add common stuff to plot."""
    plt.xlabel("Time [days, starting March 1st, 2020]")
    plt.ylabel("Cumulative number of confirmed cases and deaths")
    plt.title("COVID-19 in {} starting March 1, 2020".format(country))


def get_plot_text(slope, country, R, d_time, R0, x,
                  month, deaths_label=False):
    """Set plot title, subtitle, text."""
    header = "Daily Cases:"
    if deaths_label:
        header = "Daily Deaths (slower):"
    plot_text = header + "\n" + \
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
