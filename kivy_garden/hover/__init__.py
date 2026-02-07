"""
Hover manager and behavior
==========================

This module defines three classes to handle hover events:

1. Class :class:`HoverManager` provides dispatching of hover events to widgets
   in the `Window`'s :attr:`~kivy.core.window.WindowBase.children` list.
2. Class :class:`HoverBehavior` handles hover events for all widgets who
   inherit from it.
3. Class :class:`HoverCollideBehavior` provides filtering of hover events in
   such way that only events for which currently grabbed widget is the widget
   itself or events which collide with the widget are passed through the
   :meth:`~kivy.uix.widget.Widget.on_motion` method.

A hover event is an instance of :class:`~kivy.input.motionevent.MotionEvent`
class with its :attr:`~kivy.input.motionevent.MotionEvent.type_id` set to
"hover".

HoverManager
------------

:class:`HoverManager` is responsible for dispatching of hover events to widgets
in the `Window`'s :attr:`~kivy.core.window.WindowBase.children` list. Widgets
must register for hover events using
:meth:`~kivy.uix.widget.Widget.register_for_motion_event` to be able to receive
those events in the :meth:`~kivy.uix.widget.Widget.on_motion` method.

For your app to use a hover manager, you must register it with
:meth:`~kivy.core.window.WindowBase.register_event_manager` when app starts
and then unregister it with
:meth:`~kivy.core.window.WindowBase.unregister_event_manager` when app stops.

Example of how to register/unregister a hover manager::

    from kivy.app import App

    from kivy_garden.hover import HoverManager

    class HoverApp(App):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.hover_manager = HoverManager()

        def on_start(self):
            super().on_start()
            self.root_window.register_event_manager(self.hover_manager)

        def on_stop(self):
            super().on_stop()
            self.root_window.unregister_event_manager(self.hover_manager)

Manager expects every widget to always grab the event, if they want to receive
event type "end" for that same event while the event is in the grabbed state.
To grab an event use :meth:`~kivy.input.motionevent.MotionEvent.grab` and to
ungrab it use :meth:`~kivy.input.motionevent.MotionEvent.ungrab`. Manager
manipulates event's :attr:`~kivy.input.motionevent.MotionEvent.grab_list`
when dispatching an event to widgets, which is needed to ensure that widgets
receive "end" event type for the same event. It will also restore the original
:attr:`~kivy.input.motionevent.MotionEvent.grab_list`, received in its
:meth:`~kivy.eventmanager.EventManagerBase.dispatch` method, after the dispatch
is done.

Event dispatching works in the following way:

1. If an event is received for the first time, manager will dispatch it to all
   widgets in the :attr:`~kivy.core.window.WindowBase.children` list and
   internally store the event itself, copy of the new
   :attr:`~kivy.input.motionevent.MotionEvent.grab_list`, and the time of the
   dispatch. Values are stored for every event, per its
   :attr:`~kivy.input.motionevent.MotionEvent.uid`.
2. When the same event is received for the second time, step 1. is done again,
   and then follows the dispatch to the widgets who grabbed that same event.
   Manager will dispatch event type "end" to the widgets who are found in the
   previously stored :attr:`~kivy.input.motionevent.MotionEvent.grab_list` and
   not found in the event's current `grab_list`. This way is ensured that
   widgets can handle their state if they didn't receive "update" or "begin"
   event type in the second time dispatch.
3. If a hover event is static (its position doesn't change) and
   :attr:`HoverManager.event_repeat_timeout` is greater or equal to 0, manager
   will dispatch an event type "update" to all events stored in step 1. using
   :attr:`HoverManager.event_repeat_timeout` as timeout between the static
   events.
4. On the event type "end", data stored in the step 1. is removed from the
   manager's internal storage.

See :class:`HoverManager` for details.

HoverBehavior
-------------

:class:`HoverBehavior` is a `mixin <https://en.wikipedia.org/wiki/Mixin>`_
class which handles hover events received in the
:meth:`~kivy.uix.widget.Widget.on_motion` method. It depends on
:class:`HoverManager` and its way of dispatching of hover events - events with
:attr:`~kivy.input.motionevent.MotionEvent.type_id` set to "hover". Therefore,
for :class:`HoverBehavior` to work,
:class:`~kivy.eventmanager.hover.HoverManager` must be registered in
:class:`~kivy.core.window.WindowBase`.

For an overview of behaviors, please refer to the :mod:`~kivy.uix.behaviors`
documentation.

As a mixin class, :class:`HoverBehavior` must be combined with other widgets::

    class HoverWidget(HoverBehavior, Widget):
        pass

Behavior supports multi-hover - if one or multiple hover events are hovering
over a widget, then its property :attr:`HoverBehavior.hovered` will be set to
`True`.

Example app showing a widget which when hovered with a mouse indicator will
change color from gray to green::

    from kivy.app import App
    from kivy.lang import Builder
    from kivy.uix.widget import Widget

    from kivy_garden.hover import HoverBehavior, HoverManager

    Builder.load_string(\"""
    <RootWidget>:
        canvas.before:
            Color:
                rgba: [0, 0.5, 0, 1] if self.hovered else [0.5, 0.5, 0.5, 1]
            Rectangle:
                pos: self.pos
                size: self.size
    \""")


    class RootWidget(HoverBehavior, Widget):
        pass


    class HoverBehaviorApp(App):

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.hover_manager = HoverManager()

        def build(self):
            return RootWidget(size_hint=(0.5, 0.5),
                              pos_hint={'center_x': 0.5, 'center_y': 0.5})

        def on_start(self):
            super().on_start()
            self.root_window.register_event_manager(self.hover_manager)

        def on_stop(self):
            super().on_stop()
            self.root_window.unregister_event_manager(self.hover_manager)


    if __name__ == '__main__':
        HoverBehaviorApp().run()

See :class:`HoverBehavior` for details.

HoverCollideBehavior
--------------------

:class:`HoverCollideBehavior` is a
`mixin <https://en.wikipedia.org/wiki/Mixin>`_ class which filters hover events
which are currently grabbed by the widget itself or events which collide with
the widget.

For an overview of behaviors, please refer to the :mod:`~kivy.uix.behaviors`
documentation.

:class:`HoverCollideBehavior` is meant to be used with
:class:`~kivy.uix.stencilview.StencilView` or its subclasses so that hover
events (events with :attr:`~kivy.input.motionevent.MotionEvent.type_id` set to
"hover") don't get handled when their position is outside the view's bounding
box.

Example of using :class:`HoverCollideBehavior` with
:class:`~kivy.uix.recycleview.RecycleView`::

    from kivy.uix.recycleview import RecycleView

    from kivy_garden.hover import HoverCollideBehavior


    class HoverRecycleView(HoverCollideBehavior, RecycleView):
        pass

:class:`HoverCollideBehavior` overrides
:meth:`~kivy.uix.widget.Widget.on_motion` to add event filtering::

    class HoverCollideBehavior(object):

        def on_motion(self, etype, me):
            if me.type_id != 'hover':
                return super().on_motion(etype, me)
            if me.grab_current is self or self.collide_point(*me.pos):
                return super().on_motion(etype, me)
"""

