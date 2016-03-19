import numpy as np

# Definition of thermodynamic constant:
cp = 1004.    # Heat capacity at constant pressure for dry air [J kg^-1 K^-1]
cpv = 1870.    # Heat capacity at constant pressure of water vapor [J kg^-1 K^-1]
Cl = 4190.     # Heat capacity of liquid water [J kg^-1 K^-1]
Rv = 461.      # Gas constant of water vapor [J kg^-1 K^-1]
Rd = 287.      # Gas constant of dry air [J kg^-1 K^-1]
Lv = 2.5104e6 # Latent heat of vaporization [J kg^-1]
Lf = 0.3336e6  # Latent heat of fusion [J kg^-1]
Ls = 2.8440e6  # Latent heat of sublimation [J kg^-1]
g = 9.81       # Accelleration of gravity [m s^-2]
p_0 = 100000.
epsilon = Rd/Rv
lam = Rv/Rd - 1.
lam = 0.61


def area(data, k, j, i):
    return float(len(i))*2500.

def qn(data, k, j, i):
    return data['QN'][k, j, i].mean()/1000.

def qv(data, k, j, i):
    return data['QV'][k, j, i].mean()/1000.

def tabs(data, k, j, i):
    return data['TABS'][k, j, i].mean()

def qt(data, k, j, i):
    return (data['QN'][k, j, i] + data['QV'][k, j, i]).mean()/1000.

def u(data, k, j, i):
    return data['U'][k, j, i].mean()

def v(data, k, j, i):
    return data['V'][k, j, i].mean()

def tke(data, k, j, i):
    return data['TKE'][k, j, i].mean()

def tr01(data, k, j, i):
    return data['TR01'][k, j, i].mean()

def w(data, k, j, i):
    kk = min(k+1, (320.-1))
    return (data['W'][k, j, i] + data['W'][kk, j, i]).mean()/2.

def dw_dz(data, k, j, i):
    kk = min(k+1, (320.-1))
    return (data['W'][kk, j, i].mean() - data['W'][k, j, i].mean())/50.

def wqreyn(data, k, j, i):
    kk = min(k+1, (320.-1))
    w = (data['W'][k, j, i] + data['W'][kk, j, i])/2.
    q = (data['QV'][k, j, i] + data['QN'][k, j ,i])
    wq_reyn = (w*q - w.mean()*q.mean())
    return wq_reyn.mean()

def wwreyn(data, k, j, i):
    kk = min(k+1, (320.-1))
    w = (data['W'][k, j, i] + data['W'][kk, j, i])/2.
    ww_reyn = (w*w - w.mean()**2)
    return ww_reyn.mean()

def dp_dz(data, k, j, i):
    kplus = min(k+1, (320.-1))
    kminus = max(k-1, 0)
    return (data['PP'][kplus, j, i] - data['PP'][kminus, j, i]).mean()/2/50.

def T_v(T, qv, qn, qp):
    return T*(1. + lam*qv - qn - qp)

def theta(p, T): return T*(p_0/p)**(Rd/cp)

def theta_v(p, T, qv, qn, qp):
    return theta(p, T_v(T, qv, qn, qp))
     
def thetav(data, k, j, i):
    return theta_v(data['p'][k, np.newaxis, np.newaxis]*100., 
                       data['TABS'][k, j, i], 
                       data['QV'][k, j, i]/1000., 
                       data['QN'][k, j, i]/1000., 0.)

def moist_adiabatic_lapse_rate(T, qv):
    return g*(1 + Lv*qv/Rd/T)/(cp + Lv*Lv*qv*epsilon/Rd/T/T)

# TODO: Redo the calculations for GATE sounding

def esatw(T):
    T = np.atleast_1d(T)
    # Saturation vapor [Pa]
    a = (6.11239921, 0.443987641, 0.142986287e-1, 0.264847430e-3, 0.302950461e-5,
         0.206739458e-7, 0.640689451e-10, -0.952447341e-13, -0.976195544e-15)
    dT = T-273.16
    dT[dT<-80.] = -80.
    return (a[0] + dT*(a[1] + dT*(a[2] + dT*(a[3] + dT*(a[4] + dT*(a[5] + dT*(a[6] + dT*(a[7] + dT*a[8]))))))))*100.
    
