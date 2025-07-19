"""
报名功能路由
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from database import db_manager

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/registration", response_class=HTMLResponse)
async def registration_form(request: Request):
    """显示报名表单"""
    return templates.TemplateResponse("registration.html", {"request": request})


@router.post("/registration/submit")
async def submit_registration(
        request: Request,
        full_name: str = Form(...),
        phone: str = Form(...),
        wechat: str = Form(...),
        email: str = Form(...),
        occupation: str = Form(...),
        attendance_days: List[str] = Form([]),
        backup_plan: str = Form(...),
        experience: str = Form(...),
        goal: str = Form(...),
        competition_experience: str = Form(...),
        comp_category: Optional[str] = Form(""),
        injury_history: str = Form(...),
        questions: Optional[str] = Form(""),
        channel: str = Form(...),
        products: Optional[str] = Form(""),
        future_services: Optional[str] = Form(""),
        agree_terms: Optional[str] = Form(None)
):
    """处理报名表单提交"""

    # 验证必填字段
    if not all([full_name, phone, wechat, email, occupation, backup_plan,
                experience, goal, competition_experience, injury_history, channel]):
        return templates.TemplateResponse("registration.html", {
            "request": request,
            "error": "请填写所有必填字段"
        })

    # 验证是否同意条款
    if not agree_terms:
        return templates.TemplateResponse("registration.html", {
            "request": request,
            "error": "请同意条款及细则"
        })

    # 验证出席日期
    if not attendance_days:
        return templates.TemplateResponse("registration.html", {
            "request": request,
            "error": "请选择至少一个出席日期"
        })

    # 构建报名数据
    registration_data = {
        'full_name': full_name,
        'phone': phone,
        'wechat': wechat,
        'email': email,
        'occupation': occupation,
        'attendance_days': attendance_days,
        'backup_plan': backup_plan,
        'experience': experience,
        'goal': goal,
        'competition_experience': competition_experience,
        'comp_category': comp_category if comp_category else '',
        'injury_history': injury_history,
        'questions': questions if questions else '',
        'channel': channel,
        'products': products if products else '',
        'future_services': future_services if future_services else '',
        'agree_terms': True
    }

    # 保存到数据库
    success = db_manager.insert_registration(registration_data)

    if success:
        # 重定向到主页，并带上成功消息
        response = RedirectResponse(url="/?registration_success=true", status_code=302)
        return response
    else:
        return templates.TemplateResponse("registration.html", {
            "request": request,
            "error": "报名提交失败，请重试"
        })


@router.get("/registration/list")
async def list_registrations(request: Request):
    """查看所有报名（管理员功能）"""
    registrations = db_manager.get_all_registrations()
    return templates.TemplateResponse("registration_list.html", {
        "request": request,
        "registrations": registrations
    })