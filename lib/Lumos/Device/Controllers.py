from LynX10ControllerUnit         import LynX10ControllerUnit
from FirecrackerX10ControllerUnit import FirecrackerX10ControllerUnit
from SSR48ControllerUnit          import SSR48ControllerUnit
#
# List of supported controller device drivers, mapping the name as used
# in the show.conf file (and other interfaces) to the actual class
# implementing the driver for that device.
#
supported_controller_types = {
    'lynx10': LynX10ControllerUnit,
    '48ssr':  SSR48ControllerUnit,
    'cm17a':  FirecrackerX10ControllerUnit
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
