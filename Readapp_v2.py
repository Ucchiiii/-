#!/usr/bin/env python
# -*- coding: utf-8 -*-
#system4.0を改良
#2022/06/05追記
#メインウィンドウ・メニュー画面・ライブラリ画面の3つのウィンドウ構成に変更
#各ウィンドウのUIを変更
#ページ数の表示位置を上に変更
#次へ・戻るボタンの配置と大きさを変更．枠線を消去
#本を1ページずつ表示に変更
#本はリサイズしてから表示する
#バッテリー表示を%に変更
# 2022/07/20
# device_v, mode_vの保存 show_image関数内の記述変更（アプリ起動後にメニュー画面を開いた際に以前指定したラジオボタンが選択されているように）
# pathの指定　abs_pathでの指定はせず，相対パス（./）を使用
# Reゼロ用にcanvas，「次へ」「戻る」ボタン等のサイズを変更
# 背景の変更
# ページめくりアニメーションの変更
# PCのスクリーンサイズに合わせてGUIを調整できるように変更（このPCのスクリーンサイズ（1920*1080）が基準）

# Readapp.pyのGoogleDrive連携をなくしたバージョン

# 2022/08/01追記
# クライアント接続前に接続されているクライアントを全て切断
# ぺーじめくりアニメーション表示用canvasとバッテリー残量表示用labelを一度しか生成しないように変更
# サーバーのシャットダウン
# ・右上のXボタンが押されたときにポップアップを表示し，YESの場合サーバーをシャットダウンする
# ・シャットダウンのコマンドを変更
# ・ReadappS.pyでは，Xボタンで閉じた場合サーバーがシャットダウンされず使用されたままの状態になっていたため，次に接続しようとしたときにエラーが生じていた
# サーバー番号が変更されたときに登録しやすいように，QRコードを表示するボタンを作成
# QRコードはサーバー番号に合わせて自動生成
# アプリを開いたときに表示されるページを前回閉じたページに変更

from doctest import master
from email.mime import image
#from importlib.resources import path
import json
from msilib.schema import Class
from multiprocessing.connection import wait
import os
from os import write
from re import X
import socket
import argparse
import threading
from tkinter import messagebox
from tkinter.messagebox import showerror
from tkinter.tix import Tree
#from django import views
#from numpy import apply_along_axis
import pyautogui
import cv2
import csv
import datetime
import time
import subprocess
import sys
from regex import R
from requests import delete
from websocket_server import WebsocketServer
from playsound import playsound
# Tkinterライブラリのインポート
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk, ImageOps
#import glob
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import re
import pyqrcode

lock = threading.Lock()

abs_path = 'C:/Users/S2/OneDrive/Documents/塚本寺田研究室/研究/実験2/system/'
global path
dict_name = [None] * 10
app_on = False
sub_win = None
count = 0
blink_count = 0
start_t = 0
end_t = 0
f_flag = False
play_num = 0
server = 0
FILE_PNG = 'qrcode.png'
qrview_f = False

class VideoPlayer(tk.Frame):
    def __init__(self,master):
        super().__init__(master)
        # Canvasの作成
        self.canvas = tk.Canvas(self.master, bg = "#DDDDDD", width=img_width, height=img_height)
        #self.canvas = tk.Canvas(self.master, bg = "#DDDDDD", width=624, height=803)
        # Canvasにマウスイベント（左ボタンクリック）の追加
        #self.canvas.bind('<Button-1>', self.canvas_click)
        print(img_width, img_height)
        # Canvasを配置
        # self.canvas.place(x=400, y=150 * ht)
        #self.canvas.place(x=0, y=0)
        #self.canvas.place(x=650, y=150)

    def VideoRead(self):
        # 動画を読み込み
        self.video = cv2.VideoCapture(path)

        self.disp_id = None

        if self.disp_id is None:
            # 動画を表示
            self.disp_image()
        else:
            # 動画を停止
            self.after_cancel(self.disp_id)
            self.disp_id = None

        #self.canvas_click()

    def canvas_click(self, event):
        '''Canvasのマウスクリックイベント'''

        if self.disp_id is None:
            # 動画を表示
            self.disp_image()
        else:
            # 動画を停止
            self.after_cancel(self.disp_id)
            self.disp_id = None

    def disp_image(self):
        '''画像をCanvasに表示する'''

        # フレーム画像の取得
        ret, frame = self.video.read() #動画の読み込み

        if not ret:
            #messagebox.showerror("エラー","次のフレームがないので停止します")
            #self.playing = False
            self.canvas.place_forget() # canvasの位置を忘れさせる（消去するわけではない）
            #self.canvas.delete() # キャンバス上のオブジェクトを削除（キャンバス自体は残る）
            #self.destroy()
            #app.get_video(path)
        else:
            # BGR→RGB変換
            cv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # NumPyのndarrayからPillowのImageへ変換
            pil_image = Image.fromarray(cv_image)

            # キャンバスのサイズを取得
            #canvas_width = self.canvas.winfo_width()
            #canvas_height = self.canvas.winfo_height()

            # pil_image = pil_image.crop(10, 0, 1200, 720)

            # 画像のアスペクト比（縦横比）を崩さずに指定したサイズ（キャンバスのサイズ）全体に画像をリサイズする
            pil_image = ImageOps.pad(pil_image, (img_width, img_height))
            #pil_image = ImageOps.pad(pil_image, (canvas_width, canvas_height))

            # PIL.ImageからPhotoImageへ変換する
            self.photo_image = ImageTk.PhotoImage(image=pil_image)

            # 画像の描画
            #self.canvas.create_image(
            #    canvas_width / 2,       # 画像表示位置(Canvasの中心)
            #    canvas_height / 2,                   
            #    image=self.photo_image  # 表示画像データ
            #)
            # 画像の描画
            self.canvas.create_image(
                img_width / 2,       # 画像表示位置(Canvasの中心)
                img_height / 2,                   
                image=self.photo_image  # 表示画像データ
            )

            self.canvas.place(x=400, y=150 * ht)

            # disp_image()を10msec後に実行する
            self.disp_id = self.after(10, self.disp_image)

