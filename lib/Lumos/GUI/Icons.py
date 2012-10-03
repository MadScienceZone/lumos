# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS GUI ICONS
#
# Lumos Light Orchestration System
# Copyright (c) 2012 by Steven L. Willoughby, Aloha,
# Oregon, USA.  All Rights Reserved.  Licensed under the Open Software
# License version 3.0.
#
# This product is provided for educational, experimental or personal
# interest use, in accordance with the terms and conditions of the
# aforementioned license agreement, ON AN "AS IS" BASIS AND WITHOUT
# WARRANTY, EITHER EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION,
# THE WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A
# PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY OF THE ORIGINAL
# WORK IS WITH YOU.  (See the license agreement for full details, 
# including disclaimer of warranty and limitation of liability.)
#
# Under no curcumstances is this product intended to be used where the
# safety of any person, animal, or property depends upon, or is at
# risk of any kind from, the correct operation of this software or
# the hardware devices which it controls.
#
# USE THIS PRODUCT AT YOUR OWN RISK.
########################################################################
import Tkinter

# by holding these images in global variables we ensure they're created
# once and reused, AND that a reference to them is held in play at all
# times.

loaded = False
def init():
    global loaded
    if loaded: return

    global icon_accept
    icon_accept = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOeGAB1sGh5uGh5wGh5xGh9xGx5zGh94Gx56Gx96Gx5/Gx+DGyCIHCCKGy2WHC+WHDKdHUyXPU6bQVKgQkKpH0KrH0KtH16pSEu0JmSwTFK5K1K7LVS7LVS9MVW+NFXANG61WGy2Vm+1WG+1WW23V2q5UFnCNnC4WXS3W3S3XFvCOXG5W3K5W3O6XH23Zn+4aXy6ZHe8YHC/V3G+X328ZnDBY2/CYXTCWX2+Z2/DYW7EYW7EYnnBZHTDZHHEY27FY4O+bX7BaW/GZHDHZXPHZnLIaHTIaHXIaIfCcnbJaX7Hb3nJa3bKaoXFdYnEdn/KcHrMbYDKc4fJeYvIeIDMcpbHg4POd5rHh5bLhprKh5DOf5jLhpfMhZjMh5bNiJnNip3Oi5nQjJnRi5/SkZrUjZvXkavSm6HWlZ3YkqvTm6HXlaPXlq7Xoa/XoLPZpbTZpbTapq7cpa/cprLbqLXbqLHdp7TdqrTfrLXfrLXhrrfhr7fhsL7jtr/juMDkudns1Nbu0ub04+336/H58PT68vz9+/3+/f///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjEAP8JHEiwoMF/KThoyHBwYAkbauDAMUOCwkEPWfKcqVLlDB4pDwp2yILnyRIiRYwosdOkAcEYeZ4QEeJDR489Se5YGLghDRkkQXLgqNHHEKAwXxYIvEBnyhA9f2jwMUQIDJA1CQRWiOMEiiBDgah2UXGDzQGBE8SM4RFlkKFCV0as2GLFwEAMdXbIYOLHC4gPKN5EIOjgiBwYLEyICHGijYsBBRn8mMNlxgstbloAOKhAAhY0ZahACNBQIIICAgiUXj0wIAA7
''')

    global icon_add
    icon_add = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAMZ2ADSBLDSCLDeELzmFMDyHMj2INECJNkKLOESMOkKNNkOPOEeOPFOWRVCZQVaYSFeeRV2cTV+eUGajVmmlWGWrVWirU2uqWGyqWmqsW3WsYXeuY3qvZW61WG+1WG+1WXyxZ3i0ZH6yaXC4WXS3W3S3XICzanK5W3O6XIO1bYS2bn25any6ZH25a3e8YHG+X3+5bYe4cH28Zoe4cXm9bnDBY32+Z3nBZH7BaXzDa4m+eI2+e3rGa4rCeX7Hb4/CfYbJepLFgIbJfInIf4HMdYXNeZfHhYzLgY7MhIrPfZjLhpfMhZPNiJjMh5jMio7Sg5nRi5TTipbTiaTOlJXUipbUi6bPlpfVi6bQlp3YkqrUnavUnKDZlaDZlqXbm7PZpbTZpbTaprLbqLfaqrXbqLPdqbTdqq/fpa/fprbdrLvcr7jdr7XfrLfgr77itr3ktsXowMvmw87pydTrz9fu0tzx2ODy3P///////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAQABAAAAengH+Cg4SFhn8pJR8ah4MyUnBycWovE4cwaXVuXVxmbzwRhTBidFhLR1RTTmwsDoRFc1tQQnZ2RDg9aw+DKGhnRkEztRgtJ09AC4IhbVY/tc92IjdZB4IbZEhD0LUiNVoFghlNUTs0FNwiJko6A4MVZTYuLdwcJGAKhBIqYcUiHh0jvFwIUAgCiDFMYqxI8sUCgEMMGvi4UiVHgoeN/iAwQEBAxo+DAgEAOw==
''')

    global icon_arrow_down
    icon_arrow_down = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAKU7ACVkISZlIidmIyhoJClpJSxtJzN1LTZ6MT2CNj6DOEOKPEWMPUqMRUuNRk2PSEqSQlCSS0yVRVCaSFeZUVWaTlOeSleiTlmmUF2qU1+tVmytZWOyWWW0W2i4XWq7X22+Ym/AY3DCZXy/dnLFZn7AeXPGZ4DBenTHaILCfYXDfofFgYnGgozHhY7Jh5HKipPLi5XMjpjOkJrPk5zQlJ/SlqHTmKPUmqXUnKfWnqnXoKvYov///////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAD8ALAAAAAAQABAAAAZSwJ9wSCwaf6dS6HMsjnS5TpMIwt0206HHVsNkhRzazPL9ZWQxSfkCez3KFVdLUY6wVogyRZU6ZB8LGigmEAUDUwkTJCINAl8GDgwBZT8EAJRZQQA7
