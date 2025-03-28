import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

diag_de=0.4
diag_t=0.125
diag_dh=0.25
diag_h=1.25

cross_tb=0.06
cross_dh=0.25

pin_dh=0.25
pin_tb=0.06


def diagTearoutForce(Txy, de=diag_de, t=diag_t):
    return Txy*4*de*t
def diagAxialForce(S,t=diag_t, h=diag_h, dh=diag_dh):
    return S*2*t*(h-dh)
def diagBearingForce(S, t=diag_t, dh=diag_dh):
    return S*2*t*dh
def crossBearingForce(S, tb=cross_tb, dh=cross_dh):
    return S*tb*dh
def eulerCrossbar():
    pass
def johnsonCrossbar():
    pass
def pinShearForce(T,dh=pin_dh):
    return T*np.pi*(dh**2)/2
def pinBearingForce(T,dh=pin_dh,tb=pin_tb):
    return T*2*dh*tb

failure_stresses = [16, 16, 16, 32, 32, 140, 140]
forces = [diagTearoutForce(failure_stresses[0]), diagAxialForce(failure_stresses[1]), diagBearingForce(failure_stresses[2]), crossBearingForce(failure_stresses[3]), 0, pinShearForce(failure_stresses[5]),pinBearingForce(failure_stresses[6])]

data = {'Location of Failure': ['Diagnal member', 'Diagnal member', 'Diagnal member', 'Cross bar', 'Cross bar', 'Pin', 'Pin'], 'Failure Mode': ['Tearout', 'Axial', 'Bearing Stress', 'Bearing Stress', 'Buckling', 'Shear', 'Bearing Stress'], 'Failure Criteria': ['Von Mises','Von Mises','Von Mises','Von Mises','Johnson\nor Euler','Von Mises','Von Mises'], 'Strength Value \nused(ksi)': failure_stresses, 'Stress Equation': ['Txy = Fd/(2A) \n= Fd/(4*de*t)', 'S = Fd/(2A) \n= Fd/(2*t*(h-dh))', 'S = Fd/(2A) = \nFd/(2*t*dh)', 'S = Fcb/(dh*tb)','TBD(buckling)', 'T = V/A = \n2*Fd/(pi*dh^2)', 'T = Fcb/A = \nFcb/(2*dh*tb)' ], 'Applied Load Predicted\nto Cause Failure': forces}
df = pd.DataFrame(data)

fig, ax = plt.subplots()

ax.axis('off')

table = ax.table(cellText=df.values, colLabels=df.columns, loc='center')

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 3)  # Adjust cell size

plt.show()