from collections import defaultdict

from kivy.eventmanager import EventManagerBase, MODE_DONT_DISPATCH
from kivy.properties import AliasProperty, DictProperty, OptionProperty

Clock = None


class HoverManager(EventManagerBase):
    """Manager for dispatching hover events to widgets in the window children
    list.

    When registered, a manager will receive all events with `type_id` set to
    "hover", transform them to match :attr:`window` size and then dispatch them
    through the `window.children` list using the `on_motion` event.

    To handle the case when the hover event position did not change within
    :attr:`event_repeat_timeout` seconds, manager will re-dispatch the event
    with all delta values set to 0, so that widgets can re-handle the event.
    This is useful for the case when a mouse is used to scroll a recyclable
    list of widgets, but the mouse indicator position is not changing.

    When a manager is stopped and if there are widgets stored in its internal
    storage who grabbed hover events, then a manager will dispatch event type
    "end" to all those widgets, so that they can update their internal state.
    """

    type_ids = ('hover',)

    event_repeat_timeout = 1 / 30.0
    """Minimum wait time to repeat existing static hover events and it defaults
    to `1/30.0` seconds. Negative value will turn off the feature.

    To change the default value use `event_repeat_timeout` keyword while making
    a manager instance or set it directly after the instance is made. Changing
    the value after the manager has started will have no effect.
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.event_repeat_timeout = kwargs.get(
            'event_repeat_timeout',
            HoverManager.event_repeat_timeout
        )
        self._events = defaultdict(list)  # me.uid -> [(me, me.grab_list[:]),]
        self._event_times = {}  # me.uid -> Clock.get_time()
        self._clock_event = None

    def start(self):
        if self.event_repeat_timeout >= 0:
            global Clock
            if not Clock:
                from kivy.clock import Clock
            if not self._clock_event:
                self._clock_event = Clock.schedule_interval(
                    self._dispatch_from_clock,
                    self.event_repeat_timeout
                )

    def stop(self):
        for me_list in self._events.values():
            me, grab_list = me_list[0]
            self._dispatch_to_grabbed_widgets(me, grab_list)
        self._events.clear()
        self._event_times.clear()
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None

    def dispatch(self, etype, me):
        me_grab_list = me.grab_list[:]
        del me.grab_list[:]
        accepted = self._dispatch_to_widgets(etype, me)
        self._events[me.uid].insert(0, (me, me.grab_list[:]))
        self._event_times[me.uid] = Clock.get_time() if Clock else 0
        if len(self._events[me.uid]) == 2:
            _, prev_me_grab_list = self._events[me.uid].pop()
            self._dispatch_to_grabbed_widgets(me, prev_me_grab_list)
        if etype == 'end':
            del self._events[me.uid]
            del self._event_times[me.uid]
        me.grab_list[:] = me_grab_list
        return accepted

    def _dispatch_to_widgets(self, etype, me):
        accepted = False
        me.push()
        self.window.transform_motion_event_2d(me)
        for widget in self.window.children[:]:
            if widget.dispatch('on_motion', etype, me):
                accepted = True
                break
        me.pop()
        return accepted

    def _dispatch_to_grabbed_widgets(self, me, prev_me_grab_list):
        prev_grab_state = me.grab_state
        prev_time_end = me.time_end
        me_grab_list = me.grab_list[:]
        me.grab_list[:] = prev_me_grab_list
        me.update_time_end()
        me.grab_state = True
        for weak_widget in prev_me_grab_list:
            if weak_widget not in me_grab_list:
                widget = weak_widget()
                if widget:
                    self._dispatch_to_widget('end', me, widget)
        me.grab_list[:] = me_grab_list
        me.grab_state = prev_grab_state
        me.time_end = prev_time_end

    def _dispatch_to_widget(self, etype, me, widget):
        root_window = widget.get_root_window()
        if root_window and root_window != widget:
            me.push()
            try:
                self.window.transform_motion_event_2d(me, widget)
            except AttributeError:
                me.pop()
                return
        prev_grab_current = me.grab_current
        me.grab_current = widget
        widget._context.push()
        if widget._context.sandbox:
            with widget._context.sandbox:
                widget.dispatch('on_motion', etype, me)
        else:
            widget.dispatch('on_motion', etype, me)
        widget._context.pop()
        me.grab_current = prev_grab_current
        if root_window and root_window != widget:
            me.pop()

    def _dispatch_from_clock(self, *args):
        times = self._event_times
        time_now = Clock.get_time()
        events_to_update = []
        for me_id, items in self._events.items():
            me, _ = items[0]
            if time_now - times[me.uid] < self.event_repeat_timeout:
                continue
            events_to_update.append(me)
        for me in events_to_update:
            psx, psy, psz = me.psx, me.psy, me.psz
            dsx, dsy, dsz = me.dsx, me.dsy, me.dsz
            me.psx, me.psy, me.psz = me.sx, me.sy, me.sz
            me.dsx = me.dsy = me.dsz = 0.0
            self.dispatch('update', me)
            me.psx, me.psy, me.psz = psx, psy, psz
            me.dsx, me.dsy, me.dsz = dsx, dsy, dsz


class HoverBehavior(object):
    """HoverBehavior `mixin <https://en.wikipedia.org/wiki/Mixin>`_ to handle
    hover events.

    Behavior will register widget to receive hover events (events with
    `type_id` set to "hover") and update attributes :attr:`hovered` and
    :attr:`hover_ids` depending on the received events.

    :Events:
        `on_hover_event`: `(etype, me)`
            Dispatched when this widget receives a hover event.
        `on_hover_enter`: `(me, )`
            Dispatched when a hover event collides with this widget for the
            first time.
        `on_hover_update`: `(me, )`
            Dispatched when a hover event position has changed, but it's still
            within this widget.
        `on_hover_leave`: `(me, )`
            Dispatched when a hover event is no longer within this widget or
            when an event type "end" is received.
    """

    def _get_hovered(self):
        return bool(self.hover_ids)

    hovered = AliasProperty(_get_hovered, bind=['hover_ids'], cache=True)
    """Indicates if this widget is hovered by at least one hover event.

    :attr:`hovered` is a :class:`~kivy.properties.AliasProperty`.
    """

    hover_ids = DictProperty()
    """Holds hover `event.uid` to `event.pos` values.

    :attr:`hover_ids` is a :class:`~kivy.properties.DictProperty`.
    """

    hover_mode = OptionProperty('default', options=['default', 'all', 'self'])
    """How this widget will dispatch received hover events.

    Options:

    - ``'default'``: Dispatch to `children` first and if none of the child
    widgets accepted the event (by returning `True`), then dispatch
    `on_hover_event` so that this widget can try to handle it.

    - ``'all'``: Same as `default`, but always dispatch `on_hover_event`.

    - ``'self'``: Don't dispatch to `children`, but dispatch `on_hover_event`.
    """

    __events__ = ('on_hover_event', 'on_hover_enter', 'on_hover_update',
                  'on_hover_leave')

    def __init__(self, **kwargs):
        self.register_for_motion_event('hover')
        super().__init__(**kwargs)

    def on_motion(self, etype, me):
        if not (me.type_id == 'hover' and 'pos' in me.profile):
            return super().on_motion(etype, me)
        if self.hover_mode == 'default':
            if super().on_motion(etype, me):
                return True
            return self.dispatch('on_hover_event', etype, me)
        prev_mode = me.dispatch_mode
        if self.hover_mode == 'self':
            me.dispatch_mode = MODE_DONT_DISPATCH
        accepted = super().on_motion(etype, me)
        accepted = self.dispatch('on_hover_event', etype, me) or accepted
        me.dispatch_mode = prev_mode
        return accepted

    def on_hover_event(self, etype, me):
        """Called when a hover event is received.

        This method will test if event collides with this widget using
        :meth:`collide_point` and dispatch `on_hover_enter`, `on_hover_update`
        or `on_hover_leave` events.

        :Parameters:
            `etype`: `str`
                Event type, one of "begin", "update" or "end"
            `me`: :class:`~kivy.input.motionevent.MotionEvent`
                Hover motion event
        """
        if etype == 'update' or etype == 'begin':
            if me.grab_current is self:
                return True
            if self.disabled and self.collide_point(*me.pos):
                return True
            if self.collide_point(*me.pos):
                me.grab(self)
                if me.uid not in self.hover_ids:
                    self.hover_ids[me.uid] = me.pos
                    self.dispatch('on_hover_enter', me)
                elif self.hover_ids[me.uid] != me.pos:
                    self.hover_ids[me.uid] = me.pos
                    self.dispatch('on_hover_update', me)
                return True
        elif etype == 'end':
            if me.grab_current is self:
                self.hover_ids.pop(me.uid)
                me.ungrab(self)
                self.dispatch('on_hover_leave', me)
                return True
            if self.disabled and self.collide_point(*me.pos):
                return True

    def on_hover_enter(self, me):
        pass

    def on_hover_update(self, me):
        pass

    def on_hover_leave(self, me):
        pass


class HoverCollideBehavior(object):
    """HoverCollideBehavior `mixin <https://en.wikipedia.org/wiki/Mixin>`_
    overrides :meth:`~kivy.uix.widget.Widget.on_motion` to filter-out hover
    events which do not collide with the widget or hover events which are not
    grabbed events.

    It's recommended to use this behavior with
    :class:`~kivy.uix.stencilview.StencilView` or its subclasses
    (:class:`~kivy.uix.recycleview.RecycleView`,
    :class:`~kivy.uix.scrollview.ScrollView`, etc.), so that hover events don't
    get handled when outside of stencil view.
    """

    def on_motion(self, etype, me):
        if me.type_id != 'hover':
            return super().on_motion(etype, me)
        if me.grab_current is self or self.collide_point(*me.pos):
            return super().on_motion(etype, me)


MotionCollideBehavior = HoverCollideBehavior
""":class:`MotionCollideBehavior` is equal to
:class:`HoverCollideBehavior`, but it's kept for compatibility with version
`0.1.0`. It will be removed in version `0.3.0`.  
"""