#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Copyright 2016, Chaz Littlejohn
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

import sys
from HandHistoryConverter import *
from decimal_wrapper import Decimal

# Winning HH Format

class Winning(HandHistoryConverter):

    # Class Variables
    
    version = 0
    sitename = "WinningPoker"
    filetype = "text"
    codepage = ("utf-16", "utf8", "cp1252")
    siteId   = 24 # Needs to match id entry in Sites database
    sym = {
        'USD': "\$", 
        'T$': "", 
        "play": ""
    } 
    substitutions = {
        'LEGAL_ISO' : "USD|TB|CP",      # legal ISO currency codes
        'LS' : u"\$|", # legal currency symbols - Euro(cp1252, utf-8)
        'PLYR': r'(?P<PNAME>.+?)',
        'NUM' :u".,\dK",
        'CUR': u"(\$|)",
        'BRKTS': r'(\(button\)\s|\(small\sblind\)\s|\(big\sblind\)\s|\(button\)\s\(small\sblind\)\s|\(button\)\s\(big\sblind\)\s)?',
    }
    games1 = {# base, category
        "Hold'em" : ('hold','holdem'),
        "Six Plus Hold'em" : ('hold','6_holdem'),
        'Omaha' : ('hold','omahahi'),
        'Omaha HiLow' : ('hold','omahahilo'),
        'Seven Cards Stud' : ('stud','studhi'),
        'Seven Cards Stud HiLow' : ('stud','studhilo')
    }
    games2 = {# base, category
        "Holdem" : ('hold','holdem'),
        'Omaha' : ('hold','omahahi'),
        'Omaha H/L' : ('hold','omahahilo'),
        '5Card Omaha': ('hold','5_omahahi'),
        '5Card Omaha H/L': ('hold','5_omaha8'),
        #"Six Plus Hold'em" : ('hold','6_holdem'),
        '7Stud' : ('stud','studhi'),
        '7Stud H/L' : ('stud','studhilo')
    }
    limits = { 
          'No Limit':'nl', 
          'Pot Limit':'pl', 
          'Fixed Limit':'fl',
          'All-in or Fold Limit':'al'
    }
    speeds = {
        'Turbo': 'Turbo',
        'Hyper Turbo': 'Hyper',
        'Regular': 'Normal'
    }
    buyin = {
        'CAP': 'cap',
        'Short': 'shallow'
    }
    
    SnG_Fee = {  
        50: {'Hyper': 0, 'Turbo': 0, 'Normal': 5},
        100: {'Hyper': 0, 'Turbo': 0, 'Normal': 10},
        150: {'Hyper': 11, 'Turbo': 12, 'Normal': 15},
        300: {'Hyper': 20, 'Turbo': 25, 'Normal': 30},
        500: {'Hyper': 30, 'Turbo': 45, 'Normal': 50},
        1000: {'Hyper': 55, 'Turbo': 90, 'Normal': 100},
        1500: {'Hyper': 80, 'Turbo': 140, 'Normal': 150},
        2000: {'Hyper': 100, 'Turbo': 175, 'Normal': 200},
        3000: {'Hyper': 130, 'Turbo': 275, 'Normal': 300},
        5000: {'Hyper': 205, 'Turbo': 475, 'Normal': 500},
        8000: {'Hyper': 290, 'Turbo': 650, 'Normal': 800},
        10000: {'Hyper': 370, 'Turbo': 800, 'Normal': 900}
    }
    
    HUSnG_Fee = {
        200: {'Hyper': 10, 'Turbo': 0, 'Normal': 17},
        220: {'Hyper': 0, 'Turbo': 16, 'Normal': 0},
        240: {'Hyper': 10, 'Turbo': 0, 'Normal': 0},
        500: {'Hyper': 0, 'Turbo': 0, 'Normal': 25},
        550: {'Hyper': 0, 'Turbo': 25, 'Normal': 0},
        600: {'Hyper': 18, 'Turbo': 0, 'Normal': 0},
        1000: {'Hyper': 25, 'Turbo': 0, 'Normal': 50},
        1100: {'Hyper': 0, 'Turbo': 50, 'Normal': 0},
        1200: {'Hyper': 25, 'Turbo': 0, 'Normal': 0},
        2000: {'Hyper': 50, 'Turbo': 0, 'Normal': 100},
        2200: {'Hyper': 0, 'Turbo': 100, 'Normal': 0},
        2400: {'Hyper': 50, 'Turbo': 0, 'Normal': 0},
        3000: {'Hyper': 70, 'Turbo': 0, 'Normal': 150},
        3300: {'Hyper': 0, 'Turbo': 150, 'Normal': 0},
        3600: {'Hyper': 75, 'Turbo': 0, 'Normal': 0},
        5000: {'Hyper': 100, 'Turbo': 0, 'Normal': 250},
        5500: {'Hyper': 0, 'Turbo': 250, 'Normal': 0},
        6000: {'Hyper': 125, 'Turbo': 0, 'Normal': 0},
        10000: {'Hyper': 200, 'Turbo': 0, 'Normal': 450},
        11000: {'Hyper': 0, 'Turbo': 450, 'Normal': 0},
        12000: {'Hyper': 225, 'Turbo': 0, 'Normal': 0},
        15000: {'Hyper': 266, 'Turbo': 0, 'Normal': 0},
        20000: {'Hyper': 400, 'Turbo': 0, 'Normal': 900},
        22000: {'Hyper': 0, 'Turbo': 900, 'Normal': 0},
        24000: {'Hyper': 450, 'Turbo': 0, 'Normal': 0},
        30000: {'Hyper': 600, 'Turbo': 0, 'Normal': 1200},
        33000: {'Hyper': 0, 'Turbo': 1200, 'Normal': 0},
        36000: {'Hyper': 600, 'Turbo': 0, 'Normal': 0},
        40000: {'Hyper': 800, 'Turbo': 0, 'Normal': 0},
        50000: {'Hyper': 0, 'Turbo': 0, 'Normal': 5000},
        55000: {'Hyper': 0, 'Turbo': 2000, 'Normal': 0},
        60000: {'Hyper': 1000, 'Turbo': 0, 'Normal': 0},
        110000: {'Hyper': 0, 'Turbo': 3000, 'Normal': 0},
        120000: {'Hyper': 1500, 'Turbo': 0, 'Normal': 0}
    }
    currencies = { '$':'USD', '':'T$'}
    
    re_GameInfo1 = re.compile(u"""
        Game\sID:\s(?P<HID>\d+)\s
        (?P<SB>[%(NUM)s]+)/(?P<BB>[%(NUM)s]+)\s
        (?P<TABLE>.+?)?\s
        \((?P<GAME>(Six\sPlus\s)?Hold\'em|Omaha|Omaha\sHiLow|Seven\sCards\sStud|Seven\sCards\sStud\sHiLow)\)
        (\s(?P<MAX>\d+\-max))?$
        """ % substitutions, 
        re.MULTILINE|re.VERBOSE
    )
    
    #Hand #78708209 - Omaha H/L(Fixed Limit) - $20.00/$40.00 - 2019/07/18 15:13:01 UTC
    #Hand #68217077 - Holdem(No Limit) - $0.05/$0.10 - 2019/06/28 02:38:17 UTC
    #Game Hand #80586589 - Tournament #11182752 - Holdem(No Limit) - Level 15 (250.00/500.00)- 2019/07/21 17:44:50 UTC
    #Game Hand #82980175 - Tournament #11212445 - Omaha H/L(Pot Limit) - Level 1 (250.00/500.00)- 2019/07/25 02:31:33 UTC
    #Game Hand #1296393662 - $5,000 GTD Tournament #27099516 - Holdem(No Limit) - Level 10 (3000.00/6000.00)- 2022/07/11 01:11:44 UTC
    
    re_GameInfo2 = re.compile(u"""
          (Game\s)?Hand\s\#(?P<HID>[0-9]+)\s\-\s
          (
          (?P<TOUR>([\$.,\dKkmM]+\sGTD\s)?Tournament\s\#(?P<TOURNO>\d+)\s\-\s) # open paren of tournament info
          )?
          # close paren of tournament info
          (?P<GAME>Holdem|Omaha|Omaha\sH/L|7Stud|7Stud\sH/L|5Card\sOmaha|5Card\sOmaha\sH/L)
          \((?P<LIMIT>No\sLimit|Fixed\sLimit|Pot\sLimit|All\-in\sor\sFold\sLimit)\)\s\-\s
          (Level\s(?P<LEVEL>[IVXLC\d]+)\s)?
          \(?                            # open paren of the stakes
          (?P<CURRENCY>%(LS)s|)?
          ((?P<SB>[.0-9]+)/(%(LS)s)?(?P<BB>[.0-9]+))
          \)?                        # close paren of the stakes
          \s?\-\s
          (?P<DATETIME>.*$)
        """ % substitutions, re.MULTILINE|re.VERBOSE)
    
    #Seat 6: puccini (5.34).
    re_PlayerInfo1 = re.compile(u"""
        ^Seat\s(?P<SEAT>[0-9]+):\s
        (?P<PNAME>.*)\s
        \((?P<CASH>[%(NUM)s]+)\)
        \.$
        """ % substitutions, 
        re.MULTILINE|re.VERBOSE
    )
    
    re_PlayerInfo2 = re.compile(u"""
        ^\s?Seat\s(?P<SEAT>[0-9]+):\s
        (?P<PNAME>.*)\s
        \((%(LS)s)?(?P<CASH>[,.0-9]+)
        \)
        (?P<SITOUT>\sis\ssitting\sout)?""" % substitutions, 
        re.MULTILINE|re.VERBOSE
    )
    
    re_DateTime1 = re.compile("""
        ^Game\sstarted\sat:\s
        (?P<Y>[0-9]{4})/(?P<M>[0-9]{1,2})/(?P<D>[0-9]{1,2})\s
        (?P<H>[0-9]+):(?P<MIN>[0-9]+):(?P<S>[0-9]+)
        $""", 
        re.MULTILINE|re.VERBOSE
    )
    
    #2019/07/18 15:13:01 UTC
    re_DateTime2 = re.compile("""(?P<Y>[0-9]{4})\/(?P<M>[0-9]{2})\/(?P<D>[0-9]{2})[\- ]+(?P<H>[0-9]+):(?P<MIN>[0-9]+):(?P<S>[0-9]+)""", re.MULTILINE)
    
    #$2.20 Turbo Heads-up, Table 1
    #$2.40 Hyper Turbo Heads-up, Table 1
    #$10 Freeroll - On Demand, Table 13
    #$25 GTD - On Demand, Table 1
    #$5 Regular 9-Max, Table 1 (Hold'em)
        
    re_Table1 = re.compile(u"""
        ^(?P<CURRENCY>[%(LS)s]|)?(?P<BUYIN>[%(NUM)s]+)\s
        ((?P<GAME>(Six\sPlus\s)?Holdem|PLO|PLO8|Omaha\sHi/Lo|Omaha|PL\sOmaha|PL\sOmaha\sHi/Lo|PLO\sHi/Lo)\s?)?
        ((?P<SPECIAL>(GTD|Freeroll|FREEBUY|Freebuy))\s?)?
        ((?P<SPEED>(Turbo|Hyper\sTurbo|Regular))\s?)?
        ((?P<MAX>(\d+\-Max|Heads\-up|Heads\-Up))\s?)?
        (?P<OTHER>.*?)
        ,\sTable\s(?P<TABLENO>\d+)
        """ % substitutions,  
        re.VERBOSE|re.MULTILINE
    )
    
    re_Table2 = re.compile("Table\s\'(?P<TABLENO>\d+)\'")
    
    #St. Lucie 6-max Seat #1 is the button
    #Table '1' 9-max Seat #3 is the button
    #Blitz Poker 6-max Seat #1 is the button
    #Table '25' 9-max Seat #8 is the button

    re_HandInfo = re.compile("""
          ^(?P<TABLE>.+?)\s
          ((?P<MAX>\d+)-max\s)
          (?P<PLAY>\(Play\sMoney\)\s)?
          (Seat\s\#(?P<BUTTON>\d+)\sis\sthe\sbutton)?""", 
          re.MULTILINE|re.VERBOSE)
    
    re_TourneyName1 = re.compile(u"(?P<TOURNAME>.*),\sTable\s\d+")
    re_TourneyName2 = re.compile(u"TN\-(?P<TOURNAME>.+?)\sGAMETYPE")
    re_GTD          = re.compile(u"(?P<GTD>[%(NUM)s]+)\sGTD" % substitutions)
    re_buyinType    = re.compile("\((?P<BUYINTYPE>CAP|Short)\)", re.MULTILINE)
    re_buyin        = re.compile("%(CUR)s(?P<BUYIN>[,.0-9]+)" %  substitutions, re.MULTILINE)
    re_Step         = re.compile("\sStep\s(?P<STEPNO>\d+)")

    re_Identify     = re.compile(u'Game\sID:\s\d+|Hand\s\#\d+\s\-\s')
    re_Identify_Old = re.compile(u'Game\sID:\s\d+')
    re_SplitHands   = re.compile('\n\n')
    re_Button1      = re.compile('Seat (?P<BUTTON>\d+) is the button')
    re_Button2      = re.compile('Seat #(?P<BUTTON>\d+) is the button')
    re_Board        = re.compile(r"\[(?P<CARDS>.+)\]")    
    re_TourNo       = re.compile("\sT(?P<TOURNO>\d+)\-")
    re_File1        = re.compile("HH\d{8}\s(T\d+\-)?G\d+")
    re_File2        = re.compile("(?P<TYPE>CASHID|SITGOID|RUSHID|SCHEDULEDID)")
    
    re_PostSB1       = re.compile(r"^Player %(PLYR)s has small blind \((?P<SB>[%(NUM)s]+)\)" %  substitutions, re.MULTILINE)
    re_PostBB1       = re.compile(r"^Player %(PLYR)s has big blind \((?P<BB>[%(NUM)s]+)\)" %  substitutions, re.MULTILINE)
    re_Posts1        = re.compile(r"^Player %(PLYR)s posts \((?P<SBBB>[%(NUM)s]+)\)" %  substitutions, re.MULTILINE)
    re_Antes1        = re.compile(r"^Player %(PLYR)s (posts )?ante \((?P<ANTE>[%(NUM)s]+)\)" % substitutions, re.MULTILINE)
    re_BringIn1      = re.compile(r"^Player %(PLYR)s bring in \((?P<BRINGIN>[%(NUM)s]+)\)" % substitutions, re.MULTILINE)
    re_HeroCards1    = re.compile(r"^Player %(PLYR)s received card: \[(?P<CARD>.+)\]" %  substitutions, re.MULTILINE)
    
    re_PostSB2       = re.compile(r"^%(PLYR)s posts the small blind %(CUR)s(?P<SB>[,.0-9]+)" %  substitutions, re.MULTILINE)
    re_PostBB2       = re.compile(r"^%(PLYR)s posts the big blind %(CUR)s(?P<BB>[,.0-9]+)" %  substitutions, re.MULTILINE)
    re_PostBoth2     = re.compile(r"^%(PLYR)s posts dead %(CUR)s(?P<SBBB>[,.0-9]+)" %  substitutions, re.MULTILINE)
    re_Posts2        = re.compile(r"^%(PLYR)s posts %(CUR)s(?P<SBBB>[,.0-9]+)" %  substitutions, re.MULTILINE)
    re_Antes2        = re.compile(r"^%(PLYR)s posts ante %(CUR)s(?P<ANTE>[,.0-9]+)" % substitutions, re.MULTILINE)
    re_BringIn2      = re.compile(r"^%(PLYR)s brings[- ]in( low|) %(CUR)s(?P<BRINGIN>[,.0-9]+)" % substitutions, re.MULTILINE)
    re_HeroCards2    = re.compile(r"^Dealt to %(PLYR)s(?: \[(?P<OLDCARDS>.+?)\])?( \[(?P<NEWCARDS>.+?)\])" % substitutions, re.MULTILINE)
    re_Uncalled      = re.compile('Uncalled bet \(%(CUR)s(?P<BET>[,.\d]+)\) returned to' %  substitutions, re.MULTILINE)
    
    re_Action1       = re.compile(r"""
        ^Player\s(%(PLYR)s)?\s(?P<ATYPE>bets|checks|raises|calls|folds|allin|straddle|caps|cap)
        (\s\((?P<BET>[%(NUM)s]+)\))?
        $""" %  substitutions, 
        re.MULTILINE|re.VERBOSE
    )
    
    re_Action2       = re.compile(r"""
        ^%(PLYR)s(?P<ATYPE>\sbets|\schecks|\sraises|\scalls|\sfolds|\scaps|\scap|\sstraddle)
        (\s%(CUR)s(?P<BET>[,.\d]+))?(\sto\s%(CUR)s(?P<BETTO>[,.\d]+))? 
        \s*(and\sis\sall\-in)?\s*$"""
        %  substitutions, re.MULTILINE|re.VERBOSE
    )
    
    #Player lessthanrocko shows: Two pairs. 8s and 5s [3s 3h]. Bets: 420. Collects: 0. Loses: 420.
    #*Player ChazDazzle shows: Full House (5/8) [7s 5s]. Bets: 420. Collects: 840. Wins: 420.
    #*Player fullstacker shows: Flush, A high [2s 8h 2h Jd] Low hand (A A 2 3 4 8 ).Bets: 0.50. Collects: 0.95. Wins: 0.45.
    
    #*Player ChazDazzle shows: High card A [6h 10d 2c As 7d 4d 9s] Low hand (A A 2 4 6 7 ).Bets: 3.55. Collects: 3.53. Loses: 0.02.
    #*Player KickAzzJohnny shows: Two pairs. 8s and 3s [5d 3d 3s 6s 8s 8h Ad]. Bets: 3.55. Collects: 3.52. Loses: 0.03.
    
    re_ShownCards1       = re.compile(r"""
        ^\*?Player\s%(PLYR)s\sshows:\s
        (?P<STRING>.+?)\s
        \[(?P<CARDS>.*)\]
        (\sLow\shand\s\((?P<STRING2>.+?)\s?\))?
        \.""" %  substitutions, 
        re.MULTILINE|re.VERBOSE
    )
    
    #Seat 5: LitAF did not show and won $0.25
    #Seat 6: Thrash370 showed [Td Ad Qd 4s] and won 60600.00 with HI - a straight, Queen high [Qd Jh Td 9d 8d] | LO - [8,5,4,2,1]
    re_ShownCards2 = re.compile(r"""
        ^Seat\s(?P<SEAT>[0-9]+):\s%(PLYR)s\s%(BRKTS)s
        (?P<SHOWED>showed|mucked)\s\[(?P<CARDS>.+?)\](\sand\s(lost|(won|collected)\s%(CUR)s(?P<POT>[,\.\d]+))
        \swith (?P<STRING>.+?)
        (,\sand\s(won\s\(%(CUR)s[\.\d]+\)|lost)\swith\s(?P<STRING2>.*))?)?        
        $"""                                
        % substitutions, 
        re.MULTILINE|re.VERBOSE
    )
    
    re_CollectPot1 = re.compile(r"""
        ^\*?Player\s%(PLYR)s\s
        (does\snot\sshow|shows|mucks)
        .+?\.\s?
        Bets:\s[%(NUM)s]+\.\s
        Collects:\s(?P<POT>[%(NUM)s]+)\.\s
        (Wins|Loses):\s[%(NUM)s]+\.?
        $""" %  substitutions, 
        re.MULTILINE|re.VERBOSE
    )
    
    #Seat 5: LitAF did not show and won $0.25
    #Seat 6: Thrash370 showed [Td Ad Qd 4s] and won 60600.00 with HI - a straight, Queen high [Qd Jh Td 9d 8d] | LO - [8,5,4,2,1]
    re_CollectPot2 = re.compile(r"""
        Seat\s(?P<SEAT>[0-9]+):\s%(PLYR)s\s%(BRKTS)s
        (did\snot\sshow\sand\swon|showed\s\[.+?\]\sand\s(won|collected))\s%(CUR)s(?P<POT>[,.\d]+)
        (,\smucked|\swith.*|)
        """ %  substitutions, 
        re.MULTILINE|re.VERBOSE
    )
    #AssFungus collected $92.25 from main pot 1
    re_CollectPot3 = re.compile(r"^%(PLYR)s collected %(CUR)s(?P<POT>[,.\d]+)" %  substitutions, re.MULTILINE)
    
    def compilePlayerRegexs(self,  hand):
        pass

    def readSupportedGames(self):
        return [
            ["ring", "hold", "nl"],
            ["ring", "hold", "fl"],
            ["ring", "hold", "pl"],
            ["ring", "hold", "al"],

            ["ring", "stud", "fl"],
            
            ["tour", "hold", "nl"],
            ["tour", "hold", "fl"],
            ["tour", "hold", "pl"],
            ["tour", "hold", "al"],
            
            ["tour", "stud", "fl"]
        ]

    def determineGameType(self, handText):
        if self.re_Identify_Old.search(handText):
            self.version = 1
            return self._determineGameType1(handText)
        else:
            self.version = 2
            return self._determineGameType2(handText)
    
    def _determineGameType1(self, handText):
        info = {}
        if not self.re_File1.search(self.in_path):
            tmp = "Invalid filename: %s" % self.in_path
            log.debug(_("WinningToFpdb.determineGameType: '%s'") % tmp)
            raise FpdbHandPartial(tmp)
            
        m = self.re_GameInfo1.search(handText)
        if not m:
            tmp = handText[0:200]
            log.error(_("WinningToFpdb.determineGameType: '%s'") % tmp)
            raise FpdbParseError

        mg = m.groupdict()
        m1 = self.re_TourNo.search(self.in_path)
        if m1: mg.update(m1.groupdict())
        
        if 'GAME' in mg:
            (info['base'], info['category']) = self.games1[mg['GAME']]
        if 'SB' in mg:
            info['sb'] = mg['SB']
        if 'BB' in mg:
            info['bb'] = mg['BB']
            
        if info['base'] == 'stud':
            info['limitType'] = 'fl'
        else:
            m2 = self.re_PostBB1.search(handText)
            if m2:
                bb = self.clearMoneyString(m2.group('BB'))
                if Decimal(self.clearMoneyString(info['sb'])) == Decimal(bb):
                    info['limitType'] = 'fl'
            
            if info.get('limitType') == None:
                if 'omaha' in info['category']:
                    info['limitType'] = 'pl'
                else:
                    info['limitType'] = 'nl'
                
        if 'TOURNO' in mg and mg['TOURNO'] is not None:
            info['type'] = 'tour'
        else:
            info['type'] = 'ring'
            
        if 'TABLE' in mg and mg['TABLE'] is not None:
            if re.match('PM\s',mg['TABLE']):
                info['currency'] = 'play'
            elif info['type'] == 'tour':
                info['currency'] = 'T$'
            else:
                info['currency'] = 'USD'
            
            if '(Cap)' in mg['TABLE']:
                info['buyinType'] = 'cap'
            elif '(Short)' in mg['TABLE']:
                info['buyinType'] = 'shallow'
            else:
                info['buyinType'] = 'regular'
        else:
            info['currency'] = 'T$'

        if info['limitType'] == 'fl' and info['bb'] is not None:
            info['sb'] = str((Decimal(mg['SB'])/2).quantize(Decimal("0.01")))
            info['bb'] = str(Decimal(mg['SB']).quantize(Decimal("0.01")))    

        return info
    
    def _determineGameType2(self, handText):
        info = {}            
        m = self.re_GameInfo2.search(handText)
        if not m:
            tmp = handText[0:200]
            log.error(_("WinningToFpdb._determineGameType2: '%s'") % tmp)
            raise FpdbParseError        
        
        mg = m.groupdict()
        
        m1 = self.re_File2.search(self.in_path)
        if m1: mg.update(m1.groupdict())
        
        if 'LIMIT' in mg:
            info['limitType'] = self.limits[mg['LIMIT']]
        if 'GAME' in mg:
            (info['base'], info['category']) = self.games2[mg['GAME']]
        if 'SB' in mg:
            info['sb'] = mg['SB']
        if 'BB' in mg:
            info['bb'] = mg['BB']
        if 'CURRENCY' in mg and mg['CURRENCY'] is not None:
            info['currency'] = self.currencies[mg['CURRENCY']]
            
        if 'TYPE' in mg and 'RUSHID' == mg['TYPE']:
            info['fast'] = True
        else:
            info['fast'] = False
            
        if 'TOURNO' in mg and mg['TOURNO'] is None:
            info['type'] = 'ring'
        else:
            info['type'] = 'tour'
        
        if info.get('currency') in ('T$', None) and info['type']=='ring':
            info['currency'] = 'play'

        if info['limitType'] == 'fl' and info['bb'] is not None:
            info['sb'] = str((Decimal(mg['SB'])/2).quantize(Decimal("0.01")))
            info['bb'] = str(Decimal(mg['SB']).quantize(Decimal("0.01")))

        return info

    def readHandInfo(self, hand):
        if self.version == 1:
            self._readHandInfo1(hand)
        else:
            self._readHandInfo2(hand)
        
    def _readHandInfo1(self, hand):
        #First check if partial
        if hand.handText.count('------ Summary ------')!=1:
            raise FpdbHandPartial(_("Hand is not cleanly split into pre and post Summary"))
        
        info = {}
        m  = self.re_GameInfo1.search(hand.handText)
        m2 = self.re_DateTime1.search(hand.handText)
        if m is None or m2 is None:
            tmp = hand.handText[0:200]
            log.error(_("WinningToFpdb.readHandInfo: '%s'") % tmp)
            raise FpdbParseError

        info.update(m.groupdict())
        
        m1 = self.re_TourNo.search(self.in_path)
        if m1: info.update(m1.groupdict())

        datetimestr = "%s/%s/%s %s:%s:%s" % (m2.group('Y'), m2.group('M'), m2.group('D'), m2.group('H'), m2.group('MIN'), m2.group('S'))
        hand.startTime = datetime.datetime.strptime(datetimestr, "%Y/%m/%d %H:%M:%S") # also timezone at end, e.g. " ET"
        hand.startTime = HandHistoryConverter.changeTimezone(hand.startTime, self.import_parameters['timezone'], "UTC")
        
        if 'TOURNO' in info:
            hand.tourNo = info['TOURNO']
            
        if 'HID' in info:
            hand.handid = info['HID']
            
        if 'MAX' in info and info['MAX'] != None:
            hand.maxseats = int(info['MAX'].replace('-max', ''))
            
        if not hand.maxseats:
            if hand.gametype['base'] == 'stud':
                hand.maxseats = 8
            elif hand.gametype['type'] == 'ring':
                hand.maxseats = 9
            else:
                hand.maxseats = 10
        
        if 'TABLE' in info and info['TABLE'] is not None:
            if hand.tourNo:
                hand.buyin = 0
                hand.fee = 0
                hand.buyinCurrency="NA" 
                hand.tablename = 1
                m3 = self.re_Table1.search(info['TABLE'])                
                if m3 is not None:
                    tableinfo = m3.groupdict()
                    if 'SPECIAL' in tableinfo and tableinfo['SPECIAL'] != None:
                        if tableinfo['SPECIAL'] in ('Freeroll', 'FREEBUY', 'Freebuy'):
                            hand.buyinCurrency="FREE"
                        hand.guaranteeAmt = int(100*Decimal(self.clearMoneyString(tableinfo['BUYIN'])))
                        
                    if hand.guaranteeAmt == 0:
                        hand.buyinCurrency="USD"
                        hand.buyin = int(100*Decimal(self.clearMoneyString(tableinfo['BUYIN'])))
                    
                    if 'MAX' in tableinfo and tableinfo['MAX'] != None:
                        n = tableinfo['MAX'].replace('-Max', '')
                        if n in ('Heads-up', 'Heads-Up'):
                            hand.maxseats = 2
                        else:
                            hand.maxseats = int(n)
                    
                    if 'SPEED' in tableinfo and tableinfo['SPEED'] != None:
                        hand.speed = self.speeds[tableinfo['SPEED']]                            
                        if hand.maxseats==2 and hand.buyin in self.HUSnG_Fee:
                            hand.fee = self.HUSnG_Fee[hand.buyin][hand.speed]
                            hand.isSng = True
                        if hand.maxseats!=2 and hand.buyin in self.SnG_Fee:
                            hand.fee = self.SnG_Fee[hand.buyin][hand.speed]
                            hand.isSng = True
                        
                    hand.tablename = int(m3.group('TABLENO'))

                if "On Demand" in info['TABLE']:
                    hand.isOnDemand = True
                    
                if " KO" in info['TABLE'] or "Knockout" in info['TABLE']:
                    hand.isKO = True
                    
                if "R/A" in info['TABLE']:
                    hand.isRebuy = True
                    hand.isAddOn = True
                    
                m4 = self.re_TourneyName1.search(info['TABLE'])
                if m4:
                    hand.tourneyName = m4.group('TOURNAME')
            else:
                hand.tablename = info['TABLE']
                buyin_type = self.re_buyinType.search(info['TABLE'])
                if buyin_type:
                    hand.gametype['buyinType'] = self.buyin[buyin_type.group('BUYINTYPE')]
        else:
            hand.buyin = 0
            hand.fee = 0
            hand.buyinCurrency="NA" 
            hand.tablename = 1
            
    def _readHandInfo2(self, hand):
        #First check if partial
        if hand.handText.count('*** SUMMARY ***')!=1:
            raise FpdbHandPartial(_("Hand is not cleanly split into pre and post Summary"))
        
        info = {}
        m  = self.re_GameInfo2.search(hand.handText)
        m1 = self.re_HandInfo.search(hand.handText)
        if m is None or m1 is None:
            tmp = hand.handText[0:200]
            log.error(_("WinningToFpdb.readHandInfo: '%s'") % tmp)
            raise FpdbParseError

        info.update(m.groupdict())
        info.update(m1.groupdict())
        
        for key in info:
            if key == 'DATETIME':
                datetimestr = "2000/01/01 00:00:00"  # default used if time not found
                m2 = self.re_DateTime2.finditer(info[key])
                for a in m2:
                    datetimestr = "%s/%s/%s %s:%s:%s" % (a.group('Y'), a.group('M'),a.group('D'),a.group('H'),a.group('MIN'),a.group('S'))
                    #tz = a.group('TZ')  # just assume ET??
                    #print "   tz = ", tz, " datetime =", datetimestr
                hand.startTime = datetime.datetime.strptime(datetimestr, "%Y/%m/%d %H:%M:%S") # also timezone at end, e.g. " ET"
            if key == 'HID':
                hand.handid = info[key]
            if key == 'TOURNO':
                hand.tourNo = info[key]
            if key == 'LEVEL':
                hand.level = info[key]
            if key == 'TABLE':
                if info['TOURNO'] is not None:            
                    hand.buyin = 0
                    hand.fee = 0
                    hand.buyinCurrency = "FREE" #FIXME
                                     
                    m2 = self.re_Table2.match(info[key])
                    if m2:
                        hand.tablename = m2.group('TABLENO')
                else:
                    hand.tablename = info[key]
            if key == 'BUTTON':
                hand.buttonpos = info[key]
            if key == 'MAX' and info[key] != None:
                hand.maxseats = int(info[key])
                
        if 'SCHEDULEDID' in self.in_path:
            m3 = self.re_TourneyName2.search(self.in_path)
            if m3:
                hand.tourneyName = m3.group('TOURNAME').replace('{BACKSLASH}', '\\')
                m4 = self.re_GTD.search(hand.tourneyName)
                if m4:
                    hand.isGuarantee = True
                    hand.guaranteeAmt = int(100*Decimal(self.clearMoneyString(m4.group('GTD'))))
                if 'Satellite' in hand.tourneyName:
                    hand.isSatellite = True
                if 'Shootout' in hand.tourneyName:
                    hand.isShootout = True
                    
        elif 'SITGOID' in self.in_path:
            hand.isSng = True
            m3 = self.re_TourneyName2.search(self.in_path)
            if m3:
                hand.tourneyName = m3.group('TOURNAME').replace('{BACKSLASH}', '\\')                        
                if ' Hyper Turbo ' in hand.tourneyName:
                    speed = 'Hyper Turbo'
                elif ' Turbo ' in hand.tourneyName:
                    speed = 'Turbo'
                else:
                    speed = 'Regular'
                    
                hand.speed = self.speeds[speed]
                
                m4 = self.re_buyin.match(hand.tourneyName)
                if m4:
                    hand.buyinCurrency="USD"
                    hand.buyin = int(100*Decimal(self.clearMoneyString(m4.group('BUYIN'))))
                    
                    if hand.maxseats==2 and hand.buyin in self.HUSnG_Fee:
                        hand.fee = self.HUSnG_Fee[hand.buyin][hand.speed]
                    if hand.maxseats!=2 and hand.buyin in self.SnG_Fee:
                        hand.fee = self.SnG_Fee[hand.buyin][hand.speed]
                        
                m5 = self.re_Step.search(hand.tourneyName)
                if m5:
                    hand.isStep = True
                    hand.stepNo = int(m5.group('STEPNO'))
                
        elif 'RUSHID' in self.in_path:
            (hand.gametype['fast'], hand.isFast) = (True, True)
    
    def readButton(self, hand):
        if self.version == 1:
            self._readButton1(hand)
        else:
            self._readButton2(hand)
            
    def _readButton1(self, hand):
        m = self.re_Button1.search(hand.handText)
        if m:
            hand.buttonpos = int(m.group('BUTTON'))
        else:
            log.info('readButton: ' + _('not found'))
            
    def _readButton2(self, hand):
        m = self.re_Button2.search(hand.handText)
        if m:
            hand.buttonpos = int(m.group('BUTTON'))
        else:
            log.info('readButton: ' + _('not found'))

    def readPlayerStacks(self, hand):
        if self.version == 1:
            self._readPlayerStacks1(hand)
        else:
            self._readPlayerStacks2(hand)
            
    def _readPlayerStacks1(self, hand):
        pre, post = hand.handText.split('------ Summary ------')
        m = self.re_PlayerInfo1.finditer(pre)
        for a in m:
            hand.addPlayer(int(a.group('SEAT')), a.group('PNAME'), self.clearMoneyString(a.group('CASH')))
    
    def _readPlayerStacks2(self, hand):
        pre, post = hand.handText.split('*** SUMMARY ***')
        m = self.re_PlayerInfo2.finditer(pre)
        for a in m:
            hand.addPlayer(int(a.group('SEAT')), a.group('PNAME'), self.clearMoneyString(a.group('CASH')))
    
    def markStreets(self, hand):
        if self.version ==1:
            self._markStreets1(hand)
        else:
            self._markStreets2(hand)

    def _markStreets1(self, hand):
        if hand.gametype['base'] in ("hold"):
            m =  re.search(r"(?P<PREFLOP>.+(?=\*\*\* FLOP \*\*\*:)|.+)"
                       r"(\*\*\* FLOP \*\*\*:(?P<FLOP> (\[\S\S\S?] )?\[\S\S\S? ?\S\S\S? \S\S\S?].+(?=\*\*\* TURN \*\*\*:)|.+))?"
                       r"(\*\*\* TURN \*\*\*: \[\S\S\S? \S\S\S? \S\S\S?] (?P<TURN>\[\S\S\S?\].+(?=\*\*\* RIVER \*\*\*:)|.+))?"
                       r"(\*\*\* RIVER \*\*\*: \[\S\S\S? \S\S\S? \S\S\S? \S\S\S?] ?(?P<RIVER>\[\S\S\S?\].+))?", hand.handText,re.DOTALL)
        elif hand.gametype['base'] in ("stud"):
            m =  re.search(r"(?P<THIRD>.+(?=\*\*\* Third street \*\*\*)|.+)"
                           r"(\*\*\* Third street \*\*\*(?P<FOURTH>.+(?=\*\*\* Fourth street \*\*\*)|.+))?"
                           r"(\*\*\* Fourth street \*\*\*(?P<FIFTH>.+(?=\*\*\* Fifth street \*\*\*)|.+))?"
                           r"(\*\*\* Fifth street \*\*\*(?P<SIXTH>.+(?=\*\*\* Sixth street \*\*\*)|.+))?"
                           r"(\*\*\* Sixth street \*\*\*(?P<SEVENTH>.+))?", hand.handText,re.DOTALL)
        hand.addStreets(m)
        
    def _markStreets2(self, hand):
        if hand.gametype['base'] in ("hold"):
            m =  re.search(r"\*\*\* HOLE CARDS \*\*\*(?P<PREFLOP>(.+(?P<FLOPET>\[\S\S\]))?.+(?=\*\*\* (FLOP|FIRST FLOP|FLOP 1) \*\*\*)|.+)"
                       r"(\*\*\* FLOP \*\*\*(?P<FLOP> (\[\S\S\] )?\[(\S\S ?)?\S\S \S\S\].+(?=\*\*\* (TURN|FIRST TURN|TURN 1) \*\*\*)|.+))?"
                       r"(\*\*\* TURN \*\*\* \[\S\S \S\S \S\S] (?P<TURN>\[\S\S\].+(?=\*\*\* (RIVER|FIRST RIVER|RIVER 1) \*\*\*)|.+))?"
                       r"(\*\*\* RIVER \*\*\* \[\S\S \S\S \S\S \S\S] (?P<RIVER>\[\S\S\].+))?"
                       r"(\*\*\* (FIRST FLOP|FLOP 1) \*\*\*(?P<FLOP1> (\[\S\S\] )?\[(\S\S ?)?\S\S \S\S\].+(?=\*\*\* (FIRST TURN|TURN 1) \*\*\*)|.+))?"
                       r"(\*\*\* (FIRST TURN|TURN 1) \*\*\* \[\S\S \S\S \S\S] (?P<TURN1>\[\S\S\].+(?=\*\*\* (FIRST RIVER|RIVER 1) \*\*\*)|.+))?"
                       r"(\*\*\* (FIRST RIVER|RIVER 1) \*\*\* \[\S\S \S\S \S\S \S\S] (?P<RIVER1>\[\S\S\].+?(?=\*\*\* (SECOND (FLOP|TURN|RIVER)|(FLOP|TURN|RIVER) 2) \*\*\*)|.+))?"
                       r"(\*\*\* (SECOND FLOP|FLOP 2) \*\*\*(?P<FLOP2> (\[\S\S\] )?\[\S\S ?\S\S \S\S\].+(?=\*\*\* (SECOND TURN|TURN 2) \*\*\*)|.+))?"
                       r"(\*\*\* (SECOND TURN|TURN 2) \*\*\* \[\S\S \S\S \S\S] (?P<TURN2>\[\S\S\].+(?=\*\*\* (SECOND RIVER|RIVER 2) \*\*\*)|.+))?"
                       r"(\*\*\* (SECOND RIVER|RIVER 2) \*\*\* \[\S\S \S\S \S\S \S\S] (?P<RIVER2>\[\S\S\].+))?", hand.handText,re.DOTALL)
        elif hand.gametype['base'] in ("stud"):
            m =  re.search(r"(?P<ANTES>.+(?=\*\*\* 3rd STREET \*\*\*)|.+)"
                           r"(\*\*\* 3rd STREET \*\*\*(?P<THIRD>.+(?=\*\*\* 4th STREET \*\*\*)|.+))?"
                           r"(\*\*\* 4th STREET \*\*\*(?P<FOURTH>.+(?=\*\*\* 5th STREET \*\*\*)|.+))?"
                           r"(\*\*\* 5th STREET \*\*\*(?P<FIFTH>.+(?=\*\*\* 6th STREET \*\*\*)|.+))?"
                           r"(\*\*\* 6th STREET \*\*\*(?P<SIXTH>.+(?=\*\*\* 7th STREET \*\*\*)|.+))?"
                           r"(\*\*\* 7th STREET \*\*\*(?P<SEVENTH>.+))?", hand.handText,re.DOTALL)
        hand.addStreets(m)
    
    def readCommunityCards(self, hand, street):
        if self.version == 1:
            self._readCommunityCards1(hand, street)
        else:
            self._readCommunityCards2(hand, street)
        if street in ('FLOP1', 'TURN1', 'RIVER1', 'FLOP2', 'TURN2', 'RIVER2'):
            hand.runItTimes = 2

    def _readCommunityCards1(self, hand, street): # street has been matched by markStreets, so exists in this hand
        m = self.re_Board.search(hand.streets[street])
        if m:
            hand.setCommunityCards(street, [c.replace("10", "T") for c in m.group('CARDS').split(' ')])
        else:
            log.error("WinningToFpdb._readCommunityCards1: No community cards found on %s %s" % (street, hand.handid))
            raise FpdbParseError
        
    def _readCommunityCards2(self, hand, street): # street has been matched by markStreets, so exists in this hand
        m = self.re_Board.search(hand.streets[street])
        if m:
            hand.setCommunityCards(street, m.group('CARDS').split(' '))
        else:
            log.error("WinningToFpdb._readCommunityCards2: No community cards found on %s %s" % (street, hand.handid))
            raise FpdbParseError

    def readAntes(self, hand):
        if self.version == 1:
            self._readAntes1(hand)
        else:
            self._readAntes2(hand)
    
    def _readAntes1(self, hand):
        log.debug(_("reading antes"))
        m = self.re_Antes1.finditer(hand.handText)
        for player in m:
            #~ logging.debug("hand.addAnte(%s,%s)" %(player.group('PNAME'), player.group('ANTE')))
            hand.addAnte(player.group('PNAME'), player.group('ANTE'))
            
    def _readAntes2(self, hand):
        log.debug(_("reading antes"))
        m = self.re_Antes2.finditer(hand.handText)
        for player in m:
            #~ logging.debug("hand.addAnte(%s,%s)" %(player.group('PNAME'), player.group('ANTE')))
            hand.addAnte(player.group('PNAME'), player.group('ANTE'))
    
    def readBringIn(self, hand):
        if self.version == 1:
            self._readBringIn1(hand)
        else:
            self._readBringIn2(hand)
        
    def _readBringIn1(self, hand):
        m = self.re_BringIn1.search(hand.handText,re.DOTALL)
        if m:
            #~ logging.debug("readBringIn: %s for %s" %(m.group('PNAME'),  m.group('BRINGIN')))
            hand.addBringIn(m.group('PNAME'),  m.group('BRINGIN'))
            
    def _readBringIn2(self, hand):
        m = self.re_BringIn2.search(hand.handText,re.DOTALL)
        if m:
            #~ logging.debug("readBringIn: %s for %s" %(m.group('PNAME'),  m.group('BRINGIN')))
            hand.addBringIn(m.group('PNAME'),  m.group('BRINGIN'))
        
    def readBlinds(self, hand):
        if self.version == 1:
            self._readBlinds1(hand)
        else:
            self._readBlinds2(hand)
            
    def _readBlinds1(self, hand):
        liveBlind = True
        for a in self.re_PostSB1.finditer(hand.handText):
            if liveBlind:
                hand.addBlind(a.group('PNAME'), 'small blind', a.group('SB'))
                liveBlind = False
            else:
                pass
                # Post dead blinds as ante
                #hand.addBlind(a.group('PNAME'), 'secondsb', a.group('SB'))
        for a in self.re_PostBB1.finditer(hand.handText):
            hand.addBlind(a.group('PNAME'), 'big blind', a.group('BB'))
        for a in self.re_Posts1.finditer(hand.handText):
            if Decimal(self.clearMoneyString(a.group('SBBB'))) == Decimal(hand.bb):
                hand.addBlind(a.group('PNAME'), 'big blind', a.group('SBBB'))
            else:
                hand.addBlind(a.group('PNAME'), 'secondsb', a.group('SBBB'))
                
    def _readBlinds2(self, hand):
        liveBlind = True
        for a in self.re_PostSB2.finditer(hand.handText):
            if liveBlind:
                hand.addBlind(a.group('PNAME'), 'small blind', a.group('SB'))
                liveBlind = False
            else:
                pass
                # Post dead blinds as ante
                #hand.addBlind(a.group('PNAME'), 'secondsb', a.group('SB'))
        for a in self.re_PostBB2.finditer(hand.handText):
            hand.addBlind(a.group('PNAME'), 'big blind', a.group('BB'))
        for a in self.re_PostBoth2.finditer(hand.handText):
            hand.addBlind(a.group('PNAME'), 'both', self.clearMoneyString(a.group('SBBB')))
        for a in self.re_Posts2.finditer(hand.handText):
            if Decimal(self.clearMoneyString(a.group('SBBB'))) == Decimal(hand.bb):
                hand.addBlind(a.group('PNAME'), 'big blind', a.group('SBBB'))
            else:
                hand.addBlind(a.group('PNAME'), 'secondsb', a.group('SBBB'))

    def readHoleCards(self, hand):
        if self.version == 1:
            self._readHoleCards1(hand)
        else:
            self._readHoleCards2(hand)
            
    def _readHoleCards1(self, hand):
