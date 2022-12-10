"""Main MTGA functions."""
import copy
import time
from .talon_utils import *
from .mtga_helpers import *

from talon import Module, imgui, ctrl, cron


mod = Module()
screen_w, screen_h = pyautogui.size()


def make_card_gui_funcs(x):
    """Use Talon inbuilt GUI functions to make 'play X' overlays."""

    @imgui.open()
    def _card_gui(gui: imgui.GUI):
        gui.text(f"Play {x+1}")
        gui.line()

    return _card_gui


max_cards_to_highlight = 10
card_guis = [make_card_gui_funcs(x) for x in range(max_cards_to_highlight)]
playable_cards = []

cron_handle = None


def highlight_cards():
    """Place GUI overlay above each playable card in hand."""
    global card_guis
    gui_offset = 100

    card_info = mtga_get_card_positions()
    card_info.sort(key=lambda x: x[0])  # Sort by x location

    global playable_cards
    playable_cards = copy.deepcopy(card_info)

    for i, (x, y, y_top) in enumerate(card_info):
        card_guis[i].x = x
        card_guis[i].y = y_top - gui_offset
        card_guis[i].show()

    return card_info


def highlight_cards_continually():
    """Highlight all playable cards."""
    card_info = highlight_cards()
    [card_guis[i].hide() for i in range(len(card_info), len(card_guis))]


@mod.action_class
class Actions:
    def mtga_press_btn(colours: str = "orange", size: str = "auto"):  # "normal", "enlarged", "auto"
        """Find a button in MTGA.

        Auto tries normal size followed by enlarged if no "good" candidates appear

        Use commas to search for colours in a particular order, finishing early if one is found
        """
        colours = colours.split(",")
        for cur_colour in colours:
            if size == "auto":
                btn_loc = mtga_find_button(colour=cur_colour, enlarged=False)
                if btn_loc is None:
                    btn_loc = mtga_find_button(colour=cur_colour, enlarged=True)
            elif size == "normal":
                btn_loc = mtga_find_button(colour=cur_colour, enlarged=False)
            elif size == "enlarged":
                btn_loc = mtga_find_button(colour=cur_colour, enlarged=True)
            else:
                raise AttributeError("size input invalid.")

            if btn_loc is not None:
                boomerang_click(0, btn_loc[0], btn_loc[1])
                break

    def mtga_highlight_cards():
        """Place GUI overlay above each playable card in hand"""
        global card_guis
        card_info = highlight_cards()

        cron.after("5s", lambda: [card_guis[i].hide() for i in range(len(card_info))])

    def mtga_hide_highlighted_cards():
        """Hide any active GUIs."""
        global card_guis
        for card_gui in card_guis:
            card_gui.hide()

    def mtga_highlight_continually():
        """Activate continuous card highlighting."""
        global cron_handle
        highlight_cards()

        cron_handle = cron.interval("1s", highlight_cards_continually)

    def mtga_stop_highlighting_continually():
        """Deactivate continuous card highlighting."""
        global cron_handle
        cron.cancel(cron_handle)

        global card_guis
        for card_gui in card_guis:
            card_gui.hide()

    def mtga_select_card(card_nb: int, search_first: int = 0):
        """Select card by number."""
        global playable_cards

        if search_first:
            card_locs = mtga_get_card_positions()
            card_locs.sort(key=lambda x: x[0])  # Sort by x location

            playable_cards = copy.deepcopy(card_locs)

        if len(playable_cards) > card_nb - 1:
            (card_x, card_y, card_top) = playable_cards[card_nb - 1]
            boomerang_click(0, card_x, card_y)

    def mtga_play_a_card(card_nb: int, search_first: int = 0):
        """Play card by number."""
        global playable_cards
        global screen_h
        global screen_w

        if search_first:
            card_locs = mtga_get_card_positions()
            card_locs.sort(key=lambda x: x[0])  # Sort by x location

            playable_cards = copy.deepcopy(card_locs)

        # Drag card to middle of screen
        if len(playable_cards) > card_nb - 1:
            org_mouse_position = ctrl.mouse_pos()
            (card_x, card_y, card_top) = playable_cards[card_nb - 1]
            ctrl.mouse_move(card_x, card_y)
            ctrl.mouse_click(button=0, down=True)
            time.sleep(0.050)
            ctrl.mouse_move(int(screen_w / 2), int(screen_h / 2))
            time.sleep(0.050)
            ctrl.mouse_click(button=0, up=True)
            time.sleep(0.050)
            ctrl.mouse_move(org_mouse_position[0], org_mouse_position[1])
