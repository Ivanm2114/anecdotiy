from requests import post, delete, put, get


# Пустой запрос

print(put('http://localhost:5000/api/jobs/1').json())

# Недостаток данныхх
print(put('http://localhost:5000/api/jobs/1',
          json={'job': 'test1'}).json())

# Несуществующий id
print(put('http://localhost:5000/api/jobs/4',
          json={'id': 1,
                'job': 'etst3',
                'team_leader': 1,
                'work_size': 15,
                'is_finished': False,
                'collaborators': '4,6'}).json())

# Рабочий запрос
print(put('http://localhost:5000/api/jobs/3', json={'job': 'deployment of residential modules 3 and 6',
                                                    'team_leader': 2,
                                                    'work_size': 5,
                                                    'is_finished': False,
                                                    'collaborators': '3'}).json())

print(get('http://localhost:5000/api/jobs').json())
