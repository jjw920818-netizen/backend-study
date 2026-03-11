from fastapi import FastAPI, Path , Query

from schema import UserSignUpRequest, UserSignUpResponse

users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Charlie"},
]

app = FastAPI()

#  HTTP 요청

# def hello_world():
#     return {"msg": "Hello_World!"}

# 서버에 GET / hello 요청이 들어오면, root_handler 함수가 실행됩니다.
@app.get("/users") # @ 데코레이터: 함수에 추가적인 기능을 부여하는 문법
def get_users_handler():
    # AI 추론
    return users


# 단일 사용자 조회 API

#{user_id} 번 사용자 조회 API
#Path(경로) + Parameter(매개변수) => 동적으로 바뀌는 값을 한 번에 처리
# Path Parameter에 type hint 추가하면 -> 명시한 타입이 맞는지 검사 & 보장 "1" -> 1로 변환해줌
@app.get("/users/{user_id}")
def get_user_handler(
    user_id: int = Path(..., ge=1, description="user_id는 1 이상")
    ): 
    # gt: 초과
    # ge: 이상
    # lt: 미만
    # le: 이하
    # max_digits: 최대 자릿수
    return users[user_id - 1]

# GET / users/1
    # @app.get("/users/1")
    # def get_first_handler():
    #     return users[0]  변수처럼 바뀌는 값으로 바꾸자 해서 user_id로 바꿔줌

# 회원가입 API
# HTTP Method: POST,GET,PUT,DELETE,PATCH
@app.post("/users/sign-up") # POST: 리소스 생성 
def sign_up_user_handler(user: UserSignUpRequest):
    # 핸들러 함수에 선언한 매개변수의 타입힌트가 BaseModel을 상속 받은 경우, 요청 본문에서 가져옴
    # 데이터를 가져오면서. 타입힌트에 선언한 데이터 구조와 맞는지 검사

    # body = UserSignUpRequest(name="Alice", age=30)
    #body 데이터가 문제 없으면 -> 핸들러 함수로 전달
    # body 데이터가 문제 있으면 -> FastAPI가 자동으로 422 Unprocessable Entity 응답 반환

    new_user = {
        "id": len(users) + 1,
        "name": user.name,
        "age": user.age
    }
    users.append(new_user)
    return
#snake_case: 변수명, 함수명, 클래스명 등에서 띄어쓰기 대신 언더스코어(_)로 구분하는 방식
# HTTP 연결 '-'

# 회원 검색 API
# Query Parameter
# ?key=value 형태로 Path 뒤에 붙는 매개변수
# 데이터 조회시 부가 조건을 명시(필터링, 정렬, 페이지네이션 등)할 때 주로 사용
@app.get("/users/search")
def search_user_handler(name: str):
    # name 이라는 key로 넘어오는 Query Parameter 값을 사용하겠다
    return{"name": name}

@app.get("/users/search")
def search_user_handler(
    name: str = Query(..., min_length = 2), #... -> 필수값 (required)
    age: int = Query(None, ge=1), #default 값 지정 -> 선택적 (optional)
):
    # name 이라는 key로 넘어오는 Query Parameter 값을 사용하겠다
    return{"name": name, "age": age}

# ?field =id -> id 라는 key로 넘어오는 Query Parameter 값을 사용하겠다
# ?field =name -> name 라는 key로 넘어오는 Query Parameter 값을 사용하겠다
# 없으면 -> id,name 반환

@app.get("/users/{user_id}")
def get_user_handler(
    user_id: int = Path(..., ge=1, description="사용자의 ID"),
    field: str = Query(None,description="출력할 필드 선택(id 또는 name)") # id 또는 name만 허용
    ): 
    user = users[user_id - 1]
    if field is ("id","name"):
        return (field, user[field])
    return user


# 1번 댓글(comment) 조회
# GET / comments/1

# 10번 댓글 삭제
# DELETE / comments/10

# 새로운 댓글 생성
# POST / comments

# comments 집단에  POST 

# 요청 = HTTP Method(동작, verb) + URL(대상, object)

###### 실습 ######
# GET / items/{item_name}
# item_name : str & 최대 글자수(max_length) 6
# 응답 형식: {"item_name": ...}
@app.get("/items/{item_name}")
def get_item_handler(
    item_name: str = Path(..., max_length=6)):
    return {"item_name": item_name}

# Type Hint: 함수의 매개변수나 반환값에 데이터 타입을 명시하는 것
# 코드 가독성 향상, IDE의 자동 완성 기능 활용, 타입 검사 도구 사용 가능, 런타임 검증 도구(Pydantic, FastAPI) 활용 가능,
# FastAPI에서 Type Hint는 API 요청과 응답의 데이터 모델을 정의하는 데 사용

