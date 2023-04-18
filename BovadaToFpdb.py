#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2008-2012, Chaz Littlejohn
#    
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
########################################################################

import L10n
_ = L10n.get_translation()

# TODO: straighten out discards for draw games

import sys, copy
from HandHistoryConverter import *
import Card
from decimal_wrapper import Decimal

# Bovada HH Format

class Bovada(HandHistoryConverter):

    # Class Variables

    sitename = "Bovada"
    filetype = "text"
    codepage = ("utf8", "cp1252")
    siteId   = 21 # Needs to match id entry in Sites database
    summaryInFile = True
    copyGameHeader = True
    sym = {'USD': "\$", 'T$': "", "play": ""}         # ADD Euro, Sterling, etc HERE
    substitutions = {
                     'LEGAL_ISO' : "USD",      # legal ISO currency codes
                            'LS' : u"\$|", # legal currency symbols - Euro(cp1252, utf-8)
                           'PLYR': r'(?P<PNAME>.+?)',
                            'CUR': u"(\$|)",
                            'NUM' :u".,\d",
                    }
                    
    # translations from captured groups to fpdb info strings
    Lim_Blinds = {      '0.04': ('0.01', '0.02'),        
                        '0.08': ('0.02', '0.04'),         '0.10': ('0.02', '0.05'),
                        '0.20': ('0.05', '0.10'),         '0.25': ('0.05', '0.10'),
                        '0.40': ('0.10', '0.20'),         '0.50': ('0.10', '0.25'),
                        '1.00': ('0.25', '0.50'),         '1': ('0.25', '0.50'),
                        '2.00': ('0.50', '1.00'),         '2': ('0.50', '1.00'),
                        '4.00': ('1.00', '2.00'),         '4': ('1.00', '2.00'),
                        '6.00': ('1.50', '3.00'),         '6': ('1.50', '3.00'),
                        '8.00': ('2.00', '4.00'),         '8': ('2.00', '4.00'),
                       '10.00': ('2.50', '5.00'),        '10': ('2.50', '5.00'),
                       '16.00': ('4.00', '8.00'),        '16': ('4.00', '8.00'),
                       '20.00': ('5.00', '10.00'),       '20': ('5.00', '10.00'),
                       '30.00': ('7.50', '15.00'),       '30': ('7.50', '15.00'),
                       '40.00': ('10.00', '20.00'),      '40': ('10.00', '20.00'),
                       '60.00': ('15.00', '30.00'),      '60': ('15.00', '30.00'),
                       '80.00': ('20.00', '40.00'),      '80': ('20.00', '40.00'),
                      '100.00': ('25.00', '50.00'),     '100': ('25.00', '50.00'),
                  }

    limits = { 'No Limit':'nl', 'Pot Limit':'pl', 'Fixed Limit':'fl', 'Turbo': 'nl'}
    games = {                          # base, category
                               "HOLDEM" : ('hold','holdem'),
                                'OMAHA' : ('hold','omahahi'),
                           'OMAHA HiLo' : ('hold','omahahilo'),
                             'OMAHA_HL' : ('hold','omahahilo'),
                                '7CARD' : ('stud','studhi'),
                           '7CARD HiLo' : ('stud','studhilo'),
                             '7CARD_HL' : ('hold','studhilo'),
                      'HOLDEMZonePoker' : ('hold','holdem'),
                       'OMAHAZonePoker' : ('hold','omahahi'),
                  'OMAHA HiLoZonePoker' : ('hold','omahahilo'),
                      
               }
    currencies = {'$':'USD', '':'T$'}

    # Static regexes
    re_GameInfo     = re.compile(u"""
          (Ignition|Bovada|Bodog(\.com|\.eu|\sUK|\sCanada|88)?)\sHand\s\#C?(?P<HID>[0-9]+):?\s+
          ((?P<ZONE>Zone\sPoker\sID|TBL)\#(?P<TABLE>.+?)\s)?
          (?P<GAME>HOLDEM|OMAHA|OMAHA_HL|7CARD|7CARD\sHiLo|OMAHA\sHiLo|7CARD_HL|HOLDEMZonePoker|OMAHAZonePoker|OMAHA\sHiLoZonePoker)\s+
          (Tournament\s\#(M\-)?                # open paren of tournament info Tournament #2194767 TBL#1, 
          (?P<TOURNO>\d+)\sTBL\#(?P<TABLENO>\d+),
          \s)?
          (?P<HU>1\son\s1\s)? 
          (?P<LIMIT>No\sLimit|Fixed\sLimit|Pot\sLimit|Turbo)?
          (\s?Normal\s?)?
          (-\sLevel\s\d+?\s
          \(?                            # open paren of the stakes
          (?P<CURRENCY>%(LS)s|)?
          (?P<SB>[,.0-9]+)/(%(LS)s)?
          (?P<BB>[,.0-9]+)
          \s?(?P<ISO>%(LEGAL_ISO)s)?
          \))?
          (\s\[(?P<VERSION>MVS)\])?
          \s-\s
          (?P<DATETIME>.*$)
        """ % substitutions, re.MULTILINE|re.VERBOSE)

    re_PlayerInfo   = re.compile(u"""
          ^Seat\s(?P<SEAT>[0-9]+):\s
          %(PLYR)s\s(?P<HERO>\[ME\]\s)?
          \((%(LS)s)?(?P<CASH>[%(NUM)s]+)\sin\schips\)""" % substitutions, 
          re.MULTILINE|re.VERBOSE)
    
    re_PlayerInfoStud   = re.compile(u"""
         ^(?P<PNAME>Seat\+(?P<SEAT>[0-9]+))
         (?P<HERO>\s\[ME\])?:\s
         (%(LS)s)?(?P<CASH>[%(NUM)s]+)\sin\schips""" % substitutions, 
         re.MULTILINE|re.VERBOSE)
    
    re_PlayerSeat = re.compile(u"^Seat\+(?P<SEAT>[0-9]+)", re.MULTILINE|re.VERBOSE)
    re_Identify     = re.compile(u'(Ignition|Bovada|Bodog(\.com|\.eu|\sUK|\sCanada|88)?)\sHand')
    re_SplitHands   = re.compile('\n\n+')
    re_TailSplitHands   = re.compile('(\n\n\n+)')
    re_Button       = re.compile('Dealer : Set dealer\/Bring in spot \[(?P<BUTTON>\d+)\]', re.MULTILINE)
    re_Board1       = re.compile(r"Board \[(?P<FLOP>\S\S\S? \S\S\S? \S\S\S?)?\s+?(?P<TURN>\S\S\S?)?\s+?(?P<RIVER>\S\S\S?)?\]")
    re_Board2       = {
        "FLOP": re.compile(r"\*\*\* FLOP \*\*\* \[(?P<CARDS>\S\S \S\S \S\S)\]"),
        "TURN": re.compile(r"\*\*\* TURN \*\*\* \[\S\S \S\S \S\S\] \[(?P<CARDS>\S\S)\]"),
        "RIVER": re.compile(r"\*\*\* RIVER \*\*\* \[\S\S \S\S \S\S \S\S\] \[(?P<CARDS>\S\S)\]")
    } 
    re_DateTime     = re.compile("""(?P<Y>[0-9]{4})\-(?P<M>[0-9]{2})\-(?P<D>[0-9]{2})[\- ]+(?P<H>[0-9]+):(?P<MIN>[0-9]+):(?P<S>[0-9]+)""", re.MULTILINE)
    # These used to be compiled per player, but regression tests say
    # we don't have to, and it makes life faster.
    re_PostSB           = re.compile(r"^%(PLYR)s (\s?\[ME\]\s)?: (Ante\/Small (B|b)lind|Posts chip|Small (B|b)lind) (?P<CURRENCY>%(CUR)s)(?P<SB>[%(NUM)s]+)" %  substitutions, re.MULTILINE)
    re_PostBB           = re.compile(r"^%(PLYR)s (\s?\[ME\]\s)?: (Big (B|b)lind\/Bring in|Big (B|b)lind) (?P<CURRENCY>%(CUR)s)(?P<BB>[%(NUM)s]+)" %  substitutions, re.MULTILINE)
    re_Antes            = re.compile(r"^%(PLYR)s (\s?\[ME\]\s)?: Ante chip %(CUR)s(?P<ANTE>[%(NUM)s]+)" % substitutions, re.MULTILINE)
    re_BringIn          = re.compile(r"^%(PLYR)s (\s?\[ME\]\s)?: (Bring_in chip|Big (B|b)lind\/Bring in|Bring in)\s?(\(timeout\) )?%(CUR)s(?P<BRINGIN>[%(NUM)s]+)" % substitutions, re.MULTILINE)
    re_PostBoth         = re.compile(r"^%(PLYR)s (\s?\[ME\]\s)?: Posts dead chip %(CUR)s(?P<SBBB>[%(NUM)s]+)" %  substitutions, re.MULTILINE)
    re_HeroCards        = re.compile(r"^%(PLYR)s  ?\[ME\] : Card dealt to a spot \[(?P<NEWCARDS>.+?)\]" % substitutions, re.MULTILINE)
    re_Action           = re.compile(r"""(?P<ACTION>
                        ^%(PLYR)s\s(\s?\[ME\]\s)?:(\sD)?(?P<ATYPE>\s(B|b)ets|\sDouble\sbets|\sChecks|\s(R|r)aises|\sCalls?|\sFold|\sBring_in\schip|\sBig\sblind\/Bring\sin|\sAll\-in(\((raise|raise\-timeout)\))?|\sCard\sdealt\sto\sa\sspot)
                        (\schip\sinfo)?(\(timeout\))?(\s%(CUR)s(?P<BET>[%(NUM)s]+)(\sto\s%(CUR)s(?P<BETTO>[%(NUM)s]+))?|\s\[(?P<NEWCARDS>.+?)\])?)"""
                         %  substitutions, re.MULTILINE|re.VERBOSE)
    re_ShowdownAction   = re.compile(r"^%(PLYR)s (?P<HERO>\s?\[ME\]\s)?: Card dealt to a spot \[(?P<CARDS>.*)\]" % substitutions, re.MULTILINE)
    #re_ShownCards       = re.compile("^Seat (?P<SEAT>[0-9]+): %(PLYR)s %(BRKTS)s(?P<SHOWED>showed|mucked) \[(?P<CARDS>.*)\]( and won \([.\d]+\) with (?P<STRING>.*))?" % substitutions, re.MULTILINE)
    re_CollectPot1      = re.compile(r"^%(PLYR)s (\s?\[ME\]\s)?: Hand (R|r)esult(\-Side (P|p)ot)? %(CUR)s(?P<POT1>[%(NUM)s]+)" %  substitutions, re.MULTILINE)
    re_Bounty           = re.compile(r"^%(PLYR)s (\s?\[ME\]\s)?: BOUNTY PRIZE \[%(CUR)s(?P<BOUNTY>[%(NUM)s]+)\]" %  substitutions, re.MULTILINE)
    re_Dealt            = re.compile(r"^%(PLYR)s (\s?\[ME\]\s)?: Card dealt to a spot" % substitutions, re.MULTILINE)
    re_Buyin            = re.compile(r"(\s-\s\d+\s-\s(?P<TOURNAME>.+?))?\s-\s(?P<BUYIN>(?P<TICKET>TT)?(?P<BIAMT>[%(LS)s\d\.,]+)-(?P<BIRAKE>[%(LS)s\d\.,]+)?)\s-\s" % substitutions)
    re_Knockout         = re.compile(r"\s\((?P<BOUNTY>[%(LS)s\d\.,]+)\sKnockout" % substitutions)
    re_Stakes           = re.compile(r"(RING|ZONE)\s-\s(?P<CURRENCY>%(LS)s|)?(?P<SB>[%(NUM)s]+)-(%(LS)s)?(?P<BB>[%(NUM)s]+)" % substitutions)
    re_Summary          = re.compile(r"\*\*\*\sSUMMARY\s\*\*\*")
    re_Hole_Third       = re.compile(r"\*\*\*\s(3RD\sSTREET|HOLE\sCARDS)\s\*\*\*")
    re_ReturnBet        = re.compile(r"Return\suncalled\sportion", re.MULTILINE)
    #Small Blind : Hand result $19
    
    def compilePlayerRegexs(self, hand):
        subst = self.substitutions
        players = set(self.playersMap.keys())
        if not players <= self.compiledPlayers: # x <= y means 'x is subset of y'
            self.compiledPlayers = players
            subst['PLYR'] = "(?P<PNAME>" + "|".join(map(re.escape, players)) + ")"
            self.re_CollectPot2  = re.compile(u"""
                Seat[\+ ](?P<SEAT>[0-9]+):\s?%(PLYR)s
                (\sHI)?\s(%(LS)s)?(?P<POT1>[%(NUM)s]+)?
                (?P<STRING>[a-zA-Z ]+)
                (?P<CARDS1>\[[-a-zA-Z0-9 ]+\])
                (\sLOW?\s(%(LS)s)?(?P<POT2>[%(NUM)s]+))?
                """ % subst, re.MULTILINE|re.VERBOSE)

    def readSupportedGames(self):
        return [["ring", "hold", "nl"],
                ["ring", "hold", "pl"],
                ["ring", "hold", "fl"],
                
                ["ring", "stud", "fl"],
                
                ["tour", "hold", "nl"],
                ["tour", "hold", "pl"],
                ["tour", "hold", "fl"],
                
                ["tour", "stud", "fl"],
                ]

    def parseHeader(self, handText, whole_file):
        gametype = self.determineGameType(handText)
        if gametype['type'] == 'tour':
            handlist = re.split(self.re_SplitHands,  whole_file)
            result = re.findall(self.re_PlayerSeat, handlist[0])
            #gametype['maxSeats'] = len(result)
        return gametype

    def determineGameType(self, handText):
        info = {}            
        m = self.re_GameInfo.search(handText)
        if not m:
            tmp = handText[0:200]
            log.error(_("BovadaToFpdb.determineGameType: '%s'") % tmp)
            raise FpdbParseError
        
        m1 = self.re_Dealt.search(handText)
        m2 = self.re_Summary.split(handText)
        m3 = self.re_Hole_Third.split(handText)
        if not m1 or len(m2)!=2 or len(m3)>3:
            raise FpdbHandPartial("BovadaToFpdb.determineGameType: " + _("Partial hand history"))
        
        mg = m.groupdict()
        m = self.re_Stakes.search(self.in_path)
        if m: mg.update(m.groupdict())

        if 'LIMIT' in mg:
            if not mg['LIMIT']:
                info['limitType'] = 'nl'
            else:
                info['limitType'] = self.limits[mg['LIMIT']]
        if 'GAME' in mg:
            (info['base'], info['category']) = self.games[mg['GAME']]
            
        if 'SB' in mg:
            info['sb'] = self.clearMoneyString(mg['SB'])
        if 'BB' in mg:
            info['bb'] = self.clearMoneyString(mg['BB'])
            
        if 'TOURNO' in mg and mg['TOURNO'] is not None:
            info['type'] = 'tour'
            info['currency'] = 'T$'
        else:
            info['type'] = 'ring'
            info['currency'] = 'USD'
             
        if 'CURRENCY' in mg and mg['CURRENCY'] is not None:
            info['currency'] = self.currencies[mg['CURRENCY']]
            
        if 'Zone' in mg['GAME']:
            info['fast'] = True
        else:
            info['fast'] = False
            
        if info['limitType'] == 'fl' and info['bb'] is not None:
            if info['type'] == 'ring':
                try:
                    info['sb'] = self.Lim_Blinds[info['bb']][0]
                    info['bb'] = self.Lim_Blinds[info['bb']][1]
                except KeyError:
                    tmp = handText[0:200]
                    log.error(_("BovadaToFpdb.determineGameType: Lim_Blinds has no lookup for '%s' - '%s'") % (mg['BB'], tmp))
                    raise FpdbParseError
            else:
                info['sb'] = str((Decimal(info['sb'])/2).quantize(Decimal("0.01")))
                info['bb'] = str(Decimal(info['sb']).quantize(Decimal("0.01")))   

        return info

    def readHandInfo(self, hand):
        info = {}
        m = self.re_GameInfo.search(hand.handText)
        if m is None:
            tmp = hand.handText[0:200]
            log.error(_("BovadaToFpdb.readHandInfo: '%s'") % tmp)
            raise FpdbParseError
        
        info.update(m.groupdict())
        m = self.re_Buyin.search(self.in_path)
        if m: info.update(m.groupdict())
        hand.allInBlind = False
        m2 = self.re_Knockout.search(self.in_path)
        if m2: info.update(m2.groupdict())
        
        if "Hyper Turbo" in self.in_path:
            hand.speed = "Hyper"
        elif  "Turbo" in self.in_path:
            hand.speed = "Turbo"
        
        for key in info:
            if key == 'DATETIME':
                m1 = self.re_DateTime.finditer(info[key])
                datetimestr = "2000/01/01 00:00:00"  # default used if time not found
                for a in m1:
                    datetimestr = "%s/%s/%s %s:%s:%s" % (a.group('Y'), a.group('M'),a.group('D'),a.group('H'),a.group('MIN'),a.group('S'))
                    #tz = a.group('TZ')  # just assume ET??
                    #print "   tz = ", tz, " datetime =", datetimestr
                hand.startTime = datetime.datetime.strptime(datetimestr, "%Y/%m/%d %H:%M:%S") # also timezone at end, e.g. " ET"
                hand.startTime = HandHistoryConverter.changeTimezone(hand.startTime, "ET", "UTC")
            if key == 'HID':
                hand.handid = info[key]
            if key == 'TOURNO':
                hand.tourNo = info[key]
            if key == 'BUYIN':
                if info['TOURNO']!=None:
                    if info[key] == 'Freeroll':
                        hand.buyin = 0
                        hand.fee = 0
                        hand.buyinCurrency = "FREE"
                    else:
                        if info[key].find("$")!=-1:
                            hand.buyinCurrency="USD"
                        elif re.match("^[0-9+]*$", info[key]):
                            hand.buyinCurrency="play"
                        else:
                            #FIXME: handle other currencies, play money
                            log.error(_("BovadaToFpdb.readHandInfo: Failed to detect currency.") + " Hand ID: %s: '%s'" % (hand.handid, info[key]))
                            raise FpdbParseError
                    
                        if info.get('BOUNTY') != None:
                            info['BOUNTY'] = self.clearMoneyString(info['BOUNTY'].strip(u'$')) # Strip here where it isn't 'None'
                            hand.koBounty = int(100*Decimal(info['BOUNTY']))
                            hand.isKO = True
                        else:
                            hand.isKO = False
                            
                        info['BIAMT'] = self.clearMoneyString(info['BIAMT'].strip(u'$'))
                        
                        if info['BIRAKE']:
                            info['BIRAKE'] = self.clearMoneyString(info['BIRAKE'].strip(u'$'))
                        else:
                            info['BIRAKE'] = '0'
                        
                        if info['TICKET'] == None:
                            hand.buyin = int(100*Decimal(info['BIAMT']))
                            hand.fee = int(100*Decimal(info['BIRAKE']))
                        else:
                            hand.buyin = 0
                            hand.fee = 0
            if key == 'TABLE':
                if info.get('TABLENO'):
                    hand.tablename = info.get('TABLENO')
                elif info['ZONE'] and 'Zone' in info['ZONE']:
                    hand.tablename = info['ZONE'] + ' ' +info[key]
                else:
                    hand.tablename = info[key]        
            if key == 'MAX' and info[key] != None:
                hand.maxseats = int(info[key])
            if key == 'HU' and info[key] != None:
                hand.maxseats = 2
            if key == 'VERSION':
                hand.version = info[key]
                
        if not hand.maxseats:
            hand.maxseats = 9
            
        if not hand.version:
            hand.version = 'LEGACY'
    
    def readButton(self, hand):
        m = self.re_Button.search(hand.handText)
        if m:
            hand.buttonpos = int(m.group('BUTTON'))

    def readPlayerStacks(self, hand):
        self.playersMap, seatNo = {}, 1
        if hand.gametype['base'] in ("stud"):
            m = self.re_PlayerInfoStud.finditer(hand.handText)
        else:
            m = self.re_PlayerInfo.finditer(hand.handText)
        for a in m:
            if re.search(r"%s (\s?\[ME\]\s)?: Card dealt to a spot" % re.escape(a.group('PNAME')), hand.handText) or hand.version == 'MVS':
                if not hand.buttonpos and a.group('PNAME')=='Dealer':
                    hand.buttonpos = int(a.group('SEAT'))
                if a.group('HERO'):
                    self.playersMap[a.group('PNAME')] = 'Hero'
                else:
                    self.playersMap[a.group('PNAME')] = 'Seat %s' % a.group('SEAT')
                hand.addPlayer(seatNo, self.playersMap[a.group('PNAME')], self.clearMoneyString(a.group('CASH')))
            seatNo += 1
        if len(hand.players)==0:
            tmp = hand.handText[0:200]
            log.error(_("BovadaToFpdb.readPlayerStacks: '%s'") % tmp)
            raise FpdbParseError
        elif len(hand.players)==10:
            hand.maxseats = 10
        
    def playerSeatFromPosition(self, source, handid, position):
        player = self.playersMap.get(position)
        if player is None:
            log.error(_("Hand.%s: '%s' unknown player seat from position: '%s'") % (source, handid, position))
            raise FpdbParseError
        return player            

    def markStreets(self, hand):
        # PREFLOP = ** Dealing down cards **
        # This re fails if,  say, river is missing; then we don't get the ** that starts the river.
        if hand.gametype['base'] == "hold":
            street, firststreet = 'PREFLOP', 'PREFLOP'
        else:
            street, firststreet = 'THIRD', 'THIRD'  
        m = self.re_Action.finditer(self.re_Hole_Third.split(hand.handText)[0])
        allinblind = 0
        for action in m:
            if action.group('ATYPE') == ' All-in':
                allinblind+=1
        m = self.re_Action.finditer(self.re_Hole_Third.split(hand.handText)[-1])
        dealtIn = len(hand.players) - allinblind
        streetactions, streetno, players, i, contenders, bets, acts = 0, 1, dealtIn, 0, dealtIn, 0, None
        for action in m:
            if action.groupdict()!=acts or streetactions == 0:
                acts = action.groupdict()
                #print "DEBUG: %s, %s, %s" % (street, acts['PNAME'], acts['ATYPE']), action.group('BET'), streetactions, players, contenders
                player = self.playerSeatFromPosition('BovadaToFpdb.markStreets', hand.handid, action.group('PNAME'))
                if action.group('ATYPE') == ' Fold':
                    contenders -= 1
                elif action.group('ATYPE') in (' Raises', ' raises'):
                    if streetno==1: bets = 1
                    streetactions, players = 0, contenders
                elif action.group('ATYPE') in (' Bets', ' bets', ' Double bets'):
                    streetactions, players, bets = 0, contenders, 1
                elif action.group('ATYPE') in (' All-in(raise)', 'All-in(raise-timeout)'):
                    streetactions, players = 0, contenders
                    contenders -= 1
                elif action.group('ATYPE') == ' All-in':
                    if bets == 0 and streetno>1:
                        streetactions, players, bets = 0, contenders, 1
                    contenders -= 1
                if action.group('ATYPE') != ' Card dealt to a spot':
                    if action.group('ATYPE')!=' Big blind/Bring in' or hand.gametype['base'] == 'stud':
                        streetactions += 1
                hand.streets[street] += action.group('ACTION') + '\n'
                #print street, action.group('PNAME'), action.group('ATYPE'), streetactions, players, contenders
                if streetactions == players:
                    streetno += 1
                    if streetno < len(hand.actionStreets):
                        street = hand.actionStreets[streetno]
                    streetactions, players, bets = 0, contenders, 0
                
        if not hand.streets.get(firststreet):
            hand.streets[firststreet] = hand.handText
        if hand.gametype['base'] == "hold":
            if True: #hand.gametype['fast']:
                for street in ('FLOP', 'TURN', 'RIVER'):
                    m1 = self.re_Board2[street].search(hand.handText)
                    if m1 and m1.group('CARDS') and not hand.streets.get(street):
                        hand.streets[street] = m1.group('CARDS')
            else:
                m1 = self.re_Board1.search(hand.handText)
                for street in ('FLOP', 'TURN', 'RIVER'):
                    if m1 and m1.group(street) and not hand.streets.get(street):
                        hand.streets[street] = m1.group(street)
            

    def readCommunityCards(self, hand, street): # street has been matched by markStreets, so exists in this hand
        if True: #hand.gametype['fast']:
            m = self.re_Board2[street].search(hand.handText)
            if m and m.group('CARDS'):
                hand.setCommunityCards(street, m.group('CARDS').split(' '))
        else:
            if street in ('FLOP','TURN','RIVER'):   # a list of streets which get dealt community cards (i.e. all but PREFLOP)
                m = self.re_Board1.search(hand.handText)
                if m and m.group(street):
                    cards = m.group(street).split(' ')
                    hand.setCommunityCards(street, cards)

    def readAntes(self, hand):
        antes = None
        m = self.re_Antes.finditer(hand.handText)
        for a in m:
            if a.groupdict()!=antes:
                antes = a.groupdict()
                player = self.playerSeatFromPosition('BovadaToFpdb.readAntes', hand.handid, antes['PNAME'])
                hand.addAnte(player, self.clearMoneyString(antes['ANTE']))
    
    def readBringIn(self, hand):
        m = self.re_BringIn.search(hand.handText,re.DOTALL)
        if m:
            #~ logging.debug("readBringIn: %s for %s" %(m.group('PNAME'),  m.group('BRINGIN')))
            player = self.playerSeatFromPosition('BovadaToFpdb.readBringIn', hand.handid, m.group('PNAME'))
            hand.addBringIn(player,  self.clearMoneyString(m.group('BRINGIN')))            
            
        if hand.gametype['sb'] == None and hand.gametype['bb'] == None:
            hand.gametype['sb'] = "1"
            hand.gametype['bb'] = "2"
        
    def readBlinds(self, hand):
        sb, bb, acts, postsb, postbb, both = None, None, None, None, None, None
        if not self.re_ReturnBet.search(hand.handText):
            hand.setUncalledBets(True)
        for a in self.re_PostSB.finditer(hand.handText):
            if postsb!=a.groupdict():
                postsb = a.groupdict()
                player = self.playerSeatFromPosition('BovadaToFpdb.readBlinds.postSB', hand.handid, postsb['PNAME'])
                hand.addBlind(player, 'small blind', self.clearMoneyString(postsb['SB']))
                if not hand.gametype['sb']:
                    hand.gametype['sb'] = self.clearMoneyString(postsb['SB'])
            sb = self.clearMoneyString(postsb['SB'])
            self.allInBlind(hand, 'PREFLOP', a, 'small blind')
        for a in self.re_PostBB.finditer(hand.handText):
            if postbb!=a.groupdict():
                postbb = a.groupdict()
                player = self.playerSeatFromPosition('BovadaToFpdb.readBlinds.postBB', hand.handid, 'Big Blind')
                hand.addBlind(player, 'big blind', self.clearMoneyString(postbb['BB']))
                self.allInBlind(hand, 'PREFLOP', a, 'big blind')
                if not hand.gametype['bb']:
                    hand.gametype['bb'] = self.clearMoneyString(postbb['BB'])
                bb = self.clearMoneyString(postbb['BB'])
                if not hand.gametype['currency']:
                    if postbb['CURRENCY'].find("$")!=-1:
                        hand.gametype['currency']="USD"
                    elif re.match("^[0-9+]*$", postbb['CURRENCY']):
                        hand.gametype['currency']="play"
        for a in self.re_Action.finditer(self.re_Hole_Third.split(hand.handText)[0]):
            if acts!=a.groupdict():
                acts = a.groupdict()
                if acts['ATYPE'] == ' All-in':
                    re_Ante_Plyr  = re.compile(r"^" + re.escape(acts['PNAME']) + " (\s?\[ME\]\s)?: Ante chip %(CUR)s(?P<ANTE>[%(NUM)s]+)" % self.substitutions, re.MULTILINE)
                    m = self.re_Antes.search(hand.handText)
                    m1 = re_Ante_Plyr.search(hand.handText)
                    if (not m or m1):
                        player = self.playerSeatFromPosition('BovadaToFpdb.readBlinds.postBB', hand.handid, acts['PNAME'])
                        if acts['PNAME'] == 'Big Blind':
                            hand.addBlind(player, 'big blind', self.clearMoneyString(acts['BET']))
                            self.allInBlind(hand, 'PREFLOP', a, 'big blind')
                        elif acts['PNAME'] == 'Small Blind' or (acts['PNAME'] == 'Dealer' and len(hand.players)==2):
                            hand.addBlind(player, 'small blind', self.clearMoneyString(acts['BET']))
                            self.allInBlind(hand, 'PREFLOP', a, 'small blind')
                    elif m:
                        player = self.playerSeatFromPosition('BovadaToFpdb.readAntes', hand.handid, acts['PNAME'])
                        hand.addAnte(player, self.clearMoneyString(acts['BET']))
                        self.allInBlind(hand, 'PREFLOP', a, 'antes')
        self.fixBlinds(hand)
        for a in self.re_PostBoth.finditer(hand.handText):
            if both!=a.groupdict():
                both = a.groupdict()
                player = self.playerSeatFromPosition('BovadaToFpdb.readBlinds.postBoth', hand.handid, both['PNAME'])
                hand.addBlind(player, 'both', self.clearMoneyString(both['SBBB']))
                self.allInBlind(hand, 'PREFLOP', a, 'both')
        
        
        
    def fixBlinds(self, hand):
        if hand.gametype['sb'] == None and hand.gametype['bb'] != None:
            BB = str(Decimal(hand.gametype['bb']) * 2)
            if self.Lim_Blinds.get(BB) != None:
                hand.gametype['sb'] = self.Lim_Blinds.get(BB)[0]
        elif hand.gametype['bb'] == None and hand.gametype['sb'] != None:
            for k, v in self.Lim_Blinds.iteritems():
                if hand.gametype['sb'] == v[0]:
                    hand.gametype['bb'] = v[1]
        if hand.gametype['sb'] == None or hand.gametype['bb'] == None:
            log.error(_("BovadaToFpdb.fixBlinds: Failed to fix blinds") + " Hand ID: %s" % (hand.handid, ))
            raise FpdbParseError
        hand.sb = hand.gametype['sb']
        hand.bb = hand.gametype['bb']

    def readHoleCards(self, hand):
