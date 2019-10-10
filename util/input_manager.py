import pygame
import platform
from operator import attrgetter
from pygame.locals import *

current_platform = platform.uname()[0].upper()
if current_platform == 'WINDOWS':
    import util.xinput as xinput


class Struct(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
        self.__dict__.update(**kwargs)


class InputManager(object):
   
    def __init__(self):

        self.platform = platform.uname()[0].upper()
        self.has_joystick = False
        self.joystick = None
        if self.platform == 'WINDOWS':
            pygame.joystick.init()

            # Initialize a joystick object: grabs the first joystick
            
            windows_platform = current_platform == 'WINDOWS'
            self.windows_xbox_360 = False
            joysticks = xinput.XInputJoystick.enumerate_devices()
            device_numbers = list(map(attrgetter('device_number'), joysticks))
            self.joystick = None
            
            if device_numbers:
                self.has_joystick = True
                self.joystick = pygame.joystick.Joystick(device_numbers[0])
                joystick_name = self.joystick.get_name().upper()
                if 'XBOX 360' in joystick_name and windows_platform:
                    self.windows_xbox_360 = True
                    self.joystick = xinput.XInputJoystick(device_numbers[0])
                else:
                    # put other logic here for handling platform + device type in the event loop
                    self.joystick.init()
        else:
            pygame.joystick.init()
            # how many joysticks are there
            if pygame.joystick.get_count() > 0:
                # get the first joystick
                self.joystick = pygame.joystick.Joystick(0)
                if self.joystick is not None:
                    # init that joystick
                    self.joystick.init()
                    self.has_joystick = True

        self.button_a = Struct(key=0, value=0)
        self.button_b = Struct(key=1, value=0)
        self.button_x = Struct(key=2, value=0)
        self.button_y = Struct(key=3, value=0)
        self.button_left_bumper = Struct(key=4, value=0)
        self.button_right_bumper = Struct(key=5, value=0)
        self.button_back = Struct(key=6, value=0)
        self.button_start = Struct(key=7, value=0)
        self.button_left_stick = Struct(key=8, value=0)
        self.button_right_stick = Struct(key=9, value=0)
        self.x_box_button = Struct(key=10, value=0)
        self.controller_buttons = [
            self.button_a, self.button_b, self.button_x, self.button_y,
            self.button_left_bumper, self.button_right_bumper,
            self.button_back, self.button_start]
        if self.platform == 'WINDOWS':
            self.controller_buttons.append(self.button_left_stick)
            self.controller_buttons.append(self.button_right_stick)
        else:
            self.x_box_button = Struct(key=8, value=0)
            self.button_left_stick = Struct(key=9, value=0)
            self.button_right_stick = Struct(key=10, value=0)
            self.controller_buttons.append(self.x_box_button)
            self.controller_buttons.append(self.button_left_stick)
            self.controller_buttons.append(self.button_right_stick)

        self.right_stick = Struct(key=0, x=0.0, y=0.0)
        self.left_stick = Struct(key=1, x=0.0, y=0.0)
        self.right_trigger = Struct(key=2, value=0.0)
        self.left_trigger = Struct(key=3, value=0.0)

    @staticmethod
    def stick_center_snap(value, snap=0.2):
        # Feeble attempt to compensate for calibration and loose stick.
        if value >= snap or value <= -snap:
            return value
        else:
            return 0.0

    # -----------------------------------------------------
    # Listen for, process and store input events
    # -----------------------------------------------------
    def update_controller_input_events(self, events):
        if self.platform == 'WINDOWS':
            if self.windows_xbox_360:
                self.joystick.dispatch_events()

            for event in events: 
                if event.type == JOYAXISMOTION:
                    if event.axis == 0:  # the left stick y
                        self.left_stick.y = self.stick_center_snap(event.value)
                    elif event.axis == 1:  # the left stick x
                        self.left_stick.x = self.stick_center_snap(event.value)
                    elif event.axis == 3:  # the right stick y
                        self.right_stick.y = self.stick_center_snap(event.value)
                    elif event.axis == 4:  # the right stick x
                        self.right_stick.x = self.stick_center_snap(event.value)
                    elif event.axis == 5:  # right trigger
                        self.right_trigger.value = event.value
                    elif event.axis == 2:  # left trigger
                        self.left_trigger.value = event.value

                elif event.type == JOYBUTTONDOWN:
                    self.controller_buttons[event.button].value = 1
                elif event.type == JOYBUTTONUP:
                    self.controller_buttons[event.button].value = 0
        else:
            # LTHUMBX = 0
            # LTHUMBY = 1
            # LTRIGGER = 2
            # RTHUMBX = 3
            # RTHUMBY = 4
            # RTRIGGER = 5
            # A = 6
            # B = 7
            # X = 8
            # Y = 9
            # LB = 10
            # RB = 11
            # BACK = 12
            # START = 13
            # XBOX = 14
            # LEFTTHUMB = 15
            # RIGHTTHUMB = 16
            # DPAD = 17
            for event in events: 
                if event.type == JOYAXISMOTION:
                    if event.axis == 1:  # the left stick y
                        self.left_stick.y = self.stick_center_snap(event.value)
                    elif event.axis == 0:  # the left stick x
                        self.left_stick.x = self.stick_center_snap(event.value)
                    elif event.axis == 4:  # the right stick y
                        self.right_stick.y = self.stick_center_snap(event.value)
                    elif event.axis == 3:  # the right stick x
                        self.right_stick.x = self.stick_center_snap(event.value)
                    elif event.axis == 5:  # right trigger
                        self.right_trigger.value = event.value
                    elif event.axis == 2:  # left trigger
                        self.left_trigger.value = event.value

                elif event.type == JOYBUTTONDOWN:
                    self.controller_buttons[event.button].value = 1
                elif event.type == JOYBUTTONUP:
                    self.controller_buttons[event.button].value = 0
