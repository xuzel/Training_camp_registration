"""
管理员功能路由
"""

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional
import pandas as pd
import io
import json
from datetime import datetime
from database import db_manager

router = APIRouter()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()

# 管理员凭据
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """验证管理员身份"""
    if credentials.username == ADMIN_USERNAME and credentials.password == ADMIN_PASSWORD:
        return credentials.username
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    """显示管理员登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/admin/login")
async def admin_login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """处理管理员登录"""
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(key="admin_session", value="authenticated", httponly=True)
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "用户名或密码错误"
        })

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request, table: str = "registrations"):
    """管理员主页面"""
    # 简单的session验证
    if not request.cookies.get("admin_session"):
        return RedirectResponse(url="/admin/login", status_code=302)

    # 获取数据
    if table == "feedback":
        data = db_manager.get_all_feedback()
        table_name = "满意度反馈"
    else:
        data = db_manager.get_all_registrations()
        table_name = "报名信息"
        # 处理attendance_days字段显示
        for item in data:
            if isinstance(item.get('attendance_days'), list):
                item['attendance_days'] = ', '.join(item['attendance_days'])

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "data": data,
        "current_table": table,
        "table_name": table_name,
        "total_count": len(data)
    })

@router.post("/admin/delete")
async def delete_record(
    request: Request,
    table: str = Form(...),
    record_ids: str = Form(...)
):
    """删除记录"""
    # 验证session
    if not request.cookies.get("admin_session"):
        return RedirectResponse(url="/admin/login", status_code=302)

    try:
        # 解析ID列表
        ids = [int(id.strip()) for id in record_ids.split(',') if id.strip()]

        if table == "feedback":
            success = db_manager.delete_feedback_by_ids(ids)
        else:
            success = db_manager.delete_registrations_by_ids(ids)

        if success:
            return RedirectResponse(url=f"/admin?table={table}&delete_success=true", status_code=302)
        else:
            return RedirectResponse(url=f"/admin?table={table}&delete_error=true", status_code=302)

    except Exception as e:
        print(f"删除记录错误: {e}")
        return RedirectResponse(url=f"/admin?table={table}&delete_error=true", status_code=302)

@router.get("/admin/export")
async def export_data(request: Request, table: str = "registrations"):
    """导出数据为Excel文件"""
    # 验证session
    if not request.cookies.get("admin_session"):
        return RedirectResponse(url="/admin/login", status_code=302)

    try:
        # 获取数据
        if table == "feedback":
            data = db_manager.get_all_feedback()
            filename = f"feedback_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            # 重命名列标题
            column_mapping = {
                'id': 'ID',
                'name': '姓名',
                'participation_date': '参与日期',
                'trainer_satisfaction': '讲师满意度',
                'content_satisfaction': '内容满意度',
                'venue_satisfaction': '场地满意度',
                'equipment_satisfaction': '器材满意度',
                'schedule_satisfaction': '课程安排满意度',
                'overall_satisfaction': '整体满意度',
                'favorite': '最喜欢的部分',
                'improvement': '改善建议',
                'future_suggestions': '未来建议',
                'other_comments': '其他意见',
                'created_at': '提交时间'
            }
        else:
            data = db_manager.get_all_registrations()
            filename = f"registrations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            # 处理attendance_days字段
            for item in data:
                if isinstance(item.get('attendance_days'), list):
                    item['attendance_days'] = ', '.join(item['attendance_days'])
            # 重命名列标题
            column_mapping = {
                'id': 'ID',
                'full_name': '姓名',
                'phone': '电话',
                'wechat': '微信',
                'email': '邮箱',
                'occupation': '职业',
                'attendance_days': '出席日期',
                'backup_plan': '备选方案',
                'experience': '健身经验',
                'goal': '目标',
                'competition_experience': '比赛经验',
                'comp_category': '比赛级别',
                'injury_history': '受伤历史',
                'questions': '问题',
                'channel': '了解渠道',
                'products': '产品兴趣',
                'future_services': '未来服务',
                'agree_terms': '同意条款',
                'created_at': '报名时间'
            }

        if not data:
            return RedirectResponse(url=f"/admin?table={table}&export_error=true", status_code=302)

        # 创建DataFrame
        df = pd.DataFrame(data)

        # 重命名列
        df = df.rename(columns=column_mapping)

        # 创建Excel文件
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='数据')

        output.seek(0)

        # 返回Excel文件
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }

        return Response(
            content=output.getvalue(),
            headers=headers,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        print(f"导出数据错误: {e}")
        return RedirectResponse(url=f"/admin?table={table}&export_error=true", status_code=302)

@router.get("/admin/logout")
async def admin_logout(request: Request):
    """管理员登出"""
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="admin_session")
    return response