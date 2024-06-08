
def meets_hard_constraints(team, shift):
    if not team.is_team_available(shift):
        return False
    if team.nb_volunteers() < shift.volunteers_acceptable:
        return False
    return True

def calculate_soft_constraint_score(team, shift):
    score = 0
    score += (100 - team.average_penibility()) / 100
    score -= team.average_hours_worked() / 2
    if team.nb_volunteers() == shift.volunteers_needed:
        score += 3
    return score

def calculate_solo_shift_score(volunteer, team, shift):
    score = -volunteer.nb_of_solo_shifts_hours * 2
    score -= len(team.members) * 3
    for teammate in team.members:
        if teammate == volunteer:
            continue
        if teammate.is_otherwise_busy(shift):
            score += 20
        if teammate.nb_of_solo_shifts_hours > volunteer.nb_of_solo_shifts_hours:
            score += teammate.nb_of_solo_shifts_hours - volunteer.nb_of_solo_shifts_hours
    
    return score


def assign_solo_shifts(shifts, teams):
    solo_shifts = [shift for shift in shifts if shift.volunteers_needed == 1]
    for shift in solo_shifts:
        best_volunteer = None
        best_score = -float('inf')
        for team in teams:
            for volunteer in team.members:
                if volunteer.is_available(shift):
                    score = calculate_solo_shift_score(volunteer, team, shift)
                    if score > best_score:
                        best_score = score
                        best_volunteer = volunteer
        if best_volunteer:
            print(f"{shift} solo assigned to {best_volunteer}")
            best_volunteer.assign_shift(shift)



def assign_shifts(shifts, teams):
    assign_solo_shifts(shifts, teams)

    for shift in shifts:
        
        if len(shift.assigned_volunteers) == shift.volunteers_needed:
            continue

        best_team = None
        best_score = -float('inf')

        # First, filter teams by hard constraints
        eligible_teams = [team for team in teams if meets_hard_constraints(team, shift)]
        if len(eligible_teams) == 0:
            print(f"Error: No team available for shift {shift} need {shift.volunteers_acceptable} volunteers lowering acceptable volunteers by 1")
            shift.volunteers_acceptable -= 1
            eligible_teams = [team for team in teams if meets_hard_constraints(team, shift)]

        if len(eligible_teams) == 0:
            print(f"Error: No team available for shift {shift}")
            continue
        
        # min_hours_worked = min(team.average_hours_worked() for team in eligible_teams)
        # least_worked_teams = [team for team in eligible_teams if team.average_hours_worked() == min_hours_worked]

        # Then, among eligible teams, find the one that best meets soft constraints
        for team in eligible_teams:
            score = calculate_soft_constraint_score(team, shift)
            if score > best_score:
                best_score = score
                best_team = team

        # Assign the best team to the shift
        if best_team:
            # available_times = [(team.team_id, team.chief.hours_worked()) for team in eligible_teams]
            # print(f"{shift} assigned to team {best_team.team_id} ")
            best_team.assign_team_to_shift(shift)