def start_time():
    global start_time
    start_time = time.perf_counter()

def finish_time():
    return time.perf_counter() - start_time

def sound():
    #playsound("C:/Users/urbtg/OneDrive/Documents/塚本寺田研究室/研究/実験2/system/page_effect.mp3")
    playsound("./page_effect.mp3")
    #playsound(abs_path + "page_effect.mp3")
    #playsound("C:/Users/ichib/Documents/塚本寺田研究室/研究/system2/page_effect.mp3")

def movie():
    global root
    global path
    global app1
    #app1 = VideoPlayer(root)
    app1.VideoRead()

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", type=str, default=None)
    parser.add_argument("--port", type=int, default=8080)

    args = parser.parse_args()

    return args


def event_new_client(client, server):
    client_address = ''
    client_address += str(client['address'][0])
    client_address += ':'
    client_address += str(client['address'][1])

    print('Event New Client ' + client_address)

    if qrview_f:
        qr_win.destroy()
        qrview_f = False


def event_client_left(client, server):
    client_address = ''
    client_address += str(client['address'][0])
    client_address += ':'
    client_address += str(client['address'][1])

    print('Event Client Left ' + client_address)

def event_message_received(client, server, message):
    global app_ope, app_effect, csv_save, cnt, count, start_t, blink_count

    json_data = json.loads(message)

    # blinkSpeed(静止指標)：まばたき速度、閉眼時間(mSec)
    # 0-400(通常90−180付近)
    blinkSpeed = json_data.get('blinkSpeed')
    # blinkStrength(静止指標)：まばたき強度(uV-equiv)
    # 0-1000(通常30−150付近)
    blinkStrength = json_data.get('blinkStrength')

    # eyeMoveUp(静止指標) 視線が上に動いた時のイベント
    # 0: 検知無し、1: 極小-7: 特大
    eyeMoveUp = json_data.get('eyeMoveUp')
    # eyeMoveDown(静止指標) 視線が下に動いた時のイベント
    # 0: 検知無し、1: 極小-7: 特大
    eyeMoveDown = json_data.get('eyeMoveDown')
    # eyeMoveLeft(静止指標) 視線が左に動いた時のイベント
    # 0: 検知無し、1: 極小-7: 特大
    eyeMoveLeft = json_data.get('eyeMoveLeft')
    # eyeMoveRight(静止指標) 視線が右に動いた時のイベント
    # 0: 検知無し、1: 極小-7: 特大
    eyeMoveRight = json_data.get('eyeMoveRight')

    # roll：姿勢角のロール成分(左右傾き)を示す度
    # -180.00 ～ 180.00
    roll = json_data.get('roll')
    # pitch：姿勢角のピッチ成分（前後傾き）を示す度
    # -180.00 ～ 180.00
    pitch = json_data.get('pitch')
    # yaw：姿勢角のヨー成分（横回転）を示す度
    # 0.00 ～ 360.00
    yaw = json_data.get('yaw')

    # accX：加速度のX軸成分（左右）1G=16
    # -128(-8G) ～ 127(7.9375G)
    accX = json_data.get('accX')
    # accY：加速度のY軸成分（前後）1G=16
    # -128(-8G) ～ 127(7.9375G)
    accY = json_data.get('accY')
    # accZ：加速度のZ軸成分（上下）1G=16
    # -128(-8G) ～ 127(7.9375G)
    accZ = json_data.get('accZ')

    # walking(isWalking)(歩行指標)：かかとが地面についた時の一歩の検知(検知後0.15~0.25s後にフラグ)
    # 0/false: 検知無し、1/true: 検知有り
    walking = json_data.get('walking')

    # noiseStatus：眼電位電極のノイズ状況を表す整数値
    # 0/false: ノイズ無し、1/true: ノイズ有り
    noiseStatus = json_data.get('noiseStatus')

    # fitError：JINS MEMEが実際に装着されているかどうか、揺れで5秒に1回判定
    # 0: 装着中、1: 非装着
    fitError = json_data.get('fitError')

    # powerLeft：電池残量を表す整数値
    # 0: 充電中、1: 空 ～ 5: 満充電
    powerLeft = json_data.get('powerLeft')

    # sequenceNumber(seqNo)：0-255までの循環連番整数
    sequenceNumber = json_data.get('sequenceNumber')

    print('sequenceNumber:' + str(sequenceNumber))

    #print('blinkSpeed:' + str(blinkSpeed))
    #print('blinkStrength:' + str(blinkStrength))

    #バッテリー残量の表示
    battery = 0

    if powerLeft == 0:
        battery = 0
    elif powerLeft == 1:
        battery = 20
    elif powerLeft == 2:
        battery = 40
    elif powerLeft == 3:
        battery = 60
    elif powerLeft == 4:
        battery = 80
    elif powerLeft == 5:
        battery = 100

    # バッテリー残量を更新
    label_bty['text'] = str(battery)

    page_next = False
    page_next_b = False # csv記録用変数

    #瞬き操作検出（2回連続瞬きでページ送り）
    if blinkSpeed > 0:
        blink_count = blink_count + 1

        if blink_count == 1:
            start_t = time.perf_counter()
            # ボタンの色を変更
            app.button4['bg'] = '#DEF6DE'

        elif blink_count == 2:
            blink_count = 0
            end_t = time.perf_counter()
            time_dif = end_t - start_t
            if time_dif < 2:
                page_next = True
                page_next_b = True
            # ボタンの色を戻す
            app.button4['bg'] = '#F2F2F2'


    
    # 自然な瞬きかどうかをチェック（瞬き後1秒経過するとblink_countを0に戻す）
    t = time.perf_counter()
    t_dif = t - start_t
    if t_dif > 2:
        blink_count = 0
        # ボタンの色を戻す
        app.button4['bg'] = '#F2F2F2'

    if app_ope == True:
        if page_next == True:
            print('Enter')

            if app_effect == True:
                #エフェクト表示
                thread2 = threading.Thread(target=movie)
                thread2.setDaemon(True)
                thread2.start()
                thread2.join()
                print(count)
                #sound()
                MainWindow.book_next(True, None)
                #sound()
                #thread3 = threading.Thread(target=sound)
                #thread3.setDaemon(True)
                #thread3.start()
                #thread3.join()

            page_next = False


    #global cnt
    #print(cnt)
    #csv保存
    if csv_save == True:
        t = finish_time()
    
        data = []
        data.insert(1, t)
        data.insert(2, cnt)
        data.insert(3, count + 1)
        data.insert(4, page_next_b)
        data.insert(5, sequenceNumber)
        data.insert(6, blinkSpeed)
        data.insert(7, blinkStrength)
        data.insert(8, eyeMoveUp)
        data.insert(9, eyeMoveDown)
        data.insert(10, eyeMoveLeft)
        data.insert(11, eyeMoveRight)
        data.insert(12, roll)
        data.insert(13, pitch)
        data.insert(14, yaw)
        data.insert(15, accX)
        data.insert(16, accY)
        data.insert(17, accZ)
        data.insert(18, walking)
        data.insert(19, noiseStatus)
        data.insert(20, fitError)
        data.insert(21, powerLeft)
        print('blinkSpeed:' + str(blinkSpeed))

        #print(data)
        with open(filename, 'a', newline="") as f:
            writer = csv.writer(f)
            writer.writerow(data)
        

