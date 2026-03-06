from fastapi import FastAPI, Path, HTTPException, status

from schema import TodoCreateRequest, TodoUpdateRequest, TodoResponse

app = FastAPI()

# 임시 데이터 저장소
todos = []

next_id = 1

# ① 전체 할 일 목록 보기
@app.get("/todos",response_model=list[TodoResponse])
def get_todo_handler():
    return todos

# ② 할 일 추가하기
@app.post("/todos",status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
def create_todo_handler(body: TodoCreateRequest):
    global next_id
    
    new_todo = {
        "id": next_id,
        "title": body.title,
        "is_done": False,
    }

    todos.append(new_todo)
    next_id += 1

    return new_todo

# ③ 할 일 완료/미완료 체크하기

@app.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_todo_handler(
    body: TodoUpdateRequest,
    todo_id : int = Path(..., ge=1)
):
    for todo in todos:
        if todo["id"] == todo_id:
            todo["is_done"] = body.is_done
            return todo
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="존재하지 않는 할 일입니다",
    )

# ④ 할 일 삭제하기

@app.delete("/todos/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_handler(todo_id:int = Path(..., ge=1)):
    for i, todo in enumerate(todos):
        if todo["id"] == todo_id:
            todos.pop(i)
            return
    

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="존재하지 않는 할 일입니다",
    )