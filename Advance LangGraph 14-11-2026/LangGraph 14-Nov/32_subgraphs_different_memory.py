from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

# GYM Program
# No of visits = attendance
# No of sets = multiple/visit

class AttendanceState(BaseModel):
    new_sets: int = 0
    attendance_message: str = ''
    # private fields: the parent state does not have them
    visits: int = 0
    total_sets: int = 0

def count_visit(state: AttendanceState):
    visits = state.visits + 1
    total_sets = state.total_sets + state.new_sets
    return {
        'visits': visits,
        'total_sets': total_sets,
        'attendance_message': f'visit number {visits}, {total_sets} sets in total'
    }

attendance_graph = StateGraph(AttendanceState)
attendance_graph.add_node('count_visit', count_visit)

attendance_graph.add_edge(START, 'count_visit')
attendance_graph.add_edge('count_visit', END)
attendance_subgraph = attendance_graph.compile(checkpointer=True)

class WorkoutState(BaseModel):
    new_sets: int = 0
    workout_message: str = ''
    # private field: the parent state does not have it
    sets: int = 0

def count_set(state: WorkoutState):
    sets = state.sets + state.new_sets
    return {
        'sets': sets, # This is not saving previous values, because of no memory
        'workout_message': f'{sets} sets today'
    }

workout_graph = StateGraph(WorkoutState)
workout_graph.add_node('count_set', count_set)

workout_graph.add_edge(START, 'count_set')
workout_graph.add_edge('count_set', END)

workout_subgraph = workout_graph.compile()

class GymState(BaseModel):
    new_sets: int = 0
    attendance_message: str = ''
    workout_message: str = ''

graph = StateGraph(GymState)
graph.add_node('attendance', attendance_subgraph)
graph.add_node('workout', workout_subgraph)

graph.add_edge(START, 'attendance')
graph.add_edge('attendance', 'workout')
graph.add_edge('workout', END)
workflow = graph.compile(checkpointer=InMemorySaver())

member_1 = {'configurable': {'thread_id': 'member-1'}}
member_2 = {'configurable': {'thread_id': 'member-2'}}

result = workflow.invoke({'new_sets': 3}, member_1)
print(f"member-1: {result['attendance_message']} | {result['workout_message']}")

result = workflow.invoke({'new_sets': 5}, member_1)
print(f"member-1: {result['attendance_message']} | {result['workout_message']}")


result = workflow.invoke({'new_sets': 4}, member_1)
print(f"member-1: {result['attendance_message']} | {result['workout_message']}")
