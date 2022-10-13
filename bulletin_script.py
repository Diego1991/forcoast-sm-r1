#(C) Copyright FORCOAST H2020 project under Grant No. 870465. All rights reserved.

# Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2022 Marine Institute, Deltares
#       Diego Pereiro, Gido Stoop
#
#       diego.pereiro@marine.ie, gido.stoop@deltares.nl
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------

import PIL
from PIL import Image, ImageDraw, ImageFont
import os
import os.path, time
import sys, getopt
import glob
import cv2

area = "not defined"
x = "not defined"
y = "not defined"
durationDays = "not defined"

argv = sys.argv[1:]

opts, args = getopt.getopt(argv,"p:x:y:d:")

for opt, arg in opts:
    if opt in ("-p", "--pilot"):
        if arg == "1":
            area = "Sado Estuary"
        elif arg == "2":
            area = "Bay of Biscay"
        elif arg == "3":
            area = "Western Black Sea"
        elif arg == "4":
            area = "Southern North Sea"
        elif arg == "5":
            area = "Galway Bay"
        elif arg == "6":
            area = "Limfjord"
        elif arg == "7":
            area = "Western Black Sea"
        elif arg == "8":
            area = "Northern Adriatic Sea"
    elif opt in ("-x", "--lon"):
        x = arg
    elif opt in ("-y", "--lat"):
        y = arg
    elif opt in ("-d", "--duration"):
        duration = float(arg)
        durationDays = duration / 24        

def resize_width(image, width, height, new_width):
    new_height = int((new_width/width)*height)
    image_resize = image.resize((new_width, new_height), PIL.Image.NEAREST)
    return image_resize, new_width, new_height

def singleBulletinFrame(i, heatmap, countmap):


    img_heatmap           = Image.open(heatmap)
    img_countmap          = Image.open(countmap)
    img_exposuremap       = Image.open('./OUTPUT/HEAT/LET.png')
    img_logo              = Image.open('FORCOAST_Logo_WhiteBack.png')
    img_footer            = Image.open('FORCOAST_Footer_Blue.png')

    img_heatmap_Width             , img_heatmap_Height              = img_heatmap.size
    img_countmap_Width            , img_countmap_Height             = img_countmap.size
    img_exposuremap_Width         , img_exposuremap_Height          = img_exposuremap.size
    img_logo_Width                , img_logo_Height                 = img_logo.size
    img_footer_Width              , img_footer_Height               = img_footer.size

    #size compression constant
    c = 1.5

    margin = int( 25 / c )

    # Resize images
    img_heatmap_resize,     img_heatmap_resize_Width,     img_heatmap_resize_Height \
        = resize_width(img_heatmap, img_heatmap_Width, img_heatmap_Height, int(2000 / c))
    img_countmap_resize,    img_countmap_resize_Width,    img_countmap_resize_Height = \
        resize_width(img_countmap, img_countmap_Width, img_countmap_Height, int(1333 / c))
    img_exposuremap_resize, img_exposuremap_resize_Width, img_exposuremap_resize_Height = \
        resize_width(img_exposuremap, img_exposuremap_Width, img_exposuremap_Height, int(1333 / c))
    img_logo_resize,        img_logo_resize_Width,        img_logo_resize_Height = \
        resize_width(img_logo, img_logo_Width, img_logo_Height, int(600 / c))

    #Calculate bulletin width
    bull_width = int( 2 * margin + img_heatmap_resize_Width + margin + img_countmap_resize_Width + margin + img_exposuremap_resize_Width )
    img_footer_resize,      img_footer_resize_Width,      img_footer_resize_Height = \
        resize_width(img_footer, img_footer_Width, img_footer_Height, bull_width)

    # Calculate bulletin height
    bull_height = int( 2* margin + img_heatmap_resize_Height + img_footer_resize_Height )

    # Generate the new combined image

    newImg = Image.new('RGBA', (bull_width, bull_height), (255, 255, 255))

    newImg.paste(img_logo_resize, (int(margin + img_heatmap_resize_Width), 5*margin))
    newImg.paste(img_heatmap_resize, (margin, margin))
    newImg.paste(img_countmap_resize, (int(margin + img_heatmap_resize_Width), int(margin + (img_heatmap_resize_Height - img_countmap_resize_Height))))
    newImg.paste(img_exposuremap_resize, (int(margin + img_heatmap_resize_Width + img_countmap_resize_Width), int(margin + (img_heatmap_resize_Height - img_exposuremap_resize_Height))))
    newImg.paste(img_footer_resize, (0, int(bull_height - img_footer_resize_Height)))

    font_path_1 = "ariali.ttf"
    font_1 = ImageFont.truetype(font_path_1, int(40 / c))

    font_path_2 = "ariali.ttf"
    font_2 = ImageFont.truetype(font_path_2, int(30 / c))

    font_path_3 = "arialbd.ttf"
    font_3 = ImageFont.truetype(font_path_3, int(76 / c))

    font_path_4 = "arial.ttf"
    font_4 = ImageFont.truetype(font_path_4, int(64 / c))

    font_path_5 = "arial.ttf"
    font_5 = ImageFont.truetype(font_path_5, int(42 / c))

    filecreated = time.ctime(os.path.getctime('./OUTPUT/HEAT/LET.png'))

    draw = PIL.ImageDraw.Draw(newImg)
    
    
    draw.text((int(img_heatmap_resize_Width + img_logo_resize_Width + 150 / c), int(5*margin)), ('CONTAMINANT SOURCE RETRIEVAL SERVICE'), font=font_3,fill=(23,111,176,255))
    draw.text((int(img_heatmap_resize_Width + img_logo_resize_Width + 150 / c), int(5*margin + 100 / c)), ('Bulletin generated on: ' + filecreated), font=font_2,fill=(0,0,0,255))
    draw.text((int(img_heatmap_resize_Width + img_logo_resize_Width + 150 / c), int(5*margin + 150 / c)), ('Area: ' + area), font=font_1,fill=(0,0,0,255))
    draw.text((int(img_heatmap_resize_Width + img_logo_resize_Width + 150 / c), int(5*margin + 200 / c)), ('Your coordinates x = ' + x + '°; ' + 'y = ' + y + '°'), font=font_1,fill=(0,0,0,255))
    draw.text((int(img_heatmap_resize_Width + img_logo_resize_Width + 150 / c), int(5*margin + 250 / c)), ('Simulation length: ' + str(round(durationDays,2)) + ' days'), font=font_1,fill=(0,0,0,255))
 
    #draw.text((830, 560), ('FINAL PROBABILITY MAP'), font=font_4,fill=(0,0,0,255))
    #draw.text((2690, 380), ('INITIAL SITUATION'), font=font_5,fill=(0,0,0,255))
    #draw.text((2585, 1062), ('FINAL PARTICLES LOCATION'), font=font_5,fill=(0,0,0,255))
    #draw.text((2643, 1838), ('EXPOSURE OVER TIME'), font=font_5,fill=(0,0,0,255))

    if i < 10:
        newImg.save("./OUTPUT/BULLETIN/bulletin_0{}.png".format(i), quality = 95)
    else:
        newImg.save("./OUTPUT/BULLETIN/bulletin_{}.png".format(i), quality = 95)

    return bull_width, bull_height

