"""
A 2D TMz FDTD simulation, with second order ABCs to simulate an infinite domain
and a TFSF (total field scattered field) boundary to create a sinusoidal signal 
propogating in the positive x direction. The slit(s) are realised by having a 
gap in the TFSF region and setting the E field of the corresponding region behind
the gap to zero to simulate a PEC, giving the barrier some thickness.

Based on "2D TMz TFSF Boundary Example" in "Understanding the Finite-Difference
Time-Domain Method", John B. Schneider
(https://www.eecs.wsu.edu/~schneidj/ufdtd/ufdtd.pdf) 

Charles Tam 2019
"""

import numpy as np
import matplotlib.pyplot as plt

x = 51  # x extent
y = 51  # y extent
# set TFSF region
x_f = 3
x_l = 20
y_f = 3
y_l = y - 4

def update(t, no=1, width=10):
    """
    update fields and apply TFSF boundaries and ABCs as a function of time t
    """
    # set indices consitent with Schneider
    m1 = 0
    m2 = x
    n1 = 0
    n2 = y
    
    """Update H field"""
    # update 2D h fields
    h_x[0:x, n1:n2 - 1] = c_hxh[m1:m2, n1:n2 - 1] * h_x[m1:m2, n1:n2 - 1] - \
                            c_hxe[m1:m2, n1:n2 - 1] * (e_z[m1:m2, n1 + 1:n2] - e_z[m1:m2, n1:n2 - 1])

    h_y[m1:m2 - 1, n1:n2] = c_hyh[m1:m2 - 1, n1:n2] * h_y[m1:m2 - 1, n1:n2] + \
                            c_hye[m1:m2 - 1, n1:n2] * (e_z[m1 + 1:m2, n1:n2] - e_z[m1:m2 - 1, n1:n2])
    
    """TFSF boundary"""
    # correct h_y on left
    h_y[x_f - 1, y_f:y_l + 1] -= c_hye[x_f - 1, y_f:y_l + 1] * e_z1[x_f]
    
    # correct h_y on right and specify slits
    h_y[x_l, slit_idx] += c_hye[x_l, slit_idx] * e_z1[x_l]
  
    # correct h_x on top 
    h_x[x_f:x_l + 1, y_l] -= c_hxe[x_f:x_l + 1, y_l] * e_z1[x_f:x_l + 1]

    # correct h_x on bottom
    h_x[x_f:x_l + 1, y_f - 1] += c_hxe[x_f:x_l + 1, y_f - 1] * e_z1[x_f:x_l + 1]

    # update 1d h field
    h_y1[0:x - 1] = c_hyh1[0:x - 1] * h_y1[0:x - 1] + c_hye1[0:x - 1] * (e_z1[1:x] - e_z1[0:x - 1])
    
    # update 1d e field
    e_z1[1:x - 1] = c_eze1[1:x - 1] * e_z1[1:x - 1] + c_ezh1[1:x - 1] * (h_y1[1:x - 1] - h_y1[0: x - 2])
    
    # set 1d source
    e_z1[0] = A * np.sin(freq * t)
    
    # correct e_z on left
    e_z[x_f, y_f:y_l + 1] -= c_ezh[x_f, y_f:y_l + 1] * h_y1[x_f - 1]
    
    # correct e_z on right and specify slits
    e_z[x_l, slit_idx] += c_ezh[x_l, slit_idx] * h_y1[x_l]

    """Update E field"""
    # update 2d e field
    e_z[m1 + 1:m2 - 1, n1 + 1:n2 - 1] = c_eze[m1 + 1:m2 - 1, n1 + 1:n2 - 1] * e_z[m1 + 1:m2 - 1, n1 + 1:n2 - 1]  +\
                                        c_ezh[m1 + 1:m2 - 1, n1 + 1:n2 - 1] * \
                                        ((h_y[m1 + 1:m2 - 1, n1 + 1:n2 - 1] - h_y[m1:m2 - 2, n1 + 1:n2 - 1]) - \
                                        (h_x[m1 + 1:m2 - 1, n1 + 1:n2 - 1] - h_x[m1 + 1:m2 - 1, n1:n2 - 2]))  
                                        
    """Second order ABCs"""
    # ABCs on left
    e_z[0, n1:n2] = c_0 * (e_z[2, n1:n2] + e_zl[0, 1, n1:n2]) + \
                    c_1 * (e_zl[0, 0, n1:n2] + e_zl[2, 0, n1:n2] - e_z[1,n1:n2] - e_zl[1, 1, n1:n2]) + \
                    c_2 * e_zl[1, 0, n1:n2] - e_zl[2, 1, n1:n2]
    # store old fields
    e_zl[0:3, 1, n1:n2] = e_zl[0:3, 0, n1:n2]
    e_zl[0:3, 0, n1:n2] = e_z[0:3, n1:n2]
    
    # ABCs on right
    e_z[x - 1, n1:n2] = c_0 * (e_z[x - 3, n1:n2] + e_zr[0, 1, n1:n2]) + \
                        c_1 * (e_zr[0, 0, n1:n2] + e_zr[2, 0, n1:n2] - e_z[x - 2, n1:n2] - e_zr[1, 1, n1:n2]) + \
                        c_2 * e_zr[1, 0, n1:n2] - e_zr[2, 1, n1:n2]
    # store old fields
    e_zr[0:3, 1, n1:n2] = e_zr[0:3, 0, n1:n2]
    e_zr[0:3, 0, n1:n2] = e_z[x - 1: x - 4: - 1, n1:n2] 

    # ABCs on top
    e_z[m1:m2, y - 1] = c_0 * (e_z[m1:m2, y - 3] + e_zt[0, 1, m1:m2]) + \
                        c_1 * (e_zt[0, 0, m1:m2] + e_zt[2, 0, m1:m2] - e_z[m1:m2, y - 2] - e_zt[1, 1, m1:m2]) + \
                        c_2 * e_zt[1, 0, m1:m2] - e_zt[2, 1, m1:m2]
    # store old fields
    e_zt[0:3, 1, m1:m2] = e_zt[0:3, 0, m1:m2]
    e_zt[0:3, 0, m1:m2] = e_z[m1:m2, y - 1: y - 4: -1].T
    
    # ABCs on bottom
    e_z[m1:m2, 0] = c_0 * (e_z[m1:m2, 2] + e_zb[0, 1, m1:m2]) + \
                    c_1 * (e_zb[0, 0, m1:m2] + e_zb[2, 0, m1:m2] - e_z[m1:m2, 1] - e_zb[1, 1, m1:m2]) + \
                    c_2 * e_zb[1, 0, m1:m2] - e_zb[2, 1, m1:m2]
    # store old fields
    e_zb[0:3, 1, m1:m2] = e_zb[0:3, 0, m1:m2]
    e_zb[0:3, 0, m1:m2] = e_z[m1:m2, 0:3].T
    
    # create barrier
    e_z[21, slit_idx] = 0
    return e_z.T

