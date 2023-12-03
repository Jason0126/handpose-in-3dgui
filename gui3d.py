from panda3d.core import *
from direct.showbase.ShowBase import ShowBase
from google.protobuf.json_format import MessageToDict
from direct.gui.DirectGui import *
import sys
import pyautogui
import simplepbr
import cv2
import mediapipe as mp
import math


#使用者上傳檔案查詢視窗設定
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
#

#環境設定載入
from panda3d.core import loadPrcFile
loadPrcFile("config.prc")
#

#
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
w, h = 1280, 1024
#


import cv2
import mediapipe as mp
import math
from google.protobuf.json_format import MessageToDict

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
w, h = 1280, 1024  # 影像尺寸


# 根據兩點的座標，計算角度
class myhand:
    def __init__(self):
        self.results = 0
        self.landmark = 0

    # 處理
    def imgprocess(self, img):
        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        ) as hands:  # mediapipe 啟用偵測手掌
            self.results = hands.process(img)
            self.landmark = self.results.multi_hand_landmarks
            if self.landmark:
                for hand_landmarks in self.landmark:
                    # print(hand_landmarks)
                    finger_points = []  # 記錄手指節點座標的串列
                    for i in hand_landmarks.landmark:
                        # 將 21 個節點換算成座標，記錄到 finger_points
                        x = i.x * w
                        y = i.y * h
                        finger_points.append((x, y))
                    if finger_points:
                        finger_angle = self.hand_angle(
                            finger_points
                        )  # 計算手指角度，回傳長度為 5 的串列
                        # print(finger_angle)                     # 印出角度 ( 有需要就開啟註解 )
                        text = self.hand_pos(finger_angle)  # 取得手勢所回傳的內容
                        return text
            else:
                return " "

    # 根據兩點的座標，計算角度
    def vector_2d_angle(self, v1, v2):
        v1_x = v1[0]
        v1_y = v1[1]
        v2_x = v2[0]
        v2_y = v2[1]
        try:
            angle_ = math.degrees(
                math.acos(
                    (v1_x * v2_x + v1_y * v2_y)
                    / (
                        ((v1_x**2 + v1_y**2) ** 0.5)
                        * ((v2_x**2 + v2_y**2) ** 0.5)
                    )
                )
            )
        except:
            angle_ = 180
        return angle_

    # 根據傳入的 21 個節點座標，得到該手指的角度
    def hand_angle(self, hand_):
        angle_list = []
        # thumb 大拇指角度
        angle_ = self.vector_2d_angle(
            (
                (int(hand_[0][0]) - int(hand_[2][0])),
                (int(hand_[0][1]) - int(hand_[2][1])),
            ),
            (
                (int(hand_[3][0]) - int(hand_[4][0])),
                (int(hand_[3][1]) - int(hand_[4][1])),
            ),
        )
        angle_list.append(angle_)
        # index 食指角度
        angle_ = self.vector_2d_angle(
            (
                (int(hand_[0][0]) - int(hand_[6][0])),
                (int(hand_[0][1]) - int(hand_[6][1])),
            ),
            (
                (int(hand_[7][0]) - int(hand_[8][0])),
                (int(hand_[7][1]) - int(hand_[8][1])),
            ),
        )
        angle_list.append(angle_)
        # middle 中指角度
        angle_ = self.vector_2d_angle(
            (
                (int(hand_[0][0]) - int(hand_[10][0])),
                (int(hand_[0][1]) - int(hand_[10][1])),
            ),
            (
                (int(hand_[11][0]) - int(hand_[12][0])),
                (int(hand_[11][1]) - int(hand_[12][1])),
            ),
        )
        angle_list.append(angle_)
        # ring 無名指角度
        angle_ = self.vector_2d_angle(
            (
                (int(hand_[0][0]) - int(hand_[14][0])),
                (int(hand_[0][1]) - int(hand_[14][1])),
            ),
            (
                (int(hand_[15][0]) - int(hand_[16][0])),
                (int(hand_[15][1]) - int(hand_[16][1])),
            ),
        )
        angle_list.append(angle_)
        # pink 小拇指角度
        angle_ = self.vector_2d_angle(
            (
                (int(hand_[0][0]) - int(hand_[18][0])),
                (int(hand_[0][1]) - int(hand_[18][1])),
            ),
            (
                (int(hand_[19][0]) - int(hand_[20][0])),
                (int(hand_[19][1]) - int(hand_[20][1])),
            ),
        )
        angle_list.append(angle_)
        return angle_list

    # 根據手指角度的串列內容，返回對應的手勢名稱
    def hand_pos(self, finger_angle):
        f1 = finger_angle[0]  # 大拇指角度
        f2 = finger_angle[1]  # 食指角度
        f3 = finger_angle[2]  # 中指角度
        f4 = finger_angle[3]  # 無名指角度
        f5 = finger_angle[4]  # 小拇指角度

        # 小於 50 表示手指伸直，大於等於 50 表示手指捲縮
        if f1 > 50 and f2 <= 50 and f3 <= 50 and f4 > 50 and f5 > 50:
            return "click"
        elif f1 >= 50 and f2 <= 50 and f3 >= 50 and f4 >= 50 and f5 >= 50:
            return "point"
        elif f1 > 50 and f2 > 50 and f3 > 50 and f4 > 50 and f5 > 50:
            return "hold"
        elif f1 <= 50 and f2 >= 50 and f3 < 50 and f4 < 50 and f5 < 50:
            return "rotate"
        elif f1 >= 50 and f2 > 50 and f3 < 50 and f4 < 50 and f5 < 50:
            return "rotate"
        elif f1 <= 50 and f2 < 30 and f3 > 50 and f4 > 50 and f5 > 50:
            return "zoom"
        elif f1 > 50 and f2 <= 50 and f3 <= 50 and f4 <= 50 and f5 > 50:
            return "screenshot"
        elif f1 < 50 and f2 > 50 and f3 > 50 and f4 > 50 and f5 > 50:
            return "menu"
        else:
            return ""

    def get_hand_point_X(self, number):  # 回傳mediapipe關節點位置 數字比照mediapipe圖關節點
        re = 0
        if self.landmark:
            for hand_landmarks in self.landmark:
                # mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS) # 解開註解 畫出手掌
                if number == 0:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * w
                elif number == 1:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC].x * w
                elif number == 2:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].x * w
                elif number == 3:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x * w
                elif number == 4:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * w
                elif number == 5:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.INDEX_FINGER_MCP
                        ].x
                        * w
                    )
                elif number == 6:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.INDEX_FINGER_PIP
                        ].x
                        * w
                    )
                elif number == 7:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.INDEX_FINGER_DIP
                        ].x
                        * w
                    )
                elif number == 8:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.INDEX_FINGER_TIP
                        ].x
                        * w
                    )
                elif number == 9:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.MIDDLE_FINGER_MCP
                        ].x
                        * w
                    )
                elif number == 10:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.MIDDLE_FINGER_PIP
                        ].x
                        * w
                    )
                elif number == 11:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.MIDDLE_FINGER_DIP
                        ].x
                        * w
                    )
                elif number == 12:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.MIDDLE_FINGER_TIP
                        ].x
                        * w
                    )
                elif number == 13:
                    re = (
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].x
                        * w
                    )
                elif number == 14:
                    re = (
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].x
                        * w
                    )
                elif number == 15:
                    re = (
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].x
                        * w
                    )
                elif number == 16:
                    re = (
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].x
                        * w
                    )
                elif number == 17:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.PINK_MCP].x * w
                elif number == 18:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.PINK_PIP].x * w
                elif number == 19:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.PINK_DIP].x * w
                elif number == 20:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.PINK_TIP].x * w
                else:
                    re = 0
        else:
            re = 0
        return re

    def get_hand_point_Y(self, number):
        re = 0
        if self.landmark:
            for hand_landmarks in self.landmark:
                # mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS) # 解開註解 畫出手掌
                if number == 0:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * h
                elif number == 1:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC].y * h
                elif number == 2:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP].y * h
                elif number == 3:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].y * h
                elif number == 4:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * h
                elif number == 5:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.INDEX_FINGER_MCP
                        ].y
                        * h
                    )
                elif number == 6:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.INDEX_FINGER_PIP
                        ].y
                        * h
                    )
                elif number == 7:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.INDEX_FINGER_DIP
                        ].y
                        * h
                    )
                elif number == 8:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.INDEX_FINGER_TIP
                        ].y
                        * h
                    )
                elif number == 9:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.MIDDLE_FINGER_MCP
                        ].y
                        * h
                    )
                elif number == 10:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.MIDDLE_FINGER_PIP
                        ].y
                        * h
                    )
                elif number == 11:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.MIDDLE_FINGER_DIP
                        ].y
                        * h
                    )
                elif number == 12:
                    re = (
                        hand_landmarks.landmark[
                            mp_hands.HandLandmark.MIDDLE_FINGER_TIP
                        ].y
                        * h
                    )
                elif number == 13:
                    re = (
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y
                        * h
                    )
                elif number == 14:
                    re = (
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y
                        * h
                    )
                elif number == 15:
                    re = (
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_DIP].y
                        * h
                    )
                elif number == 16:
                    re = (
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y
                        * h
                    )
                elif number == 17:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.PINK_MCP].y * h
                elif number == 18:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.PINK_PIP].y * h
                elif number == 19:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.PINK_DIP].y * h
                elif number == 20:
                    re = hand_landmarks.landmark[mp_hands.HandLandmark.PINK_TIP].y * h
                else:
                    re = 0
        else:
            re = 0
        return re

    def get_result_land_marks(self):  # 拿land mark
        return self.landmark

    def drawing_hand(self, img):  # 畫出手掌
        if self.landmark:
            for hand_landmarks in self.landmark:
                # print(hand_landmarks)
                mp_drawing.draw_landmarks(
                    img, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )


