import PIL
from PIL import Image
import glob

def bulletin():
    
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
   
    newImg.save("OUTPUT/BULLETIN/bulletin.png", quality = 95)