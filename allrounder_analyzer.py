#!/usr/bin/env python3
"""
All-Rounder Analyzer
Specialized analysis for players who contribute with both bat and ball
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ground_scorecard_analyzer import GroundScorecardAnalyzer
import requests
from bs4 import BeautifulSoup

class AllRounderAnalyzer:
    def __init__(self):
        self.analyzer = GroundScorecardAnalyzer()
        
        # All-rounder categories based on contribution
        self.allrounder_categories = {
            'premium': {'min_batting_pts': 30, 'min_bowling_pts': 20, 'description': 'Elite all-rounder performance'},
            'excellent': {'min_batting_pts': 20, 'min_bowling_pts': 15, 'description': 'Strong dual contribution'},
            'good': {'min_batting_pts': 15, 'min_bowling_pts': 10, 'description': 'Solid all-round performance'},
            'average': {'min_batting_pts': 10, 'min_bowling_pts': 5, 'description': 'Decent contribution'},
            'specialist': {'min_batting_pts': 5, 'min_bowling_pts': 5, 'description': 'Specialist with minor contribution'}
        }
    
    def analyze_allrounders(self, scorecard_url):
        """Comprehensive all-rounder analysis"""
        print(f"🔄 ALL-ROUNDER PERFORMANCE ANALYSIS")
        print("=" * 80)
        print(f"📋 Scorecard: {scorecard_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(scorecard_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract teams and players
            teams = self.analyzer._extract_team_names(soup)
            all_players = self.analyzer._extract_all_player_data(soup, teams)
            
            # Calculate fantasy points for all players
            for player in all_players:
                player['fantasy_points'] = self.analyzer._calculate_fantasy_points(player)
                player['batting_points'] = self._calculate_batting_points(player)
                player['bowling_points'] = self._calculate_bowling_points(player)
                player['fielding_points'] = self._calculate_fielding_points(player)
            
            # Identify all-rounders (players who both batted and bowled)
            allrounders = []
            for player in all_players:
                has_batting = player['runs'] > 0 or player['balls'] > 0
                has_bowling = player['overs'] > 0
                
                if has_batting and has_bowling:
                    allrounders.append(player)
            
            if not allrounders:
                print("❌ No all-rounders found in this scorecard")
                print("💡 Looking for players with both batting and bowling contributions...")
                
                # Show potential all-rounders (players who could have bowled)
                potential_allrounders = [p for p in all_players if p['runs'] > 10 and p['role'] in ['MID', 'HIT', 'POW']]
                if potential_allrounders:
                    print(f"\n🔍 POTENTIAL ALL-ROUNDERS (batsmen who could bowl):")
                    for player in sorted(potential_allrounders, key=lambda x: x['fantasy_points'], reverse=True)[:5]:
                        print(f"   • {player['name']:<20} ({player['team']}) - {player['runs']} runs, {player['fantasy_points']:.0f} pts")
                return
            
            print(f"🎯 Found {len(allrounders)} all-rounders")
            print(f"🏏 Teams: {' vs '.join(teams)}")
            
            # Sort all-rounders by total fantasy points
            sorted_allrounders = sorted(allrounders, key=lambda x: x['fantasy_points'], reverse=True)
            
            # Comprehensive all-rounder analysis
            self._analyze_allrounder_overview(sorted_allrounders)
            self._analyze_allrounder_categories(sorted_allrounders)
            self._analyze_batting_vs_bowling_contribution(sorted_allrounders)
            self._analyze_allrounder_efficiency(sorted_allrounders)
            self._recommend_allrounder_picks(sorted_allrounders)
            
        except Exception as e:
            print(f"❌ Error analyzing all-rounders: {e}")
    
    def _calculate_batting_points(self, player):
        """Calculate fantasy points from batting only"""
        points = 0
        points += player['runs'] * 1  # 1 point per run
        points += player['fours'] * 1  # 1 point per boundary
        points += player['sixes'] * 2  # 2 points per six
        
        # Milestone bonuses
        if player['runs'] >= 100:
            points += 16
        elif player['runs'] >= 50:
            points += 8
        elif player['runs'] == 0 and player['balls'] > 0:
            points -= 2
        
        # Strike rate bonus
        if player['balls'] > 0:
            strike_rate = (player['runs'] / player['balls']) * 100
            if strike_rate > 150:
                points += 2
            elif strike_rate > 100:
                points += 1
        
        return points
    
    def _calculate_bowling_points(self, player):
        """Calculate fantasy points from bowling only"""
        points = 0
        points += player['wickets'] * 25  # 25 points per wicket
        points += player['maidens'] * 12  # 12 points per maiden
        
        # Economy bonus
        if player['overs'] > 0:
            economy = player['runs_conceded'] / player['overs']
            if economy < 4:
                points += 4
            elif economy < 6:
                points += 2
        
        return points
    
    def _calculate_fielding_points(self, player):
        """Calculate fantasy points from fielding only"""
        points = 0
        points += player['catches'] * 8
        points += player['stumpings'] * 12
        points += player['run_outs'] * 12
        return points
    
    def _analyze_allrounder_overview(self, allrounders):
        """Provide overview of all-rounder performances"""
        print(f"\n🔄 ALL-ROUNDER OVERVIEW")
        print("-" * 50)
        
        for i, player in enumerate(allrounders, 1):
            economy = (player['runs_conceded'] / player['overs']) if player['overs'] > 0 else 0
            strike_rate = (player['runs'] / player['balls'] * 100) if player['balls'] > 0 else 0
            
            print(f"\n{i}. {player['name']} ({player['team']}) - {player['fantasy_points']:.0f} total pts")
            print(f"   🏏 Batting: {player['runs']} runs ({player['balls']} balls, SR: {strike_rate:.1f}) - {player['batting_points']:.0f} pts")
            print(f"   🎳 Bowling: {player['wickets']} wickets ({player['overs']} overs, Econ: {economy:.1f}) - {player['bowling_points']:.0f} pts")
            if player['fielding_points'] > 0:
                print(f"   🥅 Fielding: {player['catches']}C, {player['stumpings']}St, {player['run_outs']}RO - {player['fielding_points']:.0f} pts")
            
            # Contribution balance
            batting_pct = (player['batting_points'] / player['fantasy_points'] * 100) if player['fantasy_points'] > 0 else 0
            bowling_pct = (player['bowling_points'] / player['fantasy_points'] * 100) if player['fantasy_points'] > 0 else 0
            print(f"   📊 Contribution: {batting_pct:.0f}% batting, {bowling_pct:.0f}% bowling")
    
    def _analyze_allrounder_categories(self, allrounders):
        """Categorize all-rounder performances"""
        print(f"\n📊 ALL-ROUNDER CATEGORIES")
        print("-" * 50)
        
        categorized = {cat: [] for cat in self.allrounder_categories.keys()}
        
        for player in allrounders:
            batting_pts = player['batting_points']
            bowling_pts = player['bowling_points']
            
            # Categorize based on dual contribution
            if batting_pts >= 30 and bowling_pts >= 20:
                categorized['premium'].append(player)
            elif batting_pts >= 20 and bowling_pts >= 15:
                categorized['excellent'].append(player)
            elif batting_pts >= 15 and bowling_pts >= 10:
                categorized['good'].append(player)
            elif batting_pts >= 10 and bowling_pts >= 5:
                categorized['average'].append(player)
            else:
                categorized['specialist'].append(player)
        
        for category, players_list in categorized.items():
            if players_list:
                cat_info = self.allrounder_categories[category]
                print(f"\n🎯 {category.upper()} ({cat_info['description']}):")
                for player in players_list:
                    print(f"   • {player['name']:<20} ({player['team']}) - {player['fantasy_points']:.0f} pts (Bat: {player['batting_points']:.0f}, Bowl: {player['bowling_points']:.0f})")
    
    def _analyze_batting_vs_bowling_contribution(self, allrounders):
        """Analyze whether players are batting or bowling all-rounders"""
        print(f"\n⚖️ BATTING vs BOWLING CONTRIBUTION")
        print("-" * 50)
        
        batting_allrounders = []
        bowling_allrounders = []
        balanced_allrounders = []
        
        for player in allrounders:
            batting_pts = player['batting_points']
            bowling_pts = player['bowling_points']
            
            if batting_pts > bowling_pts * 2:
                batting_allrounders.append(player)
            elif bowling_pts > batting_pts * 2:
                bowling_allrounders.append(player)
            else:
                balanced_allrounders.append(player)
        
        if batting_allrounders:
            print(f"\n🏏 BATTING ALL-ROUNDERS (stronger with bat):")
            for player in sorted(batting_allrounders, key=lambda x: x['batting_points'], reverse=True):
                print(f"   • {player['name']:<20} - Bat: {player['batting_points']:.0f} pts, Bowl: {player['bowling_points']:.0f} pts")
        
        if bowling_allrounders:
            print(f"\n🎳 BOWLING ALL-ROUNDERS (stronger with ball):")
            for player in sorted(bowling_allrounders, key=lambda x: x['bowling_points'], reverse=True):
                print(f"   • {player['name']:<20} - Bowl: {player['bowling_points']:.0f} pts, Bat: {player['batting_points']:.0f} pts")
        
        if balanced_allrounders:
            print(f"\n⚖️ BALANCED ALL-ROUNDERS (equal contribution):")
            for player in sorted(balanced_allrounders, key=lambda x: x['fantasy_points'], reverse=True):
                print(f"   • {player['name']:<20} - Bat: {player['batting_points']:.0f} pts, Bowl: {player['bowling_points']:.0f} pts")
    
    def _analyze_allrounder_efficiency(self, allrounders):
        """Analyze efficiency metrics for all-rounders"""
        print(f"\n⚡ ALL-ROUNDER EFFICIENCY ANALYSIS")
        print("-" * 50)
        
        for player in allrounders:
            print(f"\n🔄 {player['name']} ({player['team']}):")
            
            # Batting efficiency
            if player['balls'] > 0:
                strike_rate = (player['runs'] / player['balls']) * 100
                boundary_rate = ((player['fours'] + player['sixes']) / player['balls']) * 100
                print(f"   🏏 Batting Efficiency: SR {strike_rate:.1f}, Boundary% {boundary_rate:.1f}")
            
            # Bowling efficiency
            if player['overs'] > 0:
                economy = player['runs_conceded'] / player['overs']
                strike_rate_bowling = (player['overs'] * 6 / player['wickets']) if player['wickets'] > 0 else 0
                print(f"   🎳 Bowling Efficiency: Econ {economy:.1f}, Strike Rate {strike_rate_bowling:.1f}")
            
            # Overall efficiency (points per over involved)
            total_involvement = player['balls'] / 6 + player['overs']  # Convert balls to overs
            if total_involvement > 0:
                efficiency = player['fantasy_points'] / total_involvement
                print(f"   📊 Overall Efficiency: {efficiency:.1f} points per over of involvement")
    
    def _recommend_allrounder_picks(self, allrounders):
        """Recommend best all-rounder picks for Dream11"""
        print(f"\n🏆 DREAM11 ALL-ROUNDER RECOMMENDATIONS")
        print("-" * 50)
        
        if not allrounders:
            print("❌ No all-rounders available for recommendation")
            return
        
        # Sort by total fantasy points
        top_allrounders = sorted(allrounders, key=lambda x: x['fantasy_points'], reverse=True)
        
        print(f"🎯 ALL-ROUNDER PICKS (ranked by total points):")
        for i, player in enumerate(top_allrounders, 1):
            # Determine pick confidence
            total_pts = player['fantasy_points']
            confidence = "PREMIUM" if total_pts >= 60 else "HIGH" if total_pts >= 40 else "MEDIUM" if total_pts >= 25 else "LOW"
            
            print(f"\n   {i}. {player['name']:<20} ({player['team']}) - {total_pts:.0f} pts [{confidence}]")
            print(f"      🏏 Batting: {player['runs']}R ({player['balls']}B) - {player['batting_points']:.0f} pts")
            print(f"      🎳 Bowling: {player['wickets']}W ({player['overs']}O) - {player['bowling_points']:.0f} pts")
            
            # Value assessment
            if player['batting_points'] >= 20 and player['bowling_points'] >= 15:
                print(f"      💎 Value: Excellent dual threat - must pick!")
            elif player['batting_points'] >= 15 or player['bowling_points'] >= 15:
                print(f"      💰 Value: Strong in one discipline, useful in other")
            else:
                print(f"      🔧 Value: Utility player with modest contributions")
        
        # Captain/Vice-captain recommendations
        if top_allrounders:
            best_allrounder = top_allrounders[0]
            if best_allrounder['fantasy_points'] >= 50:
                print(f"\n🔥 CAPTAIN RECOMMENDATION: {best_allrounder['name']} ({best_allrounder['fantasy_points']:.0f} pts)")
                print(f"   Reason: Outstanding all-round performance with dual threat capability")
            
            if len(top_allrounders) > 1:
                second_best = top_allrounders[1]
                if second_best['fantasy_points'] >= 30:
                    print(f"⭐ VICE-CAPTAIN OPTION: {second_best['name']} ({second_best['fantasy_points']:.0f} pts)")
        
        # Team balance recommendation
        print(f"\n🎯 TEAM SELECTION STRATEGY:")
        premium_allrounders = [p for p in allrounders if p['fantasy_points'] >= 40]
        good_allrounders = [p for p in allrounders if 25 <= p['fantasy_points'] < 40]
        
        if premium_allrounders:
            print(f"   • Pick {min(2, len(premium_allrounders))} premium all-rounder(s) as core players")
        if good_allrounders:
            print(f"   • Consider 1-2 good all-rounders for team balance")
        
        print(f"   • All-rounders provide flexibility and multiple scoring opportunities")
        print(f"   • Ideal for captain/vice-captain due to dual contribution potential")

def main():
    """Test the all-rounder analyzer"""
    analyzer = AllRounderAnalyzer()
    
    # Test with a sample scorecard
    scorecard_url = "https://www.espncricinfo.com/series/twenty20-cup-2003-124121/glamorgan-vs-northamptonshire-midlands-wales-west-group-304750/full-scorecard"
    
    analyzer.analyze_allrounders(scorecard_url)

if __name__ == "__main__":
    main()