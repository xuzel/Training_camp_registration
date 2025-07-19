from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

# 导入路由
from routers import registration, feedback, admin

app = FastAPI(title="训练营报名系统", description="训练营报名管理系统")

# 静态文件配置
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板配置
templates = Jinja2Templates(directory="templates")

# 创建必要目录
os.makedirs("routers", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# 包含路由
app.include_router(registration.router)
app.include_router(feedback.router)
app.include_router(admin.router)

# 主页面路由
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, registration_success: bool = False, feedback_success: bool = False):
    """主页面"""
    return templates.TemplateResponse("main.html", {
        "request": request,
        "registration_success": registration_success,
        "feedback_success": feedback_success
    })

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "服务正常运行"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)