''')

    global icon_arrow_left
    icon_arrow_left = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAKUsACBeHSRjISlpJS9wKjV4LzuANUKIO0mRQU+ZR1ahTVypU2SqW2KxWGi4XXi9cnu+cXy+dnHDZX7AeIDBenTHaIPBeoLCfYTDfofFgYnGgobIe4fJfIvHhY7Jh4rMf5DKiYvNgJPLi5XMjpjOkJrPk53QlJ/SlqHTmKPUmqXVnKfWnqvYov///////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAD8ALAAAAAAQABAAAAZKwJ9wSCwaj8ikcimkMJuRJwW0aTAUCcTBUCAMmp6VCmUiiT4cjEUiEEY0qVNpFOpkLhOIIzBsPCoLWlxeAgEARFhPQgiKjY6PT0EAOw==
''')

    global icon_arrow_refresh
    icon_arrow_refresh = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAMZXACNhHyRjICVlIidmIyloJCprJixtJzJ0LDN2Ljd7Mjp+NDyANT6DN0CGOUKIO0SLPUqLRUyNR0mRQU+QSVGSS02WRVSVTk+ZR1aXUFGbSVOeS1WhTVejTmKiW1qmUGOkXWWnXl6rVGioYF+tVmiqYWusY2ytZW6wZmW0W2e2XHazb2i5Xmq7X2y8YG2+Ym7AY3y9c36/dYG+en/BeYHCd4LCeoPDeYPEeYXEfonDgIfEgIvDg4rEg4XHe4nGgovGg47GhovHhY3Hho7JhY/Jh4/JiJDKiJHKipLKiZTLjJXMjZbNj5jOj5nPkJrPkpzPlJzQlJ7RlZ/Rlp/Sl6HSmKTUm6fXnv///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAQABAAAAeLgH+Cg4SFhoQXEoeCKCMeGhUiHQqGKzZIUFFNSUQ6FgaEKUNVTE5KRj84MxEChDFUT0IgDQoIExABhCE5SjwPDIMDAIUbiQ4Li8nExsiELyyDkEBFKgiELj00IRwZJTtEPhiELTdWVVOmRjU4HwWEKDBST0tHQTImFASGHCckvwkHQC2S4ECZQUKBAAA7
''')

    global icon_arrow_right
    icon_arrow_right = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAKUrACRjISlpJTV4LzuANUKIO0WIP0mLREqMRUmRQVCRSk+ZR1ydVVahTV6hWWKjWlypU2KxWGi4XW2+YXy+dnHDZYDBenTHaILCfYTDfofFgYnGgovHhY7Jh5DKiZPLi5XMjpjOkJrPk53QlJ/SlqHTmKPUmqXVnKfWnqnXoKvYoq7apf///////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAD8ALAAAAAAQABAAAAZLwJ9wSCwaj8ikcplUMIcIAtFioUgikAdDgXAsBEOLKnUqjUKfziZzSQSEFJSJJAJ5OBpMZXIACK9ZW1EDBQ0GfkwBiEyLT46PkEdBADs=
''')

    global icon_arrow_switch
    icon_arrow_switch = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAMZ7ABdEFBdFFRhFFRhGFhpJFxxLGSNWHyVYISleJCxiJy1jKC9nKjBoKjptNjZyMDN2LjR3LjV4Lzx5Njd7MT16Njp+NDuANUt9R0t+SECFOUGGOkOGO0+CS0OKPESLPUyOQ1OLTlaKUkmRQVSOTVqOVE2WRVKZSVCaSFObSliZUVGcSVmaU1KdSmKYXVmdUFSfS12cVVudVVWgTFueU16fV1eiTmecY1ejTlikT1mlUGCmWF+nVVypU12pUl2qVF+rVGeoX2CtVWmqY2KvVmOwV2qtYWutY2SyWG6vZWW0WWa1WnOxbHe0cXuzc3u4c4G2eYO2fIS3fYS8e4u+hYfEgIrGg4vHhI3Iho/Jh5HJiZDKiZLKjpLLi5TLjJTLkJXMjpnLkZbMkZfMkpbNjpjMk5nOlJnPkJvOlp3PmJ7PmKPPmqLSnKfToKbUoKjUoq/Xp7HaqrTcrbrfs7zgtL7htr7ht7/it8DiuMDjucHjucLjuv///////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAQABAAAAengH+Cg4SFhoY1h4oqJYNKj0dDP38+OTI6TkAdgkp6eXd1YEhFWWZfXFg0FX9JeHZ0c3JqLmNdWldVKxF/REE9O1JvcTBLMxoxKRCGJk1wTxuCDg+HJx9sbhSCDAmDPDgvKEYwUG1RIAskIQaCN6dYVkwja2loZ2RhHAV/LLdVVEISWkwpI8bLFgwD/pQQ4SGDhQl/FCA40MDGBQGKChEIkLEQgI4dAwEAOw==
''')

    global icon_arrow_up
    icon_arrow_up = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAKU7ACJgHiVkISZlIilpJStrJi1uKDByKzN1LTZ6MTl9Mz2CNj+FOUOKPEaNP0qSQkyVRVCaSFOeSlikT1mmUF6sVV+tVmWsXWW0W2i4XW6/Yni9cnq9dHDCZXHDZXy/dnLEZn3Ac3LFZn7AeXPGZ4DBeoLCfYXDfobDfYPGeYfFgYnGgoXIe4zHhYfKfIjKfo7Jh5HKipPLi5XMjpjOkJrPk5zQlJ/SlqHTmKPUmqXUnKfWnv///////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAD8ALAAAAAAQABAAAAZRwJ9wSCwahSPO0RhyrTDL4aely4Eo0U4GhbudJJHo72KrWcTCCm0GQf8mspjDHYG9GO4HS6VwN1ImCG4LJSQGbgkiHgRuBxsaAm4FAwEAbmJBADs=
''')

    global icon_box
    icon_box = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOeiAHdMFXpMEnhNFXlNFnlOFnpOFn5OEntPFnxQF31QF35RF4JRFH9SGIBTGIFTGIJUGYNUGYdUFIRVGYVVGoZWGotWFYdXGohYG4lZG4pZHY5ZFYtaHIxbHI1bHJJbFo5cHY9cHY9dHY9dHpBdHZZcF5FeHpFfHpJfHpleF5RgH5VgH5VhH5ZhH5thF5ZiH5diIJliH5xkIIxoOZ9lIKFoIJRrOJhtOKRuKZhwP6ZvK8hlMMhnMcloMslpMsprM8ptNMtuNMtuNcxwNqh6P8xxN81yN6p8Qc1zOM50OM52Os93O9B6PKaEW9B7PNF8PdF9PquIWtN/P9SAQNSCQNWDQbCMX9WFQrCOZ7OOX9aHQ7WPYNeJRLeQYNiKRLmRYLuSYNiMR7yTYNmNR7yTYbyUYdqPSL6WZNqRSduSStyUS9yUUdyWTN2YTd6ZTdqYdNqYdd6bT9qZdeCcT9+dVdubduGeUOGeYuKgUdyed92feOKiUt2geeOjVN6ieuOkWeOjZuOlVN6je+SmVd+mfOWnaeWpV+aqWOCofuasXuarbuKrf+euWeCtfuOtgNmxd+SvgeiwcemyW+mzYuOygOq0deu4ZeW3g+u4eua9he68fe+/gOjBiPHDg+rGi/LFh+3Ije7Mj/TMj////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjnAP8JHEiwoMGDBl+4YLEixYkSI0B04EDwxZAwZMZ88cJFC5YqUGxY+PfCiJkcNGbEgKHChIgMOJjUkODC0Y0WKEh40FAhwgIDAWRcebACVChPnDRlukQJUiJCf+w0cpDiU6VIiwoBugNnzRkwWaYcYnCikyRDgvTIYYNGzBYqUZoEUlBiEyI+ddqkKdPFihQnSo7kQRACk5+uX8M+WYKECBA6Bz5YmtP2bdwkRYL44PGmAIdJavr+DSzkR48dOtwM2MDokaJDg/rswUMnjpvbbgRguEBhAoQHDRgoSHCgAIEBAgAgRBgQADs=