def dtesatw(T):
    T = np.atleast_1d(T)
    a = (0.443956472, 0.285976452e-1, 0.794747212e-3, 0.121167162e-4, 0.103167413e-6,
         0.385208005e-9, -0.604119582e-12, -0.792933209e-14, -0.599634321e-17)
    dT = T-273.16
    dT[dT<-80.] = -80.
    return (a[0] + dT*(a[1] + dT*(a[2] + dT*(a[3] + dT*(a[4] + dT*(a[5] + dT*(a[6] + dT*(a[7] + dT*a[8]))))))))*100.

def dtqsatw(T, p):
    return 0.622*dtesatw(T)/p
    
def density_theta_lapse_rate(T, p, qv, qn, qp, dp_dz):
    a = 1./T + epsilon*dtqsatw(T, p)
    e = esatw(T)
    b = - Rd/cp/p - 0.622*epsilon*e/(p-e)/(p-e)
    return theta_v(p, T, qv, qn, qp)*(-a*moist_adiabatic_lapse_rate(T, qv) + b*dp_dz)

def thetav_lapse(data, k, j, i):
    dp_dz = (data['p'][k+1]-data['p'][k-1])*100./50./2.
    return density_theta_lapse_rate(
                       data['TABS'][k, j, i].mean(), 
                       data['p'][k]*100., 
                       data['QV'][k, j, i].mean()/1000., 
                       data['QN'][k, j, i].mean()/1000., 
                       0.,
                       dp_dz)
    
def theta_l(p, T, qn, qp):
    return theta(p, T - Lv/cp*(qn + qp))

def thetal(data, k, j, i):
    return theta_l(data['p'][k, np.newaxis, np.newaxis]*100., 
                       data['TABS'][k, j, i], 
                       data['QN'][k, j, i]/1000., 0.).mean()
    
def h(T, z, qn, qi):
    return cp*T + g*z - Lv*qn - Ls*qi

def mse(data, k, j, i):
    return h(data['TABS'][k, j, i],
                 data['z'][k, np.newaxis, np.newaxis],
                 data['QN'][k, j, i]/1000.,
                 data['QI'][k, j, i]/1000.).mean()

def rho(data, k, j, i):
    return data['RHO'][k]

def press(data, k, j, i):
    return data['p'][k]*100.

def dwdt(data, k, j, i):
    return data['DWDT'][k, j, i].mean()

def etetcor(data, k, j, i):
    return data['ETETCOR'][k, j, i].sum()*2500.

def dtetcor(data, k, j, i):
    return data['DTETCOR'][k, j, i].sum()*2500.

def eqtetcor(data, k, j, i):
    return data['EQTETCOR'][k, j, i].sum()*2500.

def dqtetcor(data, k, j, i):
    return data['DQTETCOR'][k, j, i].sum()*2500.

def ettetcor(data, k, j, i):
    return data['ETTETCOR'][k, j, i].sum()*2500.

def dttetcor(data, k, j, i):
    return data['DTTETCOR'][k, j, i].sum()*2500.

def ewtetcor(data, k, j, i):
    return data['EWTETCOR'][k, j, i].sum()*2500.

def dwtetcor(data, k, j, i):
    return data['DWTETCOR'][k, j, i].sum()*2500.

def vtetcor(data, k, j, i):
    return data['VTETCOR'][k, j, i].sum()*2500.

def mftetcor(data, k, j, i):
    return data['MFTETCOR'][k, j, i].sum()*2500.

def etetcld(data, k, j, i):
    return data['ETETCLD'][k, j, i].sum()*2500.

def dtetcld(data, k, j, i):
    return data['DTETCLD'][k, j, i].sum()*2500.

def eqtetcld(data, k, j, i):
    return data['EQTETCLD'][k, j, i].sum()*2500.

def dqtetcld(data, k, j, i):
    return data['DQTETCLD'][k, j, i].sum()*2500.

def ettetcld(data, k, j, i):
    return data['ETTETCLD'][k, j, i].sum()*2500.

def dttetcld(data, k, j, i):
    return data['DTTETCLD'][k, j, i].sum()*2500.

def ewtetcld(data, k, j, i):
    return data['EWTETCLD'][k, j, i].sum()*2500.

def dwtetcld(data, k, j, i):
    return data['DWTETCLD'][k, j, i].sum()*2500.

def vtetcld(data, k, j, i):
    return data['VTETCLD'][k, j, i].sum()*50.*50.*50.

def mftetcld(data, k, j, i):
    return data['MFTETCLD'][k, j, i].sum()*50.*50.*50.

