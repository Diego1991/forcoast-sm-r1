import PIL
from PIL import Image, ImageDraw,ImageFont 
import os
import os.path, time
import sys, getopt
import yaml
import csv
import glob

# rdate = 0

# argv = sys.argv[1:]
# try:
#     opts, args = getopt.getopt(argv,"hy:s:c:t:T:k:d:",["yamlfile="])
# except getopt.GetoptError:
#     print(opts)
#     print ('USAGE : SM-A2-Postprocess.py -y <username>')
#     sys.exit(2)
# for opt, arg in opts:
#     if opt == '-h':
#         print ('USAGE : SM-A2-Postprocess.py -y <username>')
#         sys.exit()
#     elif opt in ("-y", "--yamlfile"):
#         USER_YAML_FILE = arg
#     elif opt in ("-s"):
#         # AC 10112021 - Not sure this is a safe parsing method .. Same below.
#         exec('source = '+arg)
#     elif opt in ("-c"):
#         sourcecount = int(arg)
#     elif opt in ("-t"):
#         exec('target = '+arg)
#     elif opt in ("-T"):
#         rdate = arg
#     elif opt in ("-k"):
#         targetcount = int(arg)
#     elif opt in ("-d"): # AC 10112021 shouldn't be needed ? 
#         datadir = arg
# USER_YAML_FILE = '../usr/' + USER_YAML_FILE + '/config/config.yaml'
# print ('yaml file is', USER_YAML_FILE)

# with open(USER_YAML_FILE) as f:
#     data = yaml.load(f, Loader=yaml.FullLoader)
#     figdir        = '../usr/'+data['username'] +'/output/target_' + str(targetcount)+'_source_' + str(sourcecount)+'/'
    
#     if rdate == 0:
#         rdate = data['sdate']
        
#     farea=data['experiment']
#     #fx0=data['x0']
#     #fy0=data['y0']

# TODO - Smart way to retrive earliest and latest maps

img_final_heatmap     = Image.open('./OUTPUT/HEAT/H26Nov20210000.png')
img_initial_heatmap   = Image.open('./OUTPUT/HEAT/H25Nov20211200.png')
img_final_countmap    = Image.open('./OUTPUT/FLOATS/F26Nov20210000.png')
img_final_exposuremap = Image.open('./OUTPUT/HEAT/LET.png')
img_logo              = Image.open('FORCOAST_Logo_WhiteBack.png')
img_footer            = Image.open('FORCOAST_Footer_Blue.png')



img_final_heatmap_Width       , img_final_heatmap_Height        = img_final_heatmap.size
img_initial_heatmap_Width     , img_initial_heatmap_Height      = img_initial_heatmap.size
img_final_countmap_Width      , img_final_countmap_Height       = img_final_countmap.size
img_final_exposuremap_Width   , img_final_exposuremap_Height    = img_final_exposuremap.size
img_logo_Width                , img_logo_Height                 = img_logo.size
img_footer_Width              , img_footer_Height               = img_footer.size


margin = 25

# Resize the logo

img_logo_new_Height = 350

img_logo_height_percent = (img_logo_new_Height / float(img_logo.size[1]))
img_logo_new_Width = int((float(img_logo.size[0]) * float(img_logo_height_percent)))
img_logo_new = img_logo.resize((img_logo_new_Width, img_logo_new_Height), PIL.Image.NEAREST)

# Resize the three maps on the right side

img_initial_heatmap_new_Height = int(img_final_heatmap_Height / 3)

img_initial_heatmap_height_percent = (img_initial_heatmap_new_Height / float(img_initial_heatmap.size[1]))
img_initial_heatmap_new_Width = int((float(img_initial_heatmap.size[0]) * float(img_initial_heatmap_height_percent)))
img_initial_heatmap_new = img_final_heatmap.resize((int(img_initial_heatmap_new_Width), int(img_initial_heatmap_new_Height)), PIL.Image.NEAREST)


