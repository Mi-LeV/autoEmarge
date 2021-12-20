import pyautogui
import time
import threading
import os
from PIL import Image
from pynput.keyboard import Key,Listener
import requests
import tkinter

h_g, b_d = ((0,0), (0,0))
seuil = 100

def on_release(key):
    if key == Key.enter:
        return False
    try:
        if key.char == '1':
            global h_g
            h_g = pyautogui.position()
        elif key.char == '2':
            global b_d
            b_d = pyautogui.position()
    except:pass
    
def on_press(y):
    y.do_run = False
    return False

def fast_draw(y,pix,x_pos,y_pos,width,height):
    n= 0
    
    for i in range(width):
        serie = []
        for j in range(height):
            if not getattr(y, "do_run", True):
                print("Keyboard interruption !")
                return n

            if sum(pix[i,j][0:3])/3 < seuil and pix[i,j][3] > seuil:
                serie.append((i,j))
                n += 1
            elif len(serie) > 0:
                pyautogui.moveTo(serie[0][0]+x_pos,serie[0][1]+y_pos)
                pyautogui.dragTo(serie[-1][0]+x_pos,serie[-1][1]+y_pos,0.2)
                serie = []
                
        if len(serie) > 0:
            pyautogui.moveTo(serie[0][0]+x_pos,serie[0][1]+y_pos)
            pyautogui.dragTo(serie[-1][0]+x_pos,serie[-1][1]+y_pos)
    return n

def resize_in_selection(img,b_d,h_g):
    im_width, im_height = img.size
    width,height = b_d[0]-h_g[0],b_d[1]-h_g[1]

    if height/im_height > width/im_width:
        new_height = height
        new_width = int(im_width*height/im_height)
    else:
        new_width = width
        new_height = int(im_height*width/im_width)

    return img.resize((new_width,new_height), Image.ANTIALIAS),new_width,new_height

def main(url):
    y = threading.current_thread()
    image_file = os.listdir()[1]
    img = Image.open(requests.get(url, stream=True).raw)
    img = img.convert('RGBA') # conversion to RGBA

    x_pos,y_pos = h_g
    img, new_width, new_height= resize_in_selection(img,b_d,h_g)
    pix = img.load()

    start = time.time()

    nb_pix = fast_draw(y,pix,x_pos,y_pos,new_width,new_height)

    end = time.time()
    print("Drew ",nb_pix," pixels in ",int(end-start)," seconds")
    print(int(nb_pix/(end-start))," pix/s")

def startMain():
    
    global entree
    url = entree.get()
    fenetre.destroy()
    
    y = threading.Thread(target=main, args=(url,))
    y.start()
    listener = Listener(on_press=lambda x=None:on_press(y),suppress=True)
    listener.start()

with Listener(
        on_release=on_release) as listener:
    listener.join()


fenetre = tkinter.Tk()
frame = tkinter.Frame(fenetre)
frame.pack()
etiquette = tkinter.Label(frame, text='URL ')
etiquette.pack(padx=5, pady=5, side=tkinter.LEFT)

entree = tkinter.Entry(frame, width=50)
entree.pack(padx=5, pady=5, side=tkinter.LEFT)
entree.focus_force()

btnAffiche = tkinter.Button(fenetre, text='GET', command=startMain)
btnAffiche.pack(padx=5, pady=5)

fenetre.mainloop()
