from flask import Flask, render_template, request, redirect
from datetime import datetime
import sqlite3

app = Flask(__name__)

# 连接数据库
def get_db_connection():
    conn = sqlite3.connect('sztweb.db')
    conn.row_factory = sqlite3.Row
    return conn

# 首页
@app.route("/")
def index():
    page = int(request.args.get('page', 1))  # 默认第1页
    per_page = 5
    offset = (page - 1) * per_page

    conn = get_db_connection()
    questions = conn.execute('SELECT * FROM questions LIMIT ? OFFSET ?', (per_page, offset)).fetchall()
    
    total = conn.execute('SELECT COUNT(*) FROM questions').fetchone()[0]
    total_pages = (total + per_page - 1) // per_page  # 向上取整
    conn.close()
    return render_template("index.html", questions=questions, page=page, total_pages=total_pages)

# 添加题目
@app.route('/questions/add', methods=['GET', 'POST'])
def question_add():
    if request.method == 'POST':
        # 题目表单数据
        question_type = request.form['question_type']
        material = request.form['material']
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        analysis = request.form['analysis']

        # 保存到数据库
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO questions (question_type, question_text, option_a, option_b, option_c, option_d, correct_answer, analysis, material)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (question_type, question_text, option_a, option_b, option_c, option_d, correct_answer, analysis, material))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_question.html')

# 编辑题目
@app.route('/questions/<int:id>/edit', methods=['GET', 'POST'])
def question_edit(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取当前题目
    cursor.execute('SELECT * FROM questions WHERE id = ?', (id,))
    question = cursor.fetchone()

    # 获取所有试卷（用于下拉选择）
    cursor.execute('SELECT id, title FROM exam_paper ORDER BY created_at DESC')
    exam_papers = cursor.fetchall()

    # 获取当前题目所在的试卷（可选）
    cursor.execute('SELECT exam_paper_id FROM exam_paper_question WHERE question_id = ?', (id,))
    current_exam = cursor.fetchone()
    current_exam_id = current_exam[0] if current_exam else None

    if request.method == 'POST':
        # 获取表单字段
        question_type = request.form['question_type']
        material = request.form['material']
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        analysis = request.form['analysis']
        exam_paper_id = request.form.get('exam_paper_id')

        # 更新题目本身
        cursor.execute('''
            UPDATE questions SET 
                question_type = ?, material = ?, question_text = ?,
                option_a = ?, option_b = ?, option_c = ?, option_d = ?,
                correct_answer = ?, analysis = ?
            WHERE id = ?
        ''', (question_type, material, question_text,
              option_a, option_b, option_c, option_d,
              correct_answer, analysis, id))

        # 更新关联（先删除旧的，再插入新的）
        cursor.execute('DELETE FROM exam_paper_question WHERE question_id = ?', (id,))
        if exam_paper_id:
            cursor.execute('''
                INSERT INTO exam_paper_question (exam_paper_id, question_id, order_in_paper)
                VALUES (?, ?, ?)
            ''', (exam_paper_id, id, 1))  # 暂时默认是第1题

        conn.commit()
        conn.close()
        return redirect('/questions')  # 回到题目列表页

    conn.close()
    return render_template('question_edit.html',
                           question=question,
                           exam_papers=exam_papers,
                           current_exam_id=current_exam_id)

# 删除题目
@app.route('/questions/<int:id>/delete', methods=['GET'])
def question_delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM questions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')


#题目详情
@app.route('/questions/<int:id>')
def question_detail(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 获取题目信息
    cursor.execute('SELECT * FROM questions WHERE id = ?', (id,))
    question = cursor.fetchone()

    if question is None:
        return "题目未找到", 404  # 如果题目不存在，返回错误

    # 获取关联的试卷
    cursor.execute('''
        SELECT ep.title FROM exam_paper ep
        JOIN exam_paper_question epq ON ep.id = epq.exam_paper_id
        WHERE epq.question_id = ?
    ''', (id,))
    exam_papers = cursor.fetchall()

    conn.close()
    return render_template('question_detail.html', question=question, exam_papers=exam_papers)

# 添加试卷
@app.route('/exams/add', methods=['GET', 'POST'])
def exam_add():
    # 生成学年列表（2024-2025, 2023-2024, ...）
    current_year = datetime.now().year
    academic_years = [f"{current_year}-{current_year+1}", f"{current_year-1}-{current_year}"]
    for i in range(2, 5):  # 继续推前几年
        academic_years.append(f"{current_year-i}-{current_year-i+1}")

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        academic_year = request.form['academic_year']
        semester = request.form['semester']

        # 保存到数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO exam_paper (title, category, academic_year, semester, created_at) VALUES (?, ?, ?, ?, ?)",
            (title, category, academic_year, semester, datetime.now())
        )
        conn.commit()
        conn.close()

        return redirect('/exams')

    return render_template('exam_add.html', academic_years=academic_years)


# 编辑试卷
@app.route('/exams/<int:id>/edit', methods=['GET', 'POST'])
def exam_edit(id):
    # 生成学年列表（2024-2025, 2023-2024, ...）
    current_year = datetime.now().year
    academic_years = [f"{current_year}-{current_year+1}", f"{current_year-1}-{current_year}"]
    for i in range(2, 5):  # 继续推前几年
        academic_years.append(f"{current_year-i}-{current_year-i+1}")
    
    # 获取当前试卷的数据
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM exam_paper WHERE id = ?', (id,))
    exam = cursor.fetchone()
    conn.close()

    if exam is None:
        return "试卷未找到", 404  # 如果找不到试卷，返回错误

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        academic_year = request.form['academic_year']
        semester = request.form['semester']

        # 更新试卷数据
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE exam_paper SET 
                title = ?, 
                category = ?, 
                academic_year = ?, 
                semester = ? 
            WHERE id = ?
        ''', (title, category, academic_year, semester, id))
        conn.commit()
        conn.close()

        return redirect('/exams')  # 编辑成功后返回试卷列表

    # 渲染模板时将试卷数据传递给模板
    return render_template('exam_edit.html', exam=exam, academic_years=academic_years)

# 删除试卷
@app.route('/exams/<int:id>/delete', methods=['GET'])
def exam_delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM exam_paper WHERE id = ?', (id,))
    cursor.execute('DELETE FROM exam_paper_question WHERE exam_paper_id = ?', (id,))  # 删除关联的题目
    conn.commit()
    conn.close()
    return redirect('/exams')

# 显示所有试卷
@app.route('/exams')
def list_exam_papers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM exam_paper ORDER BY created_at DESC")
    papers = cursor.fetchall()
    conn.close()
    return render_template('exam_papers.html', papers=papers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)