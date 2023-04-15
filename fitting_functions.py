import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks

def gaussian(self, x, a, x0, sigma):
        return a * np.exp(-(x - x0)**2 / (2 * sigma**2))

def lorentzian(self, x, a, x0, gamma):
    return a * gamma**2 / ((x - x0)**2 + gamma**2)

def voigt(self, x, a_g, x0_g, sigma, a_l, x0_l, gamma):
    return self.gaussian(x, a_g, x0_g, sigma) + self.lorentzian(x, a_l, x0_l, gamma)

def fit_gaussian(self):
    peaks, _ = find_peaks(self.y)
    peak = self.x[peaks[np.argmax(self.y[peaks])]]
    popt, _ = curve_fit(self.gaussian, self.x, self.y, p0=[1, peak, 1])
    self.y_fit = self.gaussian(self.x, *popt)

def fit_lorentzian(self):
    peaks, _ = find_peaks(self.y)
    peak = self.x[peaks[np.argmax(self.y[peaks])]]
    popt, _ = curve_fit(self.lorentzian, self.x, self.y, p0=[1, peak, 1])
    self.y_fit = self.lorentzian(self.x, *popt)

def fit_voigt(self):
    peaks, _ = find_peaks(self.y)
    peak = self.x[peaks[np.argmax(self.y[peaks])]]
    popt, _ = curve_fit(self.voigt, self.x, self.y, p0=[1, peak, 1, 1, peak, 1])
    self.y_fit = self.voigt(self.x, *popt)

def least_squares(self):
    self.m = (self.n*np.sum(self.x*self.y)-np.sum(self.x)*np.sum(self.y))/(self.n*np.sum(self.x**2)-np.sum(self.x)**2)
    self.c = (1/self.n)*(np.sum(self.y)-self.m*np.sum(self.x))
    self.y_fit = self.m*self.x+self.c
