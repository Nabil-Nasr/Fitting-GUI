import numpy as np
from lmfit.models import Model,VoigtModel,LorentzianModel,GaussianModel
from scipy.optimize import curve_fit
from scipy.special import wofz
import re
import copy

def linear_fit(self):
    # Least squares function
    self.m = (self.n*np.sum(self.x*self.y)-np.sum(self.x)*np.sum(self.y))/(self.n*np.sum(self.x**2)-np.sum(self.x)**2)
    self.c = (1/self.n)*(np.sum(self.y)-self.m*np.sum(self.x))
    self.x_smooth = np.linspace(min(self.x.min(),0), self.x.max(), 300)
    self.y_fit = self.m*self.x_smooth+self.c

# if we used the function below will give the same as above
"""
def linear_fit(self):
    model= LinearModel()
    __private_shared_fitting_body(self,model)
"""

def __private_shared_fitting_body(self,model:Model):
    # params = model.make_params(amplitude=self.amplitude, mean=self.mean, sigma=self.sigma,gamma=self.gamma)


# ======= creating interval start end x_smooth started ================================
    start_end_xsmooth_arr=[self.x[0],self.x[-1],300]
    if(self.start_end_xsmooth_edit.text()!=''):
        start_end_xsmooth=self.start_end_xsmooth_edit.text().split(',')
        n=len(start_end_xsmooth)
        for i in range(n):
            if(start_end_xsmooth[i]!=''):
                start_end_xsmooth_arr[i]=float(start_end_xsmooth[i])
# ======= creating interval start end x_smooth ended ==================================

# ======= creating amplitude center sigma started ================================
    params_length=0
    params_list=[[],[],[]]
    if(self.amplitude_edit.text()!='' and self.center_edit.text()!='' and self.sigma_edit.text()!= ''):
        amplitude=self.amplitude_edit.text().split(',')
        center=self.center_edit.text().split(',')
        sigma=self.sigma_edit.text().split(',')
        params_length=len(amplitude)
        for i in range(params_length):
            params_list[0].append(float(amplitude[i]))
            params_list[1].append(float(center[i]))
            params_list[2].append(float(sigma[i]))


# ======= creating amplitude center sigma ended ==================================
    model_temp = copy.deepcopy(model)
    model.prefix="peak1_"
    for i in range(params_length):
        amplitude=params_list[0][i]
        center=params_list[1][i]
        sigma=params_list[2][i]
        if(i==0):
            model.set_param_hint('amplitude',value=amplitude,min=0)
            model.set_param_hint('center',value=center,min=center*0.95,max=center*1.05)
            model.set_param_hint('sigma',value=sigma,min=0)
            continue
        new_model = copy.deepcopy(model_temp)
        new_model.prefix=f"peak{i+1}_"

        new_model.set_param_hint('amplitude',value=amplitude,min=0)
        new_model.set_param_hint('center',value=center,min=center*0.95,max=center*1.05)
        new_model.set_param_hint('sigma',value=sigma,min=0)
        model+=new_model

    self.x_smooth=np.linspace(start_end_xsmooth_arr[0],start_end_xsmooth_arr[1],int(start_end_xsmooth_arr[2]))

    params=model.make_params()
    if(params_length==0):
        params=model.guess(self.y,x=self.x)
    result = model.fit(self.y,params,x=self.x)
    self.y_fit = result.eval(x=self.x_smooth)
    self.peak_result=re.sub(r" (?=peak\d+_amplitude)","\n\n    ",result.fit_report(show_correl=False,sort_pars=True).split('[[Variables]]')[-1])
    


def gaussian(x, amplitude, mean, sigma):
    return amplitude * np.exp(-(x - mean) ** 2 / (2 * sigma ** 2))

def gaussian_fit(self):
    # model = Model(gaussian)
    # GaussianModel used function as the function above
    model= GaussianModel()
    __private_shared_fitting_body(self,model)


# def lorentzian(x, amplitude, mean, sigma):
#     return (amplitude * sigma**2) / ((x - mean)**2 + sigma**2)

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
