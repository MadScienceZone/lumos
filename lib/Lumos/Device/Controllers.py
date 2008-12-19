# vi:set ai sm nu ts=4 sw=4 expandtab:
#
from Lumos.Device.LynX10ControllerUnit import LynX10ControllerUnit
from Lumos.Device.SSR48ControllerUnit  import SSR48ControllerUnit
from Lumos.Device.FirecrackerX10ControllerUnit import FirecrackerX10ControllerUnit
from Lumos.Device.RenardControllerUnit import RenardControllerUnit
from Lumos.Device.Olsen595ControllerUnit import Olsen595ControllerUnit
from Lumos.Device.FireGodControllerUnit import FireGodControllerUnit
#
# List of supported controller device drivers, mapping the name as used
# in the show.conf file (and other interfaces) to the actual class
# implementing the driver for that device.
#
supported_controller_types = {
    'lynx10':   LynX10ControllerUnit,
    '48ssr':    SSR48ControllerUnit,
    'cm17a':    FirecrackerX10ControllerUnit,
    'renard':   RenardControllerUnit,
    'olsen595': Olsen595ControllerUnit,
    'firegod':  FireGodControllerUnit,
}

def controller_unit_factory(type, **kwargs):
    """
    Create and return a controller object of the requested type.
    Usage: controller_unit_factory(typename, [args...])
    where: typename is one of the defined keywords for a device
           type (as usable in the show configuration file), and
           [args] are whatever constructor arguments are applicable
           to that type of device class.
    """

    type = type.lower().strip()
    if type not in supported_controller_types:
        raise ValueError, "Invalid controller unit type '%s'" % type

    return supported_controller_types[type](**kwargs)
