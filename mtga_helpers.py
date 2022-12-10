"""Helper functions for doing visual analysis on MTGA."""
import os
import sys


try:
    import cv2
    import pyautogui

    import numpy as np

    from PIL import ImageGrab

except ImportError:
    print("Could not find needed packages in current (Talon?) venv, trying Anaconda environment shim")

    try:  # Needed to work in local and Talon space
        from custom_env import CustomEnv
    except:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from custom_env import CustomEnv

    with CustomEnv():
        import cv2
        import pyautogui

        import numpy as np

        from PIL import ImageGrab


def mtga_find_button(colour: str = "orange", enlarged: bool = False, screenshot=None, debug=False):
    """Find MTGA buttons on the screen.

    Assumes there is one blue or orange button to be found on screen and finds it or
    returns None if there are no "good" candidates. If there are multiple of the
    particular colour button then a not-entirely-random one will be returned.

    Use enlarged for the bigger buttons that appear sometimes e.g. for mulligan.

    Note this is pretty hacky and calibrated on a 2560x1440 display, may need tweaking.
    """
    if screenshot is None:
        im = ImageGrab.grab()  # RGB colour space
        screenshot = np.array(im)

    if colour == "orange":
        colour_range = [(240, 0, 0), (255, 255, 150)]
        min_size = 3000
    elif colour == "blue":
        colour_range = [(30, 0, 200), (150, 200, 255)]
        min_size = 1500
    else:
        raise AttributeError(f"Colour '{colour}' is invalid!")

    min_x_len = 350
    min_y_len = 100

    if enlarged:
        min_x_len = min_x_len * 1.5
        min_y_len = min_y_len * 1.5
        min_size = min_size * 1.5

    mask_highlights = cv2.inRange(screenshot, colour_range[0], colour_range[1])

    kernel = np.ones((5, 5), "uint8")
    mask_highlights = cv2.erode(mask_highlights, kernel)
    mask_highlights = cv2.dilate(mask_highlights, kernel)

    all_contours, _ = cv2.findContours(mask_highlights, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    largest_size = 0
    btn_info = None
    for cur_contour in all_contours:
        size = cv2.contourArea(cur_contour)
        if size < min_size:
            continue

        if size < largest_size:
            continue

        xmax, ymax = (np.max(cur_contour, axis=0)).ravel()
        xmin, ymin = (np.min(cur_contour, axis=0)).ravel()

        if (xmax - xmin) > min_x_len or (ymax - ymin) > min_y_len:
            continue

        largest_size = size

        btn_real_x = int(xmin + ((xmax - xmin) / 2))
        btn_real_y = int(ymin + ((ymax - ymin) / 2))
        btn_info = (btn_real_x, btn_real_y)

    if debug:
        cv2.drawContours(screenshot, all_contours, -1, (0, 255, 0), 3)

        if btn_info is not None:
            cv2.drawMarker(
                screenshot,
                (btn_real_x, btn_real_y),
                (0, 0, 0),
                markerType=cv2.MARKER_STAR,
                markerSize=40,
                thickness=2,
                line_type=cv2.LINE_AA,
            )

        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)  # Fix colours
        cv2.imshow("Final Selection", screenshot)
        cv2.imshow("Final Selection", mask_highlights)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return btn_info


