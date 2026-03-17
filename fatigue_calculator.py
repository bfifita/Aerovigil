def calculate_fatigue_score(duty_hours, segments, timezone_changes, rest_hours, circadian_disruption):
    score = 0
    score += duty_hours * 3
    score += segments * 4
    score += timezone_changes * 5
    score += circadian_disruption * 4
    score -= rest_hours * 2
    score = max(0, min(100, score))
    return score
