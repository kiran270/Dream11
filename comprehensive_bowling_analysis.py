#!/usr/bin/env python3
"""
Comprehensive Bowling Analysis
Complete analysis system that considers bowlers, all-rounders, and batting performances
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ground_scorecard_analyzer import GroundScorecardAnalyzer
from bowling_performance_analyzer import BowlingPerformanceAnalyzer
from allrounder_analyzer import AllRounderAnalyzer
import requests
from bs4 import BeautifulSoup

class ComprehensiveBowlingAnalysis:
    def __init__(self):
        self.scorecard_analyzer = GroundScorecardAnalyzer()
        self.bowling_analyzer = BowlingPerformanceAnalyzer()
        self.allrounder_analyzer = AllRounderAnalyzer()
    
    def complete_analysis(self, scorecard_url):
        """Run complete analysis including batting, bowling, and all-rounder performance"""
        print(f"🏏 COMPREHENSIVE CRICKET ANALYSIS")
        print("=" * 100)
        print(f"📋 Analyzing: {scorecard_url}")
        print("=" * 100)
        
        try:
            # Get basic scorecard data
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(scorecard_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract teams and all players
            teams = self.scorecard_analyzer._extract_team_names(soup)
            all_players = self.scorecard_analyzer._extract_all_player_data(soup, teams)
            
            # Calculate fantasy points for all players
            for player in all_players:
                player['fantasy_points'] = self.scorecard_analyzer._calculate_fantasy_points(player)
            
            # Separate players by type
            batsmen = [p for p in all_players if p['runs'] > 0 or p['balls'] > 0]
            bowlers = [p for p in all_players if p['overs'] > 0]
            allrounders = [p for p in all_players if (p['runs'] > 0 or p['balls'] > 0) and p['overs'] > 0]
            
            print(f"🏏 Teams: {' vs '.join(teams)}")
            print(f"👥 Total Players: {len(all_players)} | Batsmen: {len(batsmen)} | Bowlers: {len(bowlers)} | All-rounders: {len(allrounders)}")
            
            # 1. Overall Dream11 Team Analysis
            self._analyze_dream11_team(all_players)
            
            # 2. Detailed Bowling Analysis
            if bowlers:
                print(f"\n" + "=" * 100)
                self.bowling_analyzer.analyze_bowling_performance(scorecard_url)
            
            # 3. All-rounder Analysis
            if allrounders:
                print(f"\n" + "=" * 100)
                self.allrounder_analyzer.analyze_allrounders(scorecard_url)
            
            # 4. Strategic Recommendations
            self._provide_strategic_recommendations(all_players, batsmen, bowlers, allrounders, teams)
            
        except Exception as e:
            print(f"❌ Error in comprehensive analysis: {e}")
    
    def _analyze_dream11_team(self, all_players):
        """Analyze the optimal Dream11 team considering all player types"""
        print(f"\n🏆 OPTIMAL DREAM11 TEAM ANALYSIS")
        print("-" * 80)
        
        # Sort all players by fantasy points
        sorted_players = sorted(all_players, key=lambda x: x['fantasy_points'], reverse=True)
        top_11 = sorted_players[:11]
        
        # Analyze team composition
        batsmen_in_team = [p for p in top_11 if (p['runs'] > 0 or p['balls'] > 0) and p['overs'] == 0]
        bowlers_in_team = [p for p in top_11 if p['overs'] > 0 and p['runs'] == 0 and p['balls'] == 0]
        allrounders_in_team = [p for p in top_11 if (p['runs'] > 0 or p['balls'] > 0) and p['overs'] > 0]
        
        print(f"📊 Team Composition:")
        print(f"   🏏 Pure Batsmen: {len(batsmen_in_team)}")
        print(f"   🎳 Pure Bowlers: {len(bowlers_in_team)}")
        print(f"   🔄 All-rounders: {len(allrounders_in_team)}")
        print(f"   🥅 Others: {11 - len(batsmen_in_team) - len(bowlers_in_team) - len(allrounders_in_team)}")
        
        # Show Dream11 team with detailed analysis
        print(f"\n🏆 DREAM11 TEAM (Top 11 by Fantasy Points):")
        total_points = 0
        
        for i, player in enumerate(top_11, 1):
            captain_mark = "🔥 (C)" if i == 1 else "⭐ (VC)" if i == 2 else ""
            
            # Determine player type and contribution
            if player in allrounders_in_team:
                player_type = "🔄 All-rounder"
                contribution = f"Bat: {player['runs']}R, Bowl: {player['wickets']}W"
            elif player in bowlers_in_team:
                player_type = "🎳 Bowler"
                economy = (player['runs_conceded'] / player['overs']) if player['overs'] > 0 else 0
                contribution = f"Bowl: {player['wickets']}W, {player['overs']}O, Econ: {economy:.1f}"
            else:
                player_type = "🏏 Batsman"
                sr = (player['runs'] / player['balls'] * 100) if player['balls'] > 0 else 0
                contribution = f"Bat: {player['runs']}R ({player['balls']}B), SR: {sr:.1f}"
            
            print(f"   {i:2d}. {player['name']:<20} ({player['team']}) - {player['fantasy_points']:3.0f} pts {player_type} {captain_mark}")
            print(f"       {contribution}")
            
            total_points += player['fantasy_points']
        
        print(f"\n📊 Team Summary:")
        print(f"   Total Fantasy Points: {total_points:.0f}")
        print(f"   Average Points per Player: {total_points/11:.1f}")
        
        # Team balance analysis
        team_a_count = len([p for p in top_11 if p['team'] == top_11[0]['team']])
        team_b_count = 11 - team_a_count
        print(f"   Team Distribution: {team_a_count}-{team_b_count}")
    
    def _provide_strategic_recommendations(self, all_players, batsmen, bowlers, allrounders, teams):
        """Provide strategic recommendations for Dream11 team selection"""
        print(f"\n" + "=" * 100)
        print(f"🎯 STRATEGIC RECOMMENDATIONS")
        print("-" * 80)
        
        # Captain and Vice-Captain recommendations
        top_performers = sorted(all_players, key=lambda x: x['fantasy_points'], reverse=True)[:5]
        
        print(f"🔥 CAPTAIN/VICE-CAPTAIN RECOMMENDATIONS:")
        for i, player in enumerate(top_performers, 1):
            # Determine why they're a good captain choice
            reasons = []
            if player['runs'] >= 50:
                reasons.append("High run scorer")
            if player['wickets'] >= 2:
                reasons.append("Wicket-taker")
            if (player['runs'] > 0 or player['balls'] > 0) and player['overs'] > 0:
                reasons.append("All-rounder")
            if player['fantasy_points'] >= 50:
                reasons.append("High fantasy points")
            
            reason_text = ", ".join(reasons) if reasons else "Consistent performer"
            
            print(f"   {i}. {player['name']:<20} ({player['team']}) - {player['fantasy_points']:.0f} pts")
            print(f"      💡 Why: {reason_text}")
        
        # Team selection strategy
        print(f"\n🎯 TEAM SELECTION STRATEGY:")
        
        # Bowling strategy
        if bowlers:
            top_bowlers = sorted(bowlers, key=lambda x: x['fantasy_points'], reverse=True)[:3]
            print(f"   🎳 Bowling: Pick {min(3, len(top_bowlers))} bowlers")
            for bowler in top_bowlers:
                economy = (bowler['runs_conceded'] / bowler['overs']) if bowler['overs'] > 0 else 0
                print(f"      • {bowler['name']} - {bowler['wickets']}W, Econ: {economy:.1f}")
        
        # All-rounder strategy
        if allrounders:
            print(f"   🔄 All-rounders: Pick {min(2, len(allrounders))} all-rounders for balance")
            for ar in sorted(allrounders, key=lambda x: x['fantasy_points'], reverse=True)[:2]:
                print(f"      • {ar['name']} - {ar['runs']}R, {ar['wickets']}W")
        
        # Batting strategy
        top_batsmen = sorted([b for b in batsmen if b not in allrounders], key=lambda x: x['fantasy_points'], reverse=True)[:4]
        if top_batsmen:
            print(f"   🏏 Batting: Pick {min(4, len(top_batsmen))} specialist batsmen")
            for batsman in top_batsmen:
                sr = (batsman['runs'] / batsman['balls'] * 100) if batsman['balls'] > 0 else 0
                print(f"      • {batsman['name']} - {batsman['runs']}R, SR: {sr:.1f}")
        
        # Risk assessment
        print(f"\n⚠️ RISK ASSESSMENT:")
        
        # High-risk, high-reward players
        risky_players = [p for p in all_players if p['fantasy_points'] >= 40 and 
                        ((p['balls'] > 0 and (p['runs'] / p['balls'] * 100) > 150) or 
                         (p['overs'] > 0 and p['wickets'] >= 2))]
        
        if risky_players:
            print(f"   🎲 High Risk/Reward: Consider these explosive performers")
            for player in risky_players[:3]:
                print(f"      • {player['name']} - {player['fantasy_points']:.0f} pts (explosive performance)")
        
        # Safe picks
        safe_players = [p for p in all_players if 20 <= p['fantasy_points'] < 40]
        if safe_players:
            print(f"   🛡️ Safe Picks: Consistent performers for team stability")
            for player in sorted(safe_players, key=lambda x: x['fantasy_points'], reverse=True)[:3]:
                print(f"      • {player['name']} - {player['fantasy_points']:.0f} pts (consistent)")
        
        # Final recommendation
        print(f"\n🏆 FINAL RECOMMENDATION:")
        print(f"   • Captain: {top_performers[0]['name']} (highest points)")
        print(f"   • Vice-Captain: {top_performers[1]['name']} (second highest)")
        print(f"   • Focus on players who contributed with both bat and ball")
        print(f"   • Balance team with 4-5 batsmen, 3-4 bowlers, 1-2 all-rounders")
        print(f"   • Consider ground conditions and team strengths")

def main():
    """Run comprehensive bowling analysis"""
    analyzer = ComprehensiveBowlingAnalysis()
    
    # Test with sample scorecard
    scorecard_url = "https://www.espncricinfo.com/series/twenty20-cup-2003-124121/glamorgan-vs-northamptonshire-midlands-wales-west-group-304750/full-scorecard"
    
    analyzer.complete_analysis(scorecard_url)

if __name__ == "__main__":
    main()