def main():
    global server, app1, battery, label_bty
    args = get_args()

    host = args.host
    port = args.port

    if host is None:
        host = socket.gethostbyname(socket.gethostname())

    #サーバー情報の表示
    print('Server ' + str(host) + ':' + str(port))
    label = tk.Label(root, text=str(host) + ':' + str(port), font=("MSゴシック", "15", "bold"))
    label.place(x=1600 * wt, y=60 * ht)

    battery = 0

    # バッテリー残量表示用ラベルの作成
    label_bty = tk.Label(root, text=str(battery), font=("MSゴシック", "15", "bold"))
    label_bty.place(x=1800 * wt, y=20 * ht)

    # サーバーインスタンス
    server = WebsocketServer(host=host, port=port)
    server.disconnect_clients_abruptly() # 接続されているクライアントを切断する
    
    # QRコード作成
    code = pyqrcode.create('wss://' + str(host) + ':' + str(port), error='L', version=3, mode='binary')
    code.png(FILE_PNG, scale=5, module_color=[0, 0, 0, 128], background=[255, 255, 255])

    #app.qrcodeview()

    start_time()

    # アニメーション表示用canvasの作成
    app1 = VideoPlayer(root)

    if(ser_flag):
        # イベントコールバック設定
        server.set_fn_new_client(event_new_client)
        server.set_fn_client_left(event_client_left)
        server.set_fn_message_received(event_message_received)

        # サーバー起動
        server.run_forever()

