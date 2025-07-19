"""
满意度反馈功能路由
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from datetime import date
from database import db_manager

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/feedback", response_class=HTMLResponse)
async def feedback_form(request: Request):
    """显示满意度反馈表单"""
    return templates.TemplateResponse("feedback.html", {"request": request})


@router.post("/feedback/submit")
async def submit_feedback(
        request: Request,
        name: Optional[str] = Form(""),
        participation_date: date = Form(...),
        trainer_satisfaction: int = Form(...),
        content_satisfaction: int = Form(...),
        venue_satisfaction: int = Form(...),
        equipment_satisfaction: int = Form(...),
        schedule_satisfaction: int = Form(...),
        overall_satisfaction: int = Form(...),
        favorite: Optional[str] = Form(""),
        improvement: Optional[str] = Form(""),
        future_suggestions: Optional[str] = Form(""),
        other_comments: Optional[str] = Form("")
):
    """处理满意度反馈表单提交"""

    # 验证必填字段
    if not all([participation_date, trainer_satisfaction, content_satisfaction,
                venue_satisfaction, equipment_satisfaction, schedule_satisfaction,
                overall_satisfaction]):
        return templates.TemplateResponse("feedback.html", {
            "request": request,
            "error": "请填写所有必填字段"
        })

    # 验证评分范围
    satisfaction_scores = [
        trainer_satisfaction, content_satisfaction, venue_satisfaction,
        equipment_satisfaction, schedule_satisfaction, overall_satisfaction
    ]

    if not all(1 <= score <= 5 for score in satisfaction_scores):
        return templates.TemplateResponse("feedback.html", {
            "request": request,
            "error": "评分必须在1-5之间"
        })

    # 构建反馈数据
    feedback_data = {
        'name': name if name else '',
        'participation_date': participation_date,
        'trainer_satisfaction': trainer_satisfaction,
        'content_satisfaction': content_satisfaction,
        'venue_satisfaction': venue_satisfaction,
        'equipment_satisfaction': equipment_satisfaction,
        'schedule_satisfaction': schedule_satisfaction,
        'overall_satisfaction': overall_satisfaction,
        'favorite': favorite if favorite else '',
        'improvement': improvement if improvement else '',
        'future_suggestions': future_suggestions if future_suggestions else '',
        'other_comments': other_comments if other_comments else ''
    }

    # 保存到数据库
    success = db_manager.insert_feedback(feedback_data)

    if success:
        # 重定向到主页，并带上成功消息
        response = RedirectResponse(url="/?feedback_success=true", status_code=302)
        return response
    else:
        return templates.TemplateResponse("feedback.html", {
            "request": request,
            "error": "反馈提交失败，请重试"
        })


@router.get("/feedback/list")
async def list_feedback(request: Request):
    """查看所有反馈（管理员功能）"""
    feedback_list = db_manager.get_all_feedback()
    return templates.TemplateResponse("feedback_list.html", {
        "request": request,
        "feedback_list": feedback_list
    })