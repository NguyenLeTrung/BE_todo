from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializer import *
from django.db.models import Q
import datetime
import jwt
import MySQLdb
from rest_framework.views import APIView

# Create your views here.
@api_view(['GET'])
def index(request):
    return Response({"message": "Hello World"})

db = MySQLdb.connect(host='localhost', user='root', password='123456', db='todo')

# ==== USER API ====
class UserView():
    # Đăng ký thông tin 
    @api_view(['POST'])
    def register(request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=404)

    # Đăng nhập thông tin 
    @api_view(['POST'])
    def login(request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect password!")
        
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)

        # sql = """ SELECT * FROM todo_user u WHERE u.username = '""" + request.data["username"] + """' """
        # print(sql)
        # cursor = db.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute(sql)

        user = User.objects.raw("SELECT * FROM todo_user u WHERE u.username = %s", [request.data["username"]])
        cursor = UserSerializer(user, many=True).data

        response.data = {
            'jwt': token,
            'user': cursor
        }

        return response

    # Đăng xuất thông tin 
    @api_view(['POST'])
    def logout(self):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }

        return response
    
    @api_view(['GET'])
    def search_user(request):
        params = request.GET
        keyword = params.get('keyword', '')
        user = User.objects.filter(Q(username__icontains=keyword))
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)

# ==== TASK API =====
class TaskView():
    # Tạo mới một todo
    @api_view(['POST'])
    def create_task(request):
        data = request.data
        print(request.data)
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(serializer.errors)
    
    # Tìm kiếm todo
    # @api_view(['GET'])
    # def search_task(request):
    #     params = request.GET
    #     keyword = params.get('keyword', '')
    #     task = Task.objects.filter(Q(title__icontans=keyword))
    #     serializer = TaskSerializer(task, many=True)

    #     return Response(serializer.data)
      

    # @api_view(['GET'])
    # def list_task(request):
    #     task = Task.objects.all()
    #     data = TaskSerializer(task, many=True).data
    #     return Response(data)

    # Sửa thông tin todo
    @api_view(['PUT'])
    def update_task(request, pk):
        try:
            data = request.data
            task = Task.objects.get(pk=pk)
            task.title = data['title']

            task.save()
            return Response({'message': 'success'})
        except Exception as e:
            return Response({'success': False, 'error': str(e)})
    
    # Xóa thông tin 
    @api_view(['DELETE'])
    def delete_task(request, pk):
        try:
            task = Task.objects.get(pk=pk)
            task.delete()

            return Response({'message': 'success'})
        except Exception as e:
            return Response({'message': 'error', 'error': str(e)})

# Hiển thị ra danh sách các todo
class ListTodo(APIView):
    def get(self, request, pk):
        # todo = Task.objects.get(pk=pk)
        # serializer = TaskSerializer(todo).data
        # cursor = db.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute("""select t.* from todo.todo_task t join todo.todo_user u on t.user_id = u.id where u.id = """ + pk)
        # return Response(cursor)

        todo = Task.objects.raw("select t.* from todo.todo_task t join todo.todo_user u on t.user_id = u.id where u.id = %s", [pk])
        data = TaskSerializer(todo, many=True).data
        return Response(data)