import pygame
from pygame.locals import *

from util.input_manager import InputManager
from util.robot_arm import RobotArm
import time


# ------------------------------------------
# Challenge 1 starts on line 31!
# ------------------------------------------
class RobotArmControl:

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Robot Arm Control')
        self.screen = pygame.display.set_mode((640, 480))
        
        self.controller_input_manager = InputManager()
        self.arm = RobotArm()

        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert(self.screen)
        self.background.fill((255, 255, 255))

        self.previous_loop_time = time.clock()
        self.light_on = False
        self.first_light_press = True

    # -------------------------------------------------------------------------------
    # CHALLENGE 1
    # -------------
    # Create keyboard controls for the entire robot arm using pygame. You will need to use
    # the pygame events we have practiced in earlier lessons and the robot arm's motor
    # control functions.
    #
    # If you have done it right you should see your key presses show up on the arm image
    # as the little arrows change colour to green.
    #
    # When passing a parameter to the motor functions - 0 stops the motor,
    # 1 rotates it one way and 2 rotates it the other way
    #
    # These are the commands to rotate the motors on the arm:
    #
    # self.arm.move_base(1)      - controls the base motor.
    #                             
    # self.arm.move_shoulder(2)  - controls the shoulder motor
    #
    # self.arm.move_elbow(0)     - controls the elbow motor
    #
    # self.arm.move_wrist(1)     - controls the wrist
    #
    # self.arm.move_grip(0)      - opens and closes the gripper; as before 0 is stop
    #                             and 1 & 2 open and close the gripper
    #
    #
    # You can find a list of all valid pygame keys available here:
    # https://www.pygame.org/docs/ref/key.html
    #
    # OR just look at the bottom of this file where I have copied the list in a comment.
    # --
    # When you have finished we will try to get your code onto a robot arm equipped
    # raspberry pi using one of these websites:
    #
    # https://pastebin.com/
    # https://controlc.com/
    # https://paste2.org/
    # http://codepad.org/
    #
    # or the school's Fronter if that doesn't work.
    # -------------------------------------------------------------------------------
    def update(self):
        running = True
        while running:
            self.handle_time()
  
            events = pygame.event.get()
            self.handle_controller_input(events)
            for event in events:
                if event.type == QUIT:
                    running = False
                    
                if event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        print("left key down")
                       
                if event.type == KEYUP:
                    if event.key == K_LEFT:
                        print("left key up") 
                        
            self.screen.blit(self.background, (0, 0))
            self.arm.render_ui(self.screen)
            pygame.display.flip()
            
        pygame.quit()

    def handle_time(self):
        new_loop_time = time.clock()
        elapsed_time = new_loop_time - self.previous_loop_time
        self.previous_loop_time = new_loop_time
        self.arm.update_time(new_loop_time, elapsed_time)

    def handle_controller_input(self, events):

        self.controller_input_manager.update_controller_input_events(events)

        if self.controller_input_manager.joystick is not None:
            
            # Base
            if self.controller_input_manager.right_stick.x > 0.2:
                self.arm.move_base(1)
            elif self.controller_input_manager.right_stick.x < -0.2:
                self.arm.move_base(2)
            else:
                self.arm.move_base(0)
                
            # Shoulder
            if self.controller_input_manager.right_stick.y > 0.2:
                self.arm.move_shoulder(1)
            elif self.controller_input_manager.right_stick.y < -0.2:
                self.arm.move_shoulder(2)
            else:
                self.arm.move_shoulder(0)

            # Elbow
            if self.controller_input_manager.left_stick.x > 0.2:
                self.arm.move_elbow(2)
            elif self.controller_input_manager.left_stick.x < -0.2:
                self.arm.move_elbow(1)
            else:
                self.arm.move_elbow(0)

            # Wrist
            if self.controller_input_manager.left_stick.y > 0.2:
                self.arm.move_wrist(1)
            elif self.controller_input_manager.left_stick.y < -0.2:
                self.arm.move_wrist(2)
            else:
                self.arm.move_wrist(0)

            # Gripper
            if self.controller_input_manager.right_trigger.value > 0.2:
                self.arm.move_grip(1)
            elif self.controller_input_manager.left_trigger.value > 0.2:
                self.arm.move_grip(2)
            else:
                self.arm.move_grip(0)

            right_bumper_key = self.controller_input_manager.button_right_bumper.key
            right_bumper_pressed = self.controller_input_manager.controller_buttons[right_bumper_key].value != 0

            if right_bumper_pressed:
                if self.first_light_press:
                    if self.light_on:
                        self.light_on = False
                        self.arm.set_light(0)
                    else:
                        self.light_on = True
                        self.arm.set_light(1)
                self.first_light_press = False
            else:
                self.first_light_press = True


