from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# 连接数据库
def get_db_connection():
    conn = sqlite3.connect('sztweb.db')
    conn.row_factory = sqlite3.Row
    return conn

# 首页
@app.route('/')
def index():
    conn = get_db_connection()  # ✅ This line is required!
    questions = conn.execute('SELECT * FROM questions').fetchall()
    conn.close()
    return render_template('index.html', questions=questions)

# 试题上传页面
@app.route('/add', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
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

# edit question
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_question(id):
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM questions WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        question_type = request.form['question_type']
        material = request.form['material']
        question_text = request.form['question_text']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        correct_answer = request.form['correct_answer']
        analysis = request.form['analysis']

        conn.execute('''
            UPDATE questions SET 
                question_type = ?, 
                material = ?, 
                question_text = ?, 
                option_a = ?, 
                option_b = ?, 
                option_c = ?, 
                option_d = ?, 
                correct_answer = ?, 
                analysis = ?
            WHERE id = ?
        ''', (question_type, material, question_text, option_a, option_b, option_c, option_d, correct_answer, analysis, id))
        conn.commit()
        conn.close()
        return redirect('/')
    
    conn.close()
    return render_template('edit_question.html', question=question)

##question detail route
@app.route('/question/<int:id>')
def view_question(id):
    conn = get_db_connection()
    question = conn.execute('SELECT * FROM questions WHERE id = ?', (id,)).fetchone()
    conn.close()
    if question is None:
        return "Question not found", 404
    return render_template('question_detail.html', question=question)

###delete route
@app.route('/delete/<int:id>', methods=['GET'])
def delete_question(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM questions WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)