#    streets PREFLOP, PREDRAW, and THIRD are special cases beacause
#    we need to grab hero's cards
        for street in ('PREFLOP', 'DEAL'):
            if street in hand.streets.keys():
                foundDict = None
                m = self.re_HeroCards.finditer(hand.handText)
                for found in m:
                    if found.groupdict()!=foundDict:
                        foundDict = found.groupdict()
                        hand.hero = 'Hero'
                        newcards = found.group('NEWCARDS').split(' ')
                        hand.addHoleCards(street, hand.hero, closed=newcards, shown=False, mucked=False, dealt=True)
                    
        for street, text in hand.streets.iteritems():
            if not text or street in ('PREFLOP', 'DEAL'): continue  # already done these
            m = self.re_ShowdownAction.finditer(hand.streets[street])
            foundDict = None
            for found in m:
                if foundDict!=found.groupdict():
                    foundDict = found.groupdict()
                    player = self.playerSeatFromPosition('BovadaToFpdb.readHoleCards', hand.handid, found.group('PNAME'))
                    if street != 'SEVENTH' or found.group('HERO'):
                        newcards = found.group('CARDS').split(' ')
                        oldcards = []
                    else:
                        oldcards = found.group('CARDS').split(' ')
                        newcards = []
    
                    if street == 'THIRD' and found.group('HERO'): # hero in stud game
                        hand.hero = 'Hero'
                        hand.dealt.add(player) # need this for stud??
                        hand.addHoleCards(street, player, closed=newcards[0:2], open=[newcards[2]], shown=False, mucked=False, dealt=False)
                    else:
                        hand.addHoleCards(street, player, open=newcards, closed=oldcards, shown=False, mucked=False, dealt=False)

    def readAction(self, hand, street):
        acts = None
        m = self.re_Action.finditer(hand.streets[street])
        for action in m:
            if acts!=action.groupdict():
                acts = action.groupdict()
                player = self.playerSeatFromPosition('BovadaToFpdb.readAction', hand.handid, action.group('PNAME'))
                #print "DEBUG: %s, %s, %s, %s, %s" % (street, acts['PNAME'], player, acts['ATYPE'], action.group('BET'))
                if action.group('ATYPE') not in (' Checks', ' Fold', ' Card dealt to a spot', ' Big blind/Bring in') and not hand.allInBlind:
                    hand.setUncalledBets(False)
                if action.group('ATYPE') == ' Fold':
                    hand.addFold( street, player)
                elif action.group('ATYPE') == ' Checks':
                    hand.addCheck( street, player)
                elif action.group('ATYPE') == ' Calls' or action.group('ATYPE') == ' Call':
                    if not action.group('BET'):
                        log.error("BovadaToFpdb.readAction: Amount not found in Call %s" % hand.handid)
                        raise FpdbParseError
                    hand.addCall( street, player, self.clearMoneyString(action.group('BET')) )
                elif action.group('ATYPE') in (' Raises', ' raises', ' All-in(raise)', ' All-in(raise-timeout)'):
                    if action.group('BETTO'):
                        bet = self.clearMoneyString(action.group('BETTO'))
                    elif action.group('BET'):
                        bet = self.clearMoneyString(action.group('BET'))
                    else:
                        log.error("BovadaToFpdb.readAction: Amount not found in Raise %s" % hand.handid)
                        raise FpdbParseError
                    hand.addRaiseTo( street, player, bet )
                elif action.group('ATYPE') in (' Bets', ' bets', ' Double bets'):
                    if not action.group('BET'):
                        log.error("BovadaToFpdb.readAction: Amount not found in Bet %s" % hand.handid)
                        raise FpdbParseError
                    hand.addBet( street, player, self.clearMoneyString(action.group('BET')) )
                elif action.group('ATYPE') == ' All-in':
                    if not action.group('BET'):
                        log.error("BovadaToFpdb.readAction: Amount not found in All-in %s" % hand.handid)
                        raise FpdbParseError
                    hand.addAllIn( street, player, self.clearMoneyString(action.group('BET')) )
                    self.allInBlind(hand, street, action, action.group('ATYPE'))
                elif action.group('ATYPE') == ' Bring_in chip':
                    pass
                elif action.group('ATYPE') in (' Card dealt to a spot', ' Big blind/Bring in'):
                    pass
                else:
                    log.debug(_("DEBUG:") + " " + _("Unimplemented %s: '%s' '%s'") % ("readAction", action.group('PNAME'), action.group('ATYPE')))
                
    def allInBlind(self, hand, street, action, actiontype):
        if street in ('PREFLOP', 'DEAL'):
            player = self.playerSeatFromPosition('BovadaToFpdb.allInBlind', hand.handid, action.group('PNAME'))
            if hand.stacks[player]==0 and not self.re_ReturnBet.search(hand.handText):
                hand.setUncalledBets(True)
                hand.allInBlind = True

    def readShowdownActions(self, hand):
