# vi:set ai sm nu ts=4 sw=4 expandtab:
class Event:
    """An Event object describes a single event in the sequence
    being played out.  It essentially represents a specific point in time,
    at which a given channel is moved to a given output level, during a
    transition period of delta time."""

    def __init__(self, unit, channel, level=0, delta=0):
        self.unit    = unit
        self.channel = channel
        self.level   = level
        self.delta   = delta

    def __eq__(self, other):
        #if not isinstance(other, Event):
            #return False

        return self.unit == other.unit \
           and self.channel == other.channel \
           and self.level == other.level \
           and self.delta == other.delta

#   def __ne__(self, other):
#       return not self.__eq__(other)

    def __repr__(self):
        return "<Event %s.%s->%.2f%% (%dmS)>" % (
            '*' if self.unit is None else self.unit.id,
            '*' if self.channel is None else self.channel,
            self.level,
            self.delta
        )
