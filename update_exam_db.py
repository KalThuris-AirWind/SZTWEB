import sqlite3

def update_exam_paper_table():
    conn = sqlite3.connect('sztweb.db')  # 修改为你的数据库路径
    cursor = conn.cursor()

    # 为 exam_paper 表添加新字段
    cursor.execute('''
        ALTER TABLE exam_paper
        ADD COLUMN category TEXT;
    ''')
    cursor.execute('''
        ALTER TABLE exam_paper
        ADD COLUMN academic_year TEXT;
    ''')
    cursor.execute('''
        ALTER TABLE exam_paper
        ADD COLUMN semester TEXT;
    ''')

    conn.commit()
    conn.close()
    print("✅ exam_paper 表已成功更新！")

# 执行数据库更新
update_exam_paper_table()