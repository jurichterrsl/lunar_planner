import numpy as np
import matplotlib.pyplot as plt
from itertools import product
from mapdata import setup_aristarchus_hm, setup_aristarchus_cp, setup_aristarchus_imp
from globalplanner import transform, astar
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import colors
import colorsys
import matplotlib.image as mpimg
import os
from matplotlib import ticker

###### Show maps global ######
setup_hm = setup_aristarchus_hm.Setup('src/mapdata/', 1.0, 0.0, 0.0, plot_global=False)
setup_imp = setup_aristarchus_imp.Setup('src/mapdata/', 1.0, 0.0, 0.0, plot_global=False)
setup_cp = setup_aristarchus_cp.Setup('src/mapdata/', 1.0, 0.0, 0.0, plot_global=False)
setups = [setup_hm, setup_cp, setup_imp]

print('HM: ', setup_hm.map_size_in_pixel, setup_hm.maps.pixel_size, setup_hm.maps.extent)
print('IMP: ', setup_cp.map_size_in_pixel, setup_cp.maps.pixel_size, setup_cp.maps.extent)
print('CP: ', setup_imp.map_size_in_pixel, setup_imp.maps.pixel_size, setup_imp.maps.extent)

# cols = 4
# fig, axs = plt.subplots(3,cols)
# fig.tight_layout(h_pad=0.5, w_pad=0.58)
# cbar_labels = ['m', 'deg', '', '100%', '']
# titles = ['Height map', 'Slope', 'Rock abundance', 'Scientific interest', 'Banned areas']
# levels_heightmap = [15,10,20]
# fontsize = 15

# for i, setup in enumerate(setups):
#     _, xmax, _, ymax = setup.maps.extent
#     plotting_array = setup.maps.maps_array
#     for j in range(cols):
#         if j==2:
#             if i==1:
#                 img = axs[i, j].imshow(plotting_array[:, :, j].T, cmap='viridis',
#                                     extent=(0, xmax/1000, 0, ymax/1000), aspect = setup.maps.aspect_ratio,
#                                     vmin=0.0, vmax=0.3)
#             else:
#                 img = axs[i, j].imshow(plotting_array[:, :, j].T, cmap='viridis',
#                                     extent=(0, xmax/1000, 0, ymax/1000), aspect = setup.maps.aspect_ratio,
#                                     vmin=0.0, vmax=0.01)
#         else:
#             img = axs[i, j].imshow(plotting_array[:, :, j].T, cmap='viridis',
#                                 extent=(0, xmax/1000, 0, ymax/1000), aspect = setup.maps.aspect_ratio)
#         if j==0:
#             axs[i, j].contour(np.flip(plotting_array[:,:,j].T, axis=0), 
#                                 levels=levels_heightmap[i], colors='#000000', linestyles='solid', linewidths=1,
#                                 extent=(0, xmax/1000, 0, ymax/1000))

#         cbar = plt.colorbar(img, ax=axs[i, j])
#         cbar.ax.tick_params(labelsize=fontsize)
#         cbar.set_label(cbar_labels[j], fontsize=fontsize)
#         axs[i,j].set_title(titles[j], fontsize=fontsize)

# for ax in axs.flat:
#     ax.set_xlabel('x [km]', fontsize=fontsize)
#     ax.set_ylabel('y [km]', fontsize=fontsize)
#     # ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
#     # ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
#     ax.tick_params(axis='both', which='major', labelsize=fontsize)


###### Show pics local ######
setup_hm = setup_aristarchus_hm.Setup('src/mapdata/', 1.0, 0.0, 0.0, plot_global=True)
setup_imp = setup_aristarchus_imp.Setup('src/mapdata/', 1.0, 0.0, 0.0, plot_global=True)
setup_cp = setup_aristarchus_cp.Setup('src/mapdata/', 1.0, 0.0, 0.0, plot_global=True)
setups = [setup_hm, setup_cp, setup_imp]

fig2, axs2 = plt.subplots(1,3)
fig2.tight_layout(w_pad=0.5)
fontsize = 12

for i, setup in enumerate(setups):
    axs2[i].imshow(setup.maps.map_image, extent=setup.maps.extent,
                                aspect=setup.maps.aspect_ratio)

for ax in axs2.flat:
    ax.set_xlabel('LON [deg]', fontsize=fontsize)
    ax.set_ylabel('LAT [deg]', fontsize=fontsize)
    ax.xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.2f}'))
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.2f}'))
    # ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.tick_params(axis='both', which='major', labelsize=fontsize)
# axs2[0].set_title('Herodotus Mons', fontsize=fontsize)
# axs2[1].set_title('Aristarchus Central Peak', fontsize=fontsize)
# axs2[2].set_title('Aristarchus IMP', fontsize=fontsize)

# axs2[0].xaxis.set_major_locator(ticker.MaxNLocator(3))
# axs2[1].xaxis.set_major_locator(ticker.MaxNLocator(2))
# axs2[2].xaxis.set_major_locator(ticker.MaxNLocator(2))


plt.show()