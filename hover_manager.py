from collections import defaultdict

from kivy import platform
from kivy.eventmanager import EventManagerBase

Clock = None


class HoverManager(EventManagerBase):
    '''Dispatching hover events.
    '''

    type_ids = ('hover',)
    min_wait_time = 1/30.0

    def __init__(self, **kwargs):
        super().__init__()
        self.min_wait_time = kwargs.get('min_wait_time',
                                        HoverManager.min_wait_time)
        self._events = defaultdict(list)  # me.id -> [(me, me.grab_list[:]),]
        self._event_times = {}  # me.id -> Clock.get_time()
        self._clock_event = None

    def start(self):
        global Clock
        if not Clock:
            from kivy.clock import Clock
        if self.min_wait_time >= 0:
            self._clock_event = Clock.schedule_interval(
                self._dispatch_from_clock,
                self.min_wait_time
            )

    def stop(self):
        self._events.clear()
        self._event_times.clear()
        if self._clock_event:
            self._clock_event.cancel()
            self._clock_event = None

    def dispatch(self, etype, me):
        me_grab_list = me.grab_list[:]
        del me.grab_list[:]
        accepted = self._dispatch_to_widgets(etype, me)
        self._events[me.id].insert(0, (me, me.grab_list[:]))
        self._event_times[me.id] = Clock.get_time()
        if len(self._events[me.id]) == 2:
            _, prev_me_grab_list = self._events[me.id].pop()
            self._dispatch_to_grabbed_widgets(me, prev_me_grab_list)
        if etype == 'end':
            del self._events[me.id]
            del self._event_times[me.id]
        me.grab_list[:] = me_grab_list
        return accepted

    def _dispatch_to_widgets(self, etype, me):
        accepted = False
        me.push()
        self.transform_motion_event_2d(me)
        for widget in self.window.children[:]:
            if widget.dispatch('on_motion', etype, me):
                accepted = True
                break
        me.pop()
        return accepted

    def _dispatch_to_grabbed_widgets(self, me, prev_me_grab_list):
        # Dispatch 'end' event to widgets in prev_me_grab_list
        prev_grab_state = me.grab_state
        prev_time_end = me.time_end
        me_grab_list = me.grab_list[:]
        me.grab_list[:] = prev_me_grab_list
        me.update_time_end()
        me.grab_state = True
        for weak_widget in prev_me_grab_list:
            if weak_widget not in me_grab_list:
                widget = weak_widget()
                if not widget:
                    continue
                self._dispatch_to_widget('end', me, widget)
        me.grab_list[:] = me_grab_list
        me.grab_state = prev_grab_state
        me.time_end = prev_time_end

    def _dispatch_to_widget(self, etype, me, widget):
        root_window = widget.get_root_window()
        if root_window and root_window != widget:
            transform_me = getattr(
                root_window,
                'transform_motion_event_2d',
                self.transform_motion_event_2d
            )
            me.push()
            try:
                me = transform_me(me, widget)
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
        for me_id, item in self._events.items():
            me, _ = item[0]
            if time_now - times[me.id] < self.min_wait_time:
                continue
            events_to_update.append(me)
        for me in events_to_update:
            self.dispatch('update', me)

    def transform_motion_event_2d(self, me, widget=None):
        window = self.window
        width, height = self.get_window_size()
        me.scale_for_screen(
            width, height,
            rotation=window.rotation,
            smode=window.softinput_mode,
            kheight=window.keyboard_height
        )
        if widget is None:
            return me
        parent = widget.parent
        try:
            if parent:
                me.apply_transform_2d(parent.to_widget)
            else:
                me.apply_transform_2d(widget.to_widget)
                me.apply_transform_2d(widget.to_parent)
        except AttributeError:
            # when using inner window, an app have grab the touch
            # but app is removed. The touch can't access
            # to one of the parent. (i.e, self.parent will be None)
            # and BAM the bug happen.
            raise
        return me

    def get_window_size(self):
        if platform == 'ios' or self.window._density != 1:
            return self.window.size[:]
        return self.window.system_size[:]
