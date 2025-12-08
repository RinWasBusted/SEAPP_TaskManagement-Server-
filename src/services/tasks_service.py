from ..models import db
from ..models.team_model import Team
from ..models.user_model import User
from ..models.task_model import Task
from ..models.association import team_member_association, assignment_association
from sqlalchemy import select, func, case, extract, or_
from sqlalchemy.sql import exists
from datetime import datetime, date, timedelta
from flask import jsonify
from sqlalchemy.orm import joinedload
from .teams_service import isMember
def isTeamTask(team_id , task_id): 
    chk = db.session.query(Task.team_id).filter(Task.id == task_id).scalar() 
    return int(chk) == int(team_id)  
def isMember(user_id, team_id):
    stmt = select(team_member_association).where(
        team_member_association.c.user_id == user_id,
        team_member_association.c.team_id == team_id
    )
    return db.session.scalar(select(stmt.exists()))


def isViceLeader(user_id, team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return False
    return team.vice_leader_id == user_id


def isLeader(user_id, team_id):
    team = db.session.get(Team, team_id)
    if not team:
        return False
    return team.leader_id == user_id


def isTaskAssignedToUser(user_id, task_id):
    stmt = select(assignment_association).where(
        assignment_association.c.user_id == user_id,
        assignment_association.c.task_id == task_id
    )
    return db.session.scalar(select(stmt.exists()))

def getTaskUser(task_id):
    assignees_stmt = select(User).join(assignment_association, assignment_association.c.user_id == User.id).where(
        assignment_association.c.task_id == task_id)
    assignees = db.session.scalars(assignees_stmt).all()
    task = db.session.get(Task, task_id)
    formatted_assignees = [
        {"userId": str(u.id), "name": u.name, "avatarUrl": u.avatar_url}
        for u in assignees
    ]
    return formatted_assignees, task.team_id if task else None


def map_task_to_dict(task):
    if not task:
        return None
    team = db.session.get(Team, task.team_id) if task.team_id else None
    team_name = team.name if team else None
    due_time_str = task.due_time.isoformat() + 'Z' if task.due_time else None

    return {
        "taskId": str(task.id),
        "title": task.title,
        "description": task.description,
        "dueTime": due_time_str,
        "important": task.important,
        "urgent":task.urgent,
        "status": task.status,
        "teamName": team_name,
    }

def getTaskStatistics(user_id):
    user_tasks_stmt = select(assignment_association.c.task_id).where(
        assignment_association.c.user_id == user_id
    ).scalar_subquery()
    total_tasks_query = select(Task.status, func.count().label('count')).where(
        Task.id.in_(user_tasks_stmt)
    ).group_by(Task.status)

    # Lay ra danh sach cac tasks 
    result = db.session.execute(total_tasks_query).all()

    total = sum([c for s, c in result])

    if total == 0:
        return {"success": True, "data": {"totalTasks": 0, "completedPercentage": 0.0, "inProgressPercentage": 0.0,
                                          "toDoPercentage": 0.0 , "tasks": []}}

    stats = {s: c for s, c in result}

    completed = stats.get('completed', 0)
    in_progress = stats.get('in progress', 0)
    to_do = stats.get('to do', 0)

    return {
        "success": True,
        "data": {
            "totalTasks": total,
            "completedPercentage": round((completed / total) * 100, 1),
            "inProgressPercentage": round((in_progress / total) * 100, 1),
            "toDoPercentage": round((to_do/ total) * 100, 1), 
        }
    }


def getTaskStatisticsByTeamId(user_id, team_id):
    if not isMember(user_id, team_id):
        return {"success": False, "error": {"code": "FORBIDDEN", "message": "User is not a member of this team."}}, 403
    total_tasks_query = select(Task.status, func.count().label('count')).where(
        Task.team_id == team_id
    ).group_by(Task.status)

    result = db.session.execute(total_tasks_query).all()

    total = sum([c for s, c in result])

    team = db.session.get(Team, team_id)
    team_name = team.name if team else "Unknown Team"

    if total == 0:
        return {"success": True,
                "data": {"teamId": team_id, "teamName": team_name, "totalTasks": 0, "completedPercentage": 0.0,
                         "inProgressPercentage": 0.0, "toDoPercentage": 0.0}}

    stats = {s: c for s, c in result}

    completed = stats.get('completed', 0)
    in_progress = stats.get('in progress', 0)
    to_do = stats.get('to do', 0)

    return {
        "success": True,
        "data": {
            "teamId": team_id,
            "teamName": team_name,
            "totalTasks": total,
            "completedPercentage": round((completed / total) * 100, 1),
            "inProgressPercentage": round((in_progress / total) * 100, 1),
            "toDoPercentage": round((to_do / total) * 100, 1), 
            "compltedTasks": completed, 
            "inProgressTasks": in_progress, 
            "toDoTasks": to_do 
        }
    }
def getTasksOverview(user_id):
    # today tasks 
    today = date.today()
    due_today_stmt = select(Task).join(assignment_association,
                                       assignment_association.c.task_id == Task.id).where(
        assignment_association.c.user_id == user_id,
        func.date(Task.due_time) == today,
        Task.status != 'completed'
    ).limit(2)
    due_today_query = db.session.scalars(due_today_stmt).all()
    due_today = [map_task_to_dict(task) for task in due_today_query]

    # completed 
    recent_completed_stmt = select(Task).join(assignment_association,
                                              assignment_association.c.task_id == Task.id).where(
        assignment_association.c.user_id == user_id,
        Task.status == 'completed'
    ).order_by(Task.due_time.desc()).limit(2)
    recent_completed_query = db.session.scalars(recent_completed_stmt).all()
    recent_completed = [map_task_to_dict(task) for task in recent_completed_query]

    # In Progress 

    in_progress_stmt = select(Task).join(assignment_association,
                                   assignment_association.c.task_id == Task.id).where(
    assignment_association.c.user_id == user_id,Task.status == 'in progress'
    ).order_by(Task.due_time.desc()).limit(1)
    in_progress_query = db.session.scalars(in_progress_stmt).all()
    in_progress = [map_task_to_dict(task) for task in in_progress_query]


    return {
        "success": True,
        "data": {
            "dueToday": due_today,
            "recentCompleted": recent_completed, 
            "inProgress": in_progress
        }
    }


def getAllUserTasksGroupedByTeam(user_id):
    teams_stmt = select(Team).join(team_member_association,
                                   team_member_association.c.team_id == Team.id).where(
        team_member_association.c.user_id == user_id)
    teams_query = db.session.scalars(teams_stmt).all()

    teams_data = []

    for team in teams_query:
        tasks_stmt = select(Task).join(assignment_association,
                                       assignment_association.c.task_id == Task.id).where(
            Task.team_id == team.id,
            assignment_association.c.user_id == user_id
        )
        tasks_query = db.session.scalars(tasks_stmt).all()

        tasks_list = [
            {
                "taskId": str(task.id),
                "title": task.title,
                "description": task.description,
                "dueTime": task.due_time.isoformat() + 'Z' if task.due_time else None,
            }
            for task in tasks_query
        ]


        leader = db.session.get(User, team.leader_id) if team.leader_id else None

        teams_data.append({
            "teamId": str(team.id),
            "teamName": team.name,
            "teamDescription": team.description,
            "leader": {
                "userId": str(leader.id),
                "name": leader.name
            } if leader else None,
            "tasks": tasks_list
        })

    return {
        "success": True,
        "data": {
            "teams": teams_data
        }
    }

def getTaskDetail(user_id, task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Task not found."}}, 404

    team_id = task.team_id
    chk = isMember(user_id , team_id) 

    if not chk: 
        return {"success": False,
                "error": {"code": "FORBIDDEN", "message": "User does not have access to this task."}}, 403
    assignees, _ = getTaskUser(task_id)
    task_data = map_task_to_dict(task)
    task_data.pop('teamName', None)

    return {
        "success": True,
        "data": {
            **task_data,
            "assignees": assignees
        }, 
        "teamId": team_id 
    }


def updateTaskById(user_id, task_id, data):

    task = db.session.get(Task, task_id)
    if not task:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Task not found."}}, 404

    team_id = task.team_id
    if not (isLeader(user_id, team_id) or isViceLeader(user_id, team_id)):
        if 'status' in data and isTaskAssignedToUser(user_id, task_id) and len(data) == 1:
            pass
        else:
            return {"success": False, "error": {"code": "FORBIDDEN",
                                                "message": "User does not have permission to update this task's details."}}, 403

    try:
        for key, value in data.items():
            if hasattr(task, key):
                if key == 'due_time' and value is not None and isinstance(value, str):
                    value = datetime.fromisoformat(value.replace('Z', '+00:00'))



                setattr(task, key, value)

        db.session.commit()

        return {
            "success": True,
            "message": "Task updated successfully",
            "data": map_task_to_dict(task), 
            "teamId": team_id 
        }
    except Exception as e:
        db.session.rollback()
        print(f"Update Task Error: {e}")
        return {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Could not update task."}}, 500


def deleteTaskById(user_id, task_id):

    task = db.session.get(Task, task_id)
    if not task:
        return {"success": True, "message": "Task deleted successfully"}

    team_id = task.team_id

    if not (isLeader(user_id, team_id) or isViceLeader(user_id, team_id)):
        return {
            "success": False,
            "error": {
                "code": "FORBIDDEN",
                "message": "Only Leader or ViceLeader can delete tasks."
            }
        }, 403

    try:
        # XÓA CÁC DÒNG TRONG BẢNG association (db.Table)
        db.session.execute(
            assignment_association.delete().where(
                assignment_association.c.task_id == task_id
            )
        )

        # XÓA TASK
        db.session.delete(task)
        db.session.commit()

        return {
            "success": True,
            "message": "Task deleted successfully",
            "teamId": team_id
        }

    except Exception as e:
        db.session.rollback()
        print("Delete Task Error:", e)
        return {
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(e)
            }
        }, 500

def getTeamTasks(user_id, team_id):

    if not isMember(user_id, team_id):
        return {"success": False, "error": {"code": "FORBIDDEN", "message": "User is not a member of this team."}}, 403

    team = db.session.get(Team, team_id)
    if not team:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Team not found."}}, 404

    tasks_stmt = select(Task).filter(Task.team_id == team_id)
    tasks_query = db.session.scalars(tasks_stmt).all()

    tasks_list = [
        {
            "taskId": str(task.id),
            "title": task.title,
            "description": task.description,
            "dueTime": task.due_time.isoformat() + 'Z' if task.due_time else None,
            "important": task.important, 
            "urgent": task.urgent, 
            "status": task.status 
        }
        for task in tasks_query
    ]

    return {
        "success": True,
        "data": {
            "teamId": str(team.id),
            "teamName": team.name,
            "tasks": tasks_list
        }
    }


def createTask(user_id, team_id, data):

    if not isMember(user_id, team_id):
        return {"success": False, "error": {"code": "FORBIDDEN", "message": "User is not a member of this team."}}, 403

    team = db.session.get(Team, team_id)
    if not team:
        return {"success": False, "error": {"code": "NOT_FOUND", "message": "Team not found."}}, 404

    try:
        due_time_obj = data.get('dueTime')
        if due_time_obj and isinstance(due_time_obj, str):
            due_time_obj = datetime.fromisoformat(due_time_obj.replace('Z', '+00:00'))

        new_task = Task(
            team_id=team_id,
            title=data['title'],
            description=data.get('description'),
            due_time=due_time_obj,
            important=data.get('important', False),
            urgent=data.get('urgent', False),
            status=data.get('status', 'to do')
        )

        db.session.add(new_task)
        db.session.flush()

        # Gán Assignees
        assignee_ids = data.get('assigneeIds', [])
        if not assignee_ids:
            assignee_ids = [user_id]

        assignment_values = [
            {"task_id": new_task.id, "user_id": assignee_id}
            for assignee_id in assignee_ids
        ]

        if assignment_values:
            from sqlalchemy import insert
            assignment_insert_stmt = insert(assignment_association).values(assignment_values)
            db.session.execute(assignment_insert_stmt)

        db.session.commit()

        return {
            "success": True,
            "message": "Task created successfully",
            "data": map_task_to_dict(new_task)
        }, 201

    except Exception as e:
        db.session.rollback()
        print(f"Create Task Error: {e}")
        return {"success": False, "error": {"code": "INTERNAL_ERROR", "message": "Could not create task."}}, 500


def searchTasks(user_id, query, team_id=None, status=None, important=None,urgent = None):
    base_stmt = select(Task).join(assignment_association,
                                  assignment_association.c.task_id == Task.id).where(
        assignment_association.c.user_id == user_id
    ).distinct(Task.id)

    if query:
        base_stmt = base_stmt.filter(
            or_(
                Task.title.ilike(f'%{query}%'),
                Task.description.ilike(f'%{query}%')
            )
        )
    if team_id:
        if not isMember(user_id, team_id):
            return {"success": False,
                    "error": {"code": "FORBIDDEN", "message": "User is not a member of the specified team."}}, 403
        base_stmt = base_stmt.filter(Task.team_id == team_id)

    if status:
        base_stmt = base_stmt.filter(Task.status == status)

    if important:
        base_stmt = base_stmt.filter(Task.important == important)

    if urgent:
        base_stmt = base_stmt.filter(Task.urgent == urgent)

    tasks = db.session.scalars(base_stmt).all()
    results = [map_task_to_dict(task) for task in tasks]

    return {
        "success": True,
        "data": {
            "query": query,
            "results": results
        }
    }

def searchTaskByName(user_id, text):
    if not text or text.strip() == "":
        return []
    search_text = f"%{text}%"

    tasks = (
        Task.query
            .join(assignment_association, Task.id == assignment_association.c.task_id)
            .filter(assignment_association.c.user_id == user_id)
            .filter(Task.title.ilike(search_text))
            .all()
    )
    return [task.to_dict_to_send() for task in tasks]

def saveTask(user_id , team_id , task_id): 
    chk_1 = isMember(user_id=user_id , team_id = team_id) 
    chk_2 = isTeamTask(team_id=team_id , task_id= task_id)
    if not chk_1: 
        print('Loi 1') 
    if not chk_2: 
        print('Loi 2') 
    if (not chk_1) or (not chk_2):
        return None 
    stmp = assignment_association.select().where(
        assignment_association.c.user_id == user_id, 
        assignment_association.c.task_id == task_id 
    )
    res = db.session.execute(stmp).fetchone() 
    if res is not None: 
        return {
            "success": True, 
            "message": "You already save this"
        }
    stmt = assignment_association.insert().values(
        user_id = user_id, 
        task_id = task_id 
    )
    db.session.execute(stmt) 
    db.session.commit() 
    return {
        "success": True, 
        "message": "Save task successfully" 
    }

def unSavedTask(user_id , task_id): 
    stmp = assignment_association.select().where(
        assignment_association.c.user_id == user_id, 
        assignment_association.c.task_id == task_id 
    )

    res = db.session.execute(stmp).fetchone() 
    if res is None: 
        return None 
    
    stmt = assignment_association.delete().where(
        assignment_association.c.user_id == user_id,
        assignment_association.c.task_id == task_id
    )
    db.session.execute(stmt) 
    db.session.commit() 
    return {
        "success": True, 
        "message": "Unsave tasks successfully" 
    }