class MainWindow(tk.Frame):
    def __init__(self, master):        
        super().__init__(master)
        #self.pack()
        #scr_w, scr_h = pyautogui.size()
        master.title("読書アプリ")
        #master.geometry("300x200")
        #master.geometry('300x400+0+0')
        #master.state('zoomed')

        #Label
        self.label = tk.Label(
            master, text='JINS MEME',
            font=("MSゴシック", "14")
        )
        self.label.place(x=560 * wt, y=6 * ht)

        #Button
        self.button0 = tk.Button(
            master, text='接続', font=("MSゴシック", "18", "bold"), width=7, height=1, bg='#ffffff', 
            command=lambda: self.btn_click_connect(True)
        )

        self.button1 = tk.Button(
            master, text='停止', font=("MSゴシック", "18", "bold"), width=7, height=1, bg='#ffffff', 
            command=lambda: self.btn_click_end(True)
        )

        
        self.button2 = tk.Button(
            master, text='メニュー', font=("MSゴシック", "18", "bold"), width=7, height=1, bg='#ffffff', 
            command=lambda: self.btn_click_menu(True)
        )

        self.button3 = tk.Button(
            master, text='ライブラリ', font=("MSゴシック", "18", "bold"), width=9, height=1, bg='#ffffff', 
            command=lambda: self.btn_click_liblary(True)
        )

        #layout
        self.button0.place(x=460 * wt, y=40 * ht)
        self.button1.place(x=650 * wt, y=40 * ht)
        self.button2.place(x=12 * wt, y=20 * ht)
        self.button3.place(x=210 * wt, y=20 * ht)

        #Label
        self.page_label0 = tk.Label(
            master, text='ページ番号',
            font=("MSゴシック", "14")
        )
        self.page_label1 = tk.Label(
            master, text='/',
            font=("MSゴシック", "30")
        )
        self.page_label0.place(x=970 * wt, y=6 * ht)
        self.page_label1.place(x=1030 * wt, y=45 * ht)

        #Label
        self.label0 = tk.Label(
            master, text='バッテリー残量',
            font=("MSゴシック", "15", "bold")
        )

        self.label1 = tk.Label(
            master, text='サーバー番号',
            font=("MSゴシック", "15", "bold")
        )

        self.label2 = tk.Label(
            master, text='%',
            font=("MSゴシック", "15", "bold")
        )

        self.label0.place(x=1290 * wt, y=20 * ht)
        self.label1.place(x=1320 * wt, y=60 * ht)
        self.label2.place(x=1870 * wt, y=20 * ht)

        self.button4 = tk.Button(
            master, text='次へ', font=("MSゴシック", "20", "bold"), width=14, height=17, bg='#F2F2F2',
            borderwidth=0,
            command=lambda: self.book_next(True)
        )
        self.button4.place(x=30, y=150 * ht)

        self.button5 = tk.Button(
            master, text='戻る', font=("MSゴシック", "20", "bold"), width=14, height=17, bg='#F2F2F2', 
            borderwidth=0, 
            command=lambda: self.book_before(True)
        )
        self.button5.place(x=1550 * wt, y=150 * ht)

        # QRコード表示用ボタン
        self.button6 = tk.Button(
            master, text='QRコード', font=("MSゴシック", "20", "bold"), width=9, height=1, bg='#ffffff', 
            command=lambda: self.qrcodeview()
        )
        self.button6.place(x=scr_w - 300, y=150 * ht)

        # ウィンドウのXボタンが押されたときに呼ばれるメソッドを設定
        self.master.protocol("WM_DELETE_WINDOW", self.delete_window)

    def qrcodeview(self):
        global qr_win, qrview_f

        qrview_f = True

        qr_win = tk.Toplevel()
        qr_win.geometry("500x500")
        qr_win.title("QRCodeViewer")
        
        # ファイルを参照
        qr_img = Image.open('qrcode.png')
        qr_img = qr_img.resize((500, 500))
        qr_background = ImageTk.PhotoImage(qr_img)
        # Labelの作成
        qr_bg = tk.Label(qr_win, image=qr_background, width=500, height=500)
        qr_bg.place(x=0, y=0)

        #qr_win.mainloop()
        app.wait_window(qr_win)

    def delete_window(self):
        print("ウィンドウのXボタンが押されました")

        # 終了確認のメッセージ表示
        ret = messagebox.askyesno(
            title="終了確認",
            message="アプリを終了しますか？"
        )

        if ret == True:
            # 「はい」がクリックされたとき
            if server != 0:
                server.shutdown()
            self.master.destroy()

    # 接続ボタンを押すとJINS MEMEと接続（csvファイルは作成するが保存はしない），バッテリー表示（接続確認）
    def btn_click_connect(self, bln):
        print("Connect_Start")
        global app_ope, app_effect, filename0, filename, f, csv_save, writer, next_flag, ser_flag, app_on, video_f, btn_start, f_flag, abs_path
        app_ope = True
        app_effect = True
        csv_save = True
        next_flag = True
        ser_flag = True
        btn_start = True
        video_f = False

        if btn_start:
            app_on = True

        dt = datetime.datetime.now()
        #filename = 'C:/Users/urbtg/OneDrive/Documents/塚本寺田研究室/研究/実験2/system/csv/' + dt.strftime('%Y%m%d_%H%M%S') + '.csv'
        filename0 = dt.strftime('%Y%m%d_%H%M%S') + '.csv'
        filename = './csv/' + filename0
        #filename = abs_path + 'csv/' + filename0
        #filename = 'C:/Users/ichib/Documents/塚本寺田研究室/研究/system2/csv/' + dt.strftime('%Y%m%d_%H%M%S') + '.csv'
        #f = open(filename, 'w')
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['t', 'book_no', 'page_right', 'page_eff', 'sequenceNumber', 'blinkSpeed', 'blinkStrength', 'eyeMoveUp', 'eyeMoveDown', 'eyeMoveLeft', 'eyeMoveRight', 'roll', 'pitch', 'yaw', 'accX', 'accY', 'accZ', 'walking', 'noiseStatus', 'fitError', 'powerLeft'])
            f_flag = True

        # 別スレッドでwebsocket通信を実行
        thread2 = threading.Thread(target=main)
        thread2.start()       

    def btn_click_end(self, bln):
        global ser_flag, f, f_flag, rd
        print("End")
        if f_flag: # JINS MEMEと接続した場合のみ実行
            f.close()
            f_flag = False
            f = None

            #server.server_close()
            # Websocket_serverの終了処理（これがないとずっと動いてしまう）
            #server.shutdown()
            server.shutdown_abruptly()
            print("server_shutdown")

        ser_flag = False
        #self.master.destroy()
        root.destroy()
        #master.destroy()
        sys.exit()

    # メニュー画面を生成
    def btn_click_menu(self, bln):
        global menu_win, bg_menu_url, mode_v, device_v, cb_bln, entry0, rd
        menu_win = tk.Toplevel()
        menu_win.geometry("800x700")
        menu_win.title("メニュー")
        # ファイルを参照
        #background = tk.PhotoImage(file=bg_menu_url)
        # Labelの作成
        #bg = tk.Label(menu_win, image=background, width=700, height=500)
        bg = tk.Label(menu_win, width=800, height=700)
        #bg.pack(fill="x")
        bg.place(x=0, y=0)

        page_lab = tk.Label(menu_win, text = "ページ変更", font=("MSゴシック", "15"))
        page_lab.place(x=20, y=20)

        button_menu0 = tk.Button(menu_win, text = "OK", font=("MSゴシック", "15", "bold"), 
            width=7, height=2, bg='#ffffff', command=lambda: self.menu_end(True))
        button_menu1 = tk.Button(menu_win, text = "先頭ページへ", font=("MSゴシック", "15", "bold"), 
            width=11, height=2, bg='#ffffff', command=lambda: self.book_first(True))
        button_menu2 = tk.Button(menu_win, text = "最終ページへ", font=("MSゴシック", "15", "bold"), 
            width=11, height=2, bg='#ffffff', command=lambda: self.book_last(True))
        button_menu3 = tk.Button(menu_win, text = "OK", font=("MSゴシック", "9", "bold"), 
            width=3, height=1, bg='#ffffff', command=lambda: self.page_select(True))
        button_menu0.place(x=330, y=580)
        button_menu1.place(x=50, y=80)
        button_menu2.place(x=280, y=80)
        button_menu3.place(x=680, y=140)

        page_lab1 = tk.Label(menu_win, text = "指定ページへ移動", font=("MSゴシック", "12", "bold"))
        page_lab1.place(x=550, y=80)

        vcmd = self.register(self.onValidate)
        entry0 = tk.Entry(menu_win, width=10, validate="key", validatecommand=(vcmd, '%S'), invalidcommand=self.invalidText)
        entry0.place(x=550, y=140)

        lib_lab = tk.Label(menu_win, text = "操作選択", font=("MSゴシック", "15"))
        lib_lab.place(x=20, y=200)

        self.cb_txt = ['アプリ操作', 'ページめくりエフェクト', 'csv保存']
        self.cb_bln = {}

        #チェックボタン
        for i in range(len(self.cb_txt)):
            self.cb_bln[i] = tk.BooleanVar()
            cb = tk.Checkbutton(menu_win, variable=self.cb_bln[i], text=self.cb_txt[i], font=("MSゴシック", "14"))
            cb.place(x=50, y=250 + (i * 30))
            self.cb_bln[i].set(True)

        mode_lab = tk.Label(menu_win, text = "モード選択", font=("MSゴシック", "15"))
        mode_lab.place(x=20, y=380)

        self.rd1_txt = ['瞬き操作', 'クリック操作']

        #モード選択用のウィジェット変数を作成
        #mode_v = tk.IntVar(value=0)

        #ラジオボタン
        for i in range(len(self.rd1_txt)):
            rd = tk.Radiobutton(menu_win, text=self.rd1_txt[i], value=i, variable=mode_v, font=("MSゴシック", "14"))
            rd.place(x=100 + (i * 200), y=430)

        device_lab = tk.Label(menu_win, text = "デバイス選択", font=("MSゴシック", "15"))
        device_lab.place(x=20, y=480)

        self.rd2_txt = ['1', '2', '3', '4', '5']

        #デバイスNo.選択用のウィジェット変数を作成
        #device_v = tk.IntVar(value=1)

        #ラジオボタン
        for i in range(len(self.rd2_txt)):
            rd = tk.Radiobutton(menu_win, text=self.rd2_txt[i], value=i + 1, variable=device_v, font=("MSゴシック", "14"))
            rd.place(x=100 + (i * 100), y=530)
            

        app.wait_window(menu_win)

    def invalidText(self):
        print('入力に失敗しました')
    
    def onValidate(self, S):
        if re.match(re.compile('[0-9]+'), S):
            return True
        else:
            self.bell()
            return False

    # ライブラリ画面を生成
    def btn_click_liblary(self, bln):
        global menu_win, bg_menu_url
        menu_win = tk.Toplevel()
        menu_win.geometry("1000x700")
        menu_win.title("ライブラリ")
        # ファイルを参照
        background = tk.PhotoImage(file=bg_menu_url)
        # Labelの作成
        bg = tk.Label(menu_win, image=background, width=1000, height=700)
        #bg.pack(fill="x")
        bg.place(x=0, y=0)

        button_menu0 = tk.Button(menu_win, text = "戻る", font=("MSゴシック", "15", "bold"), 
            width=7, height=2, bg='#ffffff', command=lambda: self.lib_end(True))
        button_menu0.place(x=10, y=10)

        lib_lab = tk.Label(menu_win, text = "ライブラリ", font=("MSゴシック", "15"))
        lib_lab.place(x=20, y=140)

        cnt = 0

        directry = os.listdir(dir_path)
        print(directry)
        for dir in directry:
            print(dir)
            dict_name[cnt] = dir
            cnt = cnt + 1

        print(dict_name)
        button_book_list = []
        k = 0
        Lib_img = []
        
        for i in range(cnt):
            files = []
            folder_path = dir_path + dict_name[i] + '/'
            print(folder_path)
            if i > 5:
                k = 1
            for j in os.listdir(folder_path):
                files.append(j)
                if len(files) > 1:
                    break
            print(files)

            #画像読み込み
            book_url_first = folder_path + files[0]
            #print(book_url_first)
            #book_img = tk.PhotoImage(file = book_url_first)
            #book_img1 = book_img.subsample(3, 3)
            lib_img = Image.open(book_url_first)
            lib_img = lib_img.resize((156, 200))
            Lib_img.append(ImageTk.PhotoImage(lib_img))

        print(Lib_img)
        # ボタンの作成
        # lambda関数は使わない＝ボタン作成時に一度book_selected関数が実行され，returnで関数xがオブジェクトとして返ってくる
        # その後ボタンが押された場合，同様にbook_selected関数が実行され，関数xが実行される（ネストされた関数の動作）
        #button_book = tk.Button(menu_win, text = "Book No." + str(i + 1), width=15, height=8, command=self.book_selected(i))
        #self.button_book0 = tk.Button(menu_win, image=Lib_img[0], width=120, height=180, command=self.book_selected(0))
        #self.button_book1 = tk.Button(menu_win, image=Lib_img[1], width=120, height=180, command=self.book_selected(1))
        #self.button_book2 = tk.Button(menu_win, image=Lib_img[2], width=120, height=180, command=self.book_selected(2))
        #self.button_book3 = tk.Button(menu_win, image=Lib_img[3], width=120, height=180, command=self.book_selected(3))
        
        #button_book_list.append(tk.Button(menu_win, image=book_img1, command=lambda: self.book_select(True)))
        #self.button_book0.place(x=20, y=200)
        #self.button_book1.place(x=20 + 200, y=200)
        #self.button_book2.place(x=20 + 200 * 2, y=200)
        #self.button_book3.place(x=20 + 200 * 3, y=200 + 200 * 0)

        for j in range(cnt):
            print(j)
            self.button_book = tk.Button(menu_win, image=Lib_img[j], width=120, height=180, command=self.book_selected(j))
            self.button_book.place(x=20 + 200 * j, y=200)

        menu_win.mainloop()        

        #app.wait_window(menu_win)
    
    def menu_end(self, bln):
        global app_ope

        # 表示しているページ番号を記録
        f = open(path_csv, mode='w', newline="")
        writer = csv.writer(f)
        writer.writerow(['book_no', 'page', 'mode', 'device_no', 'play_num'])
        writer.writerow([book_num, count, mode_v.get(), device_v.get(), play_num])
        f.close()
        print(mode_v.get(), device_v.get())

        #モードの変更を反映
        if mode_v.get() == 0:
            app_ope = True
        else:
            app_ope = False

        menu_win.destroy()

    def lib_end(self, bln):
        menu_win.destroy()
    
    # 開いている本の先頭ページに移動
    def book_first(self, bln):
        global count
        count = 0
        self.book_before(True)
        menu_win.destroy()

    # 開いている本の最終ページに移動
    def book_last(self, bln):
        global count, file_num
        count = file_num - 1
        self.book_next(True)
        menu_win.destroy()

    def book_selected(self, num):
        # ボタンが押されたときには関数xが実行される
        # 引数numも正しく動作する
        def x():
            # 本が選択されたときに実行する処理
            global count, path1, dir_path, dict_name, files, file_num
            print(num)
            book_num = num
            path1 = dir_path + dict_name[book_num] + '/'
            # ファイルを参照
            files = []
            file_num = 0
            for i in os.listdir(path1):
                files.append(i)
                file_num = file_num + 1
            count = 0
            self.book_before(True)
            menu_win.destroy()
        # ボタン作成時には関数xをオブジェクトとしてリターンするだけ
        return x

    # 指定したページ数に移動する
    def page_select(self, bln):
        global count, entry0
        cnt = 0
        count = int(entry0.get())
        self.book_before(True)
        menu_win.destroy()

    # 次のページへ移動
    def book_next(self, bln):    
        # ファイルを参照
        global canvas1, canvas2, count, item1, item2, img1, img2, file_num, path_csv, book_num

        if count < file_num - 1: # 最後のページまで表示後は次へを押しても変化しない
            count = count + 1

        # 表示しているページ番号を記録
        f = open(path_csv, mode='w', newline="")
        writer = csv.writer(f)
        writer.writerow(['book_no', 'page', 'mode', 'device_no', 'play_num'])
        writer.writerow([book_num, count, mode_v.get(), device_v.get(), play_num]) # IntVarを参照するときは.get()を用いないとPAY_VARという文字列が返ってくる
        f.close()

        img_url1 = path1 + files[count]
        print(img_url1)
        #img_url2 = path1 + files[count + 1]
        #print(img_url2)

        #画像読み込み
        img1 = Image.open(img_url1)
        img_h, img_w = img1.height, img1.width
        t = img_w / img_h
        hi = 803 * ht
        wi = int(803 * t * ht)
        img1 = img1.resize((wi, hi))
        #img1 = img1.resize((624, 803))
        img1 = ImageTk.PhotoImage(img1)

        #img2 = Image.open(img_url2)
        #img2 = ImageTk.PhotoImage(img2)

        #canvas1.itemconfig(item1,image=img1)
        canvas1.create_image(0, 0, image=img1, anchor=tk.NW)
        #canvas2.itemconfig(item2,image=img2)
        #canvas2.create_image(0, 0, image=img2, anchor=tk.NW)
        #time.sleep(3) #3秒毎に切り替え

        # ページ番号を更新
        label_right['text'] = str(count + 1)
        label_left['text'] = str(file_num)

    # 前のページに戻る
    def book_before(self, bln):
        # ファイルを参照
        global canvas1, canvas2, count, item1, item2, img1, img2, path_csv, book_num, file_num, mode_v, device_v, play_num

        if count >= 1:
            count = count - 1

        # 表示しているページ番号を記録
        f = open(path_csv, mode='w', newline="")
        writer = csv.writer(f)
        writer.writerow(['book_no', 'page', 'mode', 'device_no', 'play_num'])
        writer.writerow([book_num, count, mode_v.get(), device_v.get(), play_num])
        f.close()

        img_url1 = path1 + files[count]
        print(img_url1)
        #img_url2 = path1 + files[count + 1]
        #print(img_url2)

        #画像読み込み
        img1 = Image.open(img_url1)
        img_h, img_w = img1.height, img1.width
        t = img_w / img_h
        hi = 803 * ht
        wi = int(803 * t * ht)
        img1 = img1.resize((wi, hi))
        #img1 = img1.resize((624, 803))
        img1 = ImageTk.PhotoImage(img1)

        #img2 = Image.open(img_url2)
        #img2 = ImageTk.PhotoImage(img2)

        #canvas1.itemconfig(item1,image=img1)
        canvas1.create_image(0, 0, image=img1, anchor=tk.NW)
        #canvas2.itemconfig(item2,image=img2)
        #canvas2.create_image(0, 0, image=img2, anchor=tk.NW)
        #time.sleep(3) #3秒毎に切り替え

        # ページ番号を更新
        label_right['text'] = str(count + 1)
        label_left['text'] = str(file_num)