''')

    global icon_cancel
    icon_cancel = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAMZnAO0AAO8AAPEAAPMAAPUAAPcAAPkAAPsAAP0AAP8AAPUJCfULC/UMDPYPD/YQEPcSEvcTE/gWFvgXF/EbFPIbFPUbFvYdGPUgGvkjHfolH/wnIvkpJPwoKPwpKf8rJv0sLP0tLfovKv0vL/0wMPczM/4yMvc0NPc1MP4zM/40NPs3Mvg5Ofk6Ovk7O/w8OPk9Pfo+PvdCMvdDM/dDNPdENPhFNfhHOPhIOPtHQvhJOvxHR/5HQ/9HQ/xISPhLPPlMPPxKSvxLS/tMSPlOP/xMTPpRQv1QUPpTRP5SUvtXSftYSv9bWPxdT/1dT/1fUv5hVP5iVf5jVv5kV/5lWP5nWv9oW/9pXP9qXf3Fxf3Jyf7Kyv7Ly/7MzP/Pz/7q6v7r6/7s7P/s7P/t7f7x8f/x8f/y8v/z8////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAQABAAAAe9gH+Cg4SFhQmICQiLCIZ/CR5WVVRTUU8aB4ceVzwpJSMgLkwZBYOQV0tdSCIfQVxCSRgEgglVO11mYkRAYWVaIUUDtFQoRmK5YmVgMBJDAoIIUqBByWVhLxEQPs9/CFAfHT3VYCwPDTfcCE4cOr1hYGReJgs1AYIHTSpbZV8tK15jsFiQYe+PgQxKcGRpAcEBCSwnaFAAMKgAhiMbzDFQUEHGBIqECFz4kcNGjRkxPjoSwFJAgAAAQDqaOSgQADs=
''')

    global icon_clock
    icon_clock = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOecACxYey9afDtrnDVspjttljdvrkF1oUp2oUR4r0Z9s0h+rEqAsHd/gU6Ht3mAgVmGtGSFoWmIo12KuF6Mu1iPv1SQwoSMjWyQv3GPw22Qx3SRxGyUvnGTwluZzXKWyWyZwnGZwmacyXKZyG+bxnSds2qfxoCfz5Wen9aaDsWcLtiaCnGmznqj2YGjzaKiooml0X6qwnWs04Wn18akOnet04eq0oiq2Ymq2NGmOJKr1emnAMyqOtCqMpau1aSusamxjO+uAMmyTciyUZi03HS8+teyR+iwKbKzs5i32bS0tPS1AIq/3q25vqO63I7C3pbA26C93p7Bv4jE7Kq93prE357D35LH4q6/36bC4LbAxb2/wpTL6afJ4rrGyejDYcPExcXGxp3Q5+vHYabP5PHJXanR5vHLXPTLW8LP0q/U7/LPafPQc/LRfNPT0/DTgfbWfMLa8MHb8NnZ2dvb28/f79Hf79ni8dbj8dzj8drl5/bjq8zs+vnotd7t8dPw+vrsv+Pw8unw8OPy+u7w8OLz+uvx9Ozx89/1/+n2+un2/eb3//P19fP1+vP2+u74/fL4+O76/+v7/+j8/+v9/+/8//X7/uv+//L9//L+//P+//f///n//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjwAP/9U0JQoMGBSg4COfPHTBAiEIkIUfMGiEEyfMTskLIlTJgtTni4WaNDIBsvM6yUwdIjB5QxUYroMSJQRYolXK7gMVTITpMqP3CgEEiCBpUpnAbl0aQp05AnMEoI7BADyZ1Ki04EesQETo0YHQRWWPECkaNNDnww6OLHw4oKAhuEMEEoESALDNBE2pMhRAOBCii0iKNIUJY+kg6lEUFBgUADC0bYsATpEiZKk1h8WGDAIIEEIG7QacSojowNCQgc/BcBwQQOGjBckPAAwup/bbQIGFCgwIADX8CsTjLnSAAAyJEfkZPkoAsXtwU+FxgQADs=
