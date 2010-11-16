from PIL import Image, ImageDraw, ImageFont
from pylab import imread, imshow, sum, average, array, argsort, show
from pylab import zeros, linspace, savetxt, digitize, vectorize, absolute
import os
from scipy import ndimage

fontpath = "/usr/share/fonts/truetype/freefont"

def txt2img(label, fontname="FreeMonoBold.ttf", fgcolor=0,
            bgcolor=255, rotate_angle=0, n=1):
    """Render label as image."""

    font = ImageFont.truetype(os.path.join(fontpath,fontname), 12)

    imgOut = Image.new("L", (20,49), bgcolor)

    # calculate space needed to render text
    # square blocks of size nxn are rendered
    draw = ImageDraw.Draw(imgOut)
    sizex, sizey = draw.textsize(label*n, font=font)

    imgOut = imgOut.resize((sizex,sizey*n))

    # render label into image draw area
    draw = ImageDraw.Draw(imgOut)
    for i in range(n):
        draw.text((0, sizey*i), label*n, fill=fgcolor, font=font)

    if rotate_angle:
        imgOut = imgOut.rotate(rotate_angle)

    return imgOut

def arr2img(arr, fontname="FreeMonoBold.ttf", fgcolor=0,
            bgcolor=255, rotate_angle=0):
    """Render label as image."""

    font = ImageFont.truetype(os.path.join(fontpath,fontname), 12)

    imgOut = Image.new("L", (20,49), bgcolor)

    r, c = arr.shape
    label = "".join(arr[1])
    # calculate space needed to render text
    # square blocks of size nxn are rendered
    draw = ImageDraw.Draw(imgOut)
    sizex, sizey = draw.textsize(label, font=font)

    imgOut = imgOut.resize((sizex,sizey*len(arr)))

    # render label into image draw area
    draw = ImageDraw.Draw(imgOut)
    for i, row in enumerate(arr):
        draw.text((0, sizey*i), "".join(row), fill=fgcolor, font=font)

    if rotate_angle:
        imgOut = imgOut.rotate(rotate_angle)

    return imgOut

def get_images(dirname="sample", num=10):
    if not os.path.isdir(dirname):
        if os.path.exists(dirname):
            print "Cannot create directory %s" %dirname
            raise SystemExit
        os.mkdir(dirname, 0755)
    for i in range(32, 127):
        i_img = txt2img(chr(i), n=num)
        i_img_name = os.path.join(".", dirname, str(i)+".png")
        i_img.save(i_img_name, format="PNG")
        print "saved %s" %i_img_name

def save_density_stats(dirname="sample"):
    img_stats = []
    chr_density_sort = []
    tree = os.walk(dirname)
    
    for subfol in tree:
        img_path = subfol[0]
        img_files = subfol[2]
        for img in img_files:
            img_char = img.split(".")[0]
            img_sum = sum(imread(os.path.join(img_path,img)))
            img_stats.append(img_sum)

            chr_density_sort.append(int(img_char))

    chr_density_sort = array(chr_density_sort)
    chr_density_sort = list(chr_density_sort[argsort(img_stats)])

    # print chr_density_sort, len(chr_density_sort)
    print "Visual density sort obtained."

    f = open('density_stats.txt', 'w')
    f.writelines("".join(map(chr, chr_density_sort)))
    f.close()

def get_density_stats():
    return list(open('density_stats.txt').read())

def file2gray(filename):
    """ Reads an image file, and returns a grayscale image array."""
    a = imread(filename)
    print "Converting ..."

    # useful only when reading .jpg files.
    # PIL is used for jpegs; converting PIL image to numpy array messes up. 
    # a = a[::-1, :] 

    # convert image to grayscale.
    if len(a.shape) > 2:
        a = 0.21 * a[:,:,0] + 0.71 * a[:,:,1] + 0.07 * a[:,:,2]

    return a

def blockify_img(I, blk_siz=2):
    "Pixelate the image?"
    
    I_r, I_c = I.shape[:2]
    I_max = float(I.max())

    c_r, c_c = I_r/(2*blk_siz), I_c/blk_siz
    c = zeros((c_r, c_c))
    
    for i in range(2*blk_siz):
        for j in range(blk_siz):
            c += I[i::2*blk_siz, j::blk_siz][:c_r, :c_c]

    c /= 2*blk_siz*blk_siz
    return c

