from talon import ctrl, Module
import time

mod = Module()


def boomerang_click(
    click_type: int,
    x: int,
    y: int,
    click_time: int = 16000,  # us
):
    org_mouse_position = ctrl.mouse_pos()

    ctrl.mouse_move(x, y)
    ctrl.mouse_click(button=click_type, hold=click_time)
    time.sleep(click_time / 1000000)
    ctrl.mouse_move(org_mouse_position[0], org_mouse_position[1])


@mod.action_class
class Actions:
    def mouse_click_at(
        click_type: int,
        x: int,
        y: int,
        click_time: int,  # us
    ):
        """Move-click-move wrapper"""
        boomerang_click(
            click_type,
            x,
            y,
            click_time,
        )