''')

    global icon_cog
    icon_cog = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOcAAAAAAAEBAQICAgMDAwQEBAUFBQYGBgcHBwgICAkJCQoKCgsLCwwMDA0NDQ4ODg8PDxAQEBERERISEhMTExQUFBUVFRYWFhcXFxgYGBkZGRoaGhsbGxwcHB0dHR4eHh8fHyAgICEhISIiIiMjIyQkJCUlJSYmJicnJygoKCkpKSoqKisrKywsLC0tLS4uLi8vLzAwMDExMTIyMjMzMzQ0NDU1NTY2Njc3Nzg4ODk5OTo6Ojs7Ozw8PD09PT4+Pj8/P0BAQEFBQUJCQkNDQ0REREVFRUZGRkdHR0hISElJSUpKSktLS0xMTE1NTU5OTk9PT1BQUFFRUVJSUlNTU1RUVFVVVVZWVldXV1hYWFlZWVpaWltbW1xcXF1dXV5eXl9fX2BgYGFhYWJiYmNjY2RkZGVlZWZmZmdnZ2hoaGlpaWpqamtra2xsbG1tbW5ubm9vb3BwcHFxcXJycnNzc3R0dHV1dXZ2dnd3d3h4eHl5eXp6ent7e3x8fH19fX5+fn9/f4CAgIGBgYKCgoODg4SEhIWFhYaGhoeHh4iIiImJiYqKiouLi4yMjI2NjY6Ojo+Pj5CQkJGRkZKSkpOTk5SUlJWVlZaWlpeXl5iYmJmZmZqampubm5ycnJ2dnZ6enp+fn6CgoKGhoaKioqOjo6SkpKWlpaampqenp6ioqKmpqaqqqqurq6ysrK2tra6urq+vr7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y8vL29vb6+vr+/v8DAwMHBwcLCwsPDw8TExMXFxcbGxsfHx8jIyMnJycrKysvLy8zMzM3Nzc7Ozs/Pz9DQ0NHR0dLS0tPT09TU1NXV1dbW1tfX19jY2NnZ2dra2tvb29zc3N3d3d7e3t/f3+Dg4OHh4eLi4uPj4+Tk5OXl5ebm5ufn5+jo6Onp6erq6uvr6+zs7O3t7e7u7u/v7/Dw8PHx8fLy8vPz8/T09PX19fb29vf39/j4+Pn5+fr6+vv7+/z8/P39/f7+/v///yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjSAP8JHPjvGDGCCAkeK0eOVUKB0Zwp+yfMWzdZ/1idGkWQW7ttwnxZowaL1bJztwgS40Yt27aR2aQtQ5aHYDFqzJLp4hRKmLFgtxIJREYMGLZmvAQJfDRMWDNGhwYRS2ctmbNSBFkR02Ws25pf4qQZaxaLICpht4BJCzPqEahnxph5WhqMVy4yWKYIZFUsWLFjqk4F81VLVRqCpqoVWxYt2TFmxXotc0OQlzdTgwoRE9bGjSlpgAgGekPm36Blx8T8w+IkycN/gXrJ2vIaIZYoDwMCADs=
''')

    global icon_cog_delete
    icon_cog_delete = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAMZnAFFRUVNTU7xCBLxCBVhYWIlOLblEA7lFA7BIDLBIDb1NBGFhYZFZOWRkZLxWHmtra8BaIm9vb8lkJd1kAXl5eeFoA8trLYGBgYKCgoODg9F1O4WFhe52AIeHh+Z3Iep5BYmJifh2AIyMjP93EY+Pj+9/GP9/GP+GIcKQdMKQdeuKQJycnJ6enqCgoKGhoaOjo/+STaWlpaampqenp6ioqKqqqvSdY6ysrLCwsLGxsbKysvWocre3t7q6ury8vL29vb6+vr+/v/a1jcDAwPe1jcHBwcLCwsPDw8TExMXFxcbGxsfHx8jIyMnJycrKysvLy8zMzM3Nzc7Ozs/Pz9HR0dLS0tTU1NXV1f7NrtbW1tjY2NnZ2dvb29zc3P7WuN3d3d7e3uLi4uTk5OXl5efn5+np6e3t7f///////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAQABAAAAfRgH+Cg39LSISIhEtjYjeJglRSTn9GYF86fzczL4RdZlxGQFlWODdPZDyESF1WW1yjW1VPTBSESVZQTT0rLkZKRTwggkxIQ1pRPhiCJEdGUSIdGUhlWU1SMYQ3SD1KXw9BYVVKUTmENEY8Q1ULLyQtU0pQLMsoEAMJBQGCN0lFSUs1ZqTQQMTLDguDZFxJ8oRKkyUOhMAYcUKFAUE+wMjIsAGJEQFYzogsIUDQhQgN/mR4sgSBDRMhOFQ4kOjCDx0MJHj4MEHBoz8EAAg6IIDmn0AAOw==
''')

    global icon_cross
    icon_cross = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAMZZAOQiJOYqLOktL+ovMekyNes0Nuw8Pu49P+0+QO0/QfE/Qe5AQu5BQ+9DRu9ER+9FSPJFR/BGSPBGSfRISvZKTPJMT/RNUPVOUPNRVPZVWPdVV/VWWPZWWf9UV/ZYWvZYW/9WWfZZW/ZaXPZaXf9YW/dbXfdcXvddYP9bXvheYfdfYfhfYvhhZPphY/hiZPpiZfljZvpjZv9iY/pkZ/loav9naPtpbPpqbfxrbvpsbvttb/9sbvttcP9ucP9wcf9wcv9wc/1xdP5xdP9xdP9ydPxzdv10d/90dv52ef92ef93ef93ev15fP95e/95fP95ff56ff96ff97fv98fv5+gf9+gP9+gf+Chv+Hiv///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAQABAAAAd+gH+Cg4SFhoeHS0iGLDQYhEtWVEGEKzpTK4RCUFhMNoIpOVEqEoU4RldFLic3TScPhzA8VVJOSiYOiH8jTygkRw26fyVJIB0/EboiM0RAPTsaB4chMUMeDAYWNRcFhR8vPhwLggQQMhMChBstGQmEAQoUA4UVCIYA88L6+3+BADs=
''')

    global icon_delete
    icon_delete = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAMZvALdKK7hKKrpLLrxLMLhOLsFNM75PNrxQMr1RNcRQNL5TOMBTOtBPPsxSPMZVQsdXRctZSdtWS8xbTOZWTOZWUOZYTNFeU9ddUeZZTulZTeZaUs9hU9ZgVOlbT+pcUOddWddiXNljXdpjX+xfVNpkYdxkY+BlXOljW/BkVttpZOpmXO5mUt1qaOBpat5qZ99qauNrYe5qXuNuY+JwZvNzXeR4cfJ3Y+J7deh6dfN5Y+l7cOl/eOqDffaCaPCDe+6EffCFcPaEbO+GfviGcO6KdfCMd+6MgfiMdvGOevSOgfCRf/eRfu6Sj+2TjvmSfveTfvqTf/iUf/qah/GclvGdlvqdi/SgnvSinvWjn/qjkfWmofOno/upnParoverofWsofqrnfKtqvWvpfivpPS0qvi2qPm5r/q6rvjDvvzHuvnLxPnTzPzUzf3b1P3c2P///////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAQABAAAAeigH+Cg4SFhn8sJSQhh4MvTWhramQzFoctYW5nWVVcaToShS1bbVJKSFFOR2UyD4Q8bFVPREG1QTljDIMuYmBFI8DBNkk7C4IpZlBAb8zNGTFUBoIiXkM9zc4qUweCIEZLNBni4x0+NwKDEV0oK+MZFRpYCYQbMF8jHhkYExRXHAGFIJjQIuTEhx9WLgA45KABDiZMahRY2OiPAgQDCFTcOCgQADs=
