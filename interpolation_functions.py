def def1(self, i):
    return (self.y_fit[i+1]-self.y_fit[i])/(self.x_smooth[i+1]-self.x_smooth[i])

def newton1(self, X):
    return self.y_fit[0]+self.def1(0)*(X-self.x_smooth[0])

def newton2(self, X):
    return self.newton1(X)+((self.def1(1)-self.def1(0))/(self.x_smooth[2]-self.x_smooth[0]))*(X-self.x_smooth[0])*(X-self.x_smooth[1])