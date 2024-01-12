import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import ticker, colors

# # ENERGY
# A = np.array([[25**2, -25],
#               [25**2, 25]])
# Emin = 300/1000
# b = np.array([800, 1000])/1000 - Emin
# x = np.linalg.solve(A, b)
# a = round(x[0], 5)
# b = round(x[1], 5)
# d = 0
# print(a,b)


# ENERGY
# A = np.array([[25**2, 0, 25],
#               [25**2, 0.3**2, 25],
#               [25**2, 0, -25]])
# Emin = 300/1000
# Emax = 1
# b = np.array([700, 1000, 500])/1000 - Emin
# x = np.linalg.solve(A, b)
# a = round(x[0], 5)
# b = round(x[1], 5)
# c = round(x[2], 5)
# d = 0
# print(a,b,c)

# RISK
# A = np.array([[25**2, 0, 0],
#               [25**2, 0.3**2, 0.3**2 * 25**2],
#               [0, 0.3**2, 0]])
# Emin = 0.05
# b = (np.array([0.4, 1, 0.4])) - 0.05
# x = np.linalg.solve(A, b)
# a = round(x[0], 5)
# b = round(x[1], 5)
# d = round(x[2], 5)
# print(a,b,d)
# c = 0

# Define the range of values for s and t
s = np.linspace(-30, 30, 1000)
t = np.linspace(0, 0.3, 1000)

# Create a grid of s and t values
S, T = np.meshgrid(s, t)

# Define the formula for the paraboloid
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('Slope [deg]',fontsize=24,labelpad=20)
ax.set_ylabel('Rock abundance',fontsize=24,labelpad=20)
ax.set_xlim(-30, 30)
ax.set_ylim(0, 0.3)
ax.tick_params(axis='both', which='major', labelsize=20)

# #E = a * S**2 + b * T**2 + c * S + d * S**2 * T**2 + Emin

# E from paper
a=803.2968238721301759
b=10.54194281076523865
c=70.24968572527038191
d=0.7385792481143100829
e=-1.419818211608492975
f=1772.951464116003308
a=803.3
b=10.54
c=70.25
d=0.7386
e=-1.420
f=1773

r = 0.3
s = 30
E_max = a + b*s + c*r + d*s**2 + e*s*r + f*r**2
print("E_max: ", E_max)
E = a + b*S + c*T + d*S**2 + e*S*T+ f*T**2 
E_min = np.min(E)
print("E_min: ", E_min)
s=-1.8083251946474188
r=0.0020000000949949026
example = (a + b*s + c*r + d*s**2 + e*s*r + f*r**2)/E_max
print("Example value: ", example)
print("E_min relativ: ", E_min/E_max)
ax.set_zlabel('Cost for energy consumption', fontsize=24, labelpad=20)
ax.plot_surface(S, T, E/E_max, cmap='viridis')
ax.set_zlim(E_min/E_max*0.5, 1)
ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
ax.zaxis.set_major_locator(ticker.MaxNLocator(5))

##### Second figure #####
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('Slope [deg]',fontsize=24,labelpad=20)
ax.set_ylabel('Rock abundance',fontsize=24,labelpad=20)
ax.set_xlim(-30, 30)
ax.set_ylim(0, 0.3)
ax.tick_params(axis='both', which='major', labelsize=20)
ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
ax.zaxis.set_major_locator(ticker.MaxNLocator(5))

#Crash rate from paper
a=-0.02877745845489390955
b=0.0005310093874191773979
c=0.3194232050084267471
d=0.0003137259635039606935
e=-0.02298305359843712606
f=10.80276197727815379
a=0#-0.02878
b=0.0005310
c=0.3194
d=0.0003137
e=-0.02298
f=10.80

crash = a + b*S + c*T + d*S**2 + e*S*T + f*T**2
r_max = 0.3
s_max = -30
crash_max = a + b*s_max + c*r_max + d*s_max**2 + e*s_max*r_max + f*r_max**2
print("Crash min: ", np.min(crash))
print("Crash max: ", crash_max)
# s=-1.8083251946474188
# r=0.0020000000949949026
# print("Example value that should be positive: ", a + b*s + c*r + d*s**2 + e*s*r + f*r**2)

R_max = (1-(1-crash_max))
print("R_max: ", R_max)
R = 1/R_max * (1-(1-crash))

s=-1.8083251946474188
r=0.0020000000949949026
crash1 = a + b*s + c*r + d*s**2 + e*s*r + f*r**2
R1 = 1/R_max * (1-(1-crash1))
print("Example value: ", R1)

ax.set_zlabel('Normalized crash rate',fontsize=24,labelpad=20)
ax.plot_surface(S, T, R, cmap='viridis')
ax.set_zlim(0, 1)

# ##### Example paraboloid formula #####
# Z = (S**2 + T**2)
# Z = Z/np.max(Z)
# ax.plot_surface(S, T, Z, cmap='viridis')

# Show both plot
plt.show()
