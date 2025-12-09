from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from .parsers import update_task_parser, search_tasks_parser, create_task_parser , search_task_by_name
from ..extensions import logger


from ..services.tasks_service import (
    getTaskStatistics,
    getTaskStatisticsByTeamId,
    getTasksOverview,
    getAllUserTasksGroupedByTeam,
    getTaskDetail,
    updateTaskById,
    deleteTaskById,
    searchTasks,
    createTask,
    getTeamTasks, 
    searchTaskByName, 
    saveTask, 
    unSavedTask 
)

tasks_bp = Blueprint('tasks', __name__)
tasks_api = Api(tasks_bp)



class TaskStatistics(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        logger.info(f"User (id:{user_id}) requested task statistics.")
        result = getTaskStatistics(user_id=user_id)
        return result


class TaskStatisticsByTeam(Resource):

    @jwt_required()
    def get(self, teamId):
        user_id = int(get_jwt_identity())
        logger.info(f"User (id:{user_id}) requested task statistics for Team (id:{teamId}).")
        result = getTaskStatisticsByTeamId(user_id=user_id, team_id=teamId)
        return result


class TasksOverview(Resource):
    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        logger.info(f"User (id:{user_id}) requested tasks overview.")
        result = getTasksOverview(user_id=user_id)
        return result


class AllUserTasks(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        logger.info(f"User (id:{user_id}) requested all tasks grouped by team.")
        result = getAllUserTasksGroupedByTeam(user_id=user_id)
        return result

class TaskDetail(Resource):
    @jwt_required()
    def get(self, taskId):
        user_id = int(get_jwt_identity())
        logger.info(f"User (id:{user_id}) requested details for Task (id:{taskId}).")
        result = getTaskDetail(user_id=user_id, task_id=taskId)
        return result

    @jwt_required()
    def put(self, taskId):
        user_id = int(get_jwt_identity())
        args = update_task_parser.parse_args()

        # Lọc các trường có giá trị None
        update_data = {k: v for k, v in args.items() if v is not None}

        logger.info(f"User (id:{user_id}) is updating Task (id:{taskId}).")
        result = updateTaskById(user_id=user_id, task_id=taskId, data=update_data)
        
        if result.get('success'):
            logger.info(f"Task (id:{taskId}) updated successfully by User (id:{user_id}).")
        else:
            logger.warning(f"Failed to update Task (id:{taskId}) by User (id:{user_id}).")
        
        return result

    @jwt_required()
    def delete(self, taskId):
        user_id = int(get_jwt_identity())
        logger.info(f"User (id:{user_id}) is deleting Task (id:{taskId}).")
        result = deleteTaskById(user_id=user_id, task_id=taskId)
        
        if result.get('success'):
            logger.info(f"Task (id:{taskId}) deleted successfully by User (id:{user_id}).")
        else:
            logger.warning(f"Failed to delete Task (id:{taskId}) by User (id:{user_id}).")
        
        return result

class TaskFilter(Resource):

    @jwt_required()
    def get(self):
        user_id = int(get_jwt_identity())
        args = search_tasks_parser.parse_args()

        query = args.get('q')
        team_id = args.get('teamId')
        status = args.get('status')
        important = args.get('important')

        logger.info(f"User (id:{user_id}) is filtering tasks with query='{query}', team_id={team_id}, status={status}, important={important}.")
        result = searchTasks(
            user_id=user_id,
            query=query,
            team_id=team_id,
            status=status,
            important=important
        )
        return result

class TaskSearch(Resource): 
    @jwt_required() 
    def post(self): 
        user_id = int(get_jwt_identity()) 
        query = search_task_by_name.parse_args() 
        text = query.get('searchText')
        
        logger.info(f"User (id:{user_id}) is searching tasks with text: '{text}'.")
        res = searchTaskByName(user_id=user_id , text=text) 
        
        return {
            "success": True, 
            "tasks": res 
        } 

class TeamTasksResource(Resource):

    @jwt_required()
    def post(self, teamId):
        user_id = int(get_jwt_identity())
        args = create_task_parser.parse_args()
        data = {k: v for k, v in args.items() if v is not None}
        
        logger.info(f"User (id:{user_id}) is creating a new task in Team (id:{teamId}).")
        result = createTask(user_id=user_id, team_id=teamId, data=data)
        
        if result.get('success'):
            task_id = result.get('data', {}).get('id')
            logger.info(f"Task (id:{task_id}) created successfully in Team (id:{teamId}) by User (id:{user_id}).")
        else:
            logger.warning(f"Failed to create task in Team (id:{teamId}) by User (id:{user_id}).")
        
        return result

    @jwt_required()
    def get(self, teamId):
        user_id = int(get_jwt_identity())
        logger.info(f"User (id:{user_id}) requested tasks for Team (id:{teamId}).")
        result = getTeamTasks(user_id=user_id, team_id=teamId)
        return result

class TaskSaving(Resource): 
    @jwt_required() 
    def post(self):     
        current_user_id = int(get_jwt_identity()) 
        if not current_user_id: 
            logger.warning("Save task failed: Token is invalid or failed.")
            return {
                "success": False, 
                "message": "Token is failed or invalid" 
            } 
        
        data = dict(request.json) 
        task_id = data.get('task_id') 
        team_id = data.get('team_id')
        
        logger.info(f"User (id:{current_user_id}) is saving Task (id:{task_id}) from Team (id:{team_id}).")
        save_result = saveTask(user_id=current_user_id , team_id=team_id , task_id=task_id) 

        if not save_result: 
            logger.warning(f"Failed to save Task (id:{task_id}) by User (id:{current_user_id}).")
            return {
                "success": False, 
            } , 401
        
        logger.info(f"Task (id:{task_id}) saved successfully by User (id:{current_user_id}).")
        return save_result
    
    @jwt_required() 
    def delete(self): 
        current_user_id = int(get_jwt_identity()) 
        if not current_user_id: 
            logger.warning("Unsave task failed: Token is invalid or failed.")
            return {
                "success": False, 
                "message": "Token is failed or invalid" 
            }
        
        data = dict(request.form) 
        task_id = data.get('task_id')
        
        logger.info(f"User (id:{current_user_id}) is unsaving Task (id:{task_id}).")
        result = unSavedTask(task_id=task_id ,user_id=current_user_id)
        
        if not result: 
            logger.warning(f"Failed to unsave Task (id:{task_id}) by User (id:{current_user_id}).")
            return {
                "success": False, 
                "message": "Unsave failed"
            } , 401
        
        logger.info(f"Task (id:{task_id}) unsaved successfully by User (id:{current_user_id}).")
        return result
    
tasks_api.add_resource(TaskStatistics, '/statistics')
tasks_api.add_resource(TaskStatisticsByTeam, '/statistics/teams/<string:teamId>')
tasks_api.add_resource(TasksOverview, '/overview')
tasks_api.add_resource(AllUserTasks, '/me')
tasks_api.add_resource(TaskDetail, '/<string:taskId>')
tasks_api.add_resource(TaskFilter, '/filter')
tasks_api.add_resource(TeamTasksResource, '/teams/<string:teamId>/tasks')
tasks_api.add_resource(TaskSearch , '/search-tasks/user')
tasks_api.add_resource(TaskSaving , '/save/user')