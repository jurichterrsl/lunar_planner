import numpy as np
import matplotlib.pyplot as plt

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import ticker, colors

x = np.linspace(0,0.3,100)
y = x**2
plt.plot(x,y/(np.max(y)), c='r')

y2 = y * (-1/0.5*np.abs(x)+1)
plt.plot(x,y2/(np.max(y2)), c='b')



# Define the range of values for s and t
s = np.linspace(-30, 30, 1000)
t = np.linspace(0, 0.3, 1000)

# Create a grid of s and t values
S, T = np.meshgrid(s, t)

# Show enhance fi
fig = plt.figure()
ax = fig.add_subplot(131, projection='3d')
ax.set_xlim(-30, 30)
ax.set_ylim(0, 0.3)

#enhance = (-1/50*np.abs(S)+1) * (-1/0.5*np.abs(T)+1)
# ENHANCE better
x1 = -30
y1 = 0.3
f1 = 0.5

x2 = 0
y2 = 0.3
f2 = 0.6

A = np.array([[-x1**2, -y1**2],
              [-x2**2, -y2**2]])
b = np.array([f1, f2]) - 1
x = np.linalg.solve(A, b)
a2 = round(x[0], 5)
b2 = round(x[1], 5)
print(a2,b2)

enhance = 1 - a2*S**2 - b2*T**2
ax.plot_surface(S, T, enhance, cmap='viridis')

# Define the formula for the paraboloid
ax = fig.add_subplot(132, projection='3d')
ax.set_xlim(-30, 30)
ax.set_ylim(0, 0.3)

a=-0.02878
b=0.0005310
c=0.3194
d=0.0003137
e=-0.02298
f=10.80

crash = a + b*S + c*T + d*S**2 + e*S*T + f*T**2
r_max = 0.3
s_max = -30
R = 1-(1-crash*enhance)**(3.25/8)

# R_max = (1-(1-crash_max))
# R_max = (-0.0288 + 0.0005310*15 + 0.3194*0.15 + 0.0003137*15**2 + -0.02298*15*0.15 + 10.8*0.15**2)/100
# print("R_max: ", R_max)
# R = 1/R_max * (1-(1-crash))

# s=-1.8083251946474188
# r=0.0020000000949949026
# crash1 = a + b*s + c*r + d*s**2 + e*s*r + f*r**2
# R1 = 1/R_max * (1-(1-crash1))
# print("Example value: ", R1)

ax.set_zlabel('Normalized crash rate',fontsize=24,labelpad=20)
ax.plot_surface(S, T, crash/np.max(crash), cmap='viridis')
ax.set_zlim(0, 1)

ax = fig.add_subplot(133, projection='3d')
ax.set_xlim(-30, 30)
ax.set_ylim(0, 0.3)
ax.set_zlim(0, 1)
ax.plot_surface(S, T, R/np.max(R), cmap='viridis')

plt.show()