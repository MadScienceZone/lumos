# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# Adapted from the TCL implementation of my readerboard driver written
# for my quiz show game system (ca. 2000).  That was written from scratch
# based on the information from the readerboard documentation.  This was
# written based on the TCL code, so I copied over a few implementation 
# decisions from that.  I need to look up a couple of them again in the
# documentation to remember why they are the way they are.
#

from string import Template

class InvalidTextAlignment (Exception):
    pass

class InvalidTextMode (Exception):
    pass

class InvalidTextAttribute (Exception):
    pass

class SpectrumReaderboardUnit (object):
    text_alignments = {
        'middle': ' ',
        'top':    '"',
        'bottom': '&',
        'fill':   '0'
    }
    text_modes = {
        'rotate':   'a',
        'hold':     'b',
        'flashing': 'c',
        'roll up':  'e', 'roll down':'f', 'roll left':'g', 'roll right':'h',
        'roll_u':   'e', 'roll_d':   'f', 'roll_l':   'g', 'roll_r':    'h',
        'roll in':  'p', 'roll out': 'q',
        'roll_i':   'p', 'roll_o':   'q',
        'wipe up':  'i', 'wipe down':'j', 'wipe left':'k', 'wipe right':'l',
        'wipe_u':   'i', 'wipe_d':   'j', 'wipe_l':   'k', 'wipe_r':    'l',
        'wipe in':  'r', 'wipe out': 's',
        'wipe_i':   'r', 'wipe_o':   's',
        'scroll':   'm',
        'comprot':  't',
        'twinkle':  'n0',
        'sparkle':  'n1',
        'snow':     'n2',
        'interlock':'n3',
        'switch':   'n4',
        'slide':    'n5',
        'spray':    'n6',
        'starburst':'n7',
        'welcome':  'n8',
        'slots':    'n9', 'slot machine': 'n9',
        'thanks':   'nS', 'thank you': 'nS',
        'nosmoke':  'nU', 'no smoking': 'nU',
        'drinkdrive':'nV', 'dont drink and drive':'nV',
        'animal':   'nW',
        'fireworks':'nX',
        'car':      'nY',
        'bomb':     'nZ',
        'random':   'o'
    }
    text_attributes = {
        # colors
        'red':       '\0341',
        'green':     '\0342',
        'yellow':    '\0343',  'amber': '\0343',
        'rainbow1':  '\0349',
        'rainbow2':  '\034A',
        'mixed':     '\034B',
        'random':    '\034C',  # random colors

        # special controls (strings/text)
        'nohold':    '\011',
        'nodblwide': '\021',
        'dblwide':   '\022',
        'time':      '\023',
        'nofixed':   '\0360',
        'fixed':     '\0361',
        'slowest':   '\025',   'speed1': '\025',
        'slow':      '\026',   'speed2': '\026',
        'medium':    '\027',   'speed3': '\027',
        'fast':      '\030',   'speed4': '\030',
        'fastest':   '\031',   'speed5': '\031',
        'mmddyy_sl': '\0130',  # mm/dd/yy
        'ddmmyy_sl': '\0131',  # dd/mm/yy
        'mmddyy_hy': '\0132',  # mm-dd-yy
        'ddmmyy_hy': '\0133',  # dd-mm-yy
        'mmddyy_dt': '\0134',  # mm.dd.yy
        'ddmmyy_dt': '\0135',  # dd.mm.yy
        'mmddyy_sp': '\0136',  # mm dd yy
        'ddmmyy_sp': '\0137',  # dd mm yy
        'mmmddyyyy': '\0138',  # mmm,dd,yyyy
        'dow':       '\0139',  # day of week

        # special controls (text only)
        'nodblhigh':   '\0050',
        'dblhigh':     '\0051',
        'nodescenders':'\0060',
        'descenders':  '\0061',
        'noflashing':  '\0070',
        'flashing':    '\0071',
        'newpage':     '\014',
        'newline':     '\015',

        # inserted variable strings
        'S0':          '\0200',
        'S1':          '\0201',
        'S2':          '\0202',
        'S3':          '\0203',
        'S4':          '\0204',
        'S5':          '\0205',
        'S6':          '\0206',
        'S7':          '\0207',
        'S8':          '\0208',
        'S9':          '\0209',
        'SA':          '\020A',
        'SB':          '\020B',
        'SC':          '\020C',
        'SD':          '\020D',
        'SE':          '\020E',
        'SF':          '\020F',
        'SG':          '\020G',
        'SH':          '\020H',
        'SI':          '\020I',
        'SJ':          '\020J',
        'SK':          '\020K',
        'SL':          '\020L',
        'SM':          '\020M',
        'SN':          '\020N',
        'SO':          '\020O',
        'SP':          '\020P',
        'SQ':          '\020Q',
        'SR':          '\020R',
        'SS':          '\020S',
        'ST':          '\020T',
        'SU':          '\020U',
        'SV':          '\020V',
        'SW':          '\020W',
        'SX':          '\020X',
        'SY':          '\020Y',
        'SZ':          '\020Z',

        # character sets
        'normal5':   '\0321',  'cs1': '\0321',
        'normal7':   '\0323',  'cs3': '\0323',
        'fancy7':    '\0325',  'cs5': '\0325',
        'normal10':  '\0326',  'cs6': '\0326',
        'fancyfull': '\0328',  'cs8': '\0328',
        'normalfull':'\0329',  'cs9': '\0329',

        # special characters (strings/text)
        'halfspace': '\176',
        #'cents':     '\136',
    
        # special characters (text only)
        'block':     '\177',
        'Ccedila':   '\x80',
        'uuml':      '\x81',
        'eacute':    '\x82',
        'ahat':      '\x83',  # a + circumflex accent
        'auml':      '\x84',  # a + umlaut accent
        'agrave':    '\x85',  # a + grave accent
        'acirc':     '\x86',  # a + circle accent
        'ccedila':   '\x87',
        'ehat':      '\x88',
        'euml':      '\x89',
        'egrave':    '\x8a',
        'iuml':      '\x8b',
        'ihat':      '\x8c',
        'igrave':    '\x8d',
        'Auml':      '\x8e',
        'Acirc':     '\x8f',
        'Eacute':    '\x90',
        'ae':        '\x91',  # ae ligature
        'AE':        '\x92',
        'ohat':      '\x93',
        'ouml':      '\x94',
        'ograve':    '\x95',
        'uhat':      '\x96',
        'ugrave':    '\x97',
        'yuml':      '\x98',
        'Ouml':      '\x99',
        'Uuml':      '\x9a',
        'cents':     '\x9b',
        'GBP':       '\x9c',  # British Pound symbol
        'JPY':       '\x9d', 'yen': '\x9d',
        'percent':   '\x9e',
        'f':         '\x9f',  # f symbol
        'aacute':    '\xa0',  # a + acute accent
        'iacute':    '\xa1',
        'oacute':    '\xa2',
        'uacute':    '\xa3',
        'ntilde':    '\xa4',
        'Ntilde':    '\xa5',
        'aord':      '\xa6',  # a (feminine ordinal)
        'oord':      '\xa7',  # o (masculine ordinal)
        'iques':     '\xa8',  # inverted question mark
        'degree':    '\xa9',
        'iexcl':     '\xaa',  # inverted exclamation mark
        'space1':    '\xab',  # single-column space
        'theta':     '\xac',
        'Theta':     '\xad',
        'capos':     '\xae',  # c'
        'Capos':     '\xaf',  # C'
        'c':         '\xb0',  # c
        'C':         '\xb1',  # C
        'd':         '\xb2',  # d
        'D':         '\xb3',  # D
        's':         '\xb4',  # s
        'z':         '\xb5',  # z
        'Z':         '\xb6',  # Z
        'esset':     '\xb7',  # German esset
        'S':         '\xb8',  # S
        'Esset':     '\xb9',  # esset ??
        'Aacute':    '\xba',
        'Agrave':    '\xbb',
        'Aacuteapos':'\xbc',  # A + acute accent + '
        'aacuteapos':'\xbd',
        'Eacute':    '\xbe',
        'Iacute':    '\xbf',
        'Otilde':    '\xc0',
        'otilde':    '\xc1',

        # XXX etc.
    }
        
    def __init__(self, address):
        '''
        Constructor for a Spectrum readerboard unit object:
            SpectrumReaderboardUnit(address)

        Specify the address of the readerboard you are controlling.
        '''
        self.address = address

    def _packet(self, *cmdlist):
        '''Send a command packet to the readerboard.  These look like this:
            \1\1\1\1\1\1 <type> <address> [, <address> ...] 
            \2 <command> [\3 [<checksum>] [ \2 <command> ...]] \4
        where:
            <type> ::= general class of readerboard models to respond.
               the value 'Z' means 'any type' and is used here for now.
            <address> ::= <hexdigit> <hexdigit> | <hexdigit> '?'
               If a '?' is used, blocks of 16 boards can be addressed
               as a group.  Currently we only send our unique addr.
            <command> ::= one of the following:
                E hhmm        Set time of day (hhmm in decimal digits, 24-hr)
                E,mmddyy      Set current date
                E&n           Set day of week n=0 (Sun) - 6 (Sat)
                E'M           Set 24-hour time display
                E'S           Set 12-hour time display
                E!vv          Set speaker volume vv=00 (off) - FF (full)
                E,            Soft reset 
                E4            Clear errors
                E7xx          Set board address to xx (2 hex digits)
                E$ltkxxxxyyyy Allocate memory slot label <l> (single char),
                    of type <t> (A=text B=string D=bitmap), locked as <k>
                    (L=locked, U=unlocked), of xxxx (4 hex digits) bytes
                    in length (for bitmaps, xxxx is encoded as rrcc, for the
                    number of rows and columns).  yyyy=ssee (start/end time 
                    for text slots [use FF00]; 0000 for strings; 1000 for 
                    monochrome bitmaps, 2000 for 3-color bitmaps, and 4000
                    for 8-color bitmaps)
                    The default text area "A" doesn't need to be pre-allocated
                    before it can be used; the others all do.
                    locked or unlocked refers to access via IR remote control.
                    multiple slots can be listed as 11-byte blocks in the same E$
                    command.
                E(0           Beep once (2 sec.)
                E(1           Make triple beep (2 sec. total)
                E(2xxyz       Beep xx=freq (01-FE), y=duration (1-F), z=repeat
                    count (0-F)
                Al<textlist>  Write <textlist> to text label <l>.
                Gl<text>      Write <text> to string label <l>.
                Il<image>     Write DOTS PIC image data to label <l>.
                Ml<ximage>    Write ALPHAVISION DOTS PIC image data to <l>.
                E)<rtlist>    Set run-time table
            <rtlist> ::= <label> <start> <stop> <enabled>
            <label> ::= label of buffer to display (single character)
            <start> ::= start hour, 2 hex digits, or:
                FF  display always
                FE  display never
                FD  display all day
            <stop> ::= stop hour, 2 hex digits.
            <enabled> ::= '0' for false or '1' for true.
            <image> ::= <yy> <xx> <rowlist>
            <ximage> ::= <yyyy> <xxxx> <rowlist>
            <xx> ::= <hexdigit> <hexdigit> number of pixels wide (max FF)
            <yy> ::= <hexdigit> <hexdigit> number of pixels high (max 1F)
            <xxxx> ::= <hexdigit>*4 number of pixels wide (max FFFF)
            <yyyy> ::= <hexdigit>*4 number of pixels high (max FFFF)
            <rowlist> ::= <imgrow> | <rowlist> <imgrow>
            <imgrow> ::= <rowbits> CR [LF]
            <rowbits> ::= <rowbit> *<xx>
            <rowbit> ::= byte value for pixel color:
                \x30 off
                \x31 red
                \x32 green
                \x33 amber
                \x34 dim red
                \x35 dim green
                \x36 brown
                \x37 orange
                \x38 yellow
            <textlist> ::= list of: \33 <fill> <mode> <text>
            <fill> ::= Text alignment; One of these:
                ' '  align in middle
                '"'  align to top
                '&'  align to bottom
                '0'  fill display
            <mode> ::= Transition/display mode; One of these:
                a    rotate
                b    hold
                c    fl
                e    roll up
                f    roll down
                g    roll left
                h    roll right
                i    wipe up
                j    wipe down
                k    wipe left
                l    wipe right
                m    scroll
                p    roll in
                q    roll out
                r    wipe in
                s    wipe out
                t    comp*rot
                n0   twinkle
                n1   sparkle
                n2   snow
                n3   interlock
                n4   switch
                n5   slide
                n6   spray
                n7   starburst
                n8   welcome (animation)
                n9   slot machine (animation)
                nS   thank you (animation)
                nU   no smoking (animation)
                nV   don't drink and drive (animation)
                nW   animal (animation)
                nX   fireworks (animation)
                nY   car (animation)
                nZ   bomb (animation)
                o    random
            <text> ::= characters of message; may include these codes:
                \011  don't delay after presentation (no hold) (except rotates)
                \021  single-width characters
                \022  double-width characters
                \023  current time of day
                \0361 fixed-width characters
                \0360 proportional-width characters
                \025  speed 1 (slowest)
                \026  speed 2 (slow)
                \027  speed 3 (medium)
                \030  speed 4 (fast)
                \031  speed 5 (fastest)
                \0321 5-pixel-high characters
                \0323 7-pixel-high characters
                \0325 7-pixel-high fancy characters
                \0326 10-pixel-high characters
                \0328 full-height fancy characters
                \0329 full-height characters
                \0341 red
                \0342 green
                \0343 amber
                \0349 rainbow 1
                \034A rainbow 2
                \034B mixed colors
                \034C random colors
                \0050 double-high characters off (text only, not strings)
                \0051 double-high characters on  (text only, not strings)
                \0060 descenders off (text only, not strings)
                \0061 descenders on  (text only, not strings)
                \0070 flashing off (text only, not strings)
                \0071 flashing on  (text only, not strings)
                \014  new page
                \015  new line
                \020l insert label <l> here
                \0130 current date as mm/dd/yy
                \0131 current date as dd/mm/yy
                \0132 current date as mm-dd-yy
                \0133 current date as dd-mm-yy
                \0134 current date as mm.dd.yy
                \0135 current date as dd.mm.yy
                \0136 current date as mm dd yy
                \0137 current date as dd mm yy
                \0138 current date as mmm,dd,yyyy
                \0139 current day of week
                \03500 double stroke off
                \03501 double stroke on
                \03510 double wide off
                \03511 double wide on
                \03520 double high off
                \03521 double high on
                \03530 descenders off
                \03531 descenders on
                \03540 fixed-width off
                \03541 fixed-width on
                \03550 fancy characters off
                \03551 fancy characters on
        '''
        return ('\1\1\1\1\1\1Z%02X' % self.address) +\
            '\3'.join(['\2' + x for x in cmdlist]) + '\4'

    def _expandSpecials(self, text):
        if '$' in text:
            try:
                return Template(text).substitute(self.text_attributes)
            except KeyError:
                raise InvalidTextAttribute, "%s contains unknown attribute keyword sequences.  Use $$ for a literal dollar sign."
        return text

    def _text(self, text, align='fill', mode='hold', label='A'):
        '''Format text for inclusion in a command.

        The text strings can contain $ codes for special
        attributes, like $red to set red text.
        '''
        if align not in self.text_alignments:
            raise InvalidTextAlignment, "%s is not a valid text alignment" % align
        if mode not in self.text_modes:
            raise InvalidTextMode, "%s is not a valid text mode" % mode

        return 'A' + label[0] + '\033' + self.text_alignments[align] + self.text_modes[mode] + \
            self._expandSpecials(text)
        
    def _str(self, text, label='0'):
        '''Format strings for "included" registers in text messages'''

        return 'G' + label[0] + self._expandSpecials(text)

    def initialize_device(self):
        return self._packet('E,', self._text(''))
