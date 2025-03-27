import sqlite3

def create_db():
    conn = sqlite3.connect('sztweb.db')
    c = conn.cursor()

    # 创建 questions 表（修改后的表结构）
    c.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_type TEXT NOT NULL,  -- '选择题', '填空题', '问答题'
        material TEXT NOT NULL,       -- 材料部分
        question_text TEXT NOT NULL,  -- 设问
        option_a TEXT,  -- 选项A
        option_b TEXT,  -- 选项B
        option_c TEXT,  -- 选项C
        option_d TEXT,  -- 选项D
        correct_answer TEXT,  -- 正确答案
        analysis TEXT  -- 解析
    )
    ''')

    conn.commit()
    conn.close()

create_db()  # 创建数据库和表