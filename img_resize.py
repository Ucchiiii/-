# 画像のサイズ変更・名前変更用プログラム
# サイズ変更で縮小すると画像が荒くなるので注意

from PIL import Image
import pyautogui
import os


#path1 = './Book/Reゼロv4_1章/'
path1 = 'C:/Users/S2/Downloads/iloveimg-resized (71)/'
i = 1459
#print(path1)

scr_w, scr_h = pyautogui.size() #スクリーンサイズの取得
print(scr_w, scr_h)
# このPCのスクリーンサイズを基準にする
# PCのスクリーンサイズと基準のスクリーンサイズの比を計算
wt = int(scr_w / 1920)
ht = int(scr_h / 1080)

for file in os.listdir(path1):
    #画像読み込み(yourimage.jpgは任意の画像へのパスにすること)
    print(file, i)
    img_path = path1 + file
    img1 = Image.open(img_path)
    # img_h, img_w = img1.height, img1.width
    # t = img_w / img_h
    # hi = 803 * ht
    # wi = int(803 * t * ht)
    # #print(file)
    # img1 = img1.resize((wi, hi))
    img1.save('ReZero_reimg_Cp2_' + str(i) + '.png', quality = 90)
    i += 1

print(path1)