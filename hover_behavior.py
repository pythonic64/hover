from kivy.eventmanager import MODE_DONT_DISPATCH
from kivy.properties import AliasProperty, DictProperty, OptionProperty


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
