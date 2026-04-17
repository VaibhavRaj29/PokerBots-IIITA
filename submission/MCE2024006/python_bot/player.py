'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot

import random


class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind
        #my_bounty = round_state.bounties[active]  # your current bounty rank
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        
        my_bounty_hit = terminal_state.bounty_hits[active]  # True if you hit bounty
        opponent_bounty_hit = terminal_state.bounty_hits[1-active] # True if opponent hit bounty
        bounty_rank = previous_state.bounties[active]  # your bounty rank

        # The following is a demonstration of accessing illegal information (will not work)
        opponent_bounty_rank = previous_state.bounties[1-active]  # attempting to grab opponent's bounty rank

        if my_bounty_hit:
            print("I hit my bounty of " + bounty_rank + "!")
        if opponent_bounty_hit:
            print("Opponent hit their bounty of " + opponent_bounty_rank + "!")

     def monte_carlo_strength(self, my_cards, board_cards, street):
        iterations = 40 + street * 20
    
        deck = [r+s for r in "23456789TJQKA" for s in "shdc"]
        for c in my_cards + board_cards:
            if c in deck:
                deck.remove(c)
    
        rank_order = "23456789TJQKA"
    
        def card_rank(card):
            return rank_order.index(card[0])
    
        def evaluate(cards):
            ranks = sorted([card_rank(c) for c in cards])
            suits = [c[1] for c in cards]
    
            counts = {}
            for r in ranks:
                counts[r] = counts.get(r, 0) + 1
    
            values = sorted(counts.values(), reverse=True)
    
            flush = max(suits.count(s) for s in suits) >= 5
    
            straight = False
            for i in range(len(ranks)-4):
                if ranks[i+4] - ranks[i] == 4:
                    straight = True
    
            if flush and straight:
                return 8
            if 4 in values:
                return 7
            if 3 in values and 2 in values:
                return 6
            if flush:
                return 5
            if straight:
                return 4
            if 3 in values:
                return 3
            if values.count(2) >= 2:
                return 2
            if 2 in values:
                return 1
            return 0
    
        wins = 0
    
        for _ in range(iterations):
            sample = random.sample(deck, 2 + (5 - len(board_cards)))
            opp_cards = sample[:2]
            future_board = board_cards + sample[2:]
    
            my_score = evaluate(my_cards + future_board)
            opp_score = evaluate(opp_cards + future_board)
    
            if my_score > opp_score:
                wins += 1
    
        return wins / iterations
     def get_action(self, game_state, round_state, active):

        legal = round_state.legal_actions()
        street = round_state.street
        hole = round_state.hands[active]
        board = round_state.deck[:street]
    
        my_pip = round_state.pips[active]
        opp_pip = round_state.pips[1-active]
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1-active]
    
        cost = opp_pip - my_pip
        pot = my_pip + opp_pip
    
        rank_order = "23456789TJQKA"
    
        def rank(c):
            return rank_order.index(c[0])
    
        def to_ints(cards):
            return [(rank(c)*4 + "shdc".index(c[1])) for c in cards]
    
        def eval5(h):
            rs = sorted([x >> 2 for x in h], reverse=True)
            ss = [x & 3 for x in h]
            fl = len(set(ss)) == 1
            st = False
            if len(set(rs)) == 5:
                if rs[0] - rs[4] == 4:
                    st = True
                elif rs == [12,3,2,1,0]:
                    st, rs = True, [3,2,1,0,-1]
            cnt = sorted([(rs.count(r), r) for r in set(rs)], reverse=True)
            g = [c[0] for c in cnt]
            hi = [c[1] for c in cnt]
            if fl and st: return (8, rs)
            if g[0] == 4: return (7, hi)
            if g[:2] == [3,2]: return (6, hi)
            if fl: return (5, rs)
            if st: return (4, rs)
            if g[0] == 3: return (3, hi)
            if g[:2] == [2,2]: return (2, hi)
            if g[0] == 2: return (1, hi)
            return (0, rs)
    
        def best7(cards):
            from itertools import combinations
            return max(eval5(list(c)) for c in combinations(cards, 5))
    
        def mc_equity(hole, board, n):
            used = set(hole + board)
            deck = [i for i in range(52) if i not in used]
            need = 5 - len(board)
            wins = 0.0
            for _ in range(n):
                draw = random.sample(deck, need + 2)
                full = board + draw[:need]
                opp = draw[need:]
                me = best7(hole + full)
                op = best7(opp + full)
                if me > op:
                    wins += 1
                elif me == op:
                    wins += 0.5
            return wins / n
    
        hole_i = to_ints(hole)
        board_i = to_ints(board)
    
        sims = 60 if game_state.game_clock > 25 else 30
        eq = mc_equity(hole_i, board_i, sims)
    
        pot_odds = cost / max(pot + cost, 1)
    
        r1, r2 = rank(hole[0]), rank(hole[1])
    
        if street == 0:
            strength = 0
            if r1 == r2:
                strength += 80
            if max(r1, r2) >= 11:
                strength += 30
            if abs(r1 - r2) <= 2:
                strength += 10
    
            if cost > 0:
                if strength >= 85 and RaiseAction in legal:
                    min_r, max_r = round_state.raise_bounds()
                    return RaiseAction(max_r)
                if strength >= 60:
                    return CallAction()
                if strength >= 40 and cost < 10:
                    return CallAction()
                return FoldAction()
            else:
                if RaiseAction in legal:
                    min_r, max_r = round_state.raise_bounds()
                    if strength >= 60:
                        return RaiseAction(min_r)
                    if random.random() < 0.4:
                        return RaiseAction(min_r)
                return CheckAction()
    
        if cost > 0:
    
            bet_ratio = cost / max(pot, 1)
    
            if bet_ratio < 0.4 and eq > 0.55 and RaiseAction in legal::
                min_r, max_r = round_state.raise_bounds()
                return RaiseAction(min(max_r, int(pot * 1.2)))
    
            if eq > 0.75 and RaiseAction in legal:
                min_r, max_r = round_state.raise_bounds()
                return RaiseAction(max_r)
    
            if eq > 0.55:
                return CallAction()
    
            if eq > pot_odds + 0.05:
                return CallAction()
    
            return FoldAction()
    
        else:
    
            if eq > 0.8 and RaiseAction in legal:
                min_r, max_r = round_state.raise_bounds()
                return RaiseAction(min_r)
    
            if eq > 0.6 and RaiseAction in legal:
                min_r, max_r = round_state.raise_bounds()
                return RaiseAction(min_r)
    
            if eq > 0.35 and random.random() < (0.35 + eq * 0.3) and RaiseAction in legal:
                min_r, max_r = round_state.raise_bounds()
                return RaiseAction(min_r)
    
            return CheckAction()

    
if __name__ == '__main__':
    run_bot(Player(), parse_args())
