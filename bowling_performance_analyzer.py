#!/usr/bin/env python3
"""
Bowling Performance Analyzer
Specialized analysis focusing on bowling performance in cricket scorecards
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ground_scorecard_analyzer import GroundScorecardAnalyzer
import requests
from bs4 import BeautifulSoup

class BowlingPerformanceAnalyzer:
    def __init__(self):
        self.analyzer = GroundScorecardAnalyzer()
        
        # Bowling performance categories
        self.bowling_categories = {
            'excellent': {'wickets': 3, 'economy': 6.0, 'description': 'Match-winning performance'},
            'very_good': {'wickets': 2, 'economy': 7.0, 'description': 'Strong bowling performance'},
            'good': {'wickets': 1, 'economy': 8.0, 'description': 'Solid contribution'},
            'average': {'wickets': 0, 'economy': 9.0, 'description': 'Average performance'},
            'poor': {'wickets': 0, 'economy': 12.0, 'description': 'Expensive bowling'}
        }
    
    def analyze_bowling_performance(self, scorecard_url):
        """Comprehensive bowling performance analysis"""
        print(f"🎳 BOWLING PERFORMANCE ANALYSIS")
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
            
            # Filter bowlers (players who bowled)
            bowlers = [p for p in all_players if p['overs'] > 0]
            
            if not bowlers:
                print("❌ No bowling data found in this scorecard")
                return
            
            print(f"🎯 Found {len(bowlers)} bowlers")
            print(f"🏏 Teams: {' vs '.join(teams)}")
            
            # Calculate fantasy points for bowlers
            for bowler in bowlers:
                bowler['fantasy_points'] = self.analyzer._calculate_fantasy_points(bowler)
            
            # Sort bowlers by fantasy points
            sorted_bowlers = sorted(bowlers, key=lambda x: x['fantasy_points'], reverse=True)
            
            # Detailed bowling analysis
            self._analyze_bowling_attack(sorted_bowlers, teams)
            self._analyze_bowling_categories(sorted_bowlers)
            self._analyze_bowling_roles(sorted_bowlers)
            self._analyze_bowling_economy(sorted_bowlers)
            self._analyze_bowling_wickets(sorted_bowlers)
            self._recommend_bowling_picks(sorted_bowlers)
            
        except Exception as e:
            print(f"❌ Error analyzing bowling performance: {e}")
    
    def _analyze_bowling_attack(self, bowlers, teams):
        """Analyze overall bowling attack"""
        print(f"\n🎳 BOWLING ATTACK OVERVIEW")
        print("-" * 50)
        
        # Team-wise bowling analysis
        for team in teams:
            team_bowlers = [b for b in bowlers if b['team'] == team]
            if not team_bowlers:
                continue
                
            total_wickets = sum(b['wickets'] for b in team_bowlers)
            total_overs = sum(b['overs'] for b in team_bowlers)
            total_runs = sum(b['runs_conceded'] for b in team_bowlers)
            total_maidens = sum(b['maidens'] for b in team_bowlers)
            
            avg_economy = (total_runs / total_overs) if total_overs > 0 else 0
            
            print(f"\n🏏 {team} Bowling:")
            print(f"   Bowlers Used: {len(team_bowlers)}")
            print(f"   Total Wickets: {total_wickets}")
            print(f"   Total Overs: {total_overs}")
            print(f"   Runs Conceded: {total_runs}")
            print(f"   Maidens: {total_maidens}")
            print(f"   Team Economy: {avg_economy:.2f}")
            
            # Best bowler from team
            best_bowler = max(team_bowlers, key=lambda x: x['fantasy_points'])
            print(f"   🏆 Best Bowler: {best_bowler['name']} ({best_bowler['fantasy_points']:.0f} pts)")
    
    def _analyze_bowling_categories(self, bowlers):
        """Categorize bowling performances"""
        print(f"\n📊 BOWLING PERFORMANCE CATEGORIES")
        print("-" * 50)
        
        categorized = {cat: [] for cat in self.bowling_categories.keys()}
        
        for bowler in bowlers:
            economy = (bowler['runs_conceded'] / bowler['overs']) if bowler['overs'] > 0 else 15
            wickets = bowler['wickets']
            
            # Categorize performance
            if wickets >= 3 and economy <= 6:
                categorized['excellent'].append(bowler)
            elif wickets >= 2 and economy <= 7:
                categorized['very_good'].append(bowler)
            elif wickets >= 1 and economy <= 8:
                categorized['good'].append(bowler)
            elif economy <= 9:
                categorized['average'].append(bowler)
            else:
                categorized['poor'].append(bowler)
        
        for category, bowlers_list in categorized.items():
            if bowlers_list:
                cat_info = self.bowling_categories[category]
                print(f"\n🎯 {category.upper()} ({cat_info['description']}):")
                for bowler in bowlers_list:
                    economy = (bowler['runs_conceded'] / bowler['overs']) if bowler['overs'] > 0 else 0
                    print(f"   • {bowler['name']:<20} ({bowler['team']}) - {bowler['wickets']}W, {bowler['overs']}O, Econ: {economy:.1f}, {bowler['fantasy_points']:.0f} pts")
    
    def _analyze_bowling_roles(self, bowlers):
        """Analyze bowling roles and effectiveness"""
        print(f"\n🎭 BOWLING ROLES ANALYSIS")
        print("-" * 50)
        
        roles = {}
        for bowler in bowlers:
            role = bowler['role']
            if role not in roles:
                roles[role] = []
            roles[role].append(bowler)
        
        for role, role_bowlers in roles.items():
            if not role_bowlers:
                continue
                
            print(f"\n🎳 {role} Bowlers ({len(role_bowlers)}):")
            
            # Calculate role statistics
            total_wickets = sum(b['wickets'] for b in role_bowlers)
            total_overs = sum(b['overs'] for b in role_bowlers)
            total_runs = sum(b['runs_conceded'] for b in role_bowlers)
            avg_economy = (total_runs / total_overs) if total_overs > 0 else 0
            
            print(f"   Role Stats: {total_wickets}W, {total_overs}O, Econ: {avg_economy:.2f}")
            
            # Best performer in role
            best_in_role = max(role_bowlers, key=lambda x: x['fantasy_points'])
            print(f"   🏆 Best: {best_in_role['name']} ({best_in_role['fantasy_points']:.0f} pts)")
            
            # List all bowlers in role
            for bowler in sorted(role_bowlers, key=lambda x: x['fantasy_points'], reverse=True):
                economy = (bowler['runs_conceded'] / bowler['overs']) if bowler['overs'] > 0 else 0
                print(f"     • {bowler['name']:<15} - {bowler['wickets']}W, {bowler['overs']}O, Econ: {economy:.1f}, {bowler['fantasy_points']:.0f} pts")
    
    def _analyze_bowling_economy(self, bowlers):
        """Analyze economy rates"""
        print(f"\n💰 ECONOMY RATE ANALYSIS")
        print("-" * 50)
        
        # Calculate economies
        economies = []
        for bowler in bowlers:
            if bowler['overs'] > 0:
                economy = bowler['runs_conceded'] / bowler['overs']
                economies.append((bowler, economy))
        
        # Sort by economy (best first)
        economies.sort(key=lambda x: x[1])
        
        print(f"🏆 MOST ECONOMICAL BOWLERS:")
        for i, (bowler, economy) in enumerate(economies[:5], 1):
            print(f"   {i}. {bowler['name']:<20} - {economy:.2f} RPO ({bowler['wickets']}W, {bowler['overs']}O)")
        
        print(f"\n💸 MOST EXPENSIVE BOWLERS:")
        for i, (bowler, economy) in enumerate(reversed(economies[-3:]), 1):
            print(f"   {i}. {bowler['name']:<20} - {economy:.2f} RPO ({bowler['wickets']}W, {bowler['overs']}O)")
        
        # Economy distribution
        excellent_economy = [b for b, e in economies if e <= 6]
        good_economy = [b for b, e in economies if 6 < e <= 8]
        average_economy = [b for b, e in economies if 8 < e <= 10]
        poor_economy = [b for b, e in economies if e > 10]
        
        print(f"\n📊 ECONOMY DISTRIBUTION:")
        print(f"   Excellent (≤6.0): {len(excellent_economy)} bowlers")
        print(f"   Good (6.1-8.0): {len(good_economy)} bowlers")
        print(f"   Average (8.1-10.0): {len(average_economy)} bowlers")
        print(f"   Poor (>10.0): {len(poor_economy)} bowlers")
    
    def _analyze_bowling_wickets(self, bowlers):
        """Analyze wicket-taking ability"""
        print(f"\n🎯 WICKET-TAKING ANALYSIS")
        print("-" * 50)
        
        # Sort by wickets
        wicket_takers = sorted(bowlers, key=lambda x: x['wickets'], reverse=True)
        
        print(f"🏆 TOP WICKET TAKERS:")
        for i, bowler in enumerate(wicket_takers[:5], 1):
            economy = (bowler['runs_conceded'] / bowler['overs']) if bowler['overs'] > 0 else 0
            strike_rate = (bowler['overs'] * 6 / bowler['wickets']) if bowler['wickets'] > 0 else 0
            print(f"   {i}. {bowler['name']:<20} - {bowler['wickets']} wickets ({bowler['overs']}O, Econ: {economy:.1f}, SR: {strike_rate:.1f})")
        
        # Wicket distribution
        three_plus = [b for b in bowlers if b['wickets'] >= 3]
        two_wickets = [b for b in bowlers if b['wickets'] == 2]
        one_wicket = [b for b in bowlers if b['wickets'] == 1]
        no_wickets = [b for b in bowlers if b['wickets'] == 0]
        
        print(f"\n📊 WICKET DISTRIBUTION:")
        print(f"   3+ Wickets: {len(three_plus)} bowlers")
        print(f"   2 Wickets: {len(two_wickets)} bowlers")
        print(f"   1 Wicket: {len(one_wicket)} bowlers")
        print(f"   No Wickets: {len(no_wickets)} bowlers")
        
        # Maiden analysis
        maiden_bowlers = [b for b in bowlers if b['maidens'] > 0]
        if maiden_bowlers:
            print(f"\n🎯 MAIDEN OVERS:")
            for bowler in sorted(maiden_bowlers, key=lambda x: x['maidens'], reverse=True):
                print(f"   • {bowler['name']:<20} - {bowler['maidens']} maiden(s)")
    
    def _recommend_bowling_picks(self, bowlers):
        """Recommend best bowling picks for Dream11"""
        print(f"\n🏆 DREAM11 BOWLING RECOMMENDATIONS")
        print("-" * 50)
        
        # Top 5 bowlers by fantasy points
        top_bowlers = sorted(bowlers, key=lambda x: x['fantasy_points'], reverse=True)[:5]
        
        print(f"🎯 TOP 5 BOWLING PICKS:")
        for i, bowler in enumerate(top_bowlers, 1):
            economy = (bowler['runs_conceded'] / bowler['overs']) if bowler['overs'] > 0 else 0
            
            # Determine pick confidence
            confidence = "HIGH" if bowler['fantasy_points'] >= 30 else "MEDIUM" if bowler['fantasy_points'] >= 20 else "LOW"
            
            print(f"   {i}. {bowler['name']:<20} ({bowler['team']}) - {bowler['fantasy_points']:.0f} pts [{confidence}]")
            print(f"      Performance: {bowler['wickets']}W, {bowler['overs']}O, Econ: {economy:.1f}, {bowler['maidens']}M")
            print(f"      Role: {bowler['role']}")
            
            # Recommendation reason
            if bowler['wickets'] >= 2:
                print(f"      💡 Reason: Excellent wicket-taker")
            elif economy <= 6:
                print(f"      💡 Reason: Outstanding economy rate")
            elif bowler['maidens'] > 0:
                print(f"      💡 Reason: Pressure bowling with maidens")
            else:
                print(f"      💡 Reason: Consistent performance")
            print()
        
        # Captain/Vice-captain recommendations
        if top_bowlers:
            captain_pick = top_bowlers[0]
            print(f"🔥 CAPTAIN RECOMMENDATION: {captain_pick['name']} ({captain_pick['fantasy_points']:.0f} pts)")
            
            if len(top_bowlers) > 1:
                vc_pick = top_bowlers[1]
                print(f"⭐ VICE-CAPTAIN OPTION: {vc_pick['name']} ({vc_pick['fantasy_points']:.0f} pts)")

def main():
    """Test the bowling performance analyzer"""
    analyzer = BowlingPerformanceAnalyzer()
    
    # Test with a sample scorecard
    scorecard_url = "https://www.espncricinfo.com/series/twenty20-cup-2003-124121/glamorgan-vs-northamptonshire-midlands-wales-west-group-304750/full-scorecard"
    
    analyzer.analyze_bowling_performance(scorecard_url)

if __name__ == "__main__":
    main()