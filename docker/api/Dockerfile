FROM python:3.13-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000","--reload"]



# 코드를 바꾸면 꼭 build를 다시 해야함

