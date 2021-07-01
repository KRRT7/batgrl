import numpy as np

from ..colors import WHITE_ON_BLACK


class Widget:
    """
    A generic TUI element.

    Parameters
    ----------
    dim : tuple[int, int]
        Dimensions of widget.
    pos : tuple[int, int], default: (0, 0)
        Position of upper-left corner in parent.
    is_transparent : bool, default: False
        If true, white-space is "see-through".
    is_visible : bool, default: True
        If false, widget won't be painted.
    default_color : ColorPair, default: WHITE_ON_BLACK
        Default color of widget.
    """
    def __init__(
        self,
        dim,
        pos=(0, 0),
        *,
        is_transparent=False,
        is_visible=True,
        default_color=WHITE_ON_BLACK,
        parent=None,
    ):
        self.top, self.left = pos
        self.is_transparent = is_transparent
        self.is_visible = is_visible

        self.parent = parent
        self.children = [ ]

        self.canvas = np.full(dim, " ", dtype=object)
        self.colors = np.zeros((*dim, 6), dtype=np.uint8)
        self.colors[:, :] = default_color

        self.default_color = default_color

    def resize(self, dim):
        """
        Resize canvas. Content is preserved as much as possible.
        """
        old_canvas = self.canvas
        old_colors = self.colors

        old_h, old_w = old_canvas.shape
        h, w = dim

        copy_h = min(old_h, h)
        copy_w = min(old_w, w)

        self.canvas = np.full(dim, " ", dtype=object)
        self.colors = np.zeros((h, w, 6), dtype=np.uint8)
        self.colors[:, :] = default_color

        self.canvas[:copy_h, :copy_w] = old_canvas[:copy_h, :copy_w]
        self.colors[:copy_h, :copy_w] = old_colors[:copy_h, :copy_w]

        for child in self.children:
            child.update_geometry(dim)

    def update_geometry(self, parent_dim):
        """
        Update geometry due to a change in parent's size.
        """

    @property
    def dim(self):
        return self.canvas.shape

    @property
    def pos(self):
        return self.top, self.left

    @property
    def height(self):
        return self.canvas.shape[0]

    @property
    def width(self):
        return self.canvas.shape[1]

    @property
    def bottom(self):
        return self.top + self.height

    @property
    def right(self):
        return self.left + self.width

    @property
    def middle(self):
        return self.top + self.height // 2, self.left + self.width // 2

    @property
    def root(self):
        """
        The root widget.
        """
        return self.parent.root

    def absolute_to_relative_coords(self, coord):
        y, x = self.parent.absolute_to_relative_coords(coord)
        return y - self.top, x - self.left

    def add_widget(self, widget):
        """
        Add a child widget.
        """
        self.children.append(widget)
        widget.parent = self
        widget.update_geometry(self.dim)

    def add_widgets(self, *widgets):
        """
        Add multiple child widgets.
        """
        if len(widgets) == 1 and not isinstance(widgets[0], Widget):
            # Assume item is an iterable of widgets.
            widgets = widgets[0]

        for widget in widgets:
            self.add_widget(widget)

    def remove_widget(self, widget):
        """
        Remove widget.
        """
        self.children.remove(widget)
        widget.parent = None

    def pull_to_front(self, widget):
        """
        Move widget to end of widget stack so that it is drawn last.
        """
        self.children.remove(widget)
        self.children.append(widget)

    def walk_from_root(self):
        """
        Yield all descendents of the root widget.
        """
        yield from self.root.walk()

    def walk(self):
        """
        Yield self and all descendents.
        """
        yield self

        for child in widget.children:
            yield from child.walk()

    def _render_child(self, child):
        """
        Render child and paint child's canvas into our own.
        """
        canvas = self.canvas
        h, w = canvas.shape

        ct = child.top
        cb = child.bottom
        cl = child.left
        cr = child.right

        # Child is not visible or off-screen.
        if (
            not child.is_visible
            or ct >= h
            or cb < 0
            or cl >= w
            or cr < 0
        ):
            return

        child.render()

        ##################################################################
        # Four cases for top / bottom of child:                          #
        #     1) child top is off-screen and child bottom is off-screen. #
        #               +-------+                                        #
        #            +--| child |------------+                           #
        #            |  |       |   parent   |                           #
        #            +--|       |------------+                           #
        #               +-------+                                        #
        #     2) child top is off-screen and child bottom is on-screen.  #
        #               +-------+                                        #
        #            +--| child |------------+                           #
        #            |  +-------+   parent   |                           #
        #            +-----------------------+                           #
        #                                                                #
        #     3) child top is on-screen and child bottom is off-screen.  #
        #            +-----------------------+                           #
        #            |  +-------+   parent   |                           #
        #            +--| child |------------+                           #
        #               +-------+                                        #
        #                                                                #
        #     4) child top is on-screen and child bottom is on-screen.   #
        #            +-----------------------+                           #
        #            |  +-------+            |                           #
        #            |  | child |   parent   |                           #
        #            |  +-------+            |                           #
        #            +-----------------------+                           #
        #                                                                #
        # Similarly, by symmetry, four cases for left / right of child.  #
        ##################################################################

        # st, dt, sb, db, sl, dl, sr, dr stand for source_top, destination_top, source_bottom,
        # destination_bottom, source_left, destination_left, source_right, destination_right.
        if ct < 0:
            st = -ct
            dt = 0

            if cb >= h:
                sb = h + st
                db = h
            else:
                sb = child.height
                db = cb
        else:
            st =  0
            dt = ct

            if cb >= h:
                sb = h - dt
                db = h
            else:
                sb = child.height
                db = cb

        if cl < 0:
            sl = -cl
            dl = 0

            if cr >= w:
                sr = w + sl
                dr = w
            else:
                sr = child.width
                dr = cr
        else:
            sl = 0
            dl = cl

            if cr >= w:
                sr = w - dl
                dr = w
            else:
                sr = child.width
                dr = cr

        dest_rect = slice(dt, db), slice(dl, dr)
        source_rect = slice(st, sb), slice(sl, sr)

        if child.is_transparent:  # " " isn't painted if child is transparent.
            source = child.canvas[source_rect]
            visible = source != " "
            canvas[dest_rect][visible] = source[visible]
            self.colors[dest_rect][visible] = child.colors[source_rect][visible]
        else:
            canvas[dest_rect] = child.canvas[source_rect]
            self.colors[dest_rect] = child.colors[source_rect]

    def render(self):
        """
        Paint canvas.
        """
        render_child = self._render_child

        for child in self.children:
            render_child(child)

    def dispatch_press(self, key_press):
        """
        Try to handle key press; if not handled, dispatch to ancestors until handled.
        """
        return (
            self.on_press(key_press)
            or any(widget.dispatch_press(key_press) for widget in reversed(self.children))
        )

    def dispatch_click(self, mouse_event):
        """
        Try to handle mouse event; if not handled, dispatch to ancestors until handled.
        """
        return (
            self.on_click(mouse_event)
            or any(widget.dispatch_click(mouse_event) for widget in reversed(self.children))
        )

    def on_press(self, key_press):
        """
        Handle key press. (Handled key presses should return True else False or None).
        """

    def on_click(self, mouse_event):
        """
        Handle mouse event. (Handled mouse events should return True else False or None).
        """
