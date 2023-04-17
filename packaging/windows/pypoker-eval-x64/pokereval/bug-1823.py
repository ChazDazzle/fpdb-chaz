#
# Copyright (C) 2007, 2008 Loic Dachary <loic@dachary.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301, USA.
# 
# http://gna.org/support/?1823
#
import sys
sys.path.insert(0, ".")
sys.path.insert(0, ".libs")

from pokereval import PokerEval

pokereval = PokerEval()

result = pokereval.poker_eval(game = "holdem", fill_pockets = 1, pockets = [ ["As", "3s"],  ["__", "__"]], dead = [], board = ["Ad", "Qs", "2c", "Ac", "Kc"])
assert result == {'info': (990, 0, 1), 'eval': [{'winlo': 0, 'tielo': 0, 'winhi': 877, 'scoop': 877, 'loselo': 0, 'ev': 903, 'losehi': 78, 'tiehi': 35}, {'winlo': 0, 'tielo': 0, 'winhi': 78, 'scoop': 78, 'loselo': 0, 'ev': 96, 'losehi': 877, 'tiehi': 35}]}

result = pokereval.poker_eval(game = "omaha8", fill_pockets = 1, pockets = [ ["As", "3s", "2s", "6s"],  ["__", "__", "__", "__"]], dead = [], board = ["Ad", "Qs", "2c", "7c", "5c"])
assert result == {'info': (123410, 1, 1), 'eval': [{'winlo': 109375, 'tielo': 5361, 'winhi': 73190, 'scoop': 69661, 'loselo': 8674, 'ev': 753, 'losehi': 48978, 'tiehi': 1242}, {'winlo': 8674, 'tielo': 5361, 'winhi': 48978, 'scoop': 8674, 'loselo': 68788, 'ev': 246, 'losehi': 73190, 'tiehi': 1242}]}

