from prompt_toolkit.styles import Attrs


class _ColorCache:
    """
    Cache of escape codes or windows colors (depending on platform).
    """
    __slots__ = (
        '_attr_cache',
        '_aliases',
    )

    def __init__(self, attr_cache):
        self._attr_cache = attr_cache
        self._aliases = { }

    def color(
        self,
        fg_color,
        bg_color='',
        *,
        bold=False,
        underline=False,
        italic=False,
        blink=False,
        reverse=False,
        alias=None
    ):
        """
        Return an escape code or windows color (depending on platform) with specified styling.
        """
        aliases = self._aliases

        if fg_color in aliases:
            return aliases[fg_color]

        attr = self._attr_cache[ Attrs(fg_color, bg_color, bold, underline, italic, blink, reverse, hidden=False) ]

        if alias is not None:
            aliases[alias] = attr

        return attr
