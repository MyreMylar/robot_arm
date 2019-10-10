# Python control class for the OWI Robotic Arm
#
# Version 1.1 - 05/01/2013
# Created by Matt Dyson: http://mattdyson.org
#
# Some inspiration from Neil Polwart and John Hale - http://python-poly.blogspot.co.uk
# USB commands reference from http://notbrainsurgery.livejournal.com/38622.html
# See more details on the project at http://mattdyson.org/projects/robotarm
import pygame
import platform
import os

import usb.core
import usb.backend
import time

# Product information for the arm
VENDOR = 0x1267
PRODUCT = 0x0000

# Timeout for our instructions through pyusb
TIMEOUT = 1000


class Motor:

    def __init__(self, name):
        self.name = name
        self.direction = 0
        self.time_since_last_change = 0.0
        self.past_motor_commands = []
        self.current_rewind_command = (0, 0.0)
        self.next_rewind_change_time = 0.0

    def change_direction(self, direction):
        # self.record_command()
        self.direction = direction
        self.time_since_last_change = 0.0

    def update_time(self, time_since_last_update):
        self.time_since_last_change += time_since_last_update

    def record_command(self):
        if self.direction is 1:
            self.past_motor_commands.append((2, self.time_since_last_change))
        elif self.direction is 2:
            self.past_motor_commands.append((1, self.time_since_last_change))
        else:
            self.past_motor_commands.append((0, self.time_since_last_change))

    def rewind_command(self, elapsed_time):
        changed_command = False
        if elapsed_time > self.next_rewind_change_time:
            if self.past_motor_commands:
                new_command = self.past_motor_commands.pop()
                self.next_rewind_change_time += new_command[1]
                self.direction = new_command[0]
                changed_command = True
        return changed_command