def map_img_chars(b, map_array):
    """ Map values of array to corresponding chars, based on map_array.
    Returns a string array. """
    
    r, c = b.shape[:2]
    
    bins = linspace(b.min(), b.max(), len(map_array), endpoint=False)
    b = digitize(b.flatten(), bins)-1
    b.shape = r, c
    
    b = array(map_array)[b]
    return b

def write_arr(arr, file, tag, size):
    out_file = open(file + tag + str(size) + '.txt', 'w')
    savetxt(out_file, arr, fmt="%s", delimiter="")
    print "%s Converted! \nWritten to %s" %(file, out_file.name)

def img2ascii(filename, map_array=None, blk_siz=2):
    """ Convert an image file to an ascii plain text file."""
    
    a = file2gray(filename)
    c = blockify_img(a, blk_siz)

    if map_array == None:
        # just linearly map gray level to characters.
        # giving lowest gray level to space character.
        f = vectorize(lambda b: chr(32+int((1-b)*94)))
        c = f(c)
        write_arr(c, filename, "-lin-", blk_siz)
    else:
        # map based on visual density of characters.
        c = map_img_chars(c, map_array)
        write_arr(c, filename, "-arr-", blk_siz)

def transition(file1, file2, map_array, blk_siz=2, n=50):
    I = file2gray(file1)
    J = file2gray(file2)

    I = blockify_img(I, blk_siz)
    J = blockify_img(J, blk_siz)

    d = absolute(I - J)
    steps = linspace(d.min(), d.max(), n+1)
    print len(steps)
    # print steps
    for i, step in enumerate(steps):
        K = I * (d>step) + J * (d<step)
        # do something with K
        k = map_img_chars(K, map_array)

        # write_arr(k, "%s-%s" %(file1,file2), "-arr-%s-" %i, blk_siz)

        im = arr2img(k)
        im.thumbnail((280,390), Image.ANTIALIAS)
        im_name = os.path.join(".", "output", "%s-%s-%02d.png" %(file1, file2, i))
        im.save(im_name, format="PNG")

        
if __name__=="__main__":
    # get_images()
    # save_density_stats()
    chr_order = get_density_stats()
    
    chr_list = chr_order[::-10][::-1]
    print "".join(chr_list)

    # chr_str = "W#H8wUOx&soIvi=+:| "
    # chr_str = "#8wOxuIi*_ "
    # chr_list = sorted(chr_str, key=chr_order.index)

    img2ascii('carsten.png', chr_list, 2)
    img2ascii('bastien.png', chr_list, 2)

    transition('carsten.png', 'bastien.png', chr_list)        



# References
# http://code.activestate.com/recipes/483756/


# def get_symmetry_stats(dirname="sample"):
#     """Gets ordering of characters based on vertical & horizontal symmetry.
#     NOTE: Make sure the images have just 1x1 array of each character. Else, the
#     results are utterly meaningless. 
#     """
#     img_stats = []
#     tree = os.walk(dirname)
    
#     for subfol in tree:
#         img_path = subfol[0]
#         img_files = subfol[2]
#         for img_f in img_files:
#             img_char = img_f.split(".")[0]
#             img = imread(os.path.join(img_path,img_f))
#             img_r, img_c = img.shape[:2]
#             if img_r*img_c>200:
#                 print get_symmetry_stats.__doc__
#             # vertical and horizontal symmetry score calculation
#             v_sym_mat = img[:, :img_c/2] - img[:, :(img_c-1)/2:-1]
#             v_sym_score = sum(abs(v_sym_mat))
#             h_sym_mat = img[:img_r/2] - img[:(img_r-1)/2:-1]
#             h_sym_score = sum(abs(h_sym_mat))
# #            print chr(int(img_char)), v_sym_score, h_sym_score, v_sym_score*h_sym_score, v_sym_score + 5*h_sym_score
#             chr_symmetry_sort = []
# #            img_stats.append(str(int(img_sum*100)) + " " + img_char)
# #    symmetry_density_sort = [int(each.split()[1]) for each in sorted(img_stats)]
#     # print chr_density_sort, len(chr_density_sort)
#     return chr_symmetry_sort
    
