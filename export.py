from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, PageBreak
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import datetime

def get_team_header_elements(team):
    elements = []
    # Define a style for the paragraph
    styles = getSampleStyleSheet()
    # Creating a list of member names and total hours
    total_hours_worked = sum(member.hours_worked() for member in team.members) / team.nb_volunteers()
    member_names = ', '.join(member.name for member in team.members)
    # Adding team details to elements
    title_style = styles['Title']
    team_members_paragraph = Paragraph(f"Equipe {team.team_id}: {member_names}", title_style)
    elements.append(team_members_paragraph)
    hours_paragraph = Paragraph(f"Heures travaillées : {total_hours_worked}", styles['Normal'])
    elements.append(hours_paragraph)
    elements.append(Spacer(1, 20))  # More spacing between the header and the table
    return elements

def custom_sort_key(time_slot):
    start_time_str = time_slot.split(' - ')[0]
    start_time = datetime.datetime.strptime(start_time_str, '%H:%M')
    
    # Adjust the hour for sorting: time slots starting at 8:00 AM or later and before midnight are adjusted by subtracting 8 hours
    # Time slots starting from midnight to before 8:00 AM are adjusted by adding 16 hours
    if start_time.hour >= 8:
        # This creates a pseudo "day" starting at 8 AM
        sort_time = start_time - datetime.timedelta(hours=8)
    else:
        # This handles the overnight shift, continuing from 24:00 to 32:00 (0:00 to 8:00 AM)
        sort_time = start_time + datetime.timedelta(hours=16)
    
    return sort_time

def build_team_elements(team, shifts):
    elements = get_team_header_elements(team)
    
    # Define festival days
    start_date = min(shift.start_time for shift in shifts)
    end_date = max(shift.end_time for shift in shifts)
    festival_days = []
    current_day = datetime.datetime(start_date.year, start_date.month, start_date.day, 11, 0)
    while current_day < end_date:
        # Getting the French name of the day
        
        festival_days.append(current_day)
        current_day += datetime.timedelta(days=1)

    # Organize shifts into a dictionary mapping festival days to activities per timeslot
    schedule = {i+1: {} for i in range(len(festival_days))}
    for shift in shifts:
        if any(volunteer in shift.assigned_volunteers for volunteer in team.members):
            shift_start = shift.start_time
            shift_end = shift.end_time
            # Identify the festival day
            for i, day_start in enumerate(festival_days):
                day_end = day_start + datetime.timedelta(hours=19)  # Till 6:00 AM next day
                if day_start <= shift_start < day_end:
                    festival_day = i + 1
                    break
            time_slot = f"{shift_start.strftime('%H:%M')} - {shift_end.strftime('%H:%M')}"
            shift_data = f"{shift.area}"
            if shift.volunteers_needed == 1:
                shift_data += f" ({shift.assigned_volunteers[0].prenom} solo)"
            schedule[festival_day][time_slot] = shift_data

    # Prepare the table data
    all_time_slots = sorted(
            {slot for day in schedule.values() for slot in day},
            key=custom_sort_key
        )

    table_data = [['Horaire / Jour'] + [f'{french_day_name[day.strftime('%A')]}' for day in festival_days]]
    for slot in all_time_slots:
        row = [slot]
        for day in sorted(schedule.keys()):
            row.append(schedule[day].get(slot, ''))
        table_data.append(row)

    # Assuming you have 5 columns and you want them to equally divide the page width (minus margins)
    page_width, page_height = letter  # letter is 612 x 792 points
    margin = 72  # assuming a 1 inch margin on each side
    usable_width = page_width - 2 * margin
    column_width = usable_width / len(table_data[0])  # Divide the usable width by the number of columns
    team_table = Table(table_data, colWidths=[column_width]*len(table_data[0]))
    
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.darkgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.lightgrey, colors.white]),  # Alternating row colors
        ('FONTSIZE', (0,0), (-1,-1), 10),  # Set font size for better readability
    ]))
    elements.append(team_table)
    return elements

def create_team_pdf(team, shifts):
    # File name includes the team ID to distinguish between different PDFs
    file_name = f"output/team_{team.team_id}_schedule.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=letter)
    doc.build(build_team_elements(team, shifts))


def create_global_pdf(shifts, teams):
    # File name includes the team ID to distinguish between different PDFs
    file_name = f"output/global_schedule.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=letter)
    elements = []
    # shifts.sort(key=lambda shift: shift.start_time)
    # shift_data = [['Lieu', 'Debut', 'Fin', 'Duree', 'Team', 'Besoin Volontaires', 'Nb vololontaires team']]
    # for shift in shifts:
    #     start_time = f"{shift.start_time}"
    #     end_time = f"{shift.end_time}"
    #     team = shift.assigned_volunteers[0].team_id 
    #     besoin_volontaire = shift.volunteers_needed
    #     nb_volontaire = len(shift.assigned_volunteers)
    #     shift_data.append([ shift.area, start_time, end_time, shift.nb_hours(), team, besoin_volontaire, nb_volontaire])
    
    # shift_table = Table(shift_data)
    # shift_table.setStyle(TableStyle([
    #     ('BACKGROUND', (0,0), (-1,0), '#CCCCCC'),
    #     ('TEXTCOLOR', (0,0), (-1,0), '#FFFFFF'),
    #     ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    #     ('GRID', (0,0), (-1,-1), 1, '#666666')
    # ]))
    # elements.append(shift_table)
    # elements.append(PageBreak())
    compteur = 0
    for team in teams:
        for team_element in build_team_elements(team, shifts):
            elements.append(team_element)
        compteur += 1
        if compteur % 3 == 0:
            elements.append(PageBreak())
        else:
            elements.append(Spacer(1, 20)) 
    
    doc.build(elements)

def create_besoin_pdf(shifts):
    file_name = f"output/besoin_benevoles.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=letter)
    elements = []
    shifts.sort(key=lambda shift: (shift.area, shift.start_time))
    shift_data = [['Lieu', 'Debut', 'Fin', 'Besoin Volontaires']]
    for shift in shifts:
        start_time = f"{shift.start_time}"
        end_time = f"{shift.end_time}"
        besoin_volontaire = shift.volunteers_needed
        shift_data.append([shift.area, start_time, end_time, besoin_volontaire])
    
    shift_table = Table(shift_data)
    shift_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), '#CCCCCC'),
        ('TEXTCOLOR', (0,0), (-1,0), '#FFFFFF'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 1, '#666666')
    ]))
    elements.append(shift_table)
    doc.build(elements)

def generate_pdfs_for_all_teams(teams, shifts):
    for team in teams:
        create_team_pdf(team, shifts)
    create_global_pdf(shifts, teams)
    create_besoin_pdf(shifts)
# Example usage:
# generate_pdfs_for_all_teams(teams, shifts)


# Translating the day into French
french_day_name = {
    'Monday': 'Lundi',
    'Tuesday': 'Mardi',
    'Wednesday': 'Mercredi',
    'Thursday': 'Jeudi',
    'Friday': 'Vendredi',
    'Saturday': 'Samedi',
    'Sunday': 'Dimanche'
}