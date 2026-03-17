# AeroVigil

Predictive Fatigue Analytics for Aviation Safety Teams

AeroVigil is a prototype fatigue risk analysis tool designed to help aviation safety departments identify potential crew fatigue risks using operational schedule data.

## Problem

Airlines must manage fatigue risk under Fatigue Risk Management Systems (FRMS).  
However, many operators lack simple tools to quickly evaluate fatigue risk across multiple crew schedules.

## Solution

AeroVigil analyzes crew scheduling factors and calculates a fatigue risk score based on:

- Duty hours
- Flight segments
- Time zone crossings
- Rest hours
- Circadian disruption

The system then flags elevated fatigue risk and explains the operational drivers behind the risk.

## Current Features

- Fatigue risk scoring algorithm
- CSV crew schedule analysis
- Fatigue risk ranking dashboard
- High-risk crew alerts
- Fatigue driver explanations
- Fatigue risk heatmap visualization

## Example Output

| Pilot | Fatigue Score | Risk | Why Flagged |
|------|------|------|------|
| Mike | 82 | CRITICAL | Long duty period, Short rest, Circadian disruption |
| John | 72 | HIGH | Multiple time zones, High segments |
| Sarah | 21 | LOW | No major fatigue drivers |

## Running the Prototype

AeroVigil is a prototype aviation fatigue risk analytics tool designed to help ariline safety teams identify fatigue risk using duty hours, circadian disruption, flight segments, rest periods, and timezone changes. 
Built with:
-python
-streamlit
-pandas

Install dependencies:
