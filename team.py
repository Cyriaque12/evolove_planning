class Team:
    def __init__(self, team_id,  regulars):
        self.team_id = team_id
        self.members = regulars
    
    def average_hours_worked(self):
        total_hours = 0
        total_members = 0  
        for member in self.members:
            total_hours += member.hours_worked()
            total_members += 1
        return total_hours / total_members
    
    def average_penibility(self):
        total_penibility = 0
        total_members = 0
        for member in self.members:
            total_penibility += member.penibility_score()
            total_members += 1
        return total_penibility / total_members

    def is_team_available(self, shift):
        for member in self.members:
            if not member.is_available(shift):
                return False
        return True

    def assign_team_to_shift(self, shift):
        for member in self.members:
            member.assign_shift(shift)

    def nb_volunteers(self):
        return len(self.members)

    def __repr__(self):
        return f"Team Members: {', '.join(map(str, self.members))}"
    
def form_teams(volunteers):
    teams = {}
    for volunteer in volunteers:
        if volunteer.team_id not in teams:
            teams[volunteer.team_id] = {'members': []}
        teams[volunteer.team_id]['members'].append(volunteer)
    return [Team(team_id,  team_info['members']) for team_id, team_info in teams.items()]
