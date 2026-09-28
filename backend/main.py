from fastapi import FastAPI

# 创建应用实例
app = FastAPI(title="校园教务规划系统")

# 根路径接口
@app.get("/")
def read_root():
    return {"msg": "Hello FastAPI，项目启动成功！"}

# 测试接口
@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"你好，{name}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