''')

    global icon_die_16
    icon_die_16 = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOfCABEVFx0YGh4eGh8dIR8fHSYkJSclHyclJScnIScnLSopMDIxMjQyMTUzNS41NjU0M0BBPkJDPkJDQEZFQUZGQkhHRkdIQEpJSVtUOl1ZU1pbWWZbQGlhQm9hRmxkSHNsTnpwW3R2fHt4d4ODfISHgYuLaIqLhI6LkZCOjpCOkpWRbJqPc5uQZ5mRcJuRcJmTaZqSdZyTZ5eUbaCRcpyTb5+TaJ6SepuVZpuUcJuVaJuVa56SgJaWcKmRbJuVcp+Uc6aTdKKVcKuTbKKXZ6CXcKeWbauVbKeWcJyZdp2aaqaZbZ2YlJuYoambcKCbi6edcqqefKmeg6mff62jjainoq2nraqpprKwhamutbetmLO2ubi3vru5ory9tr+/qMm9qsG/r8O9wcu+rsrEucfGssbGtczFsMvFtsrGtMnHts/Fuc7FwczIvs3MqszMs8/Ns87Nyc/N0c3QutDN08/Ozs/Sy9bTy9fY0ODg3ODh2ubn4erq6PLr2/ny5vvz5/j17/716Pn58vj5+vz4/Pr6+v369/v7+fv7+vr7/v76/v77+P37/f77+/38+fz98//7/v38+vz8//38/fr+9v/8/P78//n++vv9//39+vz9/f7+7/z9//39/fz+9/39//r+///9+/79/v/9/Pz++/3++f//6v/+9f/9//z+/v3/9P7++//++f//8P/++v7+/f7+////8/7/9vv/////9f/+////9v7/+f//9///+P7/+/3//v//+f//+v//+////P7//////f///v///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+OUNSRUFUT1I6IGdkLWpwZWcgdjEuMCAodXNpbmcgSUpHIEpQRUcgdjYyKSwgcXVhbGl0eSA9IDkwCgAh+QQBCgD/ACwAAAAAEAAQAAAI/gD//asjh82aNGXIjDmDxgsVNwLjCGO1itIsXLdogTKlSViJf06EHXLE6JEqV6ESJaIUq9AVDmZoLbqDogqhTJlOzTlhRVgSFv9ACbPwoACeTZ1eXWhwQNiNGv98CTMhYEIgTqlsjSBQQVgOgac8jdrT6BadLpB46cEk7EWTf7QqCZIEyk6AASmAYTokTIeSf7BcoeJlCg4AByR2TbK0a4URNcAu/RJGeQuTQbQoC9sB5A0sXVoWZPjTS5SiJQw0CIPxr00pYBAkIMhDylCuCBQMAMMxJAugVmEUhEAU6ZMsLAlE9LHxA8QXMX5wBRMGTFiwYLX4TInygQsGKTRUHSBpMcOFDx4yiEDxIBDMBoH/jvQQUiTGkyAdBAYEADs=
''')

    global icon_die_32
    icon_die_32 = Tkinter.PhotoImage(data='''
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
''')

    global icon_information
    icon_information = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOeMADRPhjVPhDRPiDRQiTRQijVQiTRQkjVRkDRSkjRTlTRVmTNVnzVWnjVmqzVpqzVrsTV9vTV+vDV+v1J6q1Z7rjuFxVeAslyDsF2DsV6Es0CLyUGLy16Fs16FtGCGtEWMzUGOy0eNz1+Jt1uKuUeOzmKKtmKKuGOKuWOLu0mR0WKMukyS0mSPvmWPvl6Rv2aQv2aRvmmRwmmSvmeTwWiUwWiUwmmVw2KXyGmWw2mWxGyWxWqXxHKWvmuYxGuYxW2Yw2yYx2uZxWyax2iczXGcy3ecw3Gdy3GdzHGey2qg0HidxXKezXSez3Wgz3eg0HehzXai0HejxXqj0Hek0Xmlxnml0Xql1H2ny32p1oGqz4Kp1oWr0YWr14Ws0I2qzYmt1Yau1Iyy2ZC00pGz2ZOz25ez0Zm11JO31ZO40pe62J264J+72Jy825+835+84KK82qK93aC/4KK/3aO/3aXA36bD2qbD26jC4KvC4ajD4ajE4qvF36rG367F46/H47DJ5LPK5rTL57jL4bjN5tDc6tPf7dTg7vT3+vT3+/X4+/z9/v7//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjFAP8JHEiwoMF/Kz5s0HBwYIokcfr0aXMDwsEQYQap4aJlDB4wDwqSCAMISxU9eaBMgdOlAcEhgaw4YZIoERIjT+iMGAjCDZkmS4jMkRMkSI8taRgIrPBHyhEhPhgtwkGjxo89CQRK8AMlyI4chhC9aMFCBh8DAiOw+QLExoxCh1CcMKEEzYGBLu7oiCFI0SJCHTiYoUDQQZY3MFSIyIDhghcqAwouuLKmSAkPPMpECXBQgYUzduqImQCgoUAEBAQUMM16YEAAOw==