# TODO: pick up mucks also??
        if hand.gametype['base'] in ("hold"):
            for shows in self.re_ShowdownAction.finditer(hand.handText):            
                cards = shows.group('CARDS').split(' ')
                player = self.playerSeatFromPosition('BovadaToFpdb.readShowdownActions', hand.handid, shows.group('PNAME'))
                hand.addShownCards(cards, player)

    def readCollectPot(self,hand):
        if self.re_CollectPot2.search(hand.handText):
            re_CollectPot = self.re_CollectPot2
        else:
            re_CollectPot = self.re_CollectPot1
        for m in re_CollectPot.finditer(hand.handText.replace(" [ME]", "") if hand.version == 'MVS' else hand.handText):# [ME]
            collect, pot = m.groupdict(), 0
            if 'POT1' in collect and collect['POT1']!=None:
                pot += Decimal(self.clearMoneyString(collect['POT1']))
            if 'POT2' in collect and collect['POT2']!=None:
                pot += Decimal(self.clearMoneyString(collect['POT2']))
            if pot>0: 
                player = self.playerSeatFromPosition('BovadaToFpdb.readCollectPot', hand.handid, collect['PNAME'])
                hand.addCollectPot(player=player,pot=str(pot))

    def readShownCards(self,hand):
        pass
    

    def readTourneyResults(self, hand):
        """Reads knockout bounties and add them to the koCounts dict"""
        for a in self.re_Bounty.finditer(hand.handText):
            player = self.playerSeatFromPosition('BovadaToFpdb.readCollectPot', hand.handid, a.group('PNAME'))
            if player not in hand.koCounts:
                hand.koCounts[player] = 0
            hand.koCounts[player] += 1    
        