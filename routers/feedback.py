"""
满意度反馈功能路由
"""

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
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
        knowledge: int = Form(...),
        technique: int = Form(...),
        planning: int = Form(...),
        confidence: int = Form(...),
        instructor: int = Form(...),
        materials: int = Form(...),
        venue: int = Form(...),
        suggestions: Optional[str] = Form(""),
        products: Optional[str] = Form(""),
        services: Optional[str] = Form("")
):
    """处理满意度反馈表单提交"""

    # 验证必填字段
    if not all([knowledge, technique, planning, confidence, instructor, materials, venue]):
        return templates.TemplateResponse("feedback.html", {
            "request": request,
            "error": "请填写所有必填字段"
        })

    # 验证评分范围
    satisfaction_scores = [knowledge, technique, planning, confidence, instructor, materials, venue]

    if not all(1 <= score <= 5 for score in satisfaction_scores):
        return templates.TemplateResponse("feedback.html", {
            "request": request,
            "error": "评分必须在1-5之间"
        })

    # 构建反馈数据
    feedback_data = {
        'knowledge_improvement': knowledge,
        'technique_understanding': technique,
        'planning_ability': planning,
        'confidence_boost': confidence,
        'instructor_satisfaction': instructor,
        'materials_satisfaction': materials,
        'venue_satisfaction': venue,
        'suggestions': suggestions if suggestions else '',
        'desired_products': products if products else '',
        'desired_services': services if services else ''
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