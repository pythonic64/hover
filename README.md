# Event manager and behavior for **hover** events

### Install
Requires `Kivy>=2.1.0` as support for event managers is introduced in that
version.
```sh
pip install git+https://github.com/pythonic64/hover.git
```

### Import
```python
from kivy_garden.hover import (
    HoverManager,
    HoverBehavior,
    MotionCollideBehavior
)
```

### Package content
- `HoverManager` - an event manager which once registered will dispatch hover
  events throughout the widget tree.
- `HoverBehavior` - a mixin class to be used with a widget which provides:
  - `hovered` boolean property which is `True` when hover indicator
    (e.g. mouse) is hovering over a widget.
  - `on_hover_enter`, `on_hover_update`, `on_hover_leave` events which will
    dispatch when a hover indicator has entered, hovered over, or left
    a widget.
- `MotionCollideBehavior` - a mixin class to be used with a `StencilView` or
  its subclasses to pass hover events to child widgets only if a hover
  indicator is hovering over a widget or when hover event is a grabbed event.

### Examples
See [simple_app.py](examples%2Fsimple_app.py) for a basic example on how to
register a `HoverManager` and use a `HoverBehavior` with a `Label` widget.

See [large_app.py](examples%2Flarge_app.py) for an example covering more
different use cases.

### License
This software is released under the terms of the MIT License. Please see the
[LICENSE.txt](LICENSE.txt) file.
