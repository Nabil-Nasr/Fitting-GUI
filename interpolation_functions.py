def def1(self, i):
    return (self.y_fit[i+1]-self.y_fit[i])/(self.x[i+1]-self.x[i])

def newton1(self, X):
    return self.y_fit[0]+self.def1(0)*(X-self.x[0])

def newton2(self, X):
    return self.newton1(X)+((self.def1(1)-self.def1(0))/(self.x[2]-self.x[0]))*(X-self.x[0])*(X-self.x[1])