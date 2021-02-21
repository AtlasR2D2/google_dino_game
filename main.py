# Google Dinosaur Game Bot
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
# import pyautogui
# pyautogui.PAUSE = 2.5
from PIL import Image
from io import BytesIO
import numpy as np
from collections import defaultdict

GREY_PIXEL = np.array((83, 83, 83))
LOWEST_Y_PIXEL = 25 # Obstacles expected above this
HIGHEST_Y_PIXEL = 130 # Obstacles expected below this

dino_dims = np.genfromtxt("dino_dims.txt", delimiter=",", skip_header=True, dtype=int)  # Stores shape of dinosaur


def obstacle_detected(dino_dims, grey_pixels):
    """finds the dino location based on the grey_pixels"""
    # print(f"number of grey pixels: {len(grey_pixels)}")
    # pixel_count =0
    for pixel in grey_pixels:
        # pixel_count += 1
        dino_found = False
        # Iterate over each pixel in dino_dims
        for x in dino_dims:
            # print([pixel[0]+x[0], pixel[1]+x[1]])
            if [pixel[0]+x[0], pixel[1]+x[1]] in grey_pixels:
                # Pixel Exists
                dino_found = True
                pass
            else:
                dino_found = False
                break
        if dino_found:
            start_pixel = pixel
            break
    # print(f"pixel_count: {pixel_count}")
    if dino_found:
        # Build dino location list
        dino_location = []
        for x in dino_dims:
            dino_location.append([start_pixel[0]+x[0], start_pixel[1]+x[1]])
        # Strip out dino location pixels from grey_pixels
        non_dino_pixels = [pixel for pixel in grey_pixels if pixel not in dino_location and pixel[0] > LOWEST_Y_PIXEL]
        # print(non_dino_pixels)
        # identify dino y pixels (height)
        dino_loc_np = np.array(dino_location)
        min_y = dino_loc_np[:, 0].min()
        max_y = dino_loc_np[:, 0].max()
        min_x = dino_loc_np[:, 1].min()
        max_x = dino_loc_np[:, 1].max()
        if max_y > HIGHEST_Y_PIXEL:
            max_y = HIGHEST_Y_PIXEL
        length_dino = max_x - min_x
        #print(length_dino)
        # print(f"min_x: {min_x}, max_x: {max_x}, min_y: {min_y}, max_y: {max_y}")
        # jump if there exists a pixel in grey_pixels within length_dino of the dino in the min_y to max_y plane
        obstacle_found = False
        for pixel in non_dino_pixels:
            # Check grey pixel in dino y_plane
            if min_y < pixel[0] < max_y:
                # Check if grey pixel within length_dino distance from the dino
                if pixel[1] > max_x and pixel[1] - max_x <= length_dino:
                    obstacle_found = True
                    break
    else:
        # Dino not found
        obstacle_found = False
    # Return whether an obstacle has been found
    print(f"obstacle_found: {obstacle_found}")
    return obstacle_found


def dino_jump():
    """Have you never seen a dinosaur jump before?"""
    driver.find_element_by_xpath("/html/body").send_keys(Keys.SPACE)


def take_canvas_photo():
    """returns a photo of the runner-canvas"""
    game_canvas = driver.find_element_by_class_name("runner-canvas")
    canvas_loc = game_canvas.location
    canvas_size = game_canvas.size
    page_screenshot = driver.get_screenshot_as_png()
    screenshot_img = Image.open(BytesIO(page_screenshot))
    canvas_img = screenshot_img.crop((canvas_loc["x"], canvas_loc["y"], canvas_loc["x"] + canvas_size["width"], canvas_loc["y"] + canvas_size["height"]))
    # canvas_img.save("canvas_screenshot.png") #    Uncomment out if you want to print the photo
    return canvas_img

def get_grey_pixels(canvas_array_x):
    """returns """
    pixel_locator = canvas_array_x[:, :] == GREY_PIXEL
    grey_pixels = []
    for x in range(pixel_locator.shape[0]):
        for y in range(pixel_locator.shape[1]):
            if pixel_locator[x, y].all():
                grey_pixels.append([x, y])
    return grey_pixels


def get_cols_dict():
    """returns the colours in the image by occurrence count"""
    cols_dict = {}
    for x in canvas_array:
        for y in x:
            strRGB = str(y[:])
            if strRGB not in cols_dict:
                cols_dict[strRGB] = 1
            else:
                cols_dict[strRGB] += 1
    print(cols_dict)


chrome_driver_path = 'chromedriver.exe'
driver = webdriver.Chrome(executable_path=chrome_driver_path)

target_url = "https://elgoog.im/t-rex/"
driver.get(target_url)
# Let the webpage load
time.sleep(2)

# Start the game
dino_jump()

play_game = True
loop_counter = 0
while play_game:
    loop_counter += 1
    canvas_photo = take_canvas_photo()
    canvas_array = np.array(canvas_photo)[:, :, :3]     # Store canvas photo as numpy array and remove 4th dimension (GIF images have 4 dimensions rather than 3 for RGB values)
    grey_pixels = get_grey_pixels(canvas_array_x=canvas_array)
    if obstacle_detected(dino_dims=dino_dims, grey_pixels=grey_pixels):
        dino_jump()