''')

    global icon_package
    icon_package = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOevAMODIsOEI8SFJMSGJcWHJsWJKMaKKMeNK8iOLMiPLciOQMmQLsmSL8qQSsiUO8uVMsyYNNCXU86dOd6fMtGkP9KlQNOoQtWmUdekX9SqROGnQOKpONWsReKqN9WtR+OrOtqtUNawSdewSteyS9iyS9uxVuSxReWvVti0TNi0TeSxTOaxR9uyYtm1Tdm1Tua0Pea1Otm3T+a1P+a1Qum1Pem0TOy2OOSzdNa4cOa2a+e6Qd25aeK3b+i7T+m9QOm9Rei+Q/C9O9y9d+i/SPW9QOrBRuW/b+HAcuDAferEQ/HBVtvDiezFR+vGSPnCSOvBguXEgvnESODGfu/HSO7Eg+zFg97Jle3Gh/XJaezKhOfMiO7KiO/KiuvMhOvNj+XPkvDOivHPhvXPf/XQePDQjPXQf+3SkvHSi+rVnPHVkPfVif/Vd/LWlf7WePXXkPfXi+3Zpf7ZfPvajfvchPvbkvjbnf/cjPLdr+3evv7flf7glP7hlP7hlvnhqv/hm/rjqv/jn/fksvrksP/kpP/kpfblv//lpf/nrf/oqP/oq//ptv/qs//qufXr0v/rt//ruvnrzf/rvfrszv/tvvvty/fu0fzux//uwf/vwf/vxP/vyP/wyf/yzP/yzv/z1P/z1f/0zP/01//02v/12fz24v/22/324v/23f724/344vz45v744f775//+8P//9v///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjnAP8JHPiPhAiCCAemGIFGC4cMCQei+KIK1Z1ARygkdCGlkqtWlEC86cOGhQSBMVrAaYTHyhIcO9yIqfMny4UHKVZBMtPFSAkHkkYxyrOG0BwGI1J5EhSmzBgVghT5aUOERpoEIUyJ+hRJDZYacuxEsTGkB5kDHkiF6qTpER0lToIw+TFjxRYDGUh52jRp0aE4U5IAkfFBQxUCFlidwuQo0SA+TXy82DAhBxUBFYQUKnXJEKA9RWB0OHHlRgMAAiUgscQJkR4dJrg8iRAAIYQHUEBlOgMGw4DaERcg8MJDgYCICAsQiBgQADs=
''')

    global icon_resultset_next
    icon_resultset_next = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAKU2ABRBtxVFuRZKvRZOwBdQvRhTwBhZxBlZxhpixhpiySNuzSxyzTtxzDx0zzV30j130D960EN/00OE1keE1kuI1lOO22CV3WGX3WKX4W6g4nKh33Si4nSj4HWj33Wk43ek4Hmm4Hmn5n6o4Xyp4Xyp6H6p6ICq44Gr4oGr44Cr6ICr6oev5Iew6Iqx5JC155K36Jm76Zm76qHB7KPC7ajH7q3I7////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAD8ALAAAAAAQABAAAAZLwJ9wSCwaj8hUCWlUkTZMYqjGskSFGdrMM7liZC/YZRGtxEyoFgXBlLg4n1PkwHSsNCNIIaoQgR4EVwkdDQJXPwYMAYc/AwCMkJFBADs=
''')

    global icon_shield
    icon_shield = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOeFANSPHdWQHtaTINqbJdyfMN2hNNyhOeCmLeCoNeCoOeGpL+CoQd6qReKrMOCqQOKsOeKtQ+WwM+GvUeayNee0Nue1N+i3OOm5Oee4Tem6Ouq7O+e6V+q8O+u8PO3BP+zBRu/COO/DOO7DQPDGP+nFcPDIP/DJOvDIRvHJRevHffDKYfLMSvHMTe3KdPLNUu3Ld/PQWu7Oge7OgvLRdvTWW/TXVvXWYvDTkPHUh/DUjfTXafLViPXZcvXacfLXmfbdVfHZkfXbePbcePTbjPbcffbcfvbde/PbmffegfbehPfgefffg/ffhPfgiPfhiffhivXgpvfikPbhpfnpWfjkj/jloPnphPnqr/rqtfvum/vuo/vwlfvurPrsw/rtxPrtxfzylPvux/zxp/vuyPzynvvvv/z0i/z0kPvvy/vwzfvx0P34hf76i/78evv01vz02P/+b/z11fz11/z4zP323f333/334P335v344P344v346P355P/+r/755/756/757P780f783v788f788///1P///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAi/AP8JHEiwoEGBGi4c/CfCg8AOGnbgoDBBYAMFAj0MUTFDSp9BguxAaYEhx4GBH/bkiXNFzx8nWNSk2UCQQx4qT6Lc8dMDBgs0CAhmwOOESRMuYnS4ODEGAkELdZYUQaKFjI0VI8I4IFiBDpEgRrKAoYEixJcFBCe4qcJDyBYzNUqA6FKAYIQXb5IoObPmhwkvKQQUbBBDjhU2baaU8WHg4IMbgfjAAXREwsJ/CWTMIQSEwWWBAwiQCPCZIICDAQEAOw==
''')

    global icon_status_away
    icon_status_away = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOeSAAARbWY4IwlHpVM7R2k5JSBKmAtXyRtXu3hOLXpOKSVlx4BcNoNcLjNpuTNtwTNty4xnNT11xz91w49tOT930ZFvOUV5z0d70Y5zWYZ3fEmB0Zt6RlGDz52ASFGJ1VuN0VuN1WGP2WmR2WeV22eV3auSYWuZ222b3W2b4XOh4XWh4bSdcJqhmZaioLahdoSo4oGp6aKnvYis5L6nfIet6aGsrImv6Zit0pSv2L+sf42x642z65O12LOyr6O1zqW2wLW0s6m3xKO43se2iKa60aG64KO76aW96qLA4aO/66nE5qrH8LHG69XGmq7J8bnJ2bbL6rPM8rrL67bO8bfP9LnQ8rnQ87zQ8rnR88LQ5MDQ7bvR9LzS9L3S87/S8r/T9MfT5r/U9L/U9cDU9L/V88DV88LV9MHW9MLW8sHW9cLW9MLW9cPX9cTX9cXX9MTY9MXY9MXY9cbY9cXZ88bZ9cfZ9sjZ9sja98na9sva9cnb9src9svc9svc98zd9szd983d98ze98/f99Hf+NDg99Ph+NTi+dXi99bi+dfk+Nvn+d/s++Pv++bv+PDz+vv8/P3+//7//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjRAP8JHKhCB40PAxMm3OEHUSE1IxQmTOFHESA9hKw0kCjQhiFAd9qEgeOB4z8Yg+ywEbPljAaTHMgI4kIlzhIBJv+BSBPFCRYHAEyeEFJExgscNyRwNPEmUSA+cnrMGJJjQ8IIUw6t+dMHSBMwWqQ86TAwxBwvZvbgWZHFUQZJjYIgEIgij5ExdeK4gCLp7SMkFQSSoHOkC5svJZREypABEg8IAi0kYdKlTBUMPxhFkrSoBYGBBkRccYMmxoQaRHywSKDwwIMLFBQUGLCAQQCBAQEAOw==
