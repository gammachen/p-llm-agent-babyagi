```python
import json
from typing import List, Dict, Optional
from datetime import datetime, date

# 模拟数据库
MOCK_STUDENTS = {
    "STU2024001": {"name": "张三", "class": "高三(1)班", "age": 17, "parent_phone": "13800138001"},
    "STU2024002": {"name": "李四", "class": "高三(2)班", "age": 16, "parent_phone": "13800138002"},
    "STU2024003": {"name": "王五", "class": "高二(1)班", "age": 16, "parent_phone": "13800138003"}
}

MOCK_GRADES = {
    "STU2024001": [
        {"subject": "数学", "score": 95, "exam_date": "2024-03-15", "exam_name": "月考"},
        {"subject": "语文", "score": 88, "exam_date": "2024-03-15", "exam_name": "月考"}
    ],
    "STU2024002": [
        {"subject": "数学", "score": 78, "exam_date": "2024-03-15", "exam_name": "月考"},
        {"subject": "英语", "score": 92, "exam_date": "2024-03-15", "exam_name": "月考"}
    ]
}

MOCK_SCHEDULES = {
    "STU2024001": {
        "周一": [
            {"time": "08:00-09:40", "course": "数学", "teacher": "张老师", "location": "教学楼A101"},
            {"time": "10:00-11:40", "course": "语文", "teacher": "李老师", "location": "教学楼A102"}
        ],
        "周二": [
            {"time": "08:00-09:40", "course": "英语", "teacher": "王老师", "location": "教学楼A103"},
            {"time": "10:00-11:40", "course": "物理", "teacher": "赵老师", "location": "实验楼B201"}
        ]
    }
}

MOCK_COURSES = {
    "数学": {"credit": 4, "description": "高等数学课程", "assessment": "闭卷考试", "textbook": "《高中数学必修》"},
    "语文": {"credit": 3, "description": "语言文学课程", "assessment": "论文+考试", "textbook": "《高中语文必修》"}
}

MOCK_LIBRARY = {
    "STU2024001": {
        "current": [
            {"book_name": "红楼梦", "borrow_date": "2024-03-01", "due_date": "2024-04-01"},
            {"book_name": "数学分析", "borrow_date": "2024-03-10", "due_date": "2024-04-10"}
        ],
        "history": [
            {"book_name": "三国演义", "borrow_date": "2024-01-01", "return_date": "2024-02-01"}
        ]
    }
}

# 1. 获取学生基本信息
def get_student_info(student_name: str) -> dict:
    """
    根据学生姓名获取学生基本信息
    :param student_name: 学生姓名
    :return: 学生基本信息 dict, 包含学生ID、姓名、班级、年龄、家长手机号，比如：
    {
        "success": True,
        "data": {
            "student_id": "STU2024001",
            "name": "张三",
            "class": "高三(1)班",
            "age": 17,
            "parent_phone": "13800138001"
        }
    }
    """
    for student_id, info in MOCK_STUDENTS.items():
        if info["name"] == student_name:
            return {
                "success": True,
                "data": {
                    "student_id": student_id,
                    "name": info["name"],
                    "class": info["class"],
                    "age": info["age"],
                    "parent_phone": info["parent_phone"]
                }
            }
    return {"success": False, "error": "学生不存在"}

# 2. 查询学生最近成绩
def get_student_latest_grade_by_id(student_id: str) -> dict:
    """
    根据学生ID获取最近一次考试的成绩
    :param student_id: 学生ID（需要通过获取学生信息接口get_student_info(student_name: str)获取）
    :return: 最近一次考试成绩 dict, 包含考试名称、考试日期、成绩列表
    """
    if student_id not in MOCK_GRADES:
        return {"success": False, "error": "该学生暂无成绩记录"}
    
    latest_grades = MOCK_GRADES[student_id]
    return {
        "success": True,
        "data": {
            "student_id": student_id,
            "latest_exam": latest_grades[0]["exam_name"],
            "exam_date": latest_grades[0]["exam_date"],
            "grades": latest_grades
        }
    }

# 3. 查询学生课程表
def get_student_schedule(student_id: str, week_day: Optional[str] = None) -> dict:
    """
    获取学生课程表，可按星期几筛选
    """
    if student_id not in MOCK_SCHEDULES:
        return {"success": False, "error": "该学生课程表未找到"}
    
    schedule = MOCK_SCHEDULES[student_id]
    if week_day and week_day in schedule:
        return {"success": True, "data": {week_day: schedule[week_day]}}
    
    return {"success": True, "data": schedule}

# 4. 查询课程详细信息
def get_course_details(course_name: str) -> dict:
    """
    获取课程的详细信息
    """
    if course_name not in MOCK_COURSES:
        return {"success": False, "error": "课程不存在"}
    
    return {
        "success": True,
        "data": {
            "course_name": course_name,
            **MOCK_COURSES[course_name]
        }
    }

# 5. 提交请假申请
def submit_leave_application(student_id: str, reason: str, 
                           start_date: str, end_date: str) -> dict:
    """
    为学生提交请假申请
    """
    if student_id not in MOCK_STUDENTS:
        return {"success": False, "error": "学生不存在"}
    
    # 模拟生成请假单号
    leave_id = f"LEAVE{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "success": True,
        "data": {
            "leave_id": leave_id,
            "student_id": student_id,
            "student_name": MOCK_STUDENTS[student_id]["name"],
            "reason": reason,
            "start_date": start_date,
            "end_date": end_date,
            "status": "待审批",
            "submit_time": datetime.now().isoformat()
        }
    }

# 6. 查询图书馆借阅记录
def get_library_records(student_id: str, query_type: str = "current") -> dict:
    """
    查询学生的图书馆借阅记录
    """
    if student_id not in MOCK_LIBRARY:
        return {"success": False, "error": "该学生无借阅记录"}
    
    if query_type not in ["current", "history"]:
        return {"success": False, "error": "查询类型必须是 current 或 history"}
    
    return {
        "success": True,
        "data": {
            "student_id": student_id,
            "records": MOCK_LIBRARY[student_id][query_type],
            "record_type": "当前借阅" if query_type == "current" else "历史借阅"
        }
    }

# 7. 查询校园卡余额和消费记录
def get_campus_card_info(student_id: str) -> dict:
    """
    查询学生的校园卡信息和最近消费记录
    """
    if student_id not in MOCK_STUDENTS:
        return {"success": False, "error": "学生不存在"}
    
    # 模拟数据
    mock_transactions = [
        {"date": "2024-03-15", "amount": -15.5, "location": "食堂一楼", "type": "消费"},
        {"date": "2024-03-14", "amount": -8.0, "location": "校园超市", "type": "消费"},
        {"date": "2024-03-10", "amount": 200.0, "location": "充值中心", "type": "充值"}
    ]
    
    return {
        "success": True,
        "data": {
            "student_id": student_id,
            "balance": 176.5,  # 计算后的余额
            "card_status": "正常",
            "recent_transactions": mock_transactions
        }
    }

# 8. 查询作业和考试安排
def get_homework_and_exams(student_id: str, subject: Optional[str] = None) -> dict:
    """
    查询学生的作业和考试安排
    """
    if student_id not in MOCK_STUDENTS:
        return {"success": False, "error": "学生不存在"}
    
    # 模拟数据
    mock_assignments = [
        {"subject": "数学", "type": "作业", "content": "练习册P35-38", "due_date": "2024-03-18"},
        {"subject": "语文", "type": "作业", "content": "背诵《滕王阁序》", "due_date": "2024-03-17"},
        {"subject": "数学", "type": "考试", "content": "单元测试", "date": "2024-03-20"}
    ]
    
    if subject:
        filtered_assignments = [a for a in mock_assignments if a["subject"] == subject]
    else:
        filtered_assignments = mock_assignments
    
    return {
        "success": True,
        "data": {
            "student_id": student_id,
            "assignments": filtered_assignments,
            "total_count": len(filtered_assignments)
        }
    }

# 9. 查询校园通知和公告
def get_school_notices(notice_type: Optional[str] = None, 
                      limit: int = 5) -> dict:
    """
    获取校园最新通知和公告
    """
    # 模拟数据
    mock_notices = [
        {"id": 1, "title": "清明节放假通知", "type": "通知", "publish_date": "2024-03-20", "content": "4月4日-4月6日放假调休..."},
        {"id": 2, "title": "数学竞赛报名开始", "type": "活动", "publish_date": "2024-03-18", "content": "全国高中数学竞赛报名开始..."},
        {"id": 3, "title": "图书馆开放时间调整", "type": "通知", "publish_date": "2024-03-15", "content": "即日起图书馆开放时间调整为..."}
    ]
    
    if notice_type:
        filtered_notices = [n for n in mock_notices if n["type"] == notice_type]
    else:
        filtered_notices = mock_notices
    
    return {
        "success": True,
        "data": {
            "notices": filtered_notices[:limit],
            "total_count": len(filtered_notices)
        }
    }

# 10. 查询体育活动信息
def get_sports_activities(student_id: str) -> dict:
    """
    查询学生的体育活动和体质测试信息
    """
    if student_id not in MOCK_STUDENTS:
        return {"success": False, "error": "学生不存在"}
    
    # 模拟数据
    mock_sports_info = {
        "pe_class": {"teacher": "刘老师", "time": "每周三下午", "location": "操场"},
        "recent_test": {"date": "2024-03-10", "item": "1000米跑", "score": "4分30秒", "result": "良好"},
        "sports_teams": ["篮球社", "田径队"],
        "next_activity": {"date": "2024-03-25", "event": "校级篮球比赛", "location": "体育馆"}
    }
    
    return {
        "success": True,
        "data": {
            "student_id": student_id,
            "sports_info": mock_sports_info
        }
    }

# 示例：测试函数调用
if __name__ == "__main__":
    # 测试获取学生信息
    result = get_student_info("张三")
    print("学生信息:", json.dumps(result, indent=2, ensure_ascii=False))
    
    if result["success"]:
        student_id = result["data"]["student_id"]
        # 测试获取成绩
        grade_result = get_student_latest_grade_by_id(student_id)
        print("\n最近成绩:", json.dumps(grade_result, indent=2, ensure_ascii=False))
        
        # 测试获取课程表
        schedule_result = get_student_schedule(student_id, "周一")
        print("\n周一课程表:", json.dumps(schedule_result, indent=2, ensure_ascii=False))

```