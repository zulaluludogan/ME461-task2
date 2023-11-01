#!/usr/bin/env python3

try:
    import pygame
    import cv2
    import numpy as np
except:
    print("Pygame, opencv and numpy should be installed. Running pip install")
    try:
        from subprocess import run
        run(['pip','install','-r','requirements.txt'])
    except:
        print("pip install failed")
        raise ImportError

try:
    from classes.mpcontroller import *
    from classes.tangui import *
    from classes.tangamegui import *
except:
    print("Missing custom libraries. Did you move this python file?")
    raise ImportError

import time
import random
import socket
import struct

HOSTIP = "192.168.43.235"  # Standard loopback interface address (localhost)
PORT = 5555  # Port to listen on (non-privileged ports are > 1023)
DATAFORMAT = "<fffi"

# import rclpy
# from rclpy.node import Node
# from example_interfaces.msg import Float64MultiArray


GAMEMODE = 0
FULLSCREEN = 0

def make_surface_rgba(array):
    """Returns a surface made from a [w, h, 4] numpy array with per-pixel alpha
    """
    shape = array.shape
    if len(shape) != 3 and shape[2] != 4:
        raise ValueError("Array not RGBA")

    # Create a surface the same width and height as array and with
    # per-pixel alpha.
    surface = pygame.Surface(shape[0:2], pygame.SRCALPHA, 32)

    # Copy the rgb part of array to the new surface.
    pygame.pixelcopy.array_to_surface(surface, array[:,:,0:3])

    # Copy the alpha part of array to the surface using a pixels-alpha
    # view of the surface.
    surface_alpha = np.array(surface.get_view('A'), copy=False)
    surface_alpha[:,:] = array[:,:,3]

    return surface

def render(display, index):
    surface = pygame.display.get_surface()
    if GAMEMODE == 0:
        for obj in menutexts + buttons + selectors:
            obj.draw(surface)
    else:
        for obj in texts + progressbars + [l_bar, r_bar, ball]:
            obj.draw(surface)

    pygame.display.flip()

def eventcheck():
    global GAMEMODE, score, result, game_flag
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            return True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #print(event.button)
            #print(np.array(event.pos)/mouse_pos_scale)
            #Check for left mouse click
            if event.button == 1:
                if GAMEMODE == 0:
                    for button in buttons:
                        if button.checkHover(np.array(event.pos)):
                            #Get which button is pressed
                            result = button.clickFunction()
                            if result == "finger":
                                game_flag = "finger"
                            elif result == "nose":
                                game_flag = "nose"
                            elif result == "host":
                                GAMEMODE = 1
                                score = [0,0]
                                s.bind((HOSTIP,PORT))
                                s.listen()
                                s.setblocking(False)
                            elif result == "client":
                                GAMEMODE = 1
                                score = [0,0]
                                s.connect((HOSTIP,PORT))
                                s.setblocking(False)
                    for selector in selectors:
                        if selector.checkHover(np.array(event.pos)):
                            selector.clickFunction()
                
    return False

