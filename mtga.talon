title: MTGA
title: Untapped.gg
mode: user.mtga
mode: command
-
settings():
    key_hold = 32

highlight cards|show cards:
    user.mtga_hide_highlighted_cards()
    user.mtga_highlight_cards()

keep highlighting cards:
    user.mtga_highlight_continually()

stop highlighting cards:
    user.mtga_stop_highlighting_continually()

stop highlight|stop highlights|remove highlights:
    user.mtga_hide_highlighted_cards()

play <number_small>:
    user.mtga_play_a_card(number_small)

fast <number_small>:
    user.mtga_play_a_card(number_small, 1)

select card <number_small>:
    user.mtga_select_card(number_small, 0)

select fast <number_small>:
    user.mtga_select_card(number_small, 1)

play game:
    user.mtga_press_btn("orange", "normal")

keep hand|keep <number_small>:
    user.mtga_press_btn("orange", "normal")

mulligan:
    user.mtga_press_btn("blue", "normal")

done|ok:
    user.mtga_press_btn("orange")

(pass|resolve|resolves|next|[auto] pay|my turn|take action):
    key(space)

all attack|confirm attack|confirm block|no blocks:
    key(space)

no attacks:
    user.mtga_press_btn("blue")

cancel:
    user.mtga_press_btn("blue,orange")

keep passing:
    key(enter)

pass turn|end turn:
    key(shift-enter)

take back:
    key(Z)

full control:
    key(ctrl)
