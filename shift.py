from datetime import datetime, timedelta

class Shift:
    def __init__(self, area,  start_time, end_time, volunteers_needed, penibility):
        self.area = area
        self.penibility = penibility
        self.start_time = start_time  # This should be a datetime object
        
        self.end_time = end_time      # This should be a datetime object
        self.volunteers_needed = volunteers_needed
        self.volunteers_acceptable = volunteers_needed
        self.assigned_volunteers = []  # To track which volunteers are assigned to this shift


    def nb_hours(self):
        duration = self.end_time - self.start_time
        return duration.total_seconds() / 3600
    
    
    def __repr__(self):
        start_day_time = f"{self.start_time.strftime('%d %H:%M')}"
        end_day_time = f"{self.end_time.strftime('%d %H:%M')}"
        return f"{self.area} from {start_day_time} to {end_day_time}"



def create_shifts(config):
    shifts = []
    for area, shifts_info in config.items():
        for shift_info in shifts_info:
            time_range = shift_info['time']
            start_str, end_str = time_range.split(' - ')
            start_datetime = datetime.strptime(start_str, "%d/%m/%Y %H:%M:%S")
            end_datetime = datetime.strptime(end_str, "%d/%m/%Y %H:%M:%S")
            volunteers_needed = shift_info['volunteers_needed']
            penibility = shift_info.get('penibilite', 1)  # Default penibility value set to 1 if not specified

            shift = Shift(area, start_datetime, end_datetime, volunteers_needed, penibility)
            shifts.append(shift)
    
    return shifts


