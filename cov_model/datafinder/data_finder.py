"""
Data finding module.
"""
import os
import csv
from datetime import datetime
import os
import numpy as np
import urllib
from xlrd import open_workbook


# data stores: governemental data
UK_DAILY_CASES_DATA = "https://www.arcgis.com/sharing/rest/content/items/e5fd11150d274bebaaf8fe2a7a2bda11/data"
UK_DAILY_DEATH_DATA = "https://www.arcgis.com/sharing/rest/content/items/bc8ee90225644ef7a6f4dd1b13ea1d67/data"

# data stores: Johns Hopkins data
JOHN_HOPKINS = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports"

# countries that need their data to be summed;
# same for US states
COUNTRIES_TO_SUM = ["US", "France", "Denmark",
                    "Netherlands"]

def _sum_up(param, country):
    """Get special csv param for US - summing is needed."""
    if country not in COUNTRIES_TO_SUM:
        param = param[0]
    else:
        if not len(set(param)) > 1:
            param = param[0]
        else:
            param = sum(param)


    return param


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


def load_daily_deaths_history(month):
    """Load previously written to disk deaths numbers."""
    if month == 3:
        deaths_list = \
            list(np.loadtxt("country_data/UK_deaths_history", dtype='float'))[0:19]
    elif month == 3:
        deaths_list = \
            list(np.loadtxt("country_data/UK_deaths_history", dtype='float'))[19:]
    return deaths_list


def get_official_uk_data(month, download):
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
    # uk changed data to remove cases before March 1st (2-04-2020)
    if month == 3:
        y_data_real = cases_cells[1:32]
    elif month == 4:
        y_data_real = cases_cells[32:]
    y_deaths_real = load_daily_deaths_history(month)

    # append to file if new data
    if death_cells[1:] not in y_deaths_real:
        y_deaths_real.extend(death_cells[1:])
        with open("country_data/UK_deaths_history", "a") as file:
            file.write(str(death_cells[1:][0]) + "\n")

    x_data = [np.float(x) for x in range(1, len(y_data_real) + 1)]
    x_deaths = [np.float(x) for x in range(13, len(y_deaths_real) + 13)]

    # compute average mortality
    mort = np.array(y_deaths_real) / np.array(y_data_real[11:])
    avg_mort = np.mean(mort)
    stdev_mort = np.std(mort)

    return (x_data, y_data_real, x_deaths,
        y_deaths_real, avg_mort, stdev_mort)


def _extract_from_csv(data_object, country, param_idx,
                      country_idx, numeric=False):
    """
    Extract and return the needed field from csv file.

    Data before 23 March 2020 is in an old format:
    sep/state country date cases deaths coord1 coord2
    ,Belgium,2020-03-22T14:13:06,3401.0,75.0,263.0

    JHU have changed the format from 23 March 2020 as:
    FIPS Admin2 Province_State Country_Region Last_Update Lat Long_ Confirmed Deaths Recovered Active Combined_Key
    53001,Adams,Washington,US,2020-03-23 23:19:34,46.98299757,-118.56017340000001,1,0,0,0,"Adams, Washington, US"
    ,,,Belgium,2020-03-23 23:19:21,50.8333,4.469936,3743,88,401,3254,Belgium

    """
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

    # list of specific data checks
    param = _sum_up(param, country)

    return param


def _reformat_date(exp_dates):
    """Reformat dates to common format."""
    time_fmt = "%Y-%m-%dT%H:%M:%S"
    wrong_time_fmt = "%Y-%m-%d %H:%M:%S"
    if exp_dates == 'NN':
        return exp_dates
    if exp_dates != 'NN' and not isinstance(exp_dates, list):
        try:
            datetime.strptime(exp_dates, time_fmt)
        except ValueError:
            exp_dates = datetime.strptime(exp_dates,
                                          wrong_time_fmt).strftime(time_fmt)

    if exp_dates != 'NN' and isinstance(exp_dates, list):
        try:
            datetime.strptime(exp_dates[0], time_fmt)
        except ValueError:
            exp_dates = [datetime.strptime(c, wrong_time_fmt).strftime(time_fmt)
                         for c in exp_dates]

    return exp_dates


def _get_extracted(data_read, country, idx_pack, cidx):
    """Get the extracted numbers depending on various data format indeces."""
    # country data
    # dates
    exp_dates = _extract_from_csv(data_read, country, idx_pack[0], cidx)
    exp_dates = _reformat_date(exp_dates)

    # cases
    count_cases = _extract_from_csv(data_read, country, idx_pack[1], cidx,
                                    numeric=True)
    # deaths
    count_deaths = _extract_from_csv(data_read, country, idx_pack[2], cidx,
                                     numeric=True)
    # recoveries
    count_rec = _extract_from_csv(data_read, country, idx_pack[3], cidx,
                                  numeric=True)

    return (exp_dates, count_cases, count_deaths, count_rec)


def _get_daily_countries_data(date, country, region):
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

        # parse for both older JHU data format and newer
        if date[1] == '03' and int(float(date[0])) < 23:
            # geography index in file
            cidx = 1
            if region:
                cidx = 0
            idx_pack = [2, 3, 4, 5]
            (exp_dates,
             count_cases,
             count_deaths,
             count_rec) = _get_extracted(data_read, country, idx_pack, cidx)
            country_data = ',' + ','.join([country, exp_dates,
                                           str(count_cases),
                                           str(count_deaths), str(count_rec)])
            if region:
                country_data = ','.join([country, "REGION",exp_dates,
                                         str(count_cases),
                                         str(count_deaths), str(count_rec)])
        else:
            # geography index in file
            cidx = 3
            if region:
                cidx = 2
            idx_pack = [4, 7, 8, 9]
            (exp_dates,
             count_cases,
             count_deaths,
             count_rec) = _get_extracted(data_read, country, idx_pack, cidx)
            country_data = ',,,' + ','.join([country, exp_dates, "c1", "c2",
                                             str(count_cases),
                                             str(count_deaths), str(count_rec)])
            if region:
                country_data = ',,' + ','.join([country, "REGION",exp_dates,
                                                "c1", "c2",
                                                str(count_cases),
                                                str(count_deaths), str(count_rec)])
        csv_file.close()
        os.remove(fullpath_file)

    # overwrite so to optimize disk use
    with open(fullpath_file, "w") as file:
        file.write(country_data)

    return count_cases, count_deaths, count_rec, exp_dates


def get_monthly_countries_data(country, month, region):
    """Assemble monthly data per country."""
    m_cases = []
    m_deaths = []
    m_rec = []
    actual_dates = []

    # start date / actual date
    today_date = datetime.today().strftime('%m-%d-%Y')
    today_day = today_date.split("-")[1]
    # jump one day in previous month
    if today_day == '02' and month == 3:
        today_day = '32'
    for day in range(1, int(float(today_day))):
        date_object = datetime(day=day,
                               month=month,
                               year=2020).strftime('%d-%m-%Y')
        date = (date_object.split("-")[0], date_object.split("-")[1])
        month_cases, month_deaths, month_rec, exp_dates = \
            _get_daily_countries_data(date, country, region)
        m_cases.append(month_cases)
        m_deaths.append(month_deaths)
        m_rec.append(month_rec)
        actual_dates.append(exp_dates)

    return m_cases, m_deaths, m_rec, actual_dates