img_final_countmap_new_Width = img_initial_heatmap_new_Width

img_final_countmap_width_percent = (img_final_countmap_new_Width / float(img_final_countmap.size[0]))
img_final_countmap_new_Height = int((float(img_final_countmap.size[1]) * float(img_final_countmap_width_percent)))
img_final_countmap_new = img_final_countmap.resize((int(img_final_countmap_new_Width), int(img_final_countmap_new_Height)), PIL.Image.NEAREST)


img_final_exposuremap_new_Height = int(img_final_heatmap_Height / 3)

img_final_exposuremap_height_percent = (img_final_exposuremap_new_Height / float(img_final_exposuremap.size[1]))
img_final_exposuremap_new_Width = int((float(img_final_exposuremap.size[0]) * float(img_final_exposuremap_height_percent)))
img_final_exposuremap_new = img_final_exposuremap.resize((int(img_final_exposuremap_new_Width), int(img_final_exposuremap_new_Height)), PIL.Image.NEAREST)

# Generate the new combined image

newImg = Image.new('RGBA', (2 * margin + img_final_heatmap_Width + img_initial_heatmap_new_Width, margin + img_logo_new_Height + img_final_heatmap_Height + img_footer_Height), (255, 255, 255))

newImg.paste(img_logo_new                       , (margin                                      , margin))
newImg.paste(img_final_heatmap              , (margin                                      , margin + img_logo_new_Height))
newImg.paste(img_initial_heatmap_new        , (margin + img_final_heatmap_Width            , margin + img_logo_new_Height))
newImg.paste(img_final_countmap_new         , (margin + img_final_heatmap_Width            , margin + img_logo_new_Height + int(img_initial_heatmap_new_Height)))
newImg.paste(img_final_exposuremap_new      , (margin + img_final_heatmap_Width            , margin + img_logo_new_Height + int(img_initial_heatmap_new_Height) + img_final_countmap_new_Height))
newImg.paste(img_footer                     , (margin + int((img_final_heatmap_Width + img_initial_heatmap_new_Width) / 2 - (img_footer_Width /2)), margin + img_logo_new_Height + img_final_heatmap_Height))



# font_path_1 = "ariali.ttf"
# font_1 = ImageFont.truetype(font_path_1, 36)

# font_path_2 = "ariali.ttf"
# font_2 = ImageFont.truetype(font_path_2, 26)

# font_path_3 = "arialbd.ttf"
# font_3 = ImageFont.truetype(font_path_3, 60)

# # print("last modified: %s" % time.ctime(os.path.getmtime(file)))
# filecreated = time.ctime(os.path.getctime(figdir+'TS_violin.png'))

# draw = PIL.ImageDraw.Draw(newImg)
# draw.text(((img_logo_new_Width + 410, img_logo_new_Height / 2.6)), ('LAND POLLUTION SERVICE'), font=font_3,fill=(23,111,176,255))
# draw.text((img_violin_Width + img_map_Width - 750, img_logo_new_Height / 1.1), ('Bulletin generated on: ' + filecreated), font=font_2,fill=(0,0,0,255))
# draw.text((img_violin_Width + img_map_Width - 750, img_logo_new_Height / 2.1), ('Release date: ' + rdate), font=font_1,fill=(0,0,0,255))
# draw.text((img_violin_Width + img_map_Width - 750, img_logo_new_Height / 4), ('Area: ' + farea), font=font_1,fill=(0,0,0,255))
# # draw.text((img_violin_Width + img_map_Width - 600, img_logo_new_Height / 5), ('x = ' + str(fx0[0]) + ' ' + 'y = ' + str(fy0[0])), font=font_1,fill=(0,0,0,255))


newImg.save("OUTPUT/BULLETIN/bulletin.png", quality = 95)

'''
# draw = PIL.ImageDraw.Draw(img)
# draw.text((100, 100),"Sample Text")
# img1.paste(img2)
# img1.save("combined.png", quality=45)
'''