def make_video(frame_folder, bull_width, bull_height):
    images = sorted(glob.glob(f"{frame_folder}/*.png"))
    for i, image in enumerate(images):
            ResizeBulletin = Image.new('RGBA', (1920, 1080), (0, 0, 0))
            Bulletin = Image.open(image)
            Bulletin_resize, Bulletin_resize_Width, Bulletin_resize_Height = resize_width(Bulletin, bull_width, bull_height, 1920)
            ResizeBulletin.paste(Bulletin_resize, (0, 540 - (int(Bulletin_resize_Height/2))))
            if i < 10:
                ResizeBulletin.save("{}/0{}_resize.png".format(frame_folder, i), quality = 95)
            else:
                ResizeBulletin.save("{}/{}_resize.png".format(frame_folder, i), quality = 95)
            
    imagesResize = [cv2.imread(imageResize) for imageResize in sorted(glob.glob(f"{frame_folder}/*_resize.png"), reverse=True)]
    if len(images) == 0:
        print("No frames for video")
    else:
        fourccTelegram = cv2.VideoWriter_fourcc(*'mp4v')
        TelegramVideo = cv2.VideoWriter("./OUTPUT/BULLETIN/bulletin.mp4", fourccTelegram, 0.7, (1920, 1080))
        print("Telegram Video Writer Initiatied")
        for imageResize in imagesResize:
            TelegramVideo.write(imageResize)
        print("Telegram Video generated")

        fourccWeb = cv2.VideoWriter_fourcc(*'vp80')
        Webvideo = cv2.VideoWriter("./OUTPUT/BULLETIN/bulletin.webm", fourccWeb, 0.7, (1920, 1080))
        print("Web Video Writer Initiatied")
        for imageResize in imagesResize:
            Webvideo.write(imageResize)
        print("Web Video generated")

heatmaps = sorted(glob.glob('./OUTPUT/HEAT/H*.png'))
countmaps = sorted(glob.glob('./OUTPUT/FLOATS/F*.png'))   

for i, (heatmap, countmap) in enumerate(zip(heatmaps, countmaps)):
    bull_width, bull_height = singleBulletinFrame(i, heatmap, countmap)

make_video("./OUTPUT/BULLETIN", bull_width, bull_height)