class MyApp(ShowBase, myhand):
    def __init__(self):
        # 控制初始化
        self.newresults = 0
        self.tx = 0
        self.ty = 0
        self.fx = 0
        self.fy = 0
        self.app = myhand()
        #

        # 畫面初始化
        ShowBase.__init__(self)
        simplepbr.init()
        self.cv2_init()
        self.cam.setPos(0, -50, 0)
        #

        # 畫面設定
        window_x = base.pipe.getDisplayWidth()
        window_y = base.pipe.getDisplayHeight()
        winProps = WindowProperties()
        # winProps.setSize(window_x, window_y)
        winProps.setCursorHidden(False)
        base.win.requestProperties(winProps)
        #

        # 停止滑鼠可以控制鏡頭
        self.disableMouse()
        #

        # 變數宣告
        self.model = None
        self.md = "null"
        self.keyMap = {"up": False, "down": False, "left": False, "right": False}

        self.mode = "move"
        self.control = "model"
        
        self.game_status = "start"
        #

        # 鍵盤事件接收(功能鍵)
        self.accept("1", self.test_click)
        # self.accept("2",self.deletemodel)
        self.accept("2",self.show_menu_GUI)
        self.accept("3", self.showinformation)
        self.accept("4", self.changemode)
        self.accept("5", self.change_model_camera)
        self.accept("6", self.screen_shot)
        self.accept("q", sys.exit)
        #

        # 鍵盤事件接收(方向鍵)
        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        self.accept("a", self.updateKeyMap, ["left", True])
        self.accept("a-up", self.updateKeyMap, ["left", False])
        self.accept("d", self.updateKeyMap, ["right", True])
        self.accept("d-up", self.updateKeyMap, ["right", False])
        #

        # 自動化函式及GUI初始化函式
        self.updateTask = taskMgr.add(self.update, "update")
        self.create_menu_GUI() 
        self.create_start_GUI() 
        self.create_intro_GUI()
        #
        
        #顯示開始畫面 new
        self.show_start_GUI()
        #

    #
    def show_cursor(self):
        props = WindowProperties()
        props.setCursorHidden(False)
        base.win.requestProperties(props)

    #
    def hide_cursor(self):
        props = WindowProperties()
        props.setCursorHidden(True)
        base.win.requestProperties(props)

    # 模擬滑鼠點擊
    def test_click(self):
        # pyautogui.moveTo(620, 320, duration = 1.5)
        pyautogui.click(clicks=1, interval=0.1, button="left")
        print("auto click")

    # 刪除模型(在切換模型會用到)
    def deletemodel(self):
        print("2")
        if self.model != None:
            self.model.detachNode()
            self.model.removeNode()
            self.model = None
            self.md = "null"

    #控制GUI的顯示  new
    def show_menu_GUI(self):
         if self.Menu_Frame.isHidden():
             self.game_status = "menu"
             self.Menu_Frame.show()
             self.show_cursor()
         else:
             self.game_status = "show"
             self.Menu_Frame.hide()   
             self.hide_cursor()
             
    def show_start_GUI(self):
         if self.Start_Frame.isHidden():
             self.game_status = "start"
             self.Start_Frame.show()
             self.show_cursor()
         else:
             self.game_status = "show"
             self.Start_Frame.hide()   
             self.hide_cursor()
             
    def show_intro_GUI(self):
         if self.Intro_Frame.isHidden():
             self.game_status = "intro"
             self.Start_Frame.hide()  
             self.Intro_Frame.show()
             self.show_cursor()
         else:
             self.Start_Frame.show()  
             self.Intro_Frame.hide()   
             self.hide_cursor()

    #初始化menu GUI   new
    def create_menu_GUI(self):
        self.Menu_Frame = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7),
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT,
                                      frameTexture = "assent/menu.png")
        
        Menu_bt1 = DirectButton(image="assent/dice.png",
                           scale=.1, 
                           command=lambda:self.spawnmodel("dice"),
                           parent = self.Menu_Frame,
                           pos=(-0.5,0,0.15))
        
        Menu_bt2 = DirectButton(image="assent/cottage.png",
                           scale=.1, 
                           command=lambda:self.spawnmodel("cottage"),
                           parent = self.Menu_Frame,
                           pos=(0,0,0.15))
        
        Menu_bt3 = DirectButton(image="assent/bike.png",
                           scale=.1, 
                           command=lambda:self.spawnmodel("bike"),
                           parent = self.Menu_Frame,
                           pos=(0.5,0,0.15))
        
        Menu_bt4 = DirectButton(image="assent/laptop1.jpg",
                           scale=.1, 
                           command=lambda:self.spawnmodel("laptop1"),
                           parent = self.Menu_Frame,
                           pos=(-0.5,0,-0.35))
        
        Menu_bt5 = DirectButton(image="assent/sofa.jpg",
                           scale=.1, 
                           command=lambda:self.spawnmodel("sofa"),
                           parent = self.Menu_Frame,
                           pos=(0,0,-0.35))
        
        Menu_bt6 = DirectButton(image="assent/upload.png",
                           scale=.1, 
                           command=lambda:self.spawnmodel("user_upload"),
                           parent = self.Menu_Frame,
                           pos=(0.5,0,-0.35))
        
        Menu_label = DirectLabel(text = "Model",
                            parent = self.Menu_Frame,
                            scale = 0.3,
                            pos = (0, 0, 0.45),
                            relief = None)
        
        self.Menu_Frame.hide()
        
    #初始化start GUI
    def create_start_GUI(self):
        self.Start_Frame = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7),
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT,
                                      frameTexture = "assent/menu.png")
        
        Start_bt1 = DirectButton(text = "開始",
                           scale=.1,
                           text_scale = 0.75,
                           command=self.show_start_GUI,
                           parent = self.Start_Frame,
                           pos=(0, 0, 0.15),
                           frameSize = (-4, 4, -1, 1))
        
        Start_bt2 = DirectButton(text = "說明",
                           scale=.1, 
                           text_scale = 0.75,
                           command=self.show_intro_GUI,
                           parent = self.Start_Frame,
                           pos=(0, 0, -0.15),
                           frameSize = (-4, 4, -1, 1))
        
        Start_bt3 = DirectButton(text = "離開",
                           scale=.1, 
                           text_scale = 0.75,
                           command=sys.exit,
                           parent = self.Start_Frame,
                           pos=(0, 0, -0.45),
                           frameSize = (-4, 4, -1, 1))
        
        Start_label = DirectLabel(text = "3D模型控制",
                            parent = self.Start_Frame,
                            scale = 0.15,
                            pos = (0, 0, 0.45),
                            relief = None)
        
        self.Start_Frame.hide()
    
    #初始化intro GUI    
    def create_intro_GUI(self):

        self.Intro_Frame = DirectDialog(frameSize = (-1, 1, -1, 1),
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT,
                                      frameTexture = "assent/menu.png")
        
        Intro_game_text = OnscreenText(text = "本專案是運用Google所開發的Mediapipe手部辦勢套件，並搭配我們用Panda3D套件所自行設計的3D模型展示視窗，來模擬手部動作透過鏡頭辨識後操控視窗內的3D模型。",
                                       pos = (-0.8 , 0.85), 
                                       scale = 0.08,
                                       parent = self.Intro_Frame,
                                       align = TextNode.ALeft,
                                       wordwrap=(20.0))
        
        Previous_buttom = DirectButton(text = "回首頁",
                                       scale=.1, 
                                       text_scale = 0.75,
                                       command=lambda:self.switch_intro_page(0,-1),
                                       pos=(-0.6, 0, -0.85),
                                       frameSize = (-3, 3, -1, 1),
                                       parent = self.Intro_Frame)
        
        Next_buttom = DirectButton(text = "下一頁",
                                   scale=.1, 
                                   text_scale = 0.75,
                                   command=lambda:self.switch_intro_page(0,1),
                                   pos=(0.6, 0, -0.85),
                                   frameSize = (-3, 3, -1, 1),
                                   parent = self.Intro_Frame)
        
        self.Intro_Frame.hide()
        
        self.Intro_Page1 = DirectDialog(frameSize = (-1, 1, -1, 1),
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT,
                                      frameTexture = "assent/menu.png")
        
        Intro_mouse_move_image = OnscreenImage(image = "assent/hand_pose/mouse_move.png",
                                                   pos = (-0.8 , 0, 0.85),
                                                   scale = 0.12,
                                                   parent = self.Intro_Page1)
        
        Intro_mouse_move_title = OnscreenText(text = "滑鼠移動",
                                                 pos = (-0.6 , 0.85), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page1,
                                                 align = TextNode.ALeft)
        
        Intro_mouse_move_detail = OnscreenText(text = "當食指伸直並且其他四指未伸直時,會觸發[滑鼠移動]模式,會根據伸直的食指末端的座標位置,來操控滑鼠到相對位置。",
                                                 pos = (-0.8 , 0.55), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page1,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Intro_mouse_click_image = OnscreenImage(image = "assent/hand_pose/mouse_click.png",
                                                   pos = (-0.8 , 0, 0),
                                                   scale = 0.12,
                                                   parent = self.Intro_Page1)
        
        Intro_mouse_click_title = OnscreenText(text = "滑鼠點擊",
                                                 pos = (-0.6 , 0), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page1,
                                                 align = TextNode.ALeft)
        
        Intro_mouse_click_detail = OnscreenText(text = "當食指和中指伸直併攏並且其他三指未伸直時,會觸發[滑鼠點擊]模式,會操控滑鼠在當下的位置,模擬左鍵點擊一下的動作。",
                                                 pos = (-0.8 , -0.3), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page1,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Previous_buttom = DirectButton(text = "上一頁",
                                       scale=.1, 
                                       text_scale = 0.75,
                                       command=lambda:self.switch_intro_page(1,0),
                                       pos=(-0.6, 0, -0.85),
                                       frameSize = (-3, 3, -1, 1),
                                       parent = self.Intro_Page1)
        
        Next_buttom = DirectButton(text = "下一頁",
                                   scale=.1, 
                                   text_scale = 0.75,
                                   command=lambda:self.switch_intro_page(1,2),
                                   pos=(0.6, 0, -0.85),
                                   frameSize = (-3, 3, -1, 1),
                                   parent = self.Intro_Page1)
        
        self.Intro_Page1.hide()
        
        self.Intro_Page2 = DirectDialog(frameSize = (-1, 1, -1, 1),
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT,
                                      frameTexture = "assent/menu.png")
        
        Intro_open_menu_image = OnscreenImage(image = "assent/hand_pose/open_menu.png",
                                                   pos = (-0.8 , 0, 0.85),
                                                   scale = 0.12,
                                                   parent = self.Intro_Page2)
        
        Intro_open_menu_title = OnscreenText(text = "模型選單開啟",
                                                 pos = (-0.6 , 0.85), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page2,
                                                 align = TextNode.ALeft)
        
        Intro_open_menu_detail = OnscreenText(text = "當大拇指伸直並且其他四指未伸直時,會觸發[選單開啟]的動作,此動作會呼叫出模型選單的頁面,讓使用者可以選擇要顯示的模型。",
                                                 pos = (-0.8 , 0.55), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page2,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Intro_model_move_image = OnscreenImage(image = "assent/hand_pose/model_move.png",
                                                   pos = (-0.8 , 0, 0),
                                                   scale = 0.12,
                                                   parent = self.Intro_Page2)
        
        Intro_model_move_title = OnscreenText(text = "模型選單關閉 / 操控模型移動",
                                                 pos = (-0.6 , 0), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page2,
                                                 align = TextNode.ALeft)
        
        Intro_model_move_detail1 = OnscreenText(text = "當五指都未伸直時:\n (1)在選單頁面下,會觸發[選單關閉]的動作,此動作會關閉呼叫出來的模型選單。 \n (2)在模型操控頁面,會觸發[模型移動]模式,會手的位置,操控模型到相對位置。",
                                                 pos = (-0.8 , -0.3), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page2,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Previous_buttom = DirectButton(text = "上一頁",
                                       scale=.1, 
                                       text_scale = 0.75,
                                       command=lambda:self.switch_intro_page(2,1),
                                       pos=(-0.6, 0, -0.85),
                                       frameSize = (-3, 3, -1, 1),
                                       parent = self.Intro_Page2)
        
        Next_buttom = DirectButton(text = "下一頁",
                                   scale=.1, 
                                   text_scale = 0.75,
                                   command=lambda:self.switch_intro_page(2,3),
                                   pos=(0.6, 0, -0.85),
                                   frameSize = (-3, 3, -1, 1),
                                   parent = self.Intro_Page2)
        
        self.Intro_Page2.hide()
        
        self.Intro_Page3 = DirectDialog(frameSize = (-1, 1, -1, 1),
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT,
                                      frameTexture = "assent/menu.png")
        
        Intro_zoom_in_image = OnscreenImage(image = "assent/hand_pose/zoom_in.png",
                                                   pos = (-0.8 , 0, 0.85),
                                                   scale = 0.12,
                                                   parent = self.Intro_Page3)
        
        Intro_zoom_in_title = OnscreenText(text = "模型放大",
                                                 pos = (-0.6 , 0.85), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page3,
                                                 align = TextNode.ALeft)
        
        Intro_zoom_in_detail = OnscreenText(text = "當大拇指和食指伸直並且其他三指未伸直時,做出大拇指和食指[遠離]的動作,會觸發[模型放大]模式,把當前操控模型的縮放比例調大。",
                                                 pos = (-0.8 , 0.55), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page3,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Intro_zoom_out_image = OnscreenImage(image = "assent/hand_pose/zoom_out.png",
                                                   pos = (-0.8 , 0, 0),
                                                   scale = 0.12,
                                                   parent = self.Intro_Page3)
        
        Intro_zoom_out_title = OnscreenText(text = "模型縮小",
                                                 pos = (-0.6 , 0), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page3,
                                                 align = TextNode.ALeft)
        
        Intro_zoom_out_detail1 = OnscreenText(text = "當大拇指和食指伸直並且其他三指未伸直時,做出大拇指和食指[靠近]的動作,會觸發[模型縮小]模式,把當前操控模型的縮放比例調小。",
                                                 pos = (-0.8 , -0.3), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page3,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Previous_buttom = DirectButton(text = "上一頁",
                                       scale=.1, 
                                       text_scale = 0.75,
                                       command=lambda:self.switch_intro_page(3,2),
                                       pos=(-0.6, 0, -0.85),
                                       frameSize = (-3, 3, -1, 1),
                                       parent = self.Intro_Page3)
        
        Next_buttom = DirectButton(text = "下一頁",
                                   scale=.1, 
                                   text_scale = 0.75,
                                   command=lambda:self.switch_intro_page(3,4),
                                   pos=(0.6, 0, -0.85),
                                   frameSize = (-3, 3, -1, 1),
                                   parent = self.Intro_Page3)
        
        self.Intro_Page3.hide()
        
        self.Intro_Page4 = DirectDialog(frameSize = (-1, 1, -1, 1),
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT,
                                      frameTexture = "assent/menu.png")
        
        Intro_rotate_image = OnscreenImage(image = "assent/hand_pose/rotate.png",
                                                   pos = (-0.8 , 0, 0.85),
                                                   scale = 0.12,
                                                   parent = self.Intro_Page4)
        
        Intro_rotate_title = OnscreenText(text = "模型旋轉",
                                                 pos = (-0.6 , 0.85), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page4,
                                                 align = TextNode.ALeft)
        
        Intro_rotate_detail = OnscreenText(text = "當大拇指和食指碰觸並且其他三指伸直時,會觸發[模型旋轉]模式,把當前操控模型......",
                                                 pos = (-0.8 , 0.55), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page4,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Intro_screenshot_image = OnscreenImage(image = "assent/hand_pose/screenshot.png",
                                                   pos = (-0.8 , 0, 0),
                                                   scale = 0.12,
                                                   parent = self.Intro_Page4)
        
        Intro_screenshot_title = OnscreenText(text = "畫面擷取",
                                                 pos = (-0.6 , 0), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page4,
                                                 align = TextNode.ALeft)
        
        Intro_screenshot_detail1 = OnscreenText(text = "當大拇指、食指和無名指伸直並且其餘未伸直時,會觸發[畫面擷取]的動作,會把當前視窗內的畫面做擷取的動作,並且儲存在sceenshot文件夾裡。",
                                                 pos = (-0.8 , -0.3), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page4,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Previous_buttom = DirectButton(text = "上一頁",
                                       scale=.1, 
                                       text_scale = 0.75,
                                       command=lambda:self.switch_intro_page(4,3),
                                       pos=(-0.6, 0, -0.85),
                                       frameSize = (-3, 3, -1, 1),
                                       parent = self.Intro_Page4)
        
        Next_buttom = DirectButton(text = "下一頁",
                                   scale=.1, 
                                   text_scale = 0.75,
                                   command=lambda:self.switch_intro_page(4,5),
                                   pos=(0.6, 0, -0.85),
                                   frameSize = (-3, 3, -1, 1),
                                   parent = self.Intro_Page4)
        
        self.Intro_Page4.hide()
        
        self.Intro_Page5 = DirectDialog(frameSize = (-1, 1, -1, 1),
                                      fadeScreen = 0.4,
                                      relief = DGG.FLAT,
                                      frameTexture = "assent/menu.png")
        
        Intro_menu_image = OnscreenImage(image = "assent/menu.jpg",
                                                   pos = (-0.4 , 0, 0.4),
                                                   scale = 0.5,
                                                   parent = self.Intro_Page5)
        
        Intro_menu_title = OnscreenText(text = "模型選單",
                                                 pos = (0.3 , 0.25), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page5,
                                                 align = TextNode.ALeft)
        
        Intro_menu_detail = OnscreenText(text = "前五個按鈕是我們預設好的模型選項,分別是骰子、別墅、腳踏車、筆電和沙發,而最後一個是讓使用者可以自行上傳自己想要的模型,但是需要特別注意模型的檔案,需要放在models的文件夾裡並且格式是.gltf格式。",
                                                 pos = (-0.8 , -0.3), 
                                                 scale = 0.08,
                                                 parent = self.Intro_Page5,
                                                 align = TextNode.ALeft,
                                                 wordwrap=(20.0))
        
        Previous_buttom = DirectButton(text = "上一頁",
                                       scale=.1, 
                                       text_scale = 0.75,
                                       command=lambda:self.switch_intro_page(5,4),
                                       pos=(-0.6, 0, -0.85),
                                       frameSize = (-3, 3, -1, 1),
                                       parent = self.Intro_Page5)
        
        Next_buttom = DirectButton(text = "下一頁",
                                   scale=.1, 
                                   text_scale = 0.75,
                                   command=lambda:self.switch_intro_page(5,0),
                                   pos=(0.6, 0, -0.85),
                                   frameSize = (-3, 3, -1, 1),
                                   parent = self.Intro_Page5)
        
        self.Intro_Page5.hide()

    #切換Intro頁面的切換
    def switch_intro_page(self,now_page_index,open_page_index):
        if now_page_index == 0:
            self.Intro_Frame.hide()
        elif now_page_index == 1:
            self.Intro_Page1.hide()
        elif now_page_index == 2:
            self.Intro_Page2.hide()
        elif now_page_index == 3:
            self.Intro_Page3.hide()
        elif now_page_index == 4:
            self.Intro_Page4.hide()
        elif now_page_index == 5:
            self.Intro_Page5.hide()
        
        if open_page_index == -1:
            self.game_status = "start"
            self.Start_Frame.show()
        elif open_page_index == 0:
            self.Intro_Frame.show()
        elif open_page_index == 1:
            self.Intro_Page1.show()
        elif open_page_index == 2:
            self.Intro_Page2.show()
        elif open_page_index == 3:
            self.Intro_Page3.show()
        elif open_page_index == 4:
            self.Intro_Page4.show()
        elif open_page_index == 5:
            self.Intro_Page5.show()
        
    # debug用
    def showinformation(self):
        print("camera pos   = " + str(self.camera.getPos()))
        print("camera scale = " + str(self.camera.getScale()))
        print("camera hpr   = " + str(self.camera.getHpr()))
        # print(self.camera.getPos())
        if self.model != None:
            print(self.model.getPos())
            print(self.model.getScale())
            print(self.model.getHpr())

    # 切換 "移動" "旋轉" "縮放" 控制
    def changemode(self):
        if self.mode == "move":
            self.mode = "rotate"
        elif self.mode == "rotate":
            self.mode = "scale"
        elif self.mode == "scale":
            self.mode = "move"
        print(self.mode)

    # 切換控制對象 "模型" "鏡頭"
    def change_model_camera(self):
        if self.control == "model":
            self.control = "camera"
        elif self.control == "camera":
            self.control = "model"
        print(self.control)

    # 螢幕截圖(會根據不同模型名稱改變檔案名稱)
    def screen_shot(self):
        base.screenshot("screenshot/" + self.md + ".png", False)

    # 根據鍵盤按鍵 更新keyMap
    def updateKeyMap(self, controlName, controlState):
        self.keyMap[controlName] = controlState

    # 根據77行  它會自動執行並根據keyMap和self.mode的狀態做相對應的動作
    def update(self, task):
        self.cam_update()
        # print(self.newresults)
        # print(self.tx)
        # print(self.ty)
        # print(self.fx)
        # print(self.fy)
        # print((((self.tx - self.fx) ** 2) + ((self.ty - self.fy) ** 2)) ** 0.5)
        # print(self.newresults)
        # print(self.Menu_Frame.isHidden())
        if self.game_status == "start" or self.game_status == "intro" or self.game_status == "menu":
            self.show_cursor()
            if self.newresults == "rotate":
                self.Menu_Frame.hide()
            if self.newresults == "point":
                pyautogui.moveTo(self.fx, self.fy, duration=0.01)
            if self.newresults == "click":
                pyautogui.press("1")
        else:
            self.hide_cursor()
            if self.newresults == "point":
                pyautogui.moveTo(self.fx, self.fy, duration=0.01)
            if self.newresults == "menu":
                self.Menu_Frame.show()
            if self.newresults == "click":
                pyautogui.press("1")
            if self.newresults == "screenshot":
                pyautogui.press("6")
            if self.newresults == "hold":
                self.mode = "move"
                if self.fx == 0:
                    if self.fy < 512:
                        pyautogui.press("w")
                    elif self.fy > 512:
                        pyautogui.press("s")
                elif self.fx > 640:
                    if self.fy == 512:
                        pyautogui.press("d")
                    elif self.fy < 512:
                        pyautogui.press(["d", "w"])
                    else:
                        pyautogui.press(["d", "s"])
                else:
                    if self.fy == 512:
                        pyautogui.press("a")
                    elif self.fy < 512:
                        pyautogui.press(["a", "w"])
                    else:
                        pyautogui.press(["a", "s"])
            if self.newresults == "rotate":
                self.mode = "rotate"
                if self.fx == 0:
                    if self.fy < 512:
                        pyautogui.press("w")
                    elif self.fy > 512:
                        pyautogui.press("s")
                elif self.fx > 640:
                    if self.fy == 512:
                        pyautogui.press("d")
                    elif self.fy < 512:
                        pyautogui.press(["d", "w"])
                    else:
                        pyautogui.press(["d", "s"])
                else:
                    if self.fy == 512:
                        pyautogui.press("a")
                    elif self.fy < 512:
                        pyautogui.press(["a", "w"])
                    else:
                        pyautogui.press(["a", "s"])
            if self.newresults == "zoom":
                self.mode = "scale"
                if (
                    ((self.tx - self.fx) ** 2) + ((self.ty - self.fy) ** 2)
                ) ** 0.5 > 250:
                    pyautogui.press("w")
                elif (
                    ((self.tx - self.fx) ** 2) + ((self.ty - self.fy) ** 2)
                ) ** 0.5 < 250:
                    pyautogui.press("s")
        self.tx = 0
        self.ty = 0
        self.fx = 0
        self.fy = 0

        dt = globalClock.getDt() * 1  # 移動單位
        if self.control == "model":
            if self.model != None:
                if self.mode == "move":
                    dt = dt * 3
                    if self.keyMap["up"]:
                        self.model.setPos(self.model.getPos() + Vec3(0, 0, dt))
                    if self.keyMap["down"]:
                        self.model.setPos(self.model.getPos() + Vec3(0, 0, -dt))
                    if self.keyMap["left"]:
                        self.model.setPos(self.model.getPos() + Vec3(-dt, 0, 0))
                    if self.keyMap["right"]:
                        self.model.setPos(self.model.getPos() + Vec3(dt, 0, 0))
                elif self.mode == "rotate":
                    dt = dt * 20
                    if self.keyMap["up"]:
                        self.model.setHpr(self.model.getHpr() + Vec3(0, -dt, 0))
                    if self.keyMap["down"]:
                        self.model.setHpr(self.model.getHpr() + Vec3(0, dt, 0))
                    if self.keyMap["left"]:
                        self.model.setHpr(self.model.getHpr() + Vec3(-dt, 0, 0))
                    if self.keyMap["right"]:
                        self.model.setHpr(self.model.getHpr() + Vec3(dt, 0, 0))
                elif self.mode == "scale":
                    if self.keyMap["up"]:
                        self.model.setScale(self.model.getScale() + (dt))
                    if self.keyMap["down"]:
                        self.model.setScale(self.model.getScale() + (-dt))
        elif self.control == "camera":
            if self.mode == "move":
                if self.keyMap["up"]:
                    self.camera.setPos(self.camera.getPos() + Vec3(0, 0, dt))
                if self.keyMap["down"]:
                    self.camera.setPos(self.camera.getPos() + Vec3(0, 0, -dt))
                if self.keyMap["left"]:
                    self.camera.setPos(self.camera.getPos() + Vec3(-dt, 0, 0))
                if self.keyMap["right"]:
                    self.camera.setPos(self.camera.getPos() + Vec3(dt, 0, 0))
            elif self.mode == "rotate":
                if self.keyMap["up"]:
                    self.camera.setHpr(self.camera.getHpr() + Vec3(0, -dt, 0))
                if self.keyMap["down"]:
                    self.camera.setHpr(self.camera.getHpr() + Vec3(0, dt, 0))
                if self.keyMap["left"]:
                    self.camera.setHpr(self.camera.getHpr() + Vec3(-dt, 0, 0))
                if self.keyMap["right"]:
                    self.camera.setHpr(self.camera.getHpr() + Vec3(dt, 0, 0))
            elif self.mode == "scale":
                if self.keyMap["up"]:
                    self.camera.setScale(self.camera.getScale() + (dt))
                if self.keyMap["down"]:
                    self.camera.setScale(self.camera.getScale() + (-dt))
        return task.cont

    #根據模型GUI生成相對應的模型
    def spawnmodel(self , model_name):
        if(self.model != None):
            self.deletemodel()
            self.model = None
        if(model_name == "dice"):
            self.spawnmodel_dice()
        elif(model_name == "cottage"):
            self.spawnmodel_cottage()
        elif(model_name == "bike"):
            self.spawnmodel_bike()
        elif(model_name == "laptop1"):
            self.spawnmodel_laptop1()
        elif(model_name == "laptop2"):
            self.spawnmodel_laptop2()
        elif(model_name == "sofa"):
            self.spawnmodel_sofa()
        elif(model_name == "cake"):
            self.spawnmodel_cake()
        elif(model_name == "user_upload"):
            self.spawnmodel_user_upload()
        self.show_menu_GUI()

    def spawnmodel_dice(self):
        self.model = self.loader.load_model("models/dice.gltf")
        self.model.setPos(0, 0, 0)
        self.model.setScale(1)
        self.model.reparent_to(self.render)

        self.md = "dice"

    def spawnmodel_cottage(self):
        self.model = self.loader.load_model("models/cottage.gltf")
        self.model.setPos(0, 0, 0)
        self.model.setScale(0.35)
        self.model.reparent_to(self.render)

        self.md = "cottage"

    def spawnmodel_bike(self):
        self.model = self.loader.load_model("models/bike.gltf")
        self.model.setPos(0, 0, 0)
        self.model.setHpr(90, 0, 0)
        self.model.setScale(0.01)
        self.model.reparent_to(self.render)

        self.md = "bike"

    def spawnmodel_laptop1(self):
        self.model = self.loader.load_model("models/Laptop.gltf")
        self.model.setPos(0, 0, 0)
        self.model.setScale(1)
        self.model.reparent_to(self.render)

        self.md = "laptop1"

    def spawnmodel_laptop2(self):
        self.model = self.loader.load_model("models/Laptop2.gltf")
        self.model.setPos(0, 0, 0)
        self.model.setScale(1)
        self.model.reparent_to(self.render)

        self.md = "laptop2"

    def spawnmodel_sofa(self):
        self.model = self.loader.load_model("models/sofa.gltf")
        self.model.setPos(0, 0, 0)
        self.model.setScale(1)
        self.model.reparent_to(self.render)

        self.md = "sofa"

    def spawnmodel_cake(self):
        self.model = self.loader.load_model("models/cake.gltf")
        self.model.setPos(0, 0, 0)
        self.model.setScale(1)
        self.model.reparent_to(self.render)

        self.md = "cake"
        
    def spawnmodel_user_upload(self):
        
        file_path = filedialog.askopenfilename()
        print(len(file_path))
        if len(file_path) !=0 : 
        
             file_path = file_path.split('/')
             path = file_path[3] + '/' + file_path[4]
             self.model = self.loader.load_model(path)
             self.model.setPos(0,0,0)
             self.model.setScale(1)
             self.model.reparent_to(self.render)
             
             self.md = "user"   

    def cv2_init(self):
        print("cv2 init")

        # open webcam
        self.cap = cv2.VideoCapture(0)
        self.fontFace = cv2.FONT_HERSHEY_SIMPLEX  # 印出文字的字型
        self.lineType = cv2.LINE_AA  # 印出文字的邊框

        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")

        # use opencv to read from webcam
        success = False
        while not success:
            success, frame = self.cap.read()
        h, w, _ = frame.shape  # accessing the width and height of the frame

        """鏡頭顯示物件 因為跟模型紋理套件有問題 無法使用
        # set up a texture for (h by w) rgb image
        self.tex = Texture()
        self.tex.setup2dTexture(w, h, Texture.T_unsigned_byte,
                           Texture.F_rgb)

        # set up a card to apply the numpy texture
        self.cm = CardMaker('card')
        self.card = base.render.attachNewNode(self.cm.generate())

        WIDTHRATIO = 1
        HEIGHTRATIO = h/w
        CAMDISTANCE = 1.5
        DEPTH = 1
        # card is square, rescale to the original image aspect ratio
        self.card.setScale(WIDTHRATIO, DEPTH, HEIGHTRATIO)
        # bring it to center, put it in front of camera
        self.card.setPos(-WIDTHRATIO/2, CAMDISTANCE, -HEIGHTRATIO/2)
        """
        # base.taskMgr.add(self.updateTex, 'video frame update')

    def cam_update(self):
        # print("cam")
        app = myhand()
        # print("1")
        # while True:
        # print("2")
        ha = 0
        whichHand = []
        ret, img = self.cap.read()
        h, w, _ = img.shape
        img = cv2.flip(img, 1)
        img = cv2.resize(img, (w, h))  # 縮小尺寸，加快處理效率

        if not ret:
            print("Cannot receive frame")
            # break
        img2 = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 轉換成 RGB 色彩

        self.newresults = app.imgprocess(img2)
        app.drawing_hand(img)

        if app.landmark:
            # if self.app.results:
            """
            print(
                "tx : "
                + str(int(app.get_hand_point_X(4)))
                + " tY : "
                + str(int(app.get_hand_point_Y(4)))
            )
            print(
                "fx : "
                + str(int(app.get_hand_point_X(8)))
                + " fY : "
                + str(int(app.get_hand_point_Y(8)))
            )
            """
            self.tx = int(app.get_hand_point_X(4))
            self.ty = int(app.get_hand_point_Y(4))
            self.fx = int(app.get_hand_point_X(8))
            self.fy = int(app.get_hand_point_Y(8))
        """
            if point:
                # print(point)
                text = 'x:' + str(int(point[0])) + 
                    'y:' + str(int(point[-1]))
                cv2.putText(img, text, (30, 500), self.fontFace,
                            2, (255, 255, 255), 3, self.lineType)
            if self.newresults == 'point':
                cv2.circle(img, (int(point[0]), int(
                    point[-1])), 15, (0, 0, 255), -1)

        cv2.putText(img, self.newresults, (30, 120), self.fontFace, 5,
                    (255, 255, 255), 10, self.lineType)  # 印出文字
        """
        # break
        # print(self.newresults)

        """看592行
        flipped_img = cv2.flip(img,0)
        self.tex.setRamImage(flipped_img)
        self.card.setTexture(self.tex)
        """


app = MyApp()
app.run()
