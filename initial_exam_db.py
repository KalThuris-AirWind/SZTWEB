import sqlite3

def create_exam_tables():
    conn = sqlite3.connect('sztweb.db')  # 连接你的数据库
    cursor = conn.cursor()

    # 1. 创建试卷表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_paper (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. 创建试卷与题目的关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_paper_question (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_paper_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            order_in_paper INTEGER NOT NULL,
            FOREIGN KEY (exam_paper_id) REFERENCES exam_paper(id),
            FOREIGN KEY (question_id) REFERENCES question(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ 数据表 exam_paper 和 exam_paper_question 创建成功！")

if __name__ == '__main__':
    create_exam_tables()