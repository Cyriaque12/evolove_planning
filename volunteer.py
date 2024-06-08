from datetime import timedelta
from datetime import datetime

class Volunteer:
    def __init__(self, name, team_id, starting_time, max_hours):
        self.name = name
        self.prenom = name.split(',')[-1].strip()
        self.team_id = team_id
        self.assigned_shifts = []  # To track the shifts assigned to this volunteer
        self.starting_time = starting_time
        self.busy_times = []  # List of tuples representing busy start and end times
        self.nb_of_solo_shifts_hours = 0
        self.max_hours = max_hours

    def add_busy_time(self, start, end):
        self.busy_times.append((start, end))


    def is_available(self, new_shift):
        # Check if the new shift starts after the volunteer's starting time
        if new_shift.start_time < self.starting_time:
            return False
        
        if self.is_otherwise_busy(new_shift):
            return False
                    
        # Check for direct overlaps and ensure a two-hour gap between shifts
        for shift in self.assigned_shifts:
            # Check for direct overlap
            if new_shift.start_time < shift.end_time and new_shift.end_time > shift.start_time:
                return False
            
            # Check for a one hour gap between shifts
            allowed_gap = timedelta(hours=1)
            if new_shift.start_time < (shift.end_time + allowed_gap) and new_shift.end_time > (shift.start_time - allowed_gap):
                return False
            
            # Additional rule for late-night shifts
            if 22 < shift.start_time.hour < 24 or 0 <= shift.start_time.hour < 4:
                # If the shift starts late at night, ensure the next shift starts no earlier than 12 hours after
                if new_shift.start_time < (shift.end_time + timedelta(hours=12)):
                    return False
            
        # Check if adding this shift exceeds the maximum allowed hours
        if self.hours_worked() + new_shift.nb_hours() > self.max_hours:
            return False
        
        return True
    
    def is_otherwise_busy(self, shift):
        for busy_start, busy_end in self.busy_times:
            if not (shift.end_time <= busy_start or shift.start_time >= busy_end):
                return True
        return False

    def assign_shift(self, shift):
        if shift.volunteers_needed == 1:
            self.nb_of_solo_shifts_hours += shift.nb_hours()
        self.assigned_shifts.append(shift)
        shift.assigned_volunteers.append(self)

    def hours_worked(self):
        return sum(shift.nb_hours() for shift in self.assigned_shifts)

    def penibility_score(self):
        return sum(shift.penibility for shift in self.assigned_shifts) 

    def __repr__(self):
        return f"{self.name}  Team: {self.team_id}"


def create_volunteers(config):
    volunteers = []
    for item in config['volunteers']:
        name = item['name']
        team_id = item['team']
        starting_time = datetime.strptime(item['starting_time'], '%d/%m/%Y %H:%M:%S')
        max_hours = item.get('max_hours', 11)  
        volunteer = Volunteer(name.strip(), team_id, starting_time, max_hours)
        # Process busy times if any
        if 'busy_times' in item:
            for busy_period in item['busy_times']:
                start, end = busy_period.split(' - ')
                busy_start = datetime.strptime(start.strip(), '%d/%m/%Y %H:%M:%S')
                busy_end = datetime.strptime(end.strip(), '%d/%m/%Y %H:%M:%S')
                volunteer.add_busy_time(busy_start, busy_end)
        volunteers.append(volunteer)
    return volunteers