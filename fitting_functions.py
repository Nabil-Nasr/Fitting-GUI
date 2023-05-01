import numpy as np
from lmfit.models import Model,VoigtModel,LorentzianModel,GaussianModel,LinearModel
from scipy.optimize import curve_fit
from scipy.special import wofz
import math

def linear_fit(self):
    # Least squares function
    self.m = (self.n*np.sum(self.x*self.y)-np.sum(self.x)*np.sum(self.y))/(self.n*np.sum(self.x**2)-np.sum(self.x)**2)
    self.c = (1/self.n)*(np.sum(self.y)-self.m*np.sum(self.x))
    self.x_smooth = np.linspace(self.x.min(), self.x.max(), 300)
    self.y_fit = self.m*self.x_smooth+self.c

# if we used the function below will give the same as above
"""
def linear_fit(self):
    model= LinearModel()
    __private_shared_fitting_body(self,model)
"""

def __private_shared_fitting_body(self,model:Model):
    # params = model.make_params(amplitude=self.amplitude, mean=self.mean, sigma=self.sigma,gamma=self.gamma)


# ======= creating interval started ================================
    if(self.interval_start_edit.text()!=''):
        interval_start=float(self.interval_start_edit.text())
        for i in range(len(self.x)):
            if(interval_start<=self.x[i]):
                self.x = self.x[i:]
                self.y = self.y[i:]
                break

    if(self.interval_end_edit.text()!=''):
        interval_end=float(self.interval_end_edit.text())
        for i in range(len(self.x)-1,-1,-1):
            if(interval_end>=self.x[i]):
                self.x = self.x[:i+1]
                self.y = self.y[:i+1]
                break
# ======= creating interval ended ==================================

# ======= creating section length started ==========================
    section_length=len(self.x)
    if(self.section_length_edit.text()!=''):
        section_length = int(self.section_length_edit.text())
    while True:
        print(section_length)
        max_increment=5
        increment=0
        if(0<len(self.x)%section_length < 5):
            section_length+=1
            increment+=1
            if(increment>=max_increment):
                break
        else:
            break
# ======= creating section length ended ============================

# ======= creating fitting points started ==========================
    fitting_points= 300
    if(self.fitting_points_edit.text()!=''):
        if(100<=float(self.fitting_points_edit.text())<=1000):
            fitting_points=int(self.fitting_points_edit.text())
# ======= creating fitting points ended ============================


    args={}
    j=0
    for i in range(0,len(self.x),section_length):
        params = model.guess(self.y[i:i+section_length], x=self.x[i:i+section_length])
        result = model.fit(self.y[i:i+section_length], params, x=self.x[i:i+section_length])

        args[f"x{j}"] = np.linspace(self.x[i:i+section_length].min(), self.x[i:i+section_length].max(), math.ceil(section_length/len(self.x)*fitting_points))
        args[f"y{j}"] =result.eval(x=args[f"x{j}"])
        j+=1
    self.x_smooth = np.array([])
    self.y_fit = np.array([])
    for i in range(j):
        self.x_smooth = np.concatenate((self.x_smooth,args[f"x{i}"]))
        self.y_fit = np.concatenate((self.y_fit,args[f"y{i}"]))
    print(result.fit_report())
    print(f"{self.x_smooth.max():2e}")

def gaussian(x, amplitude, mean, sigma):
    return amplitude * np.exp(-(x - mean) ** 2 / (2 * sigma ** 2))

def gaussian_fit(self):
    # model = Model(gaussian)
    # GaussianModel used function as the function above
    model= GaussianModel()
    __private_shared_fitting_body(self,model)


def lorentzian(x, amplitude, mean, sigma):
    return (amplitude * sigma**2) / ((x - mean)**2 + sigma**2)

def lorentzian_fit(self):
    # Fit Lorentzian distribution
    # model = Model(lorentzian)
    # LorentzianModel used function as the function above
    model=LorentzianModel()
    __private_shared_fitting_body(self,model)


def voigt(x, amplitude, mean, sigma, gamma):
    z = ((x - mean) + 1j*gamma) / (sigma * np.sqrt(2))
    return amplitude * np.real(wofz(z))

def voigt_fit(self):
    # Fit Voigt distribution
    # VoigtModel used function as the function above
    model = VoigtModel()
    __private_shared_fitting_body(self,model)


__all__=["linear_fit","gaussian_fit","lorentzian_fit","voigt_fit","np"]