def updateslit(no, width, space):
    """calculate indices for slits"""
    centre = int((y_l - y_f)/2)
    halfwidth = int(width/2)
    idx = np.arange(y_f, y_l + 1)
    if no == 1:
        slit = np.arange(centre - halfwidth, centre + halfwidth)
        idx = np.delete(idx, slit)
    elif no == 2:
        slit1 = np.arange(centre + int(space/2) - halfwidth, centre + int(space/2) + halfwidth)
        slit2 = np.arange(centre - int(space/2) - halfwidth, centre - int(space/2) + halfwidth)
        idx = np.delete(idx, np.concatenate((slit1, slit2)))
    else:
        slit1 = np.arange(centre - halfwidth, centre + halfwidth)
        slit2 = np.arange(centre + space - halfwidth, centre + space + halfwidth)
        slit3 = np.arange(centre - space - halfwidth, centre - space + halfwidth)
        idx = np.delete(idx, np.concatenate((slit1, slit2, slit3)))
    global slit_idx
    slit_idx = idx
    return idx

def updatefreq(_freq):
    global freq
    freq = _freq

def reset():
    """reset all fields and storage arrays"""
    global h_x, h_y, e_z, e_zl, e_zr, e_zt, e_zb, e_z1, h_y1
    e_z = np.zeros((x, y))
    h_x = np.zeros((x, y))  
    h_y = np.zeros((x, y))
    e_zl = np.zeros((3, 2, y))
    e_zr = np.zeros_like(e_zl)
    e_zt = np.zeros((3, 2, x))
    e_zb = np.zeros_like(e_zt)
    e_z1 = np.zeros(x_1d)
    h_y1 = np.zeros(x_1d - 1)

"""initialise all variables and field arrays"""
z_0 = 376.7    # impedance of free space
c = 1 / 2 ** 0.5    # courant stability factor
slit_idx = updateslit(1, 10, 10)    # default slit indices
A = 1.0    # source amplitude
freq = 0.5  # source frequency

# create empty field and update coefficient arrays for 2D
h_x = np.zeros((x, y))
c_hxh = np.full_like(h_x, 1.0)
c_hxe = np.full_like(h_x, c / z_0)
h_y = np.zeros((x, y))
c_hyh = np.full_like(h_y, 1.0)
c_hye = np.full_like(h_y, c / z_0)
e_z = np.zeros((x, y))
c_eze = np.full_like(e_z, 1.0)
c_ezh = np.full_like(e_z, c * z_0)

# create empty field and update coefficient arrays for 1D (TFSF)
n_loss = 20
loss_max = 0.35
x_1d = x + n_loss

e_z1 = np.zeros(x_1d)
c_eze1 = np.full_like(e_z1, 1.0)
c_ezh1 = np.full_like(e_z1, c * z_0)

h_y1 = np.zeros(x_1d - 1)
c_hyh1 = np.full_like(h_y1, 1.0)
c_hye1 = np.full_like(h_y1, c / z_0)

# make lossy cells
idx = np.arange(x_1d - n_loss - 1, x_1d - 1)
depth = idx - (x_1d - 1 - n_loss) + 0.5
loss = loss_max * np.square(depth / n_loss)
c_eze1[idx] = (1.0 - loss) / (1.0 + loss)
c_ezh1[idx] = c * z_0 / (1.0 + loss)
depth += 0.5
loss = loss_max * np.square(depth / n_loss)
c_hyh1[idx] = (1.0 - loss) / (1.0 + loss)
c_hye1[idx] = c / z_0 / (1.0 + loss)

# ABC coefficients
temp_1 = np.sqrt(c_ezh[0, 0] * c_hye[0, 0])
temp_2 = 1.0 / temp_1 + 2.0 + temp_1
c_0 = -(1.0 / temp_1 - 2.0 + temp_1) / temp_2
c_1 = -2.0 * (temp_1 - 1.0 / temp_1) / temp_2
c_2 = 4.0 * (temp_1 + 1.0 / temp_1) / temp_2

# storage arrays for ABCs
e_zl = np.zeros((3, 2, y))
e_zr = np.zeros_like(e_zl)
e_zt = np.zeros((3, 2, x))
e_zb = np.zeros_like(e_zt)

if __name__ == "__main__":
    t_max = 200
    for i in range(t_max):
        data = update(i)
    cbar = plt.imshow(data, origin="lower")
    plt.colorbar(cbar)
