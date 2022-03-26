from typing import Callable

from wcwidth import wcswidth

from .behaviors.themable import Themable
from .behaviors.toggle_button_behavior import ButtonState, ToggleState, ToggleButtonBehavior
from .text_widget import TextWidget, Anchor
from .widget import Widget

CHECK_OFF = "□ "
CHECK_ON = "▣ "
TOGGLE_OFF = "◯ "
TOGGLE_ON = "◉ "


class ToggleButton(Themable, ToggleButtonBehavior, Widget):
    """
    A toggle button widget. Without a group, a toggle button acts like a checkbox.
    With a group it behaves like a radio button (only a single button in a group is
    allowed to be in the "on" state).

    Parameters
    ----------
    label : str, default: ""
        Toggle button label.
    callback : Callable[[ToggleState], None], default: lambda: None
        Called when toggle state changes. The new state is provided as first argument.
    """
    def __init__(
        self,
        *,
        background_char=" ",
        label: str="",
        callback: Callable[[ToggleState], None]=lambda: None,
        **kwargs,
    ):
        self.normal_color_pair = (0, ) * 6  # Temporary assignment

        self._label_widget = TextWidget(pos_hint=(.5, 0), anchor=Anchor.LEFT_CENTER)

        self.callback = callback  # This must be set before `super().__init__`.

        super().__init__(background_char=background_char, **kwargs)

        self.add_widget(self._label_widget)

        self.label = label

        self.update_theme()

    def update_theme(self):
        ct = self.color_theme

        self.normal_color_pair = ct.primary_color_pair
        self.hover_color_pair = ct.primary_light_color_pair
        self.down_color_pair = ct.secondary_color_pair

        match self.state:
            case ButtonState.NORMAL:
                self.update_normal()
            case ButtonState.HOVER:
                self.update_hover()
            case ButtonState.DOWN:
                self.update_down()

    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, label: str):
        self._label = label

        if self.group is None:
            if self.toggle_state is ToggleState.OFF:
                prefix = CHECK_OFF
            else:
                prefix = CHECK_ON
        else:
            if self.toggle_state is ToggleState.OFF:
                prefix = TOGGLE_OFF
            else:
                prefix = TOGGLE_ON

        text = prefix + label
        self._label_widget.resize((1, wcswidth(text)))
        self._label_widget.update_geometry()
        self._label_widget.add_text(text)

    def update_hover(self):
        self.background_color_pair = self._label_widget.colors[:] = self.hover_color_pair

    def update_down(self):
        self.background_color_pair = self._label_widget.colors[:] = self.down_color_pair

    def update_normal(self):
        self.background_color_pair = self._label_widget.colors[:] = self.normal_color_pair

    def on_toggle(self):
        if self._label_widget.parent is not None:  # This will be false during initialization.
            self.label = self.label  # Update radio button/checkbox
        self.callback(self.toggle_state)
