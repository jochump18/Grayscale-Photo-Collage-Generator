import numpy as np
from PIL import Image
import os,random
from decimal import Decimal
import sys
import ConfigParser as configparser


lst_arguments = sys.argv

print sys.path[0] + '/collage.cfg'

config = configparser.ConfigParser()
config.read(sys.path[0] + '/collage.cfg')

'''Input Filepath,Box Size(Smaller Boxes = Higher Quality)'''
def Image_Collage_Pipeline(path,box_size):

    if len(lst_arguments) > 1:
        box_size = int(lst_arguments[1])
    '''Specifying a boxsize in the command line will override the config file'''

    def open_white(size):
        quarter = Image.open(config.get('Pixel Images','directory') + config.get('Pixel Images','white'))
        quarter = quarter.resize((size,size))
        return quarter

    def open_light_grey(size):
        quarter = Image.open(config.get('Pixel Images','directory') + config.get('Pixel Images','lightgrey'))
        quarter = quarter.resize((size,size))
        return quarter

    def open_black(size):
        quarter = Image.open(config.get('Pixel Images','directory') + config.get('Pixel Images','black'))
        quarter = quarter.resize((size,size))
        return quarter

    def open_grey(size):
        quarter = Image.open(config.get('Pixel Images','directory') + config.get('Pixel Images','grey'))
        quarter = quarter.resize((size,size))
        return quarter

    def open_darkgrey(size):
        quarter = Image.open(config.get('Pixel Images','directory') + config.get('Pixel Images','darkgrey'))
        quarter = quarter.resize((size,size))
        return quarter

    '''RGBA-->RGB Code'''
    def RGB_converter(image_filepath):
        im = Image.open(image_filepath)
        background = Image.new("RGB", im.size, (255, 255, 255))
        background.paste(im, mask=im.split()[3]) # 3 is the alpha channel
        background.save(image_filepath[0:len(image_filepath)-4] + 'RGB.png', 'JPEG', quality=80)

        return Image.open(image_filepath[0:len(image_filepath)-4] + 'RGB.png')

    im = Image.open(path)
    blank = Image.new('RGBA',im.size)

    if im.mode == 'RGBA':
        im = RGB_converter(path)
        print 'Converted Image'

    def Round_to_Ten(image):
        x_size = image.size[0]
        y_size = image.size[1]
        if x_size % box_size != 0:
            for i in range(box_size):
                x_size = image.size[0]-i
                if x_size % box_size ==0:
                    break
        if y_size % box_size != 0:
            for i in range(box_size):
                y_size = image.size[1]-i
                if y_size % box_size ==0:
                    break
        image = image.resize((x_size,y_size))
        return image
    im = Round_to_Ten(im)


    '''Boxxer takes image and divides it into
    box_size by box_size boxes and returns an
    array of the average pixel values of each box'''
    def Boxxer(im,box_size):
        pixels = im.load()
        square_lst = []
        column_counter = 0
        row_counter = 0
        print im.size
        for y in range(0,im.size[1],box_size):
            y_pix = row_counter*box_size
            column_counter = 0
            # print 'column:',column_counter
            for x in range(0,im.size[0],box_size):
                x_pix = column_counter*box_size
                # print 'row:',row_counter
                for j in range(y_pix,y_pix+box_size):
                    for i in range(x_pix,x_pix+box_size):
                        if x_pix + box_size <= im.size[0] and y_pix + box_size <= im.size[1]:
                            square_lst.append((pixels[i,j][0]+pixels[i,j][1]+pixels[i,j][2])/3.0)
                column_counter += 1
            row_counter += 1

        print 'columns:',column_counter
        print 'rows:',row_counter
        empty = np.zeros([row_counter,column_counter,1])
        print empty.shape
        print len(square_lst)/(box_size**2), 'boxes'

        ij = 0
        for i in range(0,row_counter):
            for j in range(0,column_counter):
                box_lst = square_lst[(ij)*(box_size**2):(ij)*(box_size**2)+(box_size**2)]
                avg_pix = sum(box_lst)/float(len(box_lst))
                if avg_pix > 185:
                    empty[i,j] = 0
                if avg_pix > 153 and avg_pix <= 185:
                    empty[i,j] = 4
                if avg_pix > 102 and avg_pix <= 153:
                    empty[i,j] = 1
                if avg_pix > 51 and avg_pix <= 102:
                    empty[i,j] = 3
                if avg_pix <= 51:
                    empty[i,j] = 2
                ij += 1
                '''0:White,4:LightGrey,1:Grey,3:DarkGrey,2:Black'''
        return empty

    array_result = Boxxer(im,box_size)
    print 'Segmentation Complete'

    def Paste_Function(array,blank):
        print array.shape
        column_counter = 0
        row_counter = 0
        for y in range(0,blank.size[1],box_size):
            y_pix = row_counter*box_size
            column_counter = 0
            print round(Decimal((y/float(im.size[1]))*100),2),'%'
            for x in range(0,blank.size[0],box_size):
                x_pix = row_counter*box_size
                while row_counter != array.shape[0] and column_counter != array.shape[1]:
                    if array[row_counter,column_counter]== 0:
                        neww1 = open_white(box_size)
                        blank.paste(neww1,(column_counter*box_size,row_counter*box_size))
                    if array[row_counter,column_counter]== 2:
                        neww2 = open_black(box_size)
                        blank.paste(neww2,(column_counter*box_size,row_counter*box_size))
                    if array[row_counter,column_counter]== 1:
                        neww3 = open_grey(box_size)
                        blank.paste(neww3,(column_counter*box_size,row_counter*box_size))
                    if array[row_counter,column_counter]== 3:
                        neww3 = open_darkgrey(box_size)
                        blank.paste(neww3,(column_counter*box_size,row_counter*box_size))
                    if array[row_counter,column_counter]== 4:
                        neww4 = open_light_grey(box_size)
                        blank.paste(neww4,(column_counter*box_size,row_counter*box_size))
                    column_counter += 1
            row_counter += 1


        blank.save(config.get('Save Location','filepath'), 'PNG', quality=100)
        print 'Image Saved'
        blank.show()
        return blank

    return Paste_Function(array_result,blank)

Image_Collage_Pipeline(config.get('Collage Image','path'),config.getint('Collage Image','boxsize'))
