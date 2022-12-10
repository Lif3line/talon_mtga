not mode: sleep
-
^enable magic mode$:
    mode.disable("sleep")
    mode.disable("command")
    mode.disable("dictation")
    mode.enable("user.mtga")

^disable magic mode$:
    mode.enable("command")
    mode.disable("user.mtga")
