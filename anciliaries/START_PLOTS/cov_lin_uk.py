import numpy as np
import matplotlib
import matplotlib.pyplot as plt

month = "03"

def c_of_d(ys_orig, ys_line):
    """Compute the line R squared."""
    y_mean_line = [np.mean(ys_orig) for y in ys_orig]
    squared_error_regr = sum((ys_line - ys_orig) * (ys_line - ys_orig))
    squared_error_y_mean = sum((y_mean_line - ys_orig) * \
                               (y_mean_line - ys_orig))
    return 1 - (squared_error_regr / squared_error_y_mean)


# days in January
x1 = [np.float(x) for x in range(1, 9)]
# reported number of cases
# y01 = [35., 40., 51., 85., 114., 160., 206.,
#      271., 321., 373., 460., 599., 800., 1150.]
y01 = [206., 271., 321., 373., 460., 599., 800., 1150.]
x2 = [np.float(x) for x in range(1, 8)]
# y02 = [1577., 1835., 2263., 2706., 3296., 3916., 5061., 6387.,
#       7985., 8514., 10590., 12839., 14955. ]
y02 = [221., 311., 385., 588., 821., 1049., 1577.]
ytot = []
ytot.extend(y01)
ytot.extend(y02)

# natural log of number of reported cases
y1 = np.log(y01)
y2 = np.log(y02)
ytotlog = np.log(ytot)

coef1 = np.polyfit(x1, y1, 1)
poly1d_fn1 = np.poly1d(coef1)
coef2 = np.polyfit(x2, y2, 1)
poly1d_fn2 = np.poly1d(coef2)

# statistical parameters first line
R1 = c_of_d(y1, poly1d_fn1(x1))  # R squared
yerr1 = poly1d_fn1(x1) - y1  # error
slope1 = coef1[0]  # slope
d_time1 = np.log(2.) / slope1  # doubling time
R01 = np.exp(slope1) - 1.

# statistical parameters second line
R2 = c_of_d(y2, poly1d_fn2(x2))  # R squared
yerr2 = poly1d_fn2(x2) - y2  # error
slope2 = coef2[0]  # slope
d_time2 = np.log(2.) / slope2  # doubling time
R02 = np.exp(slope2) - 1.

#plot_suptitle = "Linear fit of " + \
#                "log cases $N=Ce^{bt}$ with " + \
#                "$b=$%.2f day$^{-1}$ (red) and $b=$%.2f day$^{-1}$ (green)" % (slope1, slope2)
plot_suptitle = "Lin fit of " + \
                "log cases $N=Ce^{bt}$ with " + \
                "$b=$%.2f day$^{-1}$ (red, UK) and $b=$%.2f day$^{-1}$ (green, Italy)" % (slope1, slope2)
plot_title1 = "Coefficient of determination R=%.3f" % R1 + "\n" + \
              "Population Doubling time: %.1f days" % d_time1 + "\n" + \
              "Estimated Daily $R_0=$%.1f" % R01
plot_title2 = "Coefficient of determination R=%.3f" % R2 + "\n" + \
              "Population Doubling time: %.1f days" % d_time2 + "\n" + \
              "Estimated Daily $R_0=$%.1f" % R02
plot_name = "COV19_LIN_START_{}-{}-2020_UK-Italy.png".format(str(int(x1[-1] + 1.)), month)

# plotting
plt.plot(x1, y1, 'yo', x1, poly1d_fn1(x1), '--r', label="UK")
plt.errorbar(x1, y1, yerr=yerr1, fmt='o', color='r')
plt.plot(x2, y2, 'yo', x2, poly1d_fn2(x2), '-g', label="Italy")
plt.errorbar(x2, y2, yerr=yerr2, fmt='o', color='g')
plt.grid()
plt.axvline(27, color='red')
plt.xlim(x1[0] - 1.5, x1[-1] + 1.5)  # x2[-1] + 1.5)
plt.ylim(2.5, 11.)
plt.yticks(ytotlog, [np.int(y01) for y01 in ytot])  # ytot])
# plt.yticks(y2, [np.int(y02) for y02 in y02])
plt.xlabel("Synthetic Date (Italy: 24 Feb-1 Mar; UK: 7 Mar-13 Mar")
plt.ylabel("Number of reported cases on given day DD")
plt.suptitle("COV-19: epidemic starts in Italy and UK")
plt.title(plot_suptitle)
plt.text(2., 8.5, plot_title1)
plt.text(2., 10., plot_title2)
plt.legend(loc="lower left")
plt.savefig(plot_name)
plt.show()
