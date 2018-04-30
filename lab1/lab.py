#!/usr/bin/env python3

import sys
import math
import base64
import tkinter

from io import BytesIO
from PIL import Image as PILImage

## NO ADDITIONAL IMPORTS ALLOWED!

def box_blur(n):
    """
    Returns n-by-n box blur kernel.
    """
    kernel = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(1/n**2)
        kernel.append(row)
    return kernel

class Image:
    """
    Represents a grayscale image.
    """
    def __init__(self, width, height, pixels):
        self.width = width
        """the width of the image(in pixels)"""
        self.height = height
        """the height of the image(in pixels)"""
        self.pixels = pixels
        """a list of pixel values(0-255) stored in row-major order"""

    def get_pixel(self, x, y):
        """
        Returns the pixel value in the given position (x, y).
        """
        return self.pixels[y*self.width + x]
    
    def get_pixel_extended(self, x, y):
        """
        Returns the pixel value in the given position (x, y).
        If the position is out of range, returns closest valid pixel value.
        """
        if x > self.width-1:
            x = self.width-1
        elif x < 0:
            x = 0
        if y > self.height-1:
            y = self.height-1
        elif y < 0:
            y = 0
        return self.get_pixel(x, y)         

    def set_pixel(self, x, y, c):
        """
        Sets the pixel value at position(x, y) as c.
        """
        self.pixels[y*self.width + x] = c

    def apply_per_pixel(self, func):
        """
        Returns a new image, the result of self's pixel values
        being applied by function func.

        func has one parameter(pixel value).
        """
        result = Image.new(self.width, self.height)
        for x in range(result.width):
            for y in range(result.height):
                color = self.get_pixel(x, y)
                newcolor = func(color)
                result.set_pixel(x, y, newcolor)
        return result
    
    def clip_pixels(self):
        """
        Clips negative pixel values to 0, values > 255 to 255
        and converts all values to integer.
        """
        for i in range(len(self.pixels)):
            self.pixels[i] = int(round(self.pixels[i]))
            if self.pixels[i] < 0:
                self.pixels[i] = 0
            elif self.pixels[i] > 255:
                self.pixels[i] = 255
        
    def inverted(self):
        """
        Returns a new image, which is the inversion of self.
        """
        return self.apply_per_pixel(lambda c: 255-c)
    
    def correlate(self, kernel):
        """
        Returns a new image, the result of correlating self and kernel

        kernel is a list of lists
        """
        result = Image.new(self.width, self.height)
        kernel_size = len(kernel)//2    # distance from center to edge of kernel
        for x in range(self.width):
            for y in range(self.height):
                # loop over surrounding pixels and multiply with associated value in kernel
                # set accumulated value to pixel
                correlated = 0
                for y1 in range(len(kernel)):
                    for x1 in range(len(kernel[y1])):
                        x2 = x - kernel_size + x1
                        y2 = y - kernel_size + y1
                        correlated += self.get_pixel_extended(x2, y2) * kernel[y1][x1]
                result.set_pixel(x, y, correlated)
        return result
    
    def blurred(self, n):
        """
        Returns a new image, the result of self being blurred
        with an n-sized box blur kernel
        """
        result = self.correlate(box_blur(n))
        result.clip_pixels()
        return result
    
    def sharpened(self, n):
        """
        Returns a new image, the result of an "unsharp mask" on self.

        n is the size of box blur kernel
        """
        result = Image.new(self.width, self.height)
        blurred = self.correlate(box_blur(n))
        # compute values of sharpened image using blurred version
        for x in range(self.width):
            for y in range(self.height):
                c = 2*self.get_pixel(x, y) - blurred.get_pixel(x, y)
                result.set_pixel(x, y, c)
        result.clip_pixels()
        return result

    def edges(self):
        """
        Returns a new image, the result of applying "Sobel operator" on self.
        """
        result = Image.new(self.width, self.height)
        # correlate two images with two kernels: one - vertical, other - horizontal
        kx = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
        ky = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
        ox = self.correlate(kx)
        oy = self.correlate(ky)
        # loop over pixels and compute new values
        for x in range(self.width):
            for y in range(self.height):
                c = ((ox.get_pixel(x, y))**2 + (oy.get_pixel(x, y))**2)**0.5
                result.set_pixel(x, y, c)
        result.clip_pixels()
        return result

    def copy(self):
        """
        Returns a copy of self.
        """
        result = Image.new(self.width, self.height)
        result.pixels = self.pixels[:]
        return result

    def min_energy_column(self):
        """
        Returns position(x) of minimum energy column(defined by edge-detection method).
        """
        # compute the edges and energies of each column
        e = self.edges()
        energies = []
        for x in range(self.width):
            energy = 0
            for y in range(self.height):
                energy += e.get_pixel(x, y)
            energies.append(energy)
        # return index of minimum energy column
        return energies.index(min(energies))

    def remove_column(self, x):
        """
        Mutates self by removing pixels in the column x.
        """
        #remove pixels from the end, so that it doesn't affect location of others
        for y in reversed(range(self.height)):
            self.pixels.pop(y*self.width + x)
        self.width -= 1

    def resize(self, n_cols):
        """
        Returns a new image, the result of removing n_cols number of
        lowest energy columns
        """
        result = self.copy()
        while result.width > (self.width - n_cols):
            x = result.min_energy_column()
            result.remove_column(x)
        return result
        
    # Below this point are utilities for loading, saving, and displaying
    # images, as well as for testing.

    def __eq__(self, other):
        return all(getattr(self, i) == getattr(other, i)
                   for i in ('height', 'width', 'pixels'))

    @classmethod
    def load(cls, fname):
        """
        Loads an image from the given file and returns an instance of this
        class representing that image.  This also performs conversion to
        grayscale.

        Invoked as, for example:
           i = Image.load('test_images/cat.png')
        """
        with open(fname, 'rb') as img_handle:
            oimg = PILImage.open(img_handle)
            img = oimg.convert('L')
            w, h = img.size
            d = list(img.getdata())
            return cls(w, h, d)

    @classmethod
    def new(cls, width, height):
        """
        Creates a new blank image (all 0's) of the given height and width.

        Invoked as, for example:
            i = Image.new(640, 480)
        """
        return cls(width, height, [0 for i in range(width*height)])

    def save(self, fname, mode='PNG'):
        """
        Saves the given image to disk or to a file-like object.  If fname is
        given as a string, the file type will be inferred from the given name.
        If fname is given as a file-like object, the file type will be
        determined by the 'mode' parameter.
        """
        out = PILImage.new(mode='L', size=(self.width, self.height))
        out.putdata(self.pixels)
        if isinstance(fname, str):
            out.save(fname)
        else:
            out.save(fname, mode)
        out.close()

    def gif_data(self):
        """
        Returns a base 64 encoded string containing the given image as a GIF
        image.

        Utility function to make show_image a little cleaner.
        """
        buff = BytesIO()
        self.save(buff, mode='GIF')
        return base64.b64encode(buff.getvalue())

    def show(self):
        """
        Shows the given image in a new Tk window.
        """
        global WINDOWS_OPENED
        if tk_root is None:
            return
        WINDOWS_OPENED = True
        toplevel = tkinter.Toplevel()
        canvas = tkinter.Canvas(toplevel, height=self.height,
                                width=self.width, highlightthickness=0)
        canvas.pack()
        canvas.img = tkinter.PhotoImage(data=self.gif_data())
        canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        def on_resize(event):
            new_img = PILImage.new(mode='L', size=(self.width, self.height))
            new_img.putdata(self.pixels)
            new_img = new_img.resize((event.width, event.height), PILImage.NEAREST)
            buff = BytesIO()
            new_img.save(buff, 'GIF')
            canvas.img = tkinter.PhotoImage(data=base64.b64encode(buff.getvalue()))
            canvas.configure(height=event.height, width=event.width)
            canvas.create_image(0, 0, image=canvas.img, anchor=tkinter.NW)
        canvas.bind('<Configure>', on_resize)
        toplevel.bind('<Configure>', lambda e: canvas.configure(height=e.height, width=e.width))


try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
    tcl = tkinter.Tcl()
    def reafter():
        tcl.after(500,reafter)
    tcl.after(500,reafter)
except:
    tk_root = None
WINDOWS_OPENED = False

if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    pass

    # the following code will cause windows from Image.show to be displayed
    # properly, whether we're running interactively or not:
    if WINDOWS_OPENED and not sys.flags.interactive:
        tk_root.mainloop()