robot_arm_control = RobotArmControl()
robot_arm_control.update()

# -----------------------------------------------
# Pygame key codes
# ---------------------
#
# KeyASCII      ASCII   Common Name
# K_BACKSPACE   \b      backspace
# K_TAB         \t      tab
# K_CLEAR               clear
# K_RETURN      \r      return
# K_PAUSE               pause
# K_ESCAPE      ^[      escape
# K_SPACE               space
# K_EXCLAIM     !       exclaim
# K_QUOTEDBL    "       quotedbl
# K_HASH        #       hash
# K_DOLLAR      $       dollar
# K_AMPERSAND   &       ampersand
# K_QUOTE               quote
# K_LEFTPAREN   (       left parenthesis
# K_RIGHTPAREN  )       right parenthesis
# K_ASTERISK    *       asterisk
# K_PLUS        +       plus sign
# K_COMMA       ,       comma
# K_MINUS       -       minus sign
# K_PERIOD      .       period
# K_SLASH       /       forward slash
# K_0           0       0
# K_1           1       1
# K_2           2       2
# K_3           3       3
# K_4           4       4
# K_5           5       5
# K_6           6       6
# K_7           7       7
# K_8           8       8
# K_9           9       9
# K_COLON       :       colon
# K_SEMICOLON   ;       semicolon
# K_LESS        <       less-than sign
# K_EQUALS      =       equals sign
# K_GREATER     >       greater-than sign
# K_QUESTION    ?       question mark
# K_AT          @       at
# K_LEFTBRACKET [       left bracket
# K_BACKSLASH   \       backslash
# K_RIGHTBRACKET ]      right bracket
# K_CARET       ^       caret
# K_UNDERSCORE  _       underscore
# K_BACKQUOTE   `       grave
# K_a           a       a
# K_b           b       b
# K_c           c       c
# K_d           d       d
# K_e           e       e
# K_f           f       f
# K_g           g       g
# K_h           h       h
# K_i           i       i
# K_j           j       j
# K_k           k       k
# K_l           l       l
# K_m           m       m
# K_n           n       n
# K_o           o       o
# K_p           p       p
# K_q           q       q
# K_r           r       r
# K_s           s       s
# K_t           t       t
# K_u           u       u
# K_v           v       v
# K_w           w       w
# K_x           x       x
# K_y           y       y
# K_z           z       z
# K_DELETE              delete
# K_KP0                 keypad 0
# K_KP1                 keypad 1
# K_KP2                 keypad 2
# K_KP3                 keypad 3
# K_KP4                 keypad 4
# K_KP5                 keypad 5
# K_KP6                 keypad 6
# K_KP7                 keypad 7
# K_KP8                 keypad 8
# K_KP9                 keypad 9
# K_KP_PERIOD   .       keypad period
# K_KP_DIVIDE   /       keypad divide
# K_KP_MULTIPLY *       keypad multiply
# K_KP_MINUS    -       keypad minus
# K_KP_PLUS     +       keypad plus
# K_KP_ENTER    \r      keypad enter
# K_KP_EQUALS   =       keypad equals
# K_UP                  up arrow
# K_DOWN                down arrow
# K_RIGHT               right arrow
# K_LEFT                left arrow
# K_INSERT              insert
# K_HOME                home
# K_END                 end
# K_PAGEUP              page up
# K_PAGEDOWN            page down
# K_F1                  F1
# K_F2                  F2
# K_F3                  F3
# K_F4                  F4
# K_F5                  F5
# K_F6                  F6
# K_F7                  F7
# K_F8                  F8
# K_F9                  F9
# K_F10                 F10
# K_F11                 F11
# K_F12                 F12
# K_F13                 F13
# K_F14                 F14
# K_F15                 F15
# K_NUMLOCK             numlock
# K_CAPSLOCK            capslock
# K_SCROLLOCK           scrollock
# K_RSHIFT              right shift
# K_LSHIFT              left shift
# K_RCTRL               right ctrl
# K_LCTRL               left ctrl
# K_RALT                right alt
# K_LALT                left alt
# K_RMETA               right meta
# K_LMETA               left meta
# K_LSUPER              left windows key
# K_RSUPER              right windows key
# K_MODE                mode shift
# K_HELP                help
# K_PRINT               print screen
# K_SYSREQ              sysrq
# K_BREAK               break
# K_MENU                menu
# K_POWER               power
# K_EURO                euro
#
# ----------------------------------------------------
