from collections import defaultdict

from kivy.eventmanager import EventManagerBase, MODE_DONT_DISPATCH
from kivy.properties import AliasProperty, DictProperty, OptionProperty

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
        self._events = defaultdict(list)  # me.uid -> [(me, me.grab_list[:]),]
        self._event_times = {}  # me.uid -> Clock.get_time()
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
        self._events[me.uid].insert(0, (me, me.grab_list[:]))
        self._event_times[me.uid] = Clock.get_time()
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
            if time_now - times[me.uid] < self.min_wait_time:
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

    def _get_hovered(self):
        return bool(self.hover_ids)

    hovered = AliasProperty(_get_hovered, bind=['hover_ids'], cache=True)
    hover_ids = DictProperty()
    hover_mode = OptionProperty('default', options=['default', 'all', 'self'])

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


class MotionCollideBehavior(object):

    def on_motion(self, etype, me):
        if me.grab_current is self \
                or 'pos' in me.profile and self.collide_point(*me.pos):
            return super().on_motion(etype, me)
