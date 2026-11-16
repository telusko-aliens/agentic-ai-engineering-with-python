from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END

# ---------- grade subgraph ----------
class GradeState(BaseModel):
    marks: int = 0
    grade: str = ''

def calculate_grade(state: GradeState):
    print('--- grade subgraph: calculate_grade ---')
    return {'grade': 'Pass' if state.marks >= 40 else 'Fail'}

grade_graph = StateGraph(GradeState)
grade_graph.add_node('calculate_grade', calculate_grade)

grade_graph.add_edge(START, 'calculate_grade')
grade_graph.add_edge('calculate_grade', END)

grade_subgraph = grade_graph.compile()

# ---------- attendance subgraph ----------
class AttendanceState(BaseModel):
    days_present: int = 0
    total_days: int = 0
    status: str = ''

def check_attendance(state: AttendanceState):
    print('--- attendance subgraph: check_attendance ---')
    percentage = state.days_present * 100 / state.total_days
    return {'status': 'Regular' if percentage >= 75 else 'Irregular'}

attendance_graph = StateGraph(AttendanceState)
attendance_graph.add_node('check_attendance', check_attendance)

attendance_graph.add_edge(START, 'check_attendance')
attendance_graph.add_edge('check_attendance', END)

attendance_subgraph = attendance_graph.compile()


# ---------- parent graph ----------
class StudentState(BaseModel):
    student_marks: int = 0
    present_days: int = 0
    working_days: int = 0
    student_grade: str = ''
    attendance_status: str = ''
    report: str = ''

def get_student_info(state: StudentState):
    print('--- parent: get_student_info ---')

    # calling grade subgraph
    grade_result = grade_subgraph.invoke({
        'marks': state.student_marks
    })

    # calling attendance subgraph
    attendance_result = attendance_subgraph.invoke({
        'days_present': state.present_days,
        'total_days': state.working_days,
    })

    return {
        'student_grade': grade_result['grade'],
        'attendance_status': attendance_result['status'],
    }

def write_report(state: StudentState):
    print('--- parent: write_report ---')
    return {'report': f'Grade: {state.student_grade}, Attendance: {state.attendance_status}'}

graph = StateGraph(StudentState)
graph.add_node('get_student_info', get_student_info)
graph.add_node('write_report', write_report)

graph.add_edge(START, 'get_student_info')
graph.add_edge('get_student_info', 'write_report')
graph.add_edge('write_report', END)

workflow = graph.compile()

final_state = workflow.invoke({'student_marks': 20, 'present_days': 20, 'working_days': 100})
print(final_state['report'])

png = workflow.get_graph(xray=True).draw_mermaid_png()
with open('28_multiple_subgraphs.png', 'wb') as f:
    f.write(png)