class RobotArm:
    """On initialize, attempt to connect to the robotic arm"""

    def __init__(self):
        print("Init'ing RobotArm")
        current_platform = platform.uname()[0].upper()
        self.device = None
        if current_platform == 'WINDOWS':
            backend_dll_path = "libusb-1.0.dll"
            if os.path.isfile(backend_dll_path):
                backend = usb.backend.libusb1.get_backend(find_library=lambda x: backend_dll_path)
                self.device = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT, backend=backend)
        else:
            self.device = usb.core.find(idVendor=VENDOR, idProduct=PRODUCT)
        if self.device:
            self.device_connected = True
            self.device.set_configuration()
        else:
            print("Could not connect to Robotic Arm USB device.")
            self.device_connected = False

        self.rotate = Motor("Base")
        self.shoulder = Motor("Shoulder")
        self.elbow = Motor("Elbow")
        self.wrist = Motor("Wrist")
        self.grip = Motor("Gripper")
        self.light = 0

        self.base_motor_direction = 0
        self.shoulder_motor_direction = 0
        self.elbow_motor_direction = 0
        self.wrist_motor_direction = 0
        self.grip_motor_direction = 0

        self.current_time = 0.0

        self.robot_arm_image = pygame.image.load('robot_arm.jpg')
        self.robot_arm_image = self.robot_arm_image.convert()

        self.font = pygame.font.Font(None, 25)

        self.reset()
        if self.device_connected:
            print("RobotArm now ready!")

    "On delete object, stop what we're currently doing"
    def __del__(self):
        print("Stopping RobotArm")
        self.reset()

    def update_time(self, new_time, time_since_last_update):
        self.current_time = new_time
        self.shoulder.update_time(time_since_last_update)
        self.elbow.update_time(time_since_last_update)
        self.wrist.update_time(time_since_last_update)
        self.grip.update_time(time_since_last_update)
        self.rotate.update_time(time_since_last_update)

    def render_ui(self, screen):
        start_x = int((screen.get_width() - self.robot_arm_image.get_width()) / 2)
        start_y = int((screen.get_height() - self.robot_arm_image.get_height()) / 2)
        screen.blit(self.robot_arm_image, (start_x, start_y))

        self.render_motor(screen, "Base", self.base_motor_direction, 320, 300)
        self.render_motor(screen, "Shoulder", self.shoulder_motor_direction, 320, 200)
        self.render_motor(screen, "Elbow", self.elbow_motor_direction, 350, 130)
        self.render_motor(screen, "Wrist", self.wrist_motor_direction, 200, 100)
        self.render_motor(screen, "Grip", self.grip_motor_direction, 50, 190)

    def render_motor(self, screen, name, direction, x, y):
        text = []
        if direction == 0:
            text.append(self.font.render('< ' + name + ' >', True, (0, 0, 0)))
        if direction == 1:
            text.append(self.font.render('< ', True, (0, 255, 0)))
            text.append(self.font.render(name, True, (0, 0, 0)))
            text.append(self.font.render(' >', True, (0, 0, 0)))
        if direction == 2:
            text.append(self.font.render('< ', True, (0, 0, 0)))
            text.append(self.font.render(name, True, (0, 0, 0)))
            text.append(self.font.render(' >', True, (0, 255, 0)))

        total_width = 20
        for i in range(0, len(text)):
            text_rect = text[i].get_rect()
            total_width += text_rect.width

        pygame.draw.rect(screen, (255, 255, 255), (x, y, total_width, 40))
        # noinspection PyArgumentList
        pygame.draw.rect(screen, (0, 0, 0), (x, y, total_width, 40), 2)

        total_x = x + 10
        for i in range(0, len(text)):
            text_rect = text[i].get_rect()
            text_rect.x = total_x
            text_rect.y = y + 10
            screen.blit(text[i], text_rect)
            total_x += text_rect.width

    def return_to_start_position(self):
        start_time = time.clock()
        print('starting return to start position')
        while self.shoulder.past_motor_commands or self.elbow.past_motor_commands or \
                self.wrist.past_motor_commands or self.grip.past_motor_commands or self.rotate.past_motor_commands:
            elapsed_time = time.clock() - start_time
            changed_command1 = self.shoulder.rewind_command(elapsed_time)
            changed_command2 = self.elbow.rewind_command(elapsed_time)
            changed_command3 = self.wrist.rewind_command(elapsed_time)
            changed_command4 = self.grip.rewind_command(elapsed_time)
            changed_command5 = self.rotate.rewind_command(elapsed_time)

            changed_command = (changed_command1 or changed_command2 or changed_command3 or
                               changed_command4 or changed_command5)

            if changed_command:
                self.update()

        print('Finished returning to start position')

    "Update the device with the latest command set"
    def update(self):
        cmd = self.build_command()
        if self.device_connected:
            self.device.ctrl_transfer(0x40, 6, 0x100, 0, cmd, TIMEOUT)

    "Build a command set from our current values"
    def build_command(self):
        command_bytes = [0] * 3
        shoulder_elbow = (self.shoulder.direction << 6) + (self.elbow.direction << 4)
        wrist_grip = (self.wrist.direction << 2) + self.grip.direction
        command_bytes[0] = shoulder_elbow + wrist_grip
        command_bytes[1] = self.rotate.direction
        command_bytes[2] = self.light

        return command_bytes

    "Reset everything to zero"
    def reset(self):
        self.shoulder.change_direction(0)
        self.elbow.change_direction(0)
        self.wrist.change_direction(0)
        self.grip.change_direction(0)
        self.rotate.change_direction(0)
        self.light = 0

        self.update()

    "Set the light to the opposite of whatever it's on currently"
    def toggle_light(self):
        self.light = (1, 0)[self.light == 1]
        self.update()

    "Turn the light on or off"
    def set_light(self, light_val):
        if light_val not in range(0, 2):
            raise ValueError('Light can only be set to off (0) or on (1)')

        self.light = light_val
        self.update()

    "Rotate the base of the arm"
    def move_base(self, direction, time_to_move=-1.0):
        if direction not in range(0, 3):
            raise ValueError('Base can only be set to stop (0), clockwise (1) or counter-clockwise (2)')

        self.rotate.change_direction(direction)
        self.base_motor_direction = direction
        self.update()

        if time_to_move > 0.0:
            # sleep for the movement time
            time.sleep(time_to_move)
            new_time = time.clock()
            elapsed_time = new_time - self.current_time
            self.rotate.update_time(elapsed_time)
            self.current_time = new_time

            self.rotate.change_direction(0)
            self.base_motor_direction = 0
            self.update()

    "Open or close the grip"
    def move_grip(self, direction, time_to_move=-1.0):
        if direction not in range(0, 3):
            raise ValueError('Grip can only be set to stop (0), close (1) or open (2)')

        self.grip.change_direction(direction)
        self.grip_motor_direction = direction
        self.update()

        if time_to_move > 0.0:
            # sleep for the movement time
            time.sleep(time_to_move)
            new_time = time.clock()
            elapsed_time = new_time - self.current_time
            self.grip.update_time(elapsed_time)
            self.current_time = new_time

            self.grip.change_direction(0)
            self.grip_motor_direction = 0
            self.update()

    "Move the wrist up or down"
    def move_wrist(self, direction, time_to_move=-1.0):
        if direction not in range(0, 3):
            raise ValueError('Wrist can only be set to stop (0), up (1) or down (2)')

        self.wrist.change_direction(direction)
        self.wrist_motor_direction = direction
        self.update()

        if time_to_move > 0.0:
            # sleep for the movement time
            time.sleep(time_to_move)
            new_time = time.clock()
            elapsed_time = new_time - self.current_time
            self.wrist.update_time(elapsed_time)
            self.current_time = new_time

            self.wrist.change_direction(0)
            self.wrist_motor_direction = 0
            self.update()

    "Move the elbow up or down"
    def move_elbow(self, direction, time_to_move=-1.0):
        if direction not in range(0, 3):
            raise ValueError('Elbow can only be set to stop (0), up (1) or down (2)')

        self.elbow.change_direction(direction)
        self.elbow_motor_direction = direction
        self.update()

        if time_to_move > 0.0:
            # sleep for the movement time
            time.sleep(time_to_move)
            new_time = time.clock()
            elapsed_time = new_time - self.current_time
            self.elbow.update_time(elapsed_time)
            self.current_time = new_time

            self.elbow.change_direction(0)
            self.elbow_motor_direction = 0
            self.update()

    "Move the shoulder up or down"
    def move_shoulder(self, direction, time_to_move=-1.0):
        if direction not in range(0, 3):
            raise ValueError('Shoulder can only be set to stop (0), up (1) or down (2)')

        self.shoulder.change_direction(direction)
        self.shoulder_motor_direction = direction
        self.update()

        if time_to_move > 0.0:
            # sleep for the movement time
            time.sleep(time_to_move)
            new_time = time.clock()
            elapsed_time = new_time - self.current_time
            self.shoulder.update_time(elapsed_time)
            self.current_time = new_time

            self.shoulder.change_direction(0)
            self.shoulder_motor_direction = 0
            self.update()

    "Convenience method for moving motors by name"
    def move_motor(self, motor, direction):
        if motor == 'base':
            self.move_base(direction)
        elif motor == 'shoulder':
            self.move_shoulder(direction)
        elif motor == 'elbow':
            self.move_elbow(direction)
        elif motor == 'wrist':
            self.move_wrist(direction)
        elif motor == 'grip':
            self.move_grip(direction)
        else:
            raise ValueError('Do not know how to move %s' % motor)

    "Flash the light 'iterations' times, with a gap of 'interval' between each"
    def flash_light(self, iterations, interval):
        for i in range(iterations):
            self.set_light(1)
            time.sleep(interval)
            self.set_light(0)
            time.sleep(interval)