#画像を表示させるための関数定義
def show_image():
    global dir_path, root, count, app, cnt, path_csv, path_txt, label_left, label_right
    global files, path1, file_num, item1, canvas1, img1, book_num, play_num, mode_v, device_v
    global img_width, img_height, wt, ht, scr_w
    #img_url = 'C:/Users/urbtg/OneDrive/Documents/塚本寺田研究室/研究/実験2/system/背景.png'
    img_url = './背景5.png'
    #img_url = abs_path + '背景4.png'
    scr_w, scr_h = pyautogui.size() #スクリーンサイズの取得
    print(scr_w, scr_h)
    # このPCのスクリーンサイズを基準にする
    # PCのスクリーンサイズと基準のスクリーンサイズの比を計算
    wt = int(scr_w / 1920)
    ht = int(scr_h / 1080)
    #img = Image.open('C:/Users/urbtg/OneDrive/Documents/塚本寺田研究室/研究/実験2/system/背景.png')
    img = Image.open(img_url)
    img = img.resize((scr_w, scr_h))
    #img.save('C:/Users/urbtg/OneDrive/Documents/塚本寺田研究室/研究/実験2/system/背景_resize.png')
    #bg_url = 'C:/Users/urbtg/OneDrive/Documents/塚本寺田研究室/研究/実験2/system/背景_resize.png'
    bg_url = './背景_resize.png'
    #bg_url = abs_path + '背景_resize.png'
    img.save(bg_url)
    #dir_path = 'C:/Users/urbtg/OneDrive/Documents/塚本寺田研究室/研究/実験2/system/Book/'
    dir_path = './Book/'
    #dir_path = abs_path + 'Book/'
    path_txt = './log.txt'
    #path_txt = abs_path + 'log.txt'
    path_csv = './record.csv'
    #path_csv = abs_path + 'record.csv'
    print("Start")

    #GUIの設定
    root = tk.Tk()

    root.state('zoomed')
    # ファイルを参照
    background = tk.PhotoImage(file=bg_url)
    # Labelの作成
    bg = tk.Label(root, image=background, width=scr_w, height=scr_h)
    #bg.pack(fill="x")
    bg.place(x=0, y=0)

    cnt = 0

    directry = os.listdir(dir_path)
    print(directry)
    for dir in directry:
        print(dir)
        dict_name[cnt] = dir
        cnt = cnt + 1
    
    book_num = 0

    # ファイルを参照
    files = []
    file_num = 0
    path1 = dir_path + dict_name[book_num] + '/'
    for i in os.listdir(path1):
        files.append(i)
        file_num = file_num + 1
        
    print(files)

    rows = []

    if not os.path.isfile(path_csv):
        f = open(path_csv, mode='w', newline="")
        writer = csv.writer(f)
        writer.writerow(['book_no', 'page', 'mode', 'device_no', 'play_num'])
        writer.writerow([1, 1, 0, 1, 1])
        count = 0
        f.close()
        #mode_v = 0
        #device_v = 1
        play_num = 1
        #モード選択用のウィジェット変数を作成
        mode_v = tk.IntVar(value=0)
        #デバイスNo.選択用のウィジェット変数を作成
        device_v = tk.IntVar(value=1)

    else:
        with open(path_csv, mode='r') as f:
            reader = csv.reader(f)
            #print(reader)
            for row in reader:
                rows.append(row)
            count = int(rows[1][1]) #20220801変更
            print(rows)
            f.close()
            mode_v = tk.IntVar(value=rows[1][2])
            device_v = tk.IntVar(value=rows[1][3])
            play_num = int(rows[1][4])
            play_num = play_num + 1
    
    print(count)
    # count = 0

    img_url1 = path1 + files[count]
    print(img_url1)
    #img_url2 = path1 + files[count + 1]
    #print(img_url2)
 
    #画像読み込み(yourimage.jpgは任意の画像へのパスにすること)
    img1 = Image.open(img_url1)
    img_h, img_w = img1.height, img1.width
    t = img_w / img_h
    hi = 803 * ht
    wi = int(803 * t * ht)
    print(wi, hi)
    img1 = img1.resize((wi, hi))
    img_width, img_height = img1.width, img1.height
    img1 = ImageTk.PhotoImage(img1)
 
    #Canvasの用意
    canvas1 = tk.Canvas(bg = "black", width=img_width, height=img_height)
    canvas1.place(x=400, y=150 * ht)
    item1 = canvas1.create_image(0, 0, image=img1, anchor=tk.NW)

    #画像読み込み(yourimage.jpgは任意の画像へのパスにすること)
    #img2 = Image.open(img_url2)
    #img2 = ImageTk.PhotoImage(img2)
 
    #Canvasの用意
    #canvas2 = tk.Canvas(bg = "black", width=img_width, height=img_height)
    #canvas2.place(x=430, y=200)
    #item2 = canvas2.create_image(0, 0, image=img2, anchor=tk.NW)

    # ページ番号を表示
    label_right = tk.Label(root, text=str(count + 1), font=("MSゴシック", "30"))
    label_right.place(x=900 / wt, y=45 * ht)

    label_left = tk.Label(root, text=str(file_num), font=("MSゴシック", "30"))
    label_left.place(x=1080 * wt, y=45 * ht)

    #count = count + 2
 
    #表示
    app = MainWindow(root)
    app.mainloop()
    #root.mainloop()

#path = 'C:/Users/urbtg/OneDrive/Documents/塚本寺田研究室/研究/実験2/uchida/page_1.mp4'
path = './ページめくりv2_1_Trim.mp4'
#path = './aniamation/ページめくり8_Trim.mp4'
#path = abs_path + '/aniamation/ページめくりv2_1_Trim.mp4'
bg_menu_url = './背景_menu.png'
#bg_menu_url = abs_path + '背景_menu.png'
#スレッドを立ててtkinterの画像表示を開始する
#thread1 = threading.Thread(target=show_image)
#thread1.start()
#（2022/07/19追記）スレッドを立てないで単純に関数show_imageを呼び出せば，停止ボタンを押した際にアプリがきちんと停止する
show_image()
