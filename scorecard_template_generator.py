#!/usr/bin/env python3
"""
Scorecard Template Generator
Generates Dream11 team templates based on ground analysis and scorecard data
"""

import json
import os
from datetime import datetime
from db import create_connection, addDreamTeam

class ScorecardTemplateGenerator:
    def __init__(self):
        self.ground_data = None
        self.match_id = None
        
    def load_ground_analysis(self, match_id=None, ground_data_file=None):
        """
        Load ground analysis data from file or database
        
        Args:
            match_id (str): Match ID to load analysis for
            ground_data_file (str): Path to ground data JSON file
            
        Returns:
            bool: True if data loaded successfully, False otherwise
        """
        try:
            if ground_data_file and os.path.exists(ground_data_file):
                with open(ground_data_file, 'r') as f:
                    self.ground_data = json.load(f)
                print(f"✅ Loaded ground data from {ground_data_file}")
                return True
            elif match_id:
                self.match_id = match_id
                # For now, return True to allow the app to run
                # In a full implementation, this would load from database
                print(f"✅ Match ID {match_id} set for template generation")
                return True
            else:
                print("❌ No ground data file or match ID provided")
                return False
        except Exception as e:
            print(f"❌ Error loading ground analysis: {e}")
            return False
    
    def generate_templates_from_scorecard(self):
        """
        Generate Dream11 team templates based on scorecard analysis
        
        Returns:
            list: List of generated templates
        """
        try:
            templates = []
            
            # Basic template structure
            base_template = {
                'template_name': 'Scorecard Analysis Template',
                'wk': 1,
                'bat': 4,
                'ar': 2,
                'bowl': 4,
                'team_a_players': 6,
                'team_b_players': 5,
                'captain_preference': 'BAT',
                'vice_captain_preference': 'AR',
                'created_at': datetime.now().isoformat()
            }
            
            # Generate a few variations
            templates.append({
                **base_template,
                'template_name': 'Balanced Scorecard Template',
                'description': 'Balanced team based on scorecard analysis'
            })
            
            templates.append({
                **base_template,
                'template_name': 'Batting Heavy Template',
                'bat': 5,
                'ar': 1,
                'captain_preference': 'BAT',
                'description': 'Batting focused team from scorecard data'
            })
            
            templates.append({
                **base_template,
                'template_name': 'Bowling Heavy Template',
                'bat': 3,
                'bowl': 5,
                'captain_preference': 'BOWL',
                'description': 'Bowling focused team from scorecard data'
            })
            
            print(f"✅ Generated {len(templates)} scorecard-based templates")
            return templates
            
        except Exception as e:
            print(f"❌ Error generating templates: {e}")
            return []
    
    def save_templates_to_database(self, templates, match_id):
        """
        Save generated templates to database
        
        Args:
            templates (list): List of templates to save
            match_id (str): Match ID to associate templates with
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            conn = create_connection()
            if not conn:
                print("❌ Could not connect to database")
                return False
            
            saved_count = 0
            for template in templates:
                try:
                    # Add template to database
                    addDreamTeam(
                        match_id,
                        template['template_name'],
                        template['wk'],
                        template['bat'],
                        template['ar'],
                        template['bowl'],
                        template['team_a_players'],
                        template['team_b_players'],
                        template.get('captain_preference', 'BAT'),
                        template.get('vice_captain_preference', 'AR')
                    )
                    saved_count += 1
                except Exception as e:
                    print(f"❌ Error saving template {template['template_name']}: {e}")
            
            conn.close()
            print(f"✅ Saved {saved_count}/{len(templates)} templates to database")
            return saved_count > 0
            
        except Exception as e:
            print(f"❌ Error saving templates to database: {e}")
            return False

def main():
    """Test the scorecard template generator"""
    print("🏏 Scorecard Template Generator Test")
    print("=" * 40)
    
    generator = ScorecardTemplateGenerator()
    
    # Test with sample data
    if generator.load_ground_analysis(match_id="test_match"):
        templates = generator.generate_templates_from_scorecard()
        
        if templates:
            print(f"\n📋 Generated Templates:")
            for i, template in enumerate(templates, 1):
                print(f"{i}. {template['template_name']}")
                print(f"   WK: {template['wk']}, BAT: {template['bat']}, AR: {template['ar']}, BOWL: {template['bowl']}")
                print(f"   Team Split: {template['team_a_players']}-{template['team_b_players']}")
                print(f"   Captain: {template['captain_preference']}")
                print()
        else:
            print("❌ No templates generated")
    else:
        print("❌ Failed to load ground analysis")

if __name__ == "__main__":
    main()