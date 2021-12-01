import PIL
from PIL import Image, ImageDraw, ImageFont
import os
import os.path, time
import sys, getopt
import glob

def bulletin():

    area = "not defined"
    x = "not defined"
    y = "not defined"
    durationDays = "not defined"
    
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,"p:x:y:d:")
    except getopt.GetoptError:
        sys.exit(2)
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

    
    heatmaps = glob.glob('./OUTPUT/HEAT/H*.png')
    countmaps = glob.glob('./OUTPUT/FLOATS/F*.png')
    
    img_final_heatmap     = Image.open(heatmaps[-1])
    img_initial_heatmap   = Image.open(heatmaps[0])
    img_final_countmap    = Image.open(countmaps[-1])
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
    
    img_logo_new_Height = 300
    
    img_logo_height_percent = (img_logo_new_Height / float(img_logo.size[1]))
    img_logo_new_Width = int((float(img_logo.size[0]) * float(img_logo_height_percent)))
    img_logo_new = img_logo.resize((img_logo_new_Width, img_logo_new_Height), PIL.Image.NEAREST)
    
    # Resize the final heatmap on the left side
    
    img_final_heatmap_new_Height = img_final_heatmap_Height
    
    img_final_heatmap_height_percent = (img_final_heatmap_new_Height / float(img_final_heatmap.size[1]))
    img_final_heatmap_new_Width = int((float(img_final_heatmap.size[0]) * float(img_final_heatmap_height_percent)))
    img_final_heatmap_new = img_final_heatmap.resize((int(img_final_heatmap_new_Width), int(img_final_heatmap_new_Height)), PIL.Image.NEAREST)
    
    
    # Resize the three maps on the right side
    
    img_initial_heatmap_new_Height = int(img_final_heatmap_new_Height / 3)
    
    img_initial_heatmap_height_percent = (img_initial_heatmap_new_Height / float(img_initial_heatmap.size[1]))
    img_initial_heatmap_new_Width = int((float(img_initial_heatmap.size[0]) * float(img_initial_heatmap_height_percent)))
    img_initial_heatmap_new = img_initial_heatmap.resize((int(img_initial_heatmap_new_Width), int(img_initial_heatmap_new_Height)), PIL.Image.NEAREST)
    
    
    img_final_countmap_new_Width = img_initial_heatmap_new_Width
    
    img_final_countmap_width_percent = (img_final_countmap_new_Width / float(img_final_countmap.size[0]))
    img_final_countmap_new_Height = int((float(img_final_countmap.size[1]) * float(img_final_countmap_width_percent)))
    img_final_countmap_new = img_final_countmap.resize((int(img_final_countmap_new_Width), int(img_final_countmap_new_Height)), PIL.Image.NEAREST)
    
    
    img_final_exposuremap_new_Height = int(img_final_heatmap_new_Height / 3)
    
    img_final_exposuremap_height_percent = (img_final_exposuremap_new_Height / float(img_final_exposuremap.size[1]))
    img_final_exposuremap_new_Width = int((float(img_final_exposuremap.size[0]) * float(img_final_exposuremap_height_percent)))
    img_final_exposuremap_new = img_final_exposuremap.resize((int(img_final_exposuremap_new_Width), int(img_final_exposuremap_new_Height)), PIL.Image.NEAREST)
    
    
    # Generate the new combined image
    
    newImg = Image.new('RGBA', (2 * margin + img_final_heatmap_new_Width + img_initial_heatmap_new_Width, margin + img_logo_new_Height + img_final_heatmap_new_Height + img_footer_Height), (255, 255, 255))
    
    newImg.paste(img_logo_new                   , (margin                                          , margin))
    newImg.paste(img_final_heatmap_new          , (margin                                          , margin + img_logo_new_Height))
    newImg.paste(img_initial_heatmap_new        , (margin + img_final_heatmap_new_Width            , margin + img_logo_new_Height))
    newImg.paste(img_final_countmap_new         , (margin + img_final_heatmap_new_Width            , margin + img_logo_new_Height + int(img_initial_heatmap_new_Height)))
    newImg.paste(img_final_exposuremap_new      , (margin + img_final_heatmap_new_Width            , margin + img_logo_new_Height + int(img_initial_heatmap_new_Height) + img_final_countmap_new_Height))
    newImg.paste(img_footer                     , (margin + int((img_final_heatmap_new_Width + img_initial_heatmap_new_Width) / 2 - (img_footer_Width /2)), margin + img_logo_new_Height + img_final_heatmap_new_Height))
    
    
    
    font_path_1 = "ariali.ttf"
    font_1 = ImageFont.truetype(font_path_1, 40)
    
    font_path_2 = "ariali.ttf"
    font_2 = ImageFont.truetype(font_path_2, 30)
    
    font_path_3 = "arialbd.ttf"
    font_3 = ImageFont.truetype(font_path_3, 76)
    
    font_path_4 = "arial.ttf"
    font_4 = ImageFont.truetype(font_path_4, 64)
    
    font_path_5 = "arial.ttf"
    font_5 = ImageFont.truetype(font_path_5, 42)
    
   
    filecreated = time.ctime(os.path.getctime('./OUTPUT/HEAT/LET.png'))
    
    draw = PIL.ImageDraw.Draw(newImg)
    draw.text(((img_logo_new_Width + 180, img_logo_new_Height / 2.4)), ('CONTAMINANT SOURCE RETRIEVAL SERVICE'), font=font_3,fill=(23,111,176,255))
    draw.text((img_final_heatmap_new_Width + img_initial_heatmap_new_Width - 670, img_logo_new_Height / 6.3), ('Bulletin generated on: ' + filecreated), font=font_2,fill=(0,0,0,255))
    draw.text((img_final_heatmap_new_Width + img_initial_heatmap_new_Width - 670, img_logo_new_Height / 2.2), ('Area: ' + area), font=font_1,fill=(0,0,0,255))
    draw.text((img_final_heatmap_new_Width + img_initial_heatmap_new_Width - 670, img_logo_new_Height / 1.5), ('Your coordinates x = ' + x + '°; ' + 'y = ' + y + '°'), font=font_1,fill=(0,0,0,255))
    draw.text((img_final_heatmap_new_Width + img_initial_heatmap_new_Width - 670, img_logo_new_Height / 1.15), ('Simulation length: ' + str(round(durationDays,2)) + ' days'), font=font_1,fill=(0,0,0,255))
    
    draw.text((830, 560), ('FINAL PROBABILITY MAP'), font=font_4,fill=(0,0,0,255))
    draw.text((2690, 380), ('INITIAL SITUATION'), font=font_5,fill=(0,0,0,255))
    draw.text((2585, 1062), ('FINAL PARTICLES LOCATION'), font=font_5,fill=(0,0,0,255))
    draw.text((2643, 1838), ('EXPOSURE OVER TIME'), font=font_5,fill=(0,0,0,255))
    
    
    newImg.save("OUTPUT/BULLETIN/bulletin.png", quality = 95)
      