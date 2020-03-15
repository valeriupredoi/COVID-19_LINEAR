"""
Script to plot the evolution of daily number of cases
of COVID-19 and extract some parameters via a linear fit.

Usage
=====
$ python cov_lin_models.py --countries UK,Italy --download-data [True, False]

If download-data set to True, it will download the official,
most up to date data; currently the only data location is at:

UK_DATA_LOCATION = "https://www.arcgis.com/sharing/rest/content/items/e5fd11150d274bebaaf8fe2a7a2bda11/data"

Source (official): https://www.gov.uk/government/publications/covid-19-track-coronavirus-cases

which is an excel spreadsheet.
"""
import argparse
import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import urllib
from xlrd import open_workbook

UK_DATA_LOCATION = "https://www.arcgis.com/sharing/rest/content/items/e5fd11150d274bebaaf8fe2a7a2bda11/data"

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
    plot_suptitle = "Lin fit of " + \
                    "log cases $N=Ce^{bt}$ with " + \
                    "$b=$%.2f day$^{-1}$ (red, %s)" % (slope, country)
    plot_title = "Coefficient of determination R=%.3f" % R + "\n" + \
                 "Population Doubling time: %.1f days" % d_time + "\n" + \
                 "Estimated Daily $R_0=$%.1f" % R0
    plot_name = "2019-ncov_lin_{}-{}-2020_{}.png".format(
                    str(int(x[-1])),
                    month, country)

    return plot_suptitle, plot_title, plot_name


def get_excel_data(url, country, table_name, column, download):
    """Retrive Excel sheet and parse."""
    country_xls = "country_data/{}.xls".format(country)
    if not os.path.isfile(country_xls) or download:
        urllib.urlretrieve(url, country_xls)
    book = open_workbook(country_xls, on_demand=True)
    sheet = [
        book.sheet_by_name(name) for name in book.sheet_names()
        if name == table_name
    ][0]
    cells = [cell.value for cell in sheet.col(column)]

    return cells


def _common_plot_stuff(country, plot_suptitle):
    """Add common stuff to plot."""
    plt.xlabel("March Date (DD/03/2020)")
    plt.ylabel("Number of 2019-nCov cases on given day DD")
    plt.suptitle("COVID-19 in {} starting March 1, 2020".format(country))
    plt.title(plot_suptitle)


def plot_uk_data(download):
    """Plot the UK data starting March 1st, 2020."""
    uk_data_url = UK_DATA_LOCATION
    cells = get_excel_data(uk_data_url, "UK",
                           "DailyConfirmedCases", 2, download=download)

    # data cells
    y_data_real = cells[31:]
    y_data = np.log(y_data_real)
    x_data = [np.float(x) for x in range(1, len(y_data) + 1)]

    # statistics
    poly_x, R, y_err, slope, d_time, R0 = get_linear_parameters(x_data,
                                                                y_data)

    # plot parameters
    plot_suptitle, plot_title, plot_name = get_plot_text(slope, "UK",
                                                         R, d_time, R0,
                                                         x_data, month="03")

    # plotting
    plt.plot(x_data, y_data, 'yo', x_data, poly_x, '--k')
    plt.errorbar(x_data, y_data, yerr=y_err, fmt='o', color='r')
    plt.grid()
    plt.xlim(x_data[0] - 1.5, x_data[-1] + 1.5)
    plt.ylim(2.5, y_data[-1] + 1.5)
    plt.yticks(y_data, [np.int(y01) for y01 in y_data_real])
    _common_plot_stuff("UK", plot_suptitle)
    plt.text(2., y_data[-1] + 0.5, plot_title)
    plt.savefig(os.path.join("country_plots", plot_name))
    plt.show()


def main():
    """Execute the plotter."""
    # parse command line args
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-d',
                        '--download-data',
                        type=bool,
                        help='Flag to trigger downloading data.')
    parser.add_argument('-c',
                        '--countries',
                        type=str,
                        help='List of countries.')
    args = parser.parse_args()
    download = False
    if not args.countries:
        return
    if args.download_data:
        download = True
    if "UK" in args.countries:
        plot_uk_data(download)


if __name__ == '__main__':
    main()
