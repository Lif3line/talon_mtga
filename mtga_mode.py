from talon import Context, Module, actions, ui, actions, scope

mod = Module()

mod.mode("mtga", "Disable other commands to improve recognition and reduce chance of accidental activations")

game_list = ["MTGA.exe"]


def on_app_switch(app):
    """Auto-switch to limited mode when MTGA is on"""
    modes = scope.get("mode")

    if app.name in game_list:
        if "user.mtga" not in modes:
            actions.mode.disable("command")
            actions.mode.enable("user.mtga")
            print(f"App [{app.name}] triggered MTGA mode.")
    else:
        if "user.mtga" in modes:
            actions.mode.enable("command")
            actions.mode.disable("user.mtga")
            actions.mode.disable("sleep")
            actions.mode.disable("dictation")
            print(f"App [{app.name}] triggered command mode.")


ui.register("app_activate", on_app_switch)