def mtga_get_card_positions(screenshot=None, debug=False):
    """
    Get playable card positions from MTGA, returns of list of (x, y) tuples.

    Assumes MTGA is in focus without obstruction on main screen.

    Struggles with yellow highlighted cards on the far left due to shading.

    Tested on a 1440p screen, "border_" and "card_region" values will need tweaking for
    1080p

    Note that debug mode will crash Talon
    """
    # Blue masking
    specific_colours = []
    standard_blue_range = [(0x00, 0xAF, 0xAF), (0x01, 0xFF, 0xFF)]
    foretell_blue_range = [(0x00, 0xFA, 0xFA), (0x3F, 0xFF, 0xFF)]
    standard_yellow_range = [(0xF4, 0xF4, 0xBF), (0xFF, 0xFF, 0xFE)]
    selected_yellow_range = [(0xFD, 0xFD, 0x00), (0xFF, 0xFF, 0x01)]
    min_blue_length = 45  # Min line length - use to cut ends and short regions

    # Black border finding
    gray_range = (18, 200)  # (18, 50) without foretell-esque cards
    max_colour_diff = 3
    border_max_size = 9000
    border_min_size = 950
    border_min_vertexs = 3
    border_min_xlen = 40
    border_min_ylen = 15

    # Screen region slicing
    screen_w, screen_h = pyautogui.size()
    card_region = (
        0.1 * screen_w,
        0.85 * screen_h,
        0.9 * screen_w,
        screen_h,
    )  # (left_x, top_y, right_x, bottom_y)

    if screenshot is None:
        im = ImageGrab.grab(bbox=card_region)  # RGB colour space
        screenshot = np.array(im)

    # Grab blue highlighted cards that we can play
    mask_highlights = cv2.inRange(screenshot, standard_blue_range[0], standard_blue_range[1])
    mask_highlights = np.logical_or(
        mask_highlights,
        cv2.inRange(screenshot, foretell_blue_range[0], foretell_blue_range[1]),
    )
    mask_highlights = np.logical_or(
        mask_highlights,
        cv2.inRange(screenshot, standard_yellow_range[0], standard_yellow_range[1]),
    )
    mask_highlights = np.logical_or(
        mask_highlights,
        cv2.inRange(screenshot, selected_yellow_range[0], selected_yellow_range[1]),
    )

    for cur_colour in specific_colours:
        mask_highlights = np.logical_or(mask_highlights, cv2.inRange(screenshot, cur_colour, cur_colour))

    # Fill down below highlighted regions as long they are at least a certain length, otherwise mask out
    mask_highlights[0, :] = False  # Ensure == 0 means no white in column
    col_highest_blue_pixel = np.argmax(mask_highlights, axis=0)
    for col in range(mask_highlights.shape[1]):
        if np.all(col_highest_blue_pixel[col : col + min_blue_length] != 0):
            mask_highlights[col_highest_blue_pixel[col] :, col] = True
        else:
            mask_highlights[:, col] = False

    # Use the blue mask to pre-filter so we can grab black card borders
    screenshot[~mask_highlights] = np.array([255, 255, 255])

    # Find black borders of cards
    mask_black = cv2.inRange(screenshot, np.array([gray_range[0]] * 3), np.array([gray_range[1]] * 3))

    max_colour_val = np.max(screenshot, axis=2)
    min_colour_val = np.min(screenshot, axis=2)
    mask_colour_difference = (max_colour_val - min_colour_val) < max_colour_diff

    mask_black = np.logical_and(
        mask_black,
        mask_colour_difference,
    )
    mask_black = (mask_black * 255).astype(np.uint8)
    kernel = np.ones((5, 5), "uint8")
    mask_black = cv2.erode(mask_black, kernel)
    mask_black = cv2.dilate(mask_black, kernel)

    # Get contours
    cnts, hier = cv2.findContours(mask_black, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    valid_contours = []
    card_info = []
    for i, cur_contour in enumerate(cnts):
        size = cv2.contourArea(cur_contour)
        peri = cv2.arcLength(cur_contour, True)
        approx = cv2.approxPolyDP(cur_contour, 0.01 * peri, True)

        xmax, ymax = (np.max(cur_contour, axis=0)).ravel()
        xmin, ymin = (np.min(cur_contour, axis=0)).ravel()

        if (
            (size < border_max_size)
            and (size > border_min_size)
            and (len(approx) >= border_min_vertexs)
            and (xmax - xmin > border_min_xlen)
            and (ymax - ymin > border_min_ylen)
        ):
            valid_contours.append(cur_contour)

            card_real_x = int(card_region[0] + xmin + ((xmax - xmin) / 2))
            card_real_y = int(card_region[1] + ymin + ((ymax - ymin) / 2))
            card_top = int(card_region[1] + ymin)
            card_info.append((card_real_x, card_real_y, card_top))

    if debug:
        cv2.drawContours(screenshot, valid_contours, -1, (0, 255, 0), 3)

        print(card_info)
        for x, y, y_top in card_info:
            x = int(x - card_region[0])
            y = int(y - card_region[1])
            cv2.drawMarker(
                screenshot,
                (x, y),
                (255, 0, 0),
                markerType=cv2.MARKER_STAR,
                markerSize=20,
                thickness=2,
                line_type=cv2.LINE_AA,
            )

        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)  # Fix colours
        cv2.imshow("Blue Highlight Mask", (mask_highlights * 255).astype(np.uint8))
        cv2.imshow("Black Border Regions", mask_black)
        cv2.imshow("Final Selection", screenshot)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return card_info
