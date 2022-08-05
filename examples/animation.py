from pathlib import Path

from nurses_2.app import App
from nurses_2.widgets.widget_data_structures import Anchor
from nurses_2.widgets.animation import Animation, Interpolation

THIS_DIR = Path(__file__).parent
PATH_TO_FRAMES_DIR = THIS_DIR / "frames" / "caveman"


class MyApp(App):
    async def on_start(self):
        animation = Animation(
            size_hint=(.5, .5),
            anchor=Anchor.CENTER,
            pos_hint=(.5, .5),
            path=PATH_TO_FRAMES_DIR,
            interpolation=Interpolation.NEAREST,
        )

        self.add_widget(animation)
        animation.play()


MyApp(title="Animation Example").run()
