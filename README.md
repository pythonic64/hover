# Event manager and behavior for **hover** events

### Install
Requires Kivy>=2.1.0 as support for event managers is introduced in that
version.
```sh
pip install git+https://github.com/pythonic64/hover.git
```

### Package content
- `HoverManager` - event manager which once registered will dispatch hover
  events throughout widget tree. 
- `HoverBehavior` - mixin class to be used with a widget which provides:
  - `hovered` boolean property which is `True` when hover indicator
    (e.g. mouse) is hovering over a widget
  - `on_hover_enter`, `on_hover_update`, `on_hover_leave` events which dispatch
    when hover indicator has entered, hovered over, or left a widget
- `MotionCollideBehavior` - mixin class to be used with a `StencilView` or its
  subclasses to pass hover events through its child widgets only if indicator
  is hovering over a widget or when hover event is a grabbed event

### Import
```python
from kivy_garden.hover import (
    HoverManager,
    HoverBehavior,
    MotionCollideBehavior
)
```

### Examples
See [simple_app.py](examples%2Fsimple_app.py) for a basic example on how to
register a hover manager and use hover behavior with `Label` widget.

See [large_app.py](examples%2Flarge_app.py) for an example covering more
different use cases.


### License
This software is released under the terms of the MIT License. Please see the
[LICENSE.txt](LICENSE.txt) file.
