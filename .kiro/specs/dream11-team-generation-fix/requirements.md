# Requirements Document

## Introduction

This feature simplifies the Dream11 custom teams functionality to generate a single optimized team based on player selection percentages. The system will replace the complex 40-team generation with a streamlined approach that creates one high-quality team using the top 11 players by selection percentage.

## Requirements

### Requirement 1

**User Story:** As a Dream11 user, I want the system to generate a single optimized team based on selection percentages, so that I can focus on the best performing players without complexity.

#### Acceptance Criteria

1. WHEN the custom teams page is accessed THEN the system SHALL generate exactly one team labeled "Team 1: Top Performers"
2. WHEN generating the team THEN the system SHALL select the top 11 players sorted by highest selection percentage
3. WHEN the team is created THEN the system SHALL include strategy title "Highest Selection Percentage Strategy" and description explaining the selection criteria
4. WHEN there are insufficient players (less than 11) THEN the system SHALL handle this gracefully without crashing

### Requirement 2

**User Story:** As a Dream11 user, I want the generated team to have proper captain and vice-captain assignments, so that I can maximize my fantasy points according to Dream11 rules.

#### Acceptance Criteria

1. WHEN Team 1 is generated THEN the system SHALL assign the highest percentage player as captain
2. WHEN Team 1 is generated THEN the system SHALL assign the second highest percentage player as vice-captain
3. WHEN captain and vice-captain are assigned THEN the system SHALL mark them with is_captain and is_vice_captain flags
4. WHEN displaying the team THEN the system SHALL show captain and vice-captain designations clearly

### Requirement 3

**User Story:** As a Dream11 user, I want the system to validate team composition and handle edge cases, so that I always get a valid playable team.

#### Acceptance Criteria

1. WHEN selecting players THEN the system SHALL filter out DNS (Did Not Start) players before sorting
2. WHEN creating the team THEN the system SHALL validate that exactly 11 unique players are selected
3. WHEN team validation fails THEN the system SHALL not create the team and handle the error gracefully
4. WHEN the team is successfully created THEN the system SHALL calculate and display the total percentage score for all 11 players

### Requirement 4

**User Story:** As a Dream11 user, I want the simplified interface to load quickly and be easy to understand, so that I can make team decisions efficiently.

#### Acceptance Criteria

1. WHEN the custom teams page loads THEN the system SHALL remove all complex team generation logic (Teams 2-40)
2. WHEN displaying Team 1 THEN the system SHALL show player names, teams, roles, credits, and percentages clearly
3. WHEN the page renders THEN the system SHALL maintain the existing template structure but with simplified data
4. WHEN ground analysis is available THEN the system SHALL still apply ground insights to player percentages before sorting