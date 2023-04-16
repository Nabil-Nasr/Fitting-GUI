import numpy as np
from lmfit.models import GaussianModel,LorentzianModel,VoigtModel

def least_squares(self):
    self.m = (self.n*np.sum(self.x*self.y)-np.sum(self.x)*np.sum(self.y))/(self.n*np.sum(self.x**2)-np.sum(self.x)**2)
    self.c = (1/self.n)*(np.sum(self.y)-self.m*np.sum(self.x))
    self.x_smooth=self.x
    self.y_fit = self.m*self.x+self.c
def __private_shared_fitting_body(self,model):
    params = model.guess(self.y, x=self.x)
    result = model.fit(self.y, params, x=self.x)
    # Plot the fitted curve
    x_smooth = np.linspace(self.x.min(), self.x.max(), 1000)
    self.x_smooth=x_smooth
    self.y_fit=result.eval(x=x_smooth)

def fit_gaussian(self):
    # Fit Gaussian distribution
    model = GaussianModel()
    __private_shared_fitting_body(self,model)

def fit_lorentzian(self):
    # Fit Lorentzian distribution
    model = LorentzianModel()
    __private_shared_fitting_body(self,model)

def fit_voigt(self):
    # Fit Voigt distribution
    model = VoigtModel()
    __private_shared_fitting_body(self,model)

__all__=["least_squares","fit_gaussian","fit_lorentzian","fit_voigt","np"]