''')

    global icon_status_busy
    icon_status_busy = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOeGAAARbdIAAdMAANUAAMgDC9gAAdsAANwFBtkJC94VEtwWEglHpUU6iuQcHOMdGOYdHeceHgtXyRtXu+EyKuEzKuM3LeQ3LeY3LuY4LyVlx+k/NTNpuelBNjNtwTNty+xJPulOQelPQupPQT11xz91w+tQQuxRRO1RRD930e1SRUV5z0d70UmB0VGDz1GJ1VuN0VuN1WGP2WmR2WeV22eV3WuZ28eFmm2b3W2b4c2KnnOh4XWh4cGVrYSo4oGp6Yis5Iet6Ymv6Zit0pSv2I2x642z66O43qG64KO76aW96qO/66rH8LHG667J8bPM8rbO8bfP9LnQ8rnQ87zQ8rnR87vR9LzS9L3S87/S8r/T9L/U9L/U9cDU9L/V88DV88LV9MHW9MLW8sHW9cLW9MLW9fnKyvnLy8PX9cTX9cXX9MTY9MXY9MXY9cbY9cXZ88bZ9cfZ9sjZ9sja98na9sva9cnb9src9svc9svc98zd9szd983d98ze98/f99Hf+NDg99Ph+NTi+dXi99bi+dfk+Nvn+f///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjOAP8JHLiDCJAXAxMmLJJnEKAxMxQm1JGn0J46f6RskCgwSKA9ctBoWeOC4z8ffuKc2VIFDAuTLbr0sQKFzZIFJv/BEOOkCZUOAEzeMHLkR48hQkhwrKGGEJ87bWwcMGCgQMIRTwSR0YMnhwMOKU5gSDAwhhssX+zMOaDhA4QHJiwMEIiDDhIucNgYSGGoryERAgTSeJPkypksBk6YKcMYROB/KpQwueIlCoILJRo0CEHh8b8IMqakCcNDQQURICZ4FijBwwoUGRgQCCDgcUAAOw==
''')

    global icon_status_online
    icon_status_online = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAOeLAAARbQApjwApqQAzoQA1swU/pwlFsQlHpQtHsQVLwQtRwQtXyRtXuyNdtyVlxzNpuTNtwTNtyz11xz91w0h0zD930UV5z0d70UmB0VGDz1GJ1VuN0VuN1WGP2WmR2WeV22eV3WuZ222b3W2b4XWf3XOh4XWh4X+g3oGg3YSo4oGp6Yip24is5Iet6Y+t4Ymv6Zit0pSv2I2x642z652145m46pu46aO43py66Z266aG64J676J676qO76aK846W96qO/66i/5qbA6KbC7arF7a3G6KzG7arH8LHG663H76/H767J8bTL67PL77PM8rTM8bXM8LbO8bjO8LfP9LnQ8rnQ87vQ8bzQ8rnR87vR87vR9LzS9L3S87/S8r/T9L/U9L/U9cDU9L/V88HV78DV88DV9MLV9MHW9MLW8sHW9cLW9MLW9cPX9cTX9cXX9MTY9MXY9MXY9cbY9cXZ88bZ9cfZ9sjZ9sja98na9sva9cnb9src9svc9svc98zd9szd983d98ze98/f99Hf+NDg99Ph+NTi+dXi99bi+dfk+Nvn+f///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAQABAAAAjCAP8JHGhCRosNAxMmnOEHUSE1HxQmLOFHESA9hKo8kCjwhSFAd9p8gaOB4z8Vg+ywAaPlDAaTGcQI2jIlzpEDJv9xSONkCRYIAEyKuKGDRYoYMCZwDPEmUSA+cqyMKdJAoYQoh9b86dMGyg4mKwIk7DCni5k9eMo0yeHCR4GEI/L0CFMnThYlNlAEQZAQBJ0fXNh4eUKkxgkhBhJaAIKECxkqSYbwoEFigMIFHq64QSPFCA4KCTgyiHChggMFBAQkDAgAOw==
''')

    global icon_sword_2_16
    icon_sword_2_16 = Tkinter.PhotoImage(data='''
R0lGODlhEQAQAKUlACkkKyUlMDQqNzMwOEFBSENEQ0pITExMTExNS1RMWFNTU1RUVFZWW1dXV1hYWFlZWFxcXFxcYGBfX2JiZGRlc2VnaWhoaGhoaWxsbHZweXZ1d31+g5aYpJ2ZoJyepKytrrCytL/Bx8jHy+Xn6e7w8P///////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAD8ALAAAAAARABAAAAY9wJ9wSCwOCcYkkUFRJh8RjsdZhExCICqxcRl9tEMFhgQeHiyi8lDSUQsdGfdvkZAjBPLCQB7YyCsacgYAQQA7
''')

    global icon_sword_2_32
    icon_sword_2_32 = Tkinter.PhotoImage(data='''
R0lGODlhIQAgAOeFABgSGR0RIBcXISgeKiAgMSUiJSUlKy4iMConLDQqNzYwNzIzNjMzNzc3RD82Qzg4Sjs7Oz07PkA6Qjs8Pzs7SkQ6R0JBQ0JCSUNDT0VERkVGSUdHR0pJSktLSktLU0xMTFJKVVJKVk5OTk9PTlFOU09QT1BQUFJQUlBQWFFRUVJRU1FSYlNTWFVVVVZWW1hYV1hYWFlZWVpZWVlZXlhZZlpaWltaW15ZX2BZYlxbXlxcXF5eXV5eYWBgYF9gaF9gaWFhYWJhYWJiYWJiYmNiY2hga2NjY2NkZmRkZGRkbGVlZWdmZ2Zndmxmb21pb2tqa2prbGtsbXBtcXBvcHR0dXV2d3Z2hHd3eHt2fXx2f3d4e3d4hnt4fXh5g3p8fn9/gIB/gX+AgIaGhoiGi4eIj4yIjomLlpKMlI+PkpCPkZOUoJSVnpmYm5udpp+doqejqqipsq6usK6wtrOytby6v7y+xL2/w7/BxcbGyMbHyMrMztDP09DS1NHT1NHT19jZ2uDh4uPj5efp6/X39/r8/P///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAhACAAAAjsAP8JHEiwoMGDBhkgXMjQ4AUCDSMi7ODhAQWJGAe+QLGCRkaMI3awYGKly8eIMYS42KJmDZmTDIEMmWEGjhyYC0UoMcKjTR07OBFuUILkiBw/eoIehIAESZQ7gvooPdgjSBU+hPJMNahjRxhAg+JsLQhDhpg/gdiMJdgCxhc8e8asHZgixpU5dLjMFfihxhQ3b5zsFRjjSZkzNwb/a7EESxbF/1IQaVIEsggbOEJANnEChAPIKThUOAC5RIYEASD/szAAwQTFEBZg+AFZQIMkWiAb8IGGCmQNXtKogAwFjJQCkHOQkKA6ggIAAQEAOw==
''')

    global icon_sword_blue_16
    icon_sword_blue_16 = Tkinter.PhotoImage(data='''
