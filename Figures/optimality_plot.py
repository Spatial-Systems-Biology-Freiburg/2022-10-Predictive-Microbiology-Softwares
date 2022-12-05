import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.colors as mcolors

plt.rcParams["font.family"] = "serif"
plt.rc('text', usetex=True)
plt.rcParams['text.latex.preamble'] = r"\usepackage{bm} \usepackage{amsmath}"

def ellipse(t, u, v, a, b, alpha):
    ell = np.array([
        u + a * np.cos(t) * np.cos(alpha) - b * np.sin(t) * np.sin(alpha),
        v + a * np.cos(t) * np.sin(alpha) + b * np.sin(t) * np.cos(alpha)
    ])
    return ell

def rectangle(t, u, v, a, b, alpha):
    beta = np.arctan(b / a)
    x = []
    y = []  
    for tt in t:
        if tt <= beta or tt > (2*np.pi-beta):
            x.append(a)
            y.append(a*np.tan(tt))
        elif (beta) < tt <= (-beta+np.pi):
            x.append(b/np.tan(tt))
            y.append(b)
        elif (-beta+np.pi) < tt <= (beta+1*np.pi):
            x.append(-a)
            y.append(-a*np.tan(tt))
        elif (beta+1*np.pi) < tt <= (beta+2*np.pi):
            x.append(-b/np.tan(tt))
            y.append(-b)

    return np.array([
        u+np.array(x)*np.cos(alpha) - np.array(y)*np.sin(alpha), 
        v + np.array(x)*np.sin(alpha) + np.array(y)*np.cos(alpha)
        ])

u=3.     #x-position of the center
v=3.     #y-position of the center
a=2.     #radius on the x-axis
b=1.    #radius on the y-axis
alpha=0.1 * 2.0*np.pi #rotation angle

t = np.linspace(0, 2*np.pi, 300)
x, y = ellipse(t, u, v, a, b, alpha)
xr, yr = rectangle(t, u, v, a, b, alpha)

# Define properties for arrow. Calculate the minimum and maximum distance and the indices 
# of x, y
id_max = np.argmax((u-x)**2 + (v-y)**2)
id_min = np.argmin((u-x)**2 + (v-y)**2)

beta = np.arctan(b/a)


fig, ax = plt.subplots(figsize=(6, 6))
ax.fill(x, y, color=mcolors.CSS4_COLORS['lightsteelblue'])
ax.plot(x, y, color=mcolors.CSS4_COLORS['midnightblue'])
ax.plot(xr, yr, "--", color=mcolors.CSS4_COLORS['gray'])

# Create a rectangle in which ellipsoid is located
dxa = np.cos(alpha+beta)*np.sqrt(a**2 + b**2)
dya = np.sin(alpha+beta)*np.sqrt(a**2 + b**2)

dxr = np.cos(0.25*2.0*np.pi-alpha+beta)*np.sqrt(a**2 + b**2)
dyr = np.sin(0.25*2.0*np.pi-alpha+beta)*np.sqrt(a**2 + b**2)

# Plot the arrows at the minimum and maximum distance
ax.arrow(u, v, x[id_max]-u, y[id_max]-v, shape="full", color=mcolors.CSS4_COLORS['black'])
ax.arrow(u, v, x[id_min]-u, y[id_min]-v, color=mcolors.CSS4_COLORS['black'])
#ax.arrow(u, v, dxa, dya, color=mcolors.CSS4_COLORS['black'])
#ax.text(u+0.25, v, "E-optimality", rotation=30)
ax.text(u+0.6, v+0.1, r"$\lambda_1$", fontsize=20)
ax.text(u-0.5, v+0.15, r"$\lambda_2$", fontsize=20)


ax.set_xlim(np.min(xr)-0.15, np.max(xr)+0.15)
ax.set_ylim(np.min(xr)-0.15, np.max(yr)+0.15)
ax.set_xlabel(r'$p_2$', fontsize=20)
ax.set_ylabel(r'$p_1$', fontsize=20, rotation=90)
frame1 = plt.gca()
frame1.axes.xaxis.set_ticklabels([])
frame1.axes.yaxis.set_ticklabels([])
plt.savefig("Figures/optimality_criteria.pdf", bbox_inches='tight')
plt.close(fig) 