def main(args=None):
    global texts, menutexts, buttons, selectors, progressbars, resolution, GAMEMODE, score, l_bar, r_bar, ball, s, result
    texts = []
    menutexts = []
    buttons = []
    selectors = []
    progressbars = []
    score = [0,0]
    result = ""
    # rclpy.init(args=args)
    # node = Node("fruit_game_cam_handler")
    # pub = node.create_publisher(Float64MultiArray, "/fruit_game/finger_pos", 10)

    # msg = Float64MultiArray()
    # msg.data = [0.0, 0.0]
    
    mp_controller = MP_Controller()

    pygame.init()
    pygame.font.init()

    if FULLSCREEN:
        info = pygame.display.Info()
        resolution = (info.current_w, info.current_h)
    else:
        resolution = (640, 360)

    cap = cv2.VideoCapture(0)

    index = None

    try:
        display = pygame.display.set_mode(resolution,
            pygame.HWSURFACE | pygame.DOUBLEBUF | (pygame.FULLSCREEN if FULLSCREEN else 0))

        resolution = np.array(resolution)
        clock = pygame.time.Clock()
        pygame.display.set_caption('Robot Değilim')
        iconsurf = pygame.image.load("assets/appicon.png").convert_alpha()
        pygame.display.set_icon(iconsurf)
        
        font = pygame.font.get_default_font()
        bigfont = pygame.font.SysFont(font, int(resolution[1]*(40/360)))
        midfont = pygame.font.SysFont(font, int(resolution[1]*(26/360)))
        smallfont = pygame.font.SysFont(font, int(resolution[1]*(20/360)))
        bigfont.bold = True
        midfont.bold = True
        smallfont.bold = True

        menutexts.append(Text(resolution[0]*(320/640),resolution[1]*(80/360),"Ping Pong",bigfont))
        menutexts.append(Text(resolution[0]*(320/640),resolution[1]*(240/360),f"Last Score: {score[0]}-{score[1]}",midfont))
        menutexts.append(Text(resolution[0]*(320/640),resolution[1]*(320/360),"By Osama Awad, Tan Çağatay Acar and Zülal Uludoğan",smallfont))
        texts.append(Text(resolution[0]*(320/640),resolution[1]*(320/360),f"Score: {score[0]}-{score[1]}",bigfont))
        texts.append(Text(resolution[0]*(320/640),resolution[1]*(150/360),"Waiting",bigfont))

        buttons.append(Button("host",resolution[0]*(220/640),resolution[1]*(160/360),width=resolution[0]*(60/640),height=resolution[1]*(30/360),text="Host Game"))
        buttons.append(Button("client",resolution[0]*(420/640),resolution[1]*(160/360),width=resolution[0]*(60/640),height=resolution[1]*(30/360),text="Join Game"))

        buttons.append(Button("finger",resolution[0]*(200/640),resolution[1]*(210/360),width=resolution[0]*(60/640),height=resolution[1]*(30/360),text="Finger Game"))
        buttons.append(Button("nose",resolution[0]*(440/640),resolution[1]*(210/360),width=resolution[0]*(60/640),height=resolution[1]*(30/360),text="Nose Game"))
        
        l_bar = Bar(resolution[0]*(10/640), resolution[1]*(180/360),resolution[1]*(20/360),resolution[1]*(90/360),resolution[1])
        r_bar = Bar(resolution[0]*(630/640), resolution[1]*(180/360),resolution[1]*(20/360),resolution[1]*(90/360),resolution[1])
        vel = np.random.random(2)
        vel[1] /= 2
        vel = vel*resolution[0]*(12/640)/np.sqrt(vel.dot(vel))
        ball = Ball(resolution[0]*(320/640), resolution[1]*(180/360), resolution[1]*(10/360), vel, resolution[0], resolution[1])

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client = None

        lasttime = time.time()
        done = False
        while not done:
            done = eventcheck()

            ret, frame = cap.read()
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)
            frame = cv2.flip(frame, 1)
            bgframe = cv2.resize(frame,(np.array(frame.shape[1::-1])*(resolution[0]/640)).astype(int))
            surface = pygame.surfarray.make_surface(bgframe.swapaxes(0, 1)[:,:,::-1])
            display.blit(surface, (0,0))

            if GAMEMODE == 0:
                menutexts[1].setText(f"Last Score: {score[0]}-{score[1]}")
            else:
                if result == "host":
                    mp_controller.detect_async(frame)
                    act = 0
                    if client is None:
                        try:
                            client, _ = s.accept()
                        except BlockingIOError:
                            pass
                        if time.time() - lasttime > 1:
                            lasttime = time.time()
                            texts[1].visibility = True
                            texts[1].setText("Waiting" + "."*int(lasttime%4))
                    else:
                        texts[1].visibility = False
                        try:
                            raw, _, _, _ = client.recvmsg(struct.calcsize(DATAFORMAT))
                        except BlockingIOError:
                            pass
                        else:
                            print(raw)
                            l_bar_y,_,_,_ = struct.unpack(DATAFORMAT,raw)
                            l_bar.sety(l_bar_y*resolution[1])
                            
                        try:
                            if game_flag == "finger" :
                                index = mp_controller.get_index_tip_coordinates()
                            elif game_flag == "nose" :
                                index = mp_controller.get_nose_coordinates()
                        except:
                            pass
                            
                        if index:
                            # msg.data[0] = index[0]
                            # msg.data[1] = index[1]
                            # pub.publish(msg)
                            index = (int(index[0]*resolution[0]),int(index[1]*resolution[1]*4/3))
                            r_bar.sety(index[1])

                        ball.update()
                        if r_bar.checkHover(ball):
                            ball.vel[0] = -abs(ball.vel[0])
                        elif l_bar.checkHover(ball):
                            ball.vel[0] = abs(ball.vel[0])
                        elif ball.checkOutOfBounds():
                            if ball.x < resolution[0]//2:
                                score[1] += 1 # Increase the right score
                                act = 1
                            else:
                                score[0] += 1 # Increase the left score
                                act = 2
                            if score[0] == 9 or score[1] == 9:
                                GAMEMODE = 0
                                # client.close()
                                # s.close()
                                # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                            texts[0].setText(f"Score: {score[0]}-{score[1]}")
                            ball.setPos((resolution[0]*(320/640), resolution[1]*(180/360)))
                            vel = np.random.random(2)
                            vel[1] /= 2
                            vel = vel*resolution[0]*(12/640)/np.sqrt(vel.dot(vel))
                            ball.setVel(vel)
                        if GAMEMODE != 0:
                            client.sendmsg((struct.pack(DATAFORMAT, r_bar.y/resolution[1], ball.x/resolution[0], ball.y/resolution[1], act),))
                else:
                    mp_controller.detect_async(frame)
                    texts[1].visibility = False
                    try:
                        raw, _, _, _ = s.recvmsg(struct.calcsize(DATAFORMAT))
                    except BlockingIOError:
                        pass # No new data. Reuse old data
                    else:
                        r_bar_y, ball_x, ball_y, act = struct.unpack(DATAFORMAT, raw)
                        r_bar.sety(r_bar_y*resolution[1])
                        ball.setPos(np.array((ball_x,ball_y))*resolution)
                        if act != 0:
                            if act == 1:
                                score[1] += 1 # Increase the right score
                            else:
                                score[0] += 1 # Increase the left score
                            if score[0] == 9 or score[1] == 9:
                                GAMEMODE = 0
                            texts[0].setText(f"Score: {score[0]}-{score[1]}")

                    try:
                        if game_flag == "finger" :
                                index = mp_controller.get_index_tip_coordinates()
                        elif game_flag == "nose" :
                                index = mp_controller.get_nose_coordinates()
    
                    except:
                        pass
                        
                    if index:
                        # msg.data[0] = index[0]
                        # msg.data[1] = index[1]
                        # pub.publish(msg)
                        index = (int(index[0]*resolution[0]),int(index[1]*resolution[1]*4/3))
                        l_bar.sety(index[1])
                    if GAMEMODE != 0:
                        packet = struct.pack(DATAFORMAT,l_bar.y/resolution[1],0.,0.,0)
                        s.sendmsg((packet,))

                    
                    
            render(display,index)
            print(clock.tick(30))
    except:
        cap.release()
        pygame.quit()
        s.close()
        mp_controller.close()
        
if __name__ == '__main__':
    main()