R0lGODlhDwAQAKU3AAAAVwgIWw0NUw0NXxISVRUVUj4+aVtbbnJycoCAk4eIiYqKi5OTlJOUlpqdpJ2foaSko6Knr6iqraquta6uq7Kys7a3uLe3tre3uLe5vbW6wrq6ubu7ure8w7q8v7q8wLm9xbq9xL6/v77BxsDCx77DzcHDxsLDxcHEyMLFzcTGy8HH0MjIyMzMzsrR3M7R19DR08zU4NTU1dPV2Nba4dnb39vd4v///////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAD8ALAAAAAAPABAAAAZPwJ9wSCRGishfrJRKEl0g2scpXHVeNupPE1LVtJNRZqZ1oCQw7Y/0aKlNjRO18vMsRFoORWFRAwwXCFoCBQMHMk4YCQEEaj8bDI5CECxqQQA7
''')

    global icon_sword_blue_32
    icon_sword_blue_32 = Tkinter.PhotoImage(data='''
R0lGODlhHgAgAOfcAAYGUAUFZAYGbAYGbgYGcQcHaQoKXA4OQgwMaA0NXA0NZQ8PYhERUBAQXxISSxQUURUVRRUVSRQUVxYWUxUVZRgYQBkZQRkZSxkZTB0dPygoUywsUDc3UkZGgGZnaGtrh21tj3Fyc3R0dXZ3d3h4eHh4eXp6enl9hH19fn5+fn9/gIGBgYKEh4SEhYWGiIWHiYiKkIuLg42OjpCRkpCQpJKSk5SVl5WVl5aXmJaXmZeXl5eXmJaYm5eYmZabpJubnJydnp2foZyfpZ2fpJ+foaCgoqCgpKGhoqKioqCjqKGjp6Okp6Klq6Slp6OmqqSmqaWmp6SmqqWmqKWmqaamqKWoraaoq6ioqaeorKmpqaqrrKqrrqyrraWsuKusqqmssKysraysua2trauutamvuq6vsK+xs7CxsrCxs7GxsbCxtK+zubK1vLG2vba2srO2u7e3t7O4wLW4u7e4uLe4ubi4ubK5xbi5vLm6u7m6vLq6u7m7vbu8vLu8vre9ybm+yL2+vr6+vL6+vry/xr6/wr+/wLrAybrAyrzAxrzAx77Awr7AxL3Ax8DAwbvByrzByb/Bw8HBwb/CyLvDz8LDw8PDwr/Ey7/EzL3F08PGy8TGycTGzMbGx8LHzsTHzMjIycPJ0sXJzsTJ0cfJy8jJysfJzsrKzMnLz8nM0MnM08zMzMzMzcfN2MjN183Nz8jO183O0M7Ozs7O0MjP2s7P0c/Pz8vQ2MzQ2tDQ0cvR283R2M3S2tHS1c7T2tHT1s7U39HU2dLU2NPU1tTU1c7W4dXX28/Y5dDY49ja39rb3dnc4tzc3Nvd497e3t7e39zg597g497h5d3h6N/i5uDi5eDj6ODj6eLk6OHl7eTn7OXp7ujq8P///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAP8ALAAAAAAeACAAAAj+AP8JHEiwoMGD/04gXLiwi51DohhKHIjJ2CxHt9hMlDjpGKs/orAN2bjQD7FWjxI908aC5EEyv15dWiPN2jYPLgv6yPWqExNp1bKZyVkQlC1LSZRFu3aHKEFDuxA5AcZsGiGnA+P0GlSlFDJqfbAKbKNLUpRFxaihEftvTKpMSuQEg0aFrZBQm5Rs8ZWsCVsYjDw9CcJLmBa2/96UipKDFq0yiL+gmmJjFCwuiK2cwjJDkawjiJdoUuMCj6sbTlUM5AEpT4k5pGo41dMM9Is9fUKcoYQDa6NVsYhIoTMCCiAgbFcUceMFRQ8+PxD/e9CBRpYrMqQHUOBggxFBSBBSF8CQoYEADXVwRRJrwIIEAgsqCFQ1LKcJZzsOREAwYAIEgjrkRAInpoBAQQIXMCBdCnAEEgMHAEj3jwhpgFFJGB9I+E8LdYhRyzKfaDhQIdIFBAA7
''')

    global icon_wand
    icon_wand = Tkinter.PhotoImage(data='''
R0lGODlhEAAQAMZGABUVFRYWFhcXFzExMTU1NTc3Nzg4OD4+Pj8/P0BAQEJCQkNDQ0VFRUdHR0xMTE1NTU5OTk9PT1hYWGdnZ2lpaYGBgYODg4SEhIyMjJWVlbSXQb+hS8KkTsKlT6mpqc2wWs+xW/GxAPGzAPG1APG3APK3DfG5APG8CPO9EfO9E/K9GfO/F/O/Gdy/aPXBJfXBJ/XDK/XFL8nJyfbKQcrKyvXMS/bNS/fOTvfOUPbPUffQWtPT0/fWavjXbfjZdPjZd/jcffjdg97e3vf39/j4+P7+/v///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAH8ALAAAAAAQABAAAAd0gH+Cg4SFhoUwh4UxMC84fyyKgzo9QDYoijAuN0EcIC0zJyaKOR1ERR88JIorDjRDOxs+I4cpERMYHho/I7SGEBMGCg81KiWHwAUJASMifyGGEhcFCACC0IYNFtTWkgsVBAfdihRCAwzj5DIZAZKEBwLug4EAOw==
''')

    loaded=True

if __name__ == '__main__':
#from Tkconstants import *
    import ttk

    class Application (ttk.Frame):
        pass

    root = Tkinter.Tk()
    app = Application(master=root)
    init()
    for name in sorted(globals()):
        if name.startswith('icon_'):
            f=ttk.Frame(app)
            ttk.Label(f, text=name).pack(side=Tkinter.LEFT), 
            ttk.Label(f, image=globals()[name]).pack(side=Tkinter.LEFT)
            f.pack()

    app.pack()
    app.mainloop()
    try:
        root.destroy()
    except:
        pass