#    streets PREFLOP, PREDRAW, and THIRD are special cases beacause
#    we need to grab hero's cards
        for street in ('PREFLOP', 'DEAL'):
            if street in hand.streets.keys():
                newcards = []
                m = self.re_HeroCards1.finditer(hand.streets[street])
                for found in m:
                    hand.hero = found.group('PNAME')
                    newcards.append(found.group('CARD').replace("10", "T"))
                if hand.hero:
                    hand.addHoleCards(street, hand.hero, closed=newcards, shown=False, mucked=False, dealt=True)

        for street, text in hand.streets.iteritems():
            if not text or street in ('PREFLOP', 'DEAL'): continue  # already done these
            m = self.re_HeroCards1.finditer(hand.streets[street])
            players = {}
            for found in m:
                player = found.group('PNAME')
                if players.get(player) == None:
                    players[player] = []
                players[player].append(found.group('CARD').replace("10", "T"))
            
            for player, cards in players.iteritems():
                if street == 'THIRD': # hero in stud game
                    hand.dealt.add(player) # need this for stud??
                    if len(cards)==3:
                        hand.hero = player
                        hand.addHoleCards(street, player, closed=cards[0:2], open=[cards[2]], shown=False, mucked=False, dealt=False)
                    else:
                        hand.addHoleCards(street, player, closed=[], open=cards, shown=False, mucked=False, dealt=False)
                elif street == 'SEVENTH':
                    if hand.hero==player:
                        hand.addHoleCards(street, player, open=cards, closed=[], shown=False, mucked=False, dealt=False)
                    else:
                        hand.addHoleCards(street, player, open=[], closed=cards, shown=False, mucked=False, dealt=False)
                else:
                    hand.addHoleCards(street, player, open=cards, closed=[], shown=False, mucked=False, dealt=False)
                    
    def _readHoleCards2(self, hand):
