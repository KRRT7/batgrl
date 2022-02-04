from ...clamp import clamp
from .grabbable_behavior import GrabbableBehavior


class ScatterBehavior(GrabbableBehavior):
    """
    Scatter behavior allows a widget's children to be translated by dragging them.

    Parameters
    ----------
    disable_child_oob : bool, default: False
        Disallow child widgets from being translated out-of-bounds if true.
    disable_child_ptf : bool, default: False
        If true, child widgets won't be pulled-to-front when clicked.
    """
    def __init__(self, *, disable_child_oob=False, disable_child_ptf=False, **kwargs):
        super().__init__(**kwargs)
        self.disable_child_oob = disable_child_oob
        self.disable_child_ptf = disable_child_ptf

        self._grabbed_child = None

    def grab(self, mouse_event):
        for child in reversed(self.children):
            if child.collides_point(mouse_event.position):
                self._is_grabbed = True
                self._grabbed_child = child

                if not self.disable_child_ptf:
                    child.pull_to_front()

                break
        else:
            super().grab(mouse_event)

    def ungrab(self, mouse_event):
        self._grabbed_child = None
        super().ungrab(mouse_event)

    def grab_update(self, mouse_event):
        if grabbed_child := self._grabbed_child:
            dy, dx = self.mouse_dyx
            h, w = self.size
            ch, cw = grabbed_child.size
            ct, cl = grabbed_child.pos

            if self.disable_child_oob:
                grabbed_child.top = clamp(ct + dy, 0, h - ch)
                grabbed_child.left = clamp(cl + dx, 0, w - cw)
            else:
                grabbed_child.top = ct + dy
                grabbed_child.left = cl + dx
        else:
            super().grab_update(mouse_event)
