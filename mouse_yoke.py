from pyautogui import size, moveTo
from pynput import mouse, keyboard
from threading import Thread, Event
import vgamepad as vg
import json
import tkinter
import logging

with open("./config.json") as config_file:
    configs = json.load(config_file)

gamepad = vg.VX360Gamepad()
screen_size = size()

# Globals created by the UI thread
label1 = None
label2 = None
label3 = None
root = None

# Signal that UI is ready
ui_ready = Event()

pixelsToFloatX = 0.0
pixelsToFloatY = 0.0
global_x = 0
global_y = 0
active = False
activeRightStick = False
deactivatedByRightMouse = False

last_x_position = (screen_size.width / 2)
last_y_position = (screen_size.height / 2)

def change_label(widget, **kwargs):
    """Schedule a thread-safe widget config from non-UI threads."""
    if widget is None:
        return
    try:
        widget.after(0, lambda: widget.configure(**kwargs))
    except Exception:
        # If widget has been destroyed or not ready, just ignore
        pass

def printOnScreen():
    global root, label1, label2, label3

    root = tkinter.Tk()
    root.overrideredirect(True)  # No border, no title bar
    root.geometry(f"{screen_size.width}x{screen_size.height}+0+0")
    root.lift()
    root.wm_attributes("-topmost", True)
    root.wm_attributes("-disabled", True)
    root.wm_attributes("-transparentcolor", "white")
    root.config(bg="white")  # Needed for transparency to work

    label1 = tkinter.Label(root, text='OFF', font=('Times', '11'), fg='black', bg='red')
    label1.place(x=0, y=0)

    """ # Debugging
    label2 = tkinter.Label(root, text='OFF', font=('Times', '11'), fg='black', bg='red')
    label2.place(x=500, y=700)

    label3 = tkinter.Label(root, text='OFF', font=('Times', '11'), fg='black', bg='red')
    label3.place(x=500, y=720)
    """

    ui_ready.set()  # UI widgets are ready to receive updates
    root.mainloop()

def mouseYoke(x, y):
    global pixelsToFloatX, pixelsToFloatY
    global global_x, global_y

    global_x = x
    global_y = y

    """ # Debugging
    if ui_ready.is_set():
        change_label(label2, text=f"{global_x} | {global_y}", bg='lightgreen')
        change_label(label3, text=f"{last_x_position} | {last_y_position}", bg='lightgreen')
    """

    if active:
        if 0 <= x <= screen_size.width:
            pixelsToFloatX = x / (screen_size.width / 2) - 1
        if 0 <= y <= screen_size.height:
            pixelsToFloatY = y / (screen_size.height / 2) - 1

        if activeRightStick:
            gamepad.right_joystick_float(x_value_float=pixelsToFloatX, y_value_float=pixelsToFloatY)
        else:
            gamepad.left_joystick_float(x_value_float=pixelsToFloatX, y_value_float=pixelsToFloatY)
        gamepad.update()

def on_click(x, y, button, pressed):
    if not pressed and button == mouse.Button.middle:
        onKeyRelease('mouseMiddleClick')
    elif pressed and button == mouse.Button.right:
        onPress('mouseRightClick')
    elif not pressed and button == mouse.Button.right:
        onKeyRelease('mouseRightClick')

def onPress(key):
    global activeRightStick, last_x_position, last_y_position, active, deactivatedByRightMouse
    if key == keyboard.KeyCode.from_char(configs["rudder_key"]) and active:
        if activeRightStick == False:  
            last_x_position = global_x
            last_y_position = global_y
        activeRightStick = True
        if ui_ready.is_set():
            change_label(label1, text='ON (RUDDER)', bg='lightgreen')

    elif key == 'mouseRightClick' and active:
        deactivatedByRightMouse = True
        active = False

def onKeyRelease(key):
    global active, activeRightStick, deactivatedByRightMouse
    global last_x_position, last_y_position

    if key == keyboard.KeyCode.from_char(configs["rudder_key"]) and active:
        activeRightStick = False
        moveTo(last_x_position, last_y_position)

        if ui_ready.is_set():
            change_label(label1, text='ON', bg='lightgreen')

    elif key == keyboard.KeyCode.from_char(configs["master_key"]) or key == 'mouseMiddleClick':
        if active:
            last_x_position = global_x
            last_y_position = global_y
            if ui_ready.is_set():
                change_label(label1, text='OFF', bg='red')
        else:
            if ui_ready.is_set():
                change_label(label1, text='ON', bg='lightgreen')

        active = not active

        if active:
            moveTo(last_x_position, last_y_position)

    elif key == 'mouseRightClick' and deactivatedByRightMouse:
        active = True
        deactivatedByRightMouse = False

    elif key == keyboard.KeyCode.from_char(configs["center_xy_axes_key"]):
        moveTo(screen_size.width / 2, screen_size.height / 2)
        if active:
            mouseYoke(screen_size.width / 2, screen_size.height / 2)

if __name__ == "__main__":
    print("MOUSE YOKE READY")
    print("Enable / disable with middle mouse click.")
    try:
        ui = Thread(target=printOnScreen, daemon=True)  # UI thread runs Tkinter
        ms = mouse.Listener(on_move=mouseYoke, on_click=on_click)
        kb = keyboard.Listener(on_release=onKeyRelease, on_press=onPress)

        ui.start()
        ms.start()
        kb.start()

        ms.join()
        kb.join()
    except Exception:
        logging.critical("Exception occurred", exc_info=True)