#    streets PREFLOP, PREDRAW, and THIRD are special cases beacause
#    we need to grab hero's cards
        for street in ('PREFLOP', 'DEAL'):
            if street in hand.streets.keys():
                newcards = []
                m = self.re_HeroCards2.finditer(hand.streets[street])
                for found in m:
                    hand.hero = found.group('PNAME')
                    newcards = found.group('NEWCARDS').split(' ')
                if hand.hero:
                    hand.addHoleCards(street, hand.hero, closed=newcards, shown=False, mucked=False, dealt=True)

        for street, text in hand.streets.iteritems():
            if not text or street in ('PREFLOP', 'DEAL'): continue  # already done these
            m = self.re_HeroCards2.finditer(hand.streets[street])
            for found in m:
                player = found.group('PNAME')
                if found.group('NEWCARDS') is None:
                    newcards = []
                else:
                    newcards = found.group('NEWCARDS').split(' ')
                if found.group('OLDCARDS') is None:
                    oldcards = []
                else:
                    oldcards = found.group('OLDCARDS').split(' ')

                if street == 'THIRD' and len(newcards) == 3: # hero in stud game
                    hand.hero = player
                    hand.dealt.add(player) # need this for stud??
                    hand.addHoleCards(street, player, closed=newcards[0:2], open=[newcards[2]], shown=False, mucked=False, dealt=False)
                else:
                    hand.addHoleCards(street, player, open=newcards, closed=oldcards, shown=False, mucked=False, dealt=False)

    def readAction(self, hand, street):
        if self.version == 1:
            self._readAction1(hand, street)
        else:
            self._readAction2(hand, street)
    
    def _readAction1(self, hand, street):
        m = self.re_Action1.finditer(hand.streets[street])
        for action in m:
            acts = action.groupdict()
            if action.group('PNAME') == None:    
                log.error("WinningToFpdb.readAction: Unknown player %s %s" % (action.group('ATYPE'), hand.handid))   
                raise FpdbParseError
                
            if action.group('ATYPE') == 'folds':
                hand.addFold( street, action.group('PNAME'))
            elif action.group('ATYPE') == 'checks':
                hand.addCheck( street, action.group('PNAME'))
            elif action.group('ATYPE') == 'calls':
                hand.addCall( street, action.group('PNAME'), self.clearMoneyString(action.group('BET')) )
            elif action.group('ATYPE') in ('raises', 'straddle', 'caps', 'cap'):
                hand.addCallandRaise( street, action.group('PNAME'), self.clearMoneyString(action.group('BET')) )
            elif action.group('ATYPE') ==  'bets':
                hand.addBet( street, action.group('PNAME'), self.clearMoneyString(action.group('BET')) )
            elif action.group('ATYPE') ==  'allin':
                player = action.group('PNAME')
                # disconnected all in
                if action.group('BET') == None:
                    amount = str(hand.stacks[player])
                else:
                    amount = self.clearMoneyString(action.group('BET')).replace(u',', u'') #some sites have commas
                Ai = Decimal(amount)
                Bp = hand.lastBet[street]
                Bc = sum(hand.bets[street][player])
                C = Bp - Bc
                if Ai <= C:
                    hand.addCall(street, player, amount)
                elif Bp == 0:
                    hand.addBet(street, player, amount)
                else:
                    hand.addCallandRaise(street, player, amount)
            else:
                log.debug(_("DEBUG:") + " " + _("Unimplemented %s: '%s' '%s'") % ("readAction", action.group('PNAME'), action.group('ATYPE')))
                
    def _readAction2(self, hand, street):
        m = self.re_Action2.finditer(hand.streets[street])
        for action in m:
            acts = action.groupdict()
            #log.error("DEBUG: %s acts: %s" % (street, acts))
            if action.group('ATYPE') == ' folds':
                hand.addFold( street, action.group('PNAME'))
            elif action.group('ATYPE') == ' checks':
                hand.addCheck( street, action.group('PNAME'))
            elif action.group('ATYPE') == ' calls':
                hand.addCall( street, action.group('PNAME'), self.clearMoneyString(action.group('BET')) )
            elif action.group('ATYPE') in (' raises', ' straddle', ' caps', ' cap'):
                if action.group('BETTO') is not None:
                    hand.addRaiseTo( street, action.group('PNAME'), self.clearMoneyString(action.group('BETTO')) )
                elif action.group('BET') is not None:
                   hand.addCallandRaise( street, action.group('PNAME'), self.clearMoneyString(action.group('BET')) ) 
            elif action.group('ATYPE') == ' bets':
                hand.addBet( street, action.group('PNAME'), self.clearMoneyString(action.group('BET')) )
            else:
                log.debug(_("DEBUG:") + " " + _("Unimplemented %s: '%s' '%s'") % ("readAction", action.group('PNAME'), action.group('ATYPE')))

    def readCollectPot(self,hand):
        if self.version == 1:
            self._readCollectPot1(hand)
        elif hand.runItTimes == 2:
            self._readCollectPot3(hand)
        else:
            self._readCollectPot2(hand)
    
    def _readCollectPot1(self,hand):
        for m in self.re_CollectPot1.finditer(hand.handText):
            if Decimal(self.clearMoneyString(m.group('POT'))) > 0:
                hand.addCollectPot(player=m.group('PNAME'),pot=m.group('POT'))
    
    def _readCollectPot2(self,hand):
        pre, post = hand.handText.split('*** SUMMARY ***')        
        acts, bovadaUncalled_v1, bovadaUncalled_v2, blindsantes, adjustment = hand.actions.get('PREFLOP'), False, False, 0, 0
        names = [p[1] for p in hand.players]
        if acts != None and len([a for a in acts if a[1] != 'folds']) == 0:
            m0 = self.re_Uncalled.search(hand.handText)
            if m0 and Decimal(m0.group('BET')) == Decimal(hand.bb):
                bovadaUncalled_v2 = True
            elif m0 == None:
                bovadaUncalled_v1 = True
                has_sb = len([a[2] for a in hand.actions.get('BLINDSANTES') if a[1] == 'small blind']) > 0
                adjustment = (Decimal(hand.bb) - Decimal(hand.sb)) if has_sb else Decimal(hand.bb)
                blindsantes = sum([a[2] for a in hand.actions.get('BLINDSANTES')])
        else:
            m0 = self.re_Uncalled.search(hand.handText)
            if not m0:
                hand.setUncalledBets(True)
                
        for m in self.re_CollectPot2.finditer(post):
            pot = self.clearMoneyString(m.group('POT'))
            if bovadaUncalled_v1 and Decimal(pot) == (blindsantes):
                hand.addCollectPot(player=m.group('PNAME'),pot=str(Decimal(pot) - adjustment))
            elif bovadaUncalled_v2:
                hand.addCollectPot(player=m.group('PNAME'),pot=str(Decimal(pot)*2))
            else:
                hand.addCollectPot(player=m.group('PNAME'),pot=pot)
    
    def _readCollectPot3(self,hand):
        for m in self.re_CollectPot3.finditer(hand.handText):
            hand.addCollectPot(player=m.group('PNAME'),pot=m.group('POT'))
            
    def readShowdownActions(self, hand):
        # TODO: pick up mucks also??
        pass

    def readShownCards(self,hand):
        if self.version == 1:
            self._readShownCards1(hand)
        else:
            self._readShownCards2(hand)
    
    def _readShownCards1(self,hand):
        for m in self.re_ShownCards1.finditer(hand.handText):
            if m.group('CARDS') is not None:
                cards = m.group('CARDS')
                cards = [c.replace("10", "T") for c in cards.split(' ')] # needs to be a list, not a set--stud needs the order
                string = m.group('STRING')
                if m.group('STRING2'):
                    string += '|' + m.group('STRING2')

                (shown, mucked) = (False, False)
                #if m.group('SHOWED') == "showed": shown = True
                #elif m.group('SHOWED') == "mucked": mucked = True

                #print "DEBUG: hand.addShownCards(%s, %s, %s, %s)" %(cards, m.group('PNAME'), shown, mucked)
                hand.addShownCards(cards=cards, player=m.group('PNAME'), shown=shown, mucked=mucked, string=string)
    
    def _readShownCards2(self,hand):                
        for m in self.re_ShownCards2.finditer(hand.handText):
            if m.group('CARDS') is not None:
                cards = m.group('CARDS')
                cards = cards.split(' ') # needs to be a list, not a set--stud needs the order
                string = m.group('STRING')
                if m.group('STRING2'):
                    string += '|' + m.group('STRING2')

                (shown, mucked) = (False, False)
                if m.group('SHOWED') == "showed": shown = True
                elif m.group('SHOWED') == "mucked": mucked = True

                #print "DEBUG: hand.addShownCards(%s, %s, %s, %s)" %(cards, m.group('PNAME'), shown, mucked)
                hand.addShownCards(cards=cards, player=m.group('PNAME'), shown=shown, mucked=mucked, string=string)

    @staticmethod
    def getTableTitleRe(type, table_name=None, tournament = None, table_number=None):
        "Returns string to search in windows titles"
        regex = re.escape(str(table_name))
        if type=="tour":
            regex = ", Table " + re.escape(str(table_number)) + "\s\-.*\s\(" + re.escape(str(tournament)) + "\)"
        log.info("Winning.getTableTitleRe: table_name='%s' tournament='%s' table_number='%s'" % (table_name, tournament, table_number))
        log.info("Winning.getTableTitleRe: returns: '%s'" % (regex))
        return regex

