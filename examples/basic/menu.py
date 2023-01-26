from nurses_2.app import App
from nurses_2.widgets.button import Button
from nurses_2.widgets.menu import Menu
from nurses_2.widgets.text_widget import TextWidget

class MyApp(App):
    async def on_start(self):
        label = TextWidget(size=(1, 50))

        def add_label(text):
            def inner():
                label.add_str(f"{text:<50}"[:50])
            return inner

        def add_label_toggle(text):
            def inner(toggle_state):
                label.add_str(f"{f'{text} {toggle_state}':<50}"[:50])
            return inner

        # These "keybinds" aren't implemented.
        menu_dict = {
            ("New File", "Ctrl+N"): add_label("New File"),
            ("Open File...", "Ctrl+O"): add_label("Open File..."),
            ("Save", "Ctrl+S"): add_label("Save"),
            ("Save as...", "Ctrl+Shift+S"): add_label("Save as..."),
            ("Preferences", ""): {
                ("Settings", "Ctrl+,"): add_label("Settings"),
                ("Keyboard Shortcuts", "Ctrl+K Ctrl+S"): add_label("Keyboard Shortcuts"),
                ("Toggle Item 1", ""): add_label_toggle("Toggle Item 1"),
                ("Toggle Item 2", ""): add_label_toggle("Toggle Item 2"),
            },
        }

        self.add_widget(label)
        self.add_widgets(Menu.from_dict_of_dicts(menu_dict, pos=(2, 0)))

        root_menu = self.children[-1]
        root_menu.is_enabled = False
        root_menu.children[1].item_disabled = True

        def toggle_root_menu():
            if root_menu.is_enabled:
                root_menu.close_menu()
            else:
                root_menu.open_menu()

        self.add_widget(Button(label="File", callback=toggle_root_menu, pos=(1, 0), size=(1, 6)))


MyApp(title="Menu Example").run()
