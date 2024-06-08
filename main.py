from shift import  create_shifts
from team import form_teams
from assigner import assign_shifts
from volunteer import  create_volunteers
from export import generate_pdfs_for_all_teams
import yaml
import random



def load_config(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)

def main():
    shifts = create_shifts(load_config('config/shifts.yaml'))
    shifts.sort(key=lambda shift: shift.start_time)
    total_work_hours_needed = 0
    for shift in shifts:
        total_work_hours_needed += shift.nb_hours() * shift.volunteers_needed
    print(f"Total work hours needed: {total_work_hours_needed}")

    volunteers = create_volunteers(load_config('config/volunteers.yaml'))
    print(f"Total volunteers: {len(volunteers)}")
    teams = form_teams(volunteers)
    # for team in teams:
    #     print(f"Team {team.team_id} has {team.nb_volunteers()} members members {team.members}")
    assign_shifts(shifts, teams)
    total_work_hours_worked = 0
    for volunteer in volunteers:
        total_work_hours_worked += volunteer.hours_worked()
    print(f"Total work hours worked: {total_work_hours_worked}")
    
    shifts.sort(key=lambda shift: shift.start_time)
    for shift in shifts:
        volunteers_names = [volunteer.name for volunteer in shift.assigned_volunteers]
        # print(f"{shift} has {len(shift.assigned_volunteers)} volunteers assigned {volunteers_names}")
        if len(shift.assigned_volunteers) == 0:
            print(f"Error: {shift} has no volunteers assigned")


    # for volunter in volunteers:
    #     print(f"{volunter} has {len(volunter.assigned_shifts)} shifts assigned for a total of {volunter.hours_worked()} hours")
    for team in teams:
        print(f'Team {team.team_id} has {team.average_hours_worked()} avg hours')
    

    generate_pdfs_for_all_teams(teams, shifts)

if __name__ == '__main__':
    main()