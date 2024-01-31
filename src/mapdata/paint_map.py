'''This file includes several functions to create and edit binary maps.'''

import tkinter as tk
from PIL import ImageTk, Image
import cv2
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

plt.rcParams['font.size'] = 20

class Paint():
    """
    A class to paint binary images and save them.
    
    Attributes and Methods can be seen in the class diagram by running 'pyreverse -o png \
        path/to/src/globalplanner'
    """

    def __init__(self, map_size, path):
        '''
        Initialize object Paint
            Parameters:
                map_size (int-tupel): size of map in pixel
                path (String): path to data folder
        '''
        self.pixel_height, self.pixel_width = map_size
        self.root = None
        self.bg_image = None
        self.new_layer_name = None
        self.canvas = None
        self.scale = None
        self.path = path


    def draw_mask_and_save_to_file(self, name, map_picture, zoom):
        '''
        Allows user create a binary mask in the size of the map
            Parameters:
                name (String): Name which is used to save the mask to a file
                map_picture (String): path to satellite image
                zoom (int): Zooming factor to make the picture bigger on the screen for small files
        '''
        self.root = tk.Tk()
        zoom = zoom
        self.bg_image = mpimg.imread(self.path+map_picture)
        self.bg_image = cv2.cvtColor(self.bg_image, cv2.COLOR_BGR2GRAY)

        self.new_layer_name = name

        # Resize the image to match the canvas size and make Tkinter compatible
        self.bg_image = cv2.resize(self.bg_image, (self.pixel_height*zoom, self.pixel_width*zoom))
        self.bg_image = ImageTk.PhotoImage(image=Image.fromarray((self.bg_image * 255).astype(np.uint8)))
        # Create canvas and add image
        self.canvas = tk.Canvas(self.root, width=self.pixel_height*zoom,
                                height=self.pixel_width*zoom)
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)
        self.canvas.grid(row=0, column=0, columnspan=3)

        # Add several controls and buttons
        scale_label = tk.Label(self.root, text='Pencil Size')
        scale_label.grid(row=1, column=0)
        self.scale = tk.Scale(self.root, from_=zoom, to=20*zoom, orient=tk.HORIZONTAL, length = 500)
        self.scale.grid(row=2, column=0)
        save_button = tk.Button(self.root, text='Paint', command=self.__changecolorpaint)
        save_button.grid(row=2, column=1)
        save_button = tk.Button(self.root, text='Erase', command=self.__changecolorerase)
        save_button.grid(row=2, column=2)
        save_button = tk.Button(self.root, text='Reset', command=self.__erase_mask)
        save_button.grid(row=3, column=1)
        save_button = tk.Button(self.root, text='Save', command=self.__save_mask)
        save_button.grid(row=3, column=2)

        self.canvas.bind('<B1-Motion>', self.__paint)
        self.color = 'red'

        self.root.mainloop()

    def __paint(self, event):
        '''Function gets called when the user clicks/ "paints" on the Canvas'''
        x = event.x
        y = event.y
        size = self.scale.get()
        self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=self.color, outline='')
    
    def __save_mask(self):
        '''Save the file as a numpy array'''
        # Save the file, open via PIL and convert to a numpy array
        self.canvas.postscript(file=self.path+'temp_image_save.eps', colormode='color')
        image = Image.open(self.path+'temp_image_save.eps')

        # save_sizes = [(2048, 2048), (1024, 1024), (512, 512), (256, 256), (128, 128), (64, 64)]
        # sizes_string = ['2048', '1024', '512', '256', '128', '64']
        save_sizes = [(self.pixel_height, self.pixel_width)]
        sizes_string = ['']
        for i in range(len(save_sizes)):
            array = np.array(image.resize(save_sizes[i]))
            binary_mask = np.all(array == [255, 0, 0], axis=2).astype(np.uint8)
            np.save(self.path+"binary_map_"+self.new_layer_name+sizes_string[i], binary_mask)

        print("The mask was successfully saved as 'binary_map_"+self.new_layer_name+".npy'")

        # Cleanly close Tkinter
        self.bg_image = None
        self.new_layer_name = None
        self.canvas = None
        self.scale = None
        self.root.destroy()
    
    def __erase_mask(self):
        '''Resets the canvas'''
        self.canvas.create_image(0, 0, image=self.bg_image, anchor=tk.NW)

    def __changecolorpaint(self):
        '''Resets the canvas'''
        self.color = 'red'

    def __changecolorerase(self):
        '''Resets the canvas'''
        self.color = 'black'


    def blur_binary_mask(self, path, name_image, minimal_value, blur_size, name_subtract=''):
        '''
        Modifies binary mask and sets a gradient to the binary values
            Parameters:
                path (String): path to work folder
                name_image (String): name of the mask-data in the workfolder (data must be
                    .npy file, name must be without '.npy' ending)
                minimal_value (float): cuts of blurring at this value
                blur_size (float): defines area of blur (fitting examples (mapsize:sigma_kernel):
                (256,256):7, (762,1110):30)
                name_subtract (String): blur will naturally enhance the marked areas ->
                    this mask can be used to delete blur in certain areas 
        '''
        # Load np image
        binary_image = np.load(self.path+path+'/'+name_image+'.npy')
        if name_subtract=='':
            subtract_image = np.zeros(binary_image.shape)
        else:
            subtract_image = np.load(self.path+path+'/'+name_subtract+'.npy')

        # Find the coordinates of 1s in the binary image
        rows, cols = binary_image.shape
        larger_rows = rows + 2 * blur_size
        larger_cols = cols + 2 * blur_size
        larger_array = np.zeros((larger_rows, larger_cols))
        start_x = (larger_rows - rows) // 2
        start_y = (larger_cols - cols) // 2
        larger_array[start_x:start_x + rows, start_y:start_y + cols] = binary_image

        coordinates = np.argwhere(larger_array == 1)
        washed_out_image_large = np.zeros((larger_rows, larger_cols), dtype=np.float32)
        
        kernel_size = int(2*blur_size+1)
        img=np.zeros((kernel_size,kernel_size))
        img[kernel_size//2,kernel_size//2]=1
        kernel = cv2.GaussianBlur(img, (kernel_size, kernel_size), blur_size/4)
        kernel = kernel/np.max(kernel)
        print(kernel[:, kernel.shape[0]//2+1])

        # Apply the gradient to the new image around each (x, y) coordinate
        for (x, y) in coordinates:
            x_min = x-blur_size
            x_max = x+blur_size+1
            y_min = y-blur_size
            y_max = y+blur_size+1

            washed_out_image_large[x_min:x_max, y_min:y_max] = \
                np.maximum(washed_out_image_large[x_min:x_max, y_min:y_max], kernel)

        washed_out_image = washed_out_image_large[start_x:start_x + rows, start_y:start_y + cols]
        #washed_out_image = washed_out_image/np.max(washed_out_image)

        # Add original mask on top of image
        washed_out_image[binary_image==1] = 1
        # Set a minimal value threshold
        washed_out_image[washed_out_image < minimal_value] = 0

        if name_subtract!='':
            # Show image before subtraction of binary
            plt.figure()
            plt.imshow(washed_out_image, cmap='gray_r')
            plt.colorbar()
            plt.xlabel('x_pixel')
            plt.ylabel('y-pixel')

        # Subtract binary image
        washed_out_image[subtract_image==1] = 0

        # Save to workfolder
        np.save(self.path+path+name_image+'_blurred.npy', washed_out_image)
        print("Image saved as '"+self.path+path+name_image+"_blurred.npy'.")

        # Show final image
        fig = plt.figure()
        plt.imshow(washed_out_image)
        plt.colorbar()
        plt.xlabel('x_pixel')
        plt.ylabel('y-pixel')

        plt.show()


### Examples of working with this class
if __name__ == "__main__":
    painter = Paint((256, 237), "src/mapdata/Aristarchus_IMP/")
    # painter.draw_mask_and_save_to_file('science',"pic.png",7)
    painter.blur_binary_mask("","science", 0, 13)
