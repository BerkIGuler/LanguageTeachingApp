import PySimpleGUI as sg
import sqlite3

con = sqlite3.connect('app_data2.db')
cur = con.cursor()

sg.theme('DarkAmber')

#global variables
login_user_ID = -1
login_user_name = -1
login_user_type = -1
selected_courses = []
teacher_quizzes = []
manager_discount_info = []
manager_evaluator_info = []
manager_evaluator_session_info = []
manager_sessions = []
ratings = []


# latest added data
quiz_number = 11
session_ID = 55
SSN_student = 200

# window functions
def window_login():
    layout = [[sg.Text('Welcome to the TongueMaster. Please enter your information to login.', font='Calibri 16')],
              [sg.Text('ID:', size=(8, 1)), sg.Input(size=(10, 1), key='id')],
              [sg.Text('Surname:', size=(8, 1)), sg.Input(size=(10, 1), key='user_surname')],
              [sg.Button('Login')],
              [sg.Text('Developed by Data Masters',size=(100,1), font='Calibri 8', justification='right')]]

    return sg.Window('Login Window', layout)

def window_student():
    layout = [[sg.Text('Welcome ' + login_user_name + '(' + login_user_type + ')',
               font='Calibri 20', text_color='red', background_color='yellow')],
              [sg.Button('Courses',font='Calibri 16', auto_size_button=True)],
              [sg.Button('Quizzes',font='Calibri 16', auto_size_button=True)],
              [sg.Button('Discount',font='Calibri 16', auto_size_button=True)],
              [sg.Button('Logout',font='Calibri 16', auto_size_button=True)]]

    return sg.Window('Student Window', layout)

def window_teacher():
    cur.execute('''SELECT Salary FROM Teacher WHERE SSNtea = ?''',(login_user_ID,))
    salary = int(cur.fetchone()[0])
    layout = [[sg.Text('Welcome ' + login_user_name + '(' + login_user_type + ')',
               font='Calibri 20', text_color='red', background_color='yellow')],
              [sg.Text('Salary:' + str(salary), size=(30,1), font='Calibri 18', text_color='Yellow', justification='right')],
              [sg.Button('Courses',font='Calibri 16', auto_size_button=True)],
              [sg.Button('Quizzes',font='Calibri 16', auto_size_button=True)],
              [sg.Button('Logout',font='Calibri 16', auto_size_button=True)]]

    return sg.Window('Teacher Window', layout)

def window_manager():

    layout = [[sg.Text('Welcome ' + login_user_name + '(' + login_user_type + ')',
                       font='Calibri 20', text_color='red', background_color='yellow')],
              [sg.Button('Courses', font='Calibri 16', auto_size_button=True)],
              [sg.Button('Assign Evaluator', font='Calibri 16', auto_size_button=True)],
              [sg.Button('Evaluate Sessions', font='Calibri 16', auto_size_button=True)],
              [sg.Button('Discounts', font='Calibri 16', auto_size_button=True)],
              [sg.Button('Logout', font='Calibri 16', auto_size_button=True)]]

    return sg.Window('Manager Window', layout)

def window_teacher_add_new_courses():

    layout = [[sg.Text('Course Name:', size=15), sg.Input(size=(15, 1), key='course_name')],
              [sg.Text('Course Level:', size=15), sg.Input(size=(15, 1), key='course_level')],
              [sg.Text('Materials:', size=15), sg.Input(size=(15, 1), key='materials')],
              [sg.Text('Subject:', size=15), sg.Input(size=(15, 1), key='subject')],
              [sg.Text('Course Price:', size=15), sg.Input(size=(15, 1), key='course_price')],
              [sg.Button('Add Course'), sg.Button('Cancel')]]

    return sg.Window('Teacher Add new Courses Window', layout)

def window_my_courses(Teacher = None, Subject = None):
    global selected_courses
    selected_courses = []
    courses = []
    combo_teachers = []
    combo_subjects = []

    cur.execute('''SELECT Discount_rate
                                   FROM Student
                                   WHERE Student.SSNstu = ?''',(login_user_ID,))
    discount_rate = cur.fetchone()[0]

    try:
        discount_rate = int(discount_rate)
    except:
        discount_rate = 0

    for row in cur.execute('''SELECT Course.course_name, Course.Subject,
                              Course.Course_Price, Teacher.Name, Teacher.Surname, Session.sessionID
                                    FROM Session, Teacher, Course, Student
                                    WHERE Course.course_name = Session.course_name
                                    AND Session.SSNteacher = Teacher.SSNtea'''):
        row_list = list(row)
        row_list[2] = round(row_list[2] * (1 - (discount_rate/100)), 2)
        if row_list not in courses:
            courses.append(row_list)



    cur.execute('SELECT credit FROM Student WHERE SSNstu = ?', (login_user_ID, ))
    balance = cur.fetchone()[0]

    for row in courses:
        if row[1] not in combo_subjects:
            combo_subjects.append(row[1])
        if row[3] + ' ' + row[4] not in combo_teachers:
            combo_teachers.append(row[3] + ' ' + row[4])

    if Teacher == None and Subject == None:
        selected_courses = courses[:]

    elif Teacher == None and Subject != None:
        for row in courses:
            if row[1] == Subject:
                selected_courses.append(row)

    elif Teacher != None and Subject == None:
        for row in courses:
            teacher_name_surname = row[3] + ' ' + row[4]
            if teacher_name_surname == Teacher:
                selected_courses.append(row)
    else:
        for row in courses:
            teacher_name_surname = row[3] + ' ' + row[4]
            if teacher_name_surname == Teacher and row[1] == Subject:
                selected_courses.append(row)


    if len(selected_courses) == 0:
        sg.popup("no course with searched subject found")
        return

    headings = ['Course', 'Subject', 'Price', 'Teacher Name', 'Teacher Surname', 'Session ID']

    layout = [[sg.Table(values=selected_courses, headings=headings,
              auto_size_columns=True,
              justification='middle',
              num_rows=10, key='course_table')],
              [sg.Text('Remaining Credits:', font='Raleway 14', text_color='red', background_color='yellow'),
               sg.Text(str(balance), font='Raleway 14', text_color='red', background_color='yellow'),
               sg.Text('Your Discount Rate: %' + str(discount_rate), justification='right', size= (30,1), font='Raleway 14', text_color='yellow')],
              [sg.Button('Search by Subject'), sg.Input(size=(10, 1), key='searched_subject'),
               sg.Button('Register to Selected Course')],
              [sg.Text('Subject', size=(22, 1)), sg.Text('Teacher')],
              [sg.Combo(combo_subjects, size=(20, 7), default_value='None', key='Subject'),
               sg.Combo(combo_teachers, size=(20, 7), default_value='None', key='Teacher')],
              [sg.Button('Filter'), sg.Button('Main Menu')]]

    return sg.Window('Course Window', layout)

def window_charge(data):
    layout = [[sg.Text("Are you sure?\n" + str(data[2]) + '$ will be charged from your account')],
              [sg.Button('Yes'), sg.Button('No')]]

    return sg.Window('charging window', layout)



def window_teacher_bonus(bonus_amount):

    layout = [[sg.Text('Congragulations!', font='Calibri 20')],
              [sg.Text('You have been provided a bonus of ' + bonus_amount + ' ', font='Calibri 14', justification='middle')],
              [sg.Text('Your salary is updated!', font='Calibri 14', justification='middle')],
              [sg.Button('Ok')]]

    cur.execute('''SELECT Salary FROM TEACHER WHERE SSNtea = ?''', (login_user_ID,))
    salary = cur.fetchone()[0]
    new_salary = salary + 100

    cur.execute('''UPDATE Teacher SET Salary = ? WHERE SSNtea = ?''', (new_salary, login_user_ID))

    return sg.Window('Salary Update Window', layout)



def window_teacher_my_courses():
    courses = []
    course_info = cur.execute("""SELECT Session.course_name, Course.Course_level, Course.Materials, Course.Subject
                                 FROM Course, Session
                                 WHERE Course.course_name = Session.course_name
                                 AND Session.SSNteacher = ?""", (login_user_ID,))
    for row in course_info:
        if row not in courses:
            courses.append(row)


    headings = ['Course Name', 'Course Level', 'Materials', 'Subject']

    layout = [[sg.Table(values=courses, headings=headings,
              auto_size_columns=True,
              justification='middle',
              num_rows=10, key='teacher_course_table')],
              [sg.Button('Main Menu'), sg.Button('Add New Course')]]

    return sg.Window('Teacher Courses Windows', layout)


def window_quizzes():
    quizzes = []
    for row in cur.execute('''SELECT Session.course_name, Give.Quiz_Grade
                              FROM Session, Give, Student
                              WHERE Session.quiz_number = Give.quiz_number 
                              AND Session.SSNstudent = ?''', (login_user_ID,)):
        if row not in quizzes:
            quizzes.append(row)

    headings = ['Course', 'Grade']
    data_cols_width = [15, 15]

    layout = [
              [sg.Text('Previous Quiz Grades')],
              [sg.Table(values=quizzes, headings=headings,
                        col_widths=data_cols_width,
                        auto_size_columns=False,
                        justification='middle',
                        num_rows=10, key='grade_table')],
              [sg.Button('Main Menu'), sg.Button('Participate quizzes')]]


    return sg.Window('Quiz Window', layout)

def window_teacher_quizzes():
    global teacher_quizzes
    teacher_quizzes = []
    for row in cur.execute('''SELECT Give.Quiz_Number, Give.Quiz_Grade, Student.Name, Student.Surname, Student.SSNstu, Quiz.Subject
                              FROM Quiz, Give, Student
                              WHERE Quiz.quiz_number = Give.Quiz_Number 
                              AND Give.SSNStu = Student.SSNstu
                              AND Give.SSNTea = ?''', (login_user_ID,)):

        if row not in teacher_quizzes:
            teacher_quizzes.append(row)

    headings = ['Quiz no', 'Grade', 'Name', 'Surname', 'Student ID', 'Subject']

    layout = [
              [sg.Text('Quizzes')],
              [sg.Table(values=teacher_quizzes, headings=headings,
                        auto_size_columns=True,
                        justification='middle',
                        num_rows=10, key='teacher_grade_table')],
              [sg.Button('Main Menu'), sg.Button('Enter New Grade')]]


    return sg.Window('Quiz Window', layout)

def window_participate_quiz(q_num):

    cur.execute('''SELECT Session.course_name
                   FROM Session
                   WHERE Session.quiz_number = ?''', ( q_num,))
    quiz_course_name =cur.fetchone()[0]

    layout = [[sg.Text("You have a new quiz!!")],
              [sg.Text("Course Name: "), sg.Text(quiz_course_name)],
              [sg.Button("Start the Quiz"), sg.Button("Cancel")]]

    return sg.Window('quiz participate Window', layout)

def window_manager_courses():
    courses = {}
    courses_lst = []
    course_info = cur.execute('''SELECT Session.course_name, Session.SSNteacher, Teacher.Name, Teacher.Surname
                                 FROM Session, Teacher
                                 WHERE Session.SSNteacher = Teacher.SSNtea 
                                 ''')
    for row in course_info:

        if row[1] not in courses:
            courses[row[1]] = [row[0], row[1], row[2], row[3], 1]
        else:
            courses[row[1]][4] += 1

    for key in courses:
        courses_lst.append(courses[key])

    headings = ['Course Name', 'Teacher ID', 'Teacher Name', 'Teacher Surname', 'Number of Student']

    layout = [[sg.Table(values=courses_lst, headings=headings,
              auto_size_columns=True,
              justification='middle',
              num_rows=10, key='manager_course_table')],
              [sg.Button('Main Menu')]]

    return sg.Window('Manager Courses Windows', layout)

def window_manager_evaluate():
    global manager_evaluator_info
    manager_evaluator_info = []

    for row in cur.execute('''SELECT Manager.SSNman, Manager.Name, Manager.Surname, Manager.Rank, Manager.Job,
                                             evaluate.sessionID
                              FROM Manager, evaluate
                              WHERE Manager.SSNman = evaluate.SSNman2'''):
        if row[0] != login_user_ID:
            manager_evaluator_info.append(row)

    headings = ['Manager ID', 'Manager Name', 'Manager Surname', 'Rank', 'Job', 'Assigned Session']

    layout = [
              [sg.Text('Manager Information')],
              [sg.Table(values=manager_evaluator_info, headings=headings,
                        auto_size_columns=True,
                        justification='middle',
                        num_rows=10, key='manager_evaluate_table')],
              [sg.Button('Main Menu'), sg.Button('Assign as Evaluator')]]



    return sg.Window('Evaluator Window', layout)


def window_manager_discount():
    global manager_discount_info
    manager_discount_info = []

    for row in cur.execute('''SELECT Student.SSNstu, Student.Name, Student.Surname, Student.Attendance, Student.Discount_rate, Student.Phone
                              FROM Student'''):
        manager_discount_info.append(row)

    headings = ['Student ID', 'Student Name', 'Student Surname', 'Attendance', 'Discount', 'Phone']

    layout = [
              [sg.Text('Student Information')],
              [sg.Table(values=manager_discount_info, headings=headings,
                        auto_size_columns=True,
                        justification='middle',
                        num_rows=10, key='manager_discount_table')],
              [sg.Button('Main Menu'), sg.Button('Change Discount Rate')]]


    return sg.Window('Quiz Window', layout)

def window_discount():
    cur.execute('''SELECT Student.Attendance
                FROM Student, provides_discount
                WHERE Student.SSNstu = provides_discount.SSNstu
                AND   Student.SSNstu = ?''', (login_user_ID,))
    attendance_rate = cur.fetchone()[0]

    if attendance_rate is None or attendance_rate == 'null':
        discount = 0
    else:
        attendance_rate = int(attendance_rate)
        if attendance_rate >= 95:
            discount = 50
        elif attendance_rate >= 90:
            discount = 40
        elif attendance_rate >= 85:
            discount = 30
        elif attendance_rate >= 80:
            discount = 20
        elif attendance_rate >= 75:
            discount = 10
        else:
            discount = 0

    headings = ['Attendance Rate', 'Discount']
    data = [(attendance_rate, discount)]

    layout = [[sg.Table(values=data, headings=headings,
              auto_size_columns=True,
              justification='middle',
              num_rows=1, key='discount_table')],
              [sg.Button('Main Menu')]]

    return sg.Window('Quiz Window', layout)

def window_grade():
    layout = [[sg.Text("new grade for chosen quiz:"), sg.Input(size=(5, 1), key='quiz_grade')],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    return sg.Window('grading window', layout)


def window_enter_manager_discount():
    layout = [[sg.Text("new discount rate for chosen student:"), sg.Input(size=(5, 1), key='discount_rate')],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    return sg.Window('Manager Discount Window', layout)



def window_enter_manager_rating(ses_info):
    layout = [[sg.Text("New rating for " + ses_info[0] + ' ' + ses_info[1] + ' '), sg.Input(size=(5, 1), key='rating')],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    return sg.Window('Manager Rating Window', layout)


def window_manager_assing_evaluator_to_sessions(selected_manager_data):
    global manager_evaluator_session_info
    manager_evaluator_session_info = []

    for row in cur.execute('''SELECT Course.course_name, Course.Subject,
                              Course.Course_Price, Teacher.Name, Teacher.Surname, Session.sessionID
                                    FROM Session, Teacher, Course
                                    WHERE Course.course_name = Session.course_name
                                    AND Session.SSNteacher = Teacher.SSNtea'''):
        manager_evaluator_session_info.append(row)

    headings = ['Course', 'Subject', 'Price', 'Teacher Name', 'Teacher Surname', 'Session ID']

    layout = [[sg.Text('Select a session to assign ' + selected_manager_data[0] + ' ' + selected_manager_data[1]
                                                     + ' as evaluator', font=('Calibri', '16'))],
              [sg.Table(values=manager_evaluator_session_info, headings=headings,
              auto_size_columns=True,
              justification='middle',
              num_rows=10, key='assign_evaluator_table')],
              [sg.Button('Assign to Selected Session'), sg.Button('Cancel')]]

    return sg.Window('Manager Assign Evaluator Window', layout)



def window_manager_assigned_sessions():
    global manager_sessions
    manager_sessions = []

    for row in cur.execute('''SELECT Teacher.Name, Teacher.Surname, Session.sessionID, Session.teacher_rating
                                    FROM Session, evaluate, Teacher
                                    WHERE Session.sessionID = evaluate.sessionID
                                    AND Session.SSNteacher = Teacher.SSNtea
                                    AND evaluate.SSNman2 = ?''', (login_user_ID,)):
        manager_sessions.append(row)

    headings = ['Teacher Name', 'Teacher Surname', 'Session ID', 'Rating']

    layout = [[sg.Text('Select a session to update its rating')],
              [sg.Table(values=manager_sessions, headings=headings,
              auto_size_columns=True,
              justification='middle',
              num_rows=10, key='update_rating_table')],
              [sg.Button('Change Rating'), sg.Button('Main Menu')]]

    return sg.Window('Manager Rating Window', layout)

# Button functions
def button_filter(values):
    global window
    teacher = values['Teacher']
    subject = values['Subject']

    if teacher == 'None' and subject == 'None':
        sg.popup("Select teacher or Subject to filter")
    elif teacher != 'None' and subject == 'None':
        window.close()
        window = window_my_courses(teacher)
    elif teacher == 'None' and subject != 'None':
        window.close()
        window = window_my_courses(None, subject)
    else:
        window.close()
        window = window_my_courses(teacher, subject)


def button_enter_new_grade(values):
    global window
    try:
        choice = teacher_quizzes[values['teacher_grade_table'][0]]
    except:
        sg.popup('Select Quiz to enter Grade')
        return

    new_window = window_grade()
    event, vals = new_window.read()
    new_window.close()

    try:
        new_grade = int(vals['quiz_grade'])
    except:
        window.close()
        window = window_teacher_quizzes()

    if event == 'Ok':
        while not (0 <= new_grade <= 100 and type(new_grade) == int):
            sg.popup('This is not a valid grade! Enter an integer between 0 and 100')
            new_window = window_grade()
            event, vals = new_window.read()
            new_window.close()

            try:
                new_grade = int(vals['quiz_grade'])
            except:
                window.close()
                window = window_teacher_quizzes()

            if event == 'Cancel':
                break

        cur.execute('''UPDATE Give
                       SET Quiz_Grade = ?
                       WHERE Give.Quiz_Number = ?
                       AND Give.SSNTea = ?''', (new_grade, choice[0], login_user_ID))
        window.close()
        window = window_teacher_quizzes()

    elif event == 'Cancel':
        window = window_teacher_quizzes()

def button_manager_assign_as_evaluator(values):
    global window
    global manager_evaluator_info
    global manager_evaluator_session_info

    try:
        selected_manager_info = manager_evaluator_info[values['manager_evaluate_table'][0]]
    except:
        sg.popup('Select Manager to Assign as Evaluator')
        return

    new_window = window_manager_assing_evaluator_to_sessions(selected_manager_info[1:3])
    event, vals = new_window.read()
    new_window.close()

    if event == 'Assign to Selected Session':
        try:
            assigned_ses_ID = manager_evaluator_session_info[vals['assign_evaluator_table'][0]][5]
        except:
            sg.popup('Select a Session.')
            return
        sg.popup(selected_manager_info[1] + ' ' + selected_manager_info[2] + ' is successfully assigned'
                                                                       ' to session with ID ' + str(assigned_ses_ID))
        cur.execute('''UPDATE evaluate
                       SET sessionID = ?
                       WHERE SSNman2 = ?''', (assigned_ses_ID, selected_manager_info[0]))

        cur.execute('''UPDATE assign 
                       SET SSNman2 = ?
                       WHERE SSNman1 = ?;''', (selected_manager_info[0], login_user_ID))


        window.close()
        window = window_manager_evaluate()
    else:
        return

def button_manager_change_rating(session_info):
    global window

    new_window = window_enter_manager_rating(session_info)
    event, vals = new_window.read()
    new_window.close()


    if event == 'Ok':
        new_rating = vals['rating']
        cur.execute('''UPDATE Session
                       SET teacher_rating = ?
                       WHERE Session.sessionID = ?''', (new_rating, session_info[2]))
        window.close()
        window = window_manager_assigned_sessions()
    else:
        return


def button_manager_change_discount_rate(values):

    global window
    try:
        student_info = manager_discount_info[values['manager_discount_table'][0]]
    except:
        sg.popup('Select Student to enter Discount Rate')
        return

    new_window = window_enter_manager_discount()
    event, vals = new_window.read()
    new_window.close()

    try:
        new_discount = int(vals['discount_rate'])
    except:
        window.close()
        window = window_manager_discount()

    if event == 'Ok':
        while not (0 <= new_discount <= 100 and type(new_discount) == int):
            sg.popup('This is not a valid rate! Enter an integer between 0 and 100')
            new_window = window_enter_manager_discount()
            event, vals = new_window.read()
            new_window.close()

            try:
                new_discount = int(vals['discount_rate'])
            except:
                window.close()
                window = window_manager_discount()

            if event == 'Cancel':
                return

        cur.execute('''UPDATE Student
                       SET Discount_rate = ?
                       WHERE Student.SSNstu = ?''', (new_discount, student_info[0]))
        window.close()
        window = window_manager_discount()

    elif event == 'Cancel':
        window = window_manager_discount()


def button_teacher_add_new_courses():
    global window
    global session_ID
    global SSN_student
    global quiz_number

    new_window = window_teacher_add_new_courses()
    event, vals = new_window.read()
    new_window.close()

    if event == 'Add Course':

        course_name = vals['course_name']
        course_level = vals['course_level']
        materials = vals['materials']
        subject = vals['subject']
        course_price = vals['course_price']

        cur.execute('''INSERT INTO Course (course_name, Course_level, Materials, Subject, Course_Price)
                       VALUES(?, ?, ?, ?, ?);''', (course_name, course_level, materials, subject, course_price))
        session_ID += 1
        SSN_student += 1
        quiz_number += 1
        cur.execute('''INSERT INTO Session (sessionID, quiz_number, course_name, SSNteacher, SSNstudent, teacher_rating)
                       VALUES(?, ?, ?, ?, ?, null);''', (session_ID, quiz_number, course_name, login_user_ID, SSN_student))

        window.close()
        window = window_teacher_my_courses()

    else:
        return


def button_register_course(values):
    global window
    global selected_courses
    global quiz_number
    global session_ID


    try:
        new_course_data = selected_courses[values['course_table'][0]]
    except:
        sg.popup('Select a Course to Register')
        return

    cur.execute('''SELECT Register.SSN, Register.course_name
                  FROM Register
                  WHERE Register.SSN = ?''', (login_user_ID,))
    register_data = cur.fetchone()

    if register_data != None:
        sg.popup("You are already enrolled in " + register_data[1])
    else:
        new_window = window_charge(new_course_data)
        event ,vals = new_window.read()

        if event == 'Yes':
            new_window.close()
            cur.execute('''INSERT INTO Register (course_name, SSN)
                          VALUES(?, ?);''', (new_course_data[0], login_user_ID))

            cur.execute('''SELECT Session.SSNteacher
                           FROM Session
                           WHERE ? = Session.sessionID''', (new_course_data[5],))

            Teacher_SSN = cur.fetchone()[0]
            quiz_number += 1
            session_ID += 1
            ses_data = [session_ID, quiz_number, new_course_data[0], Teacher_SSN, login_user_ID]

            cur.execute('''INSERT INTO Session (sessionID, quiz_number, course_name, SSNteacher, SSNstudent)
                          VALUES(?, ?, ?, ?, ?);''', ses_data)

            cur.execute('SELECT credit FROM Student WHERE SSNstu = ?', (login_user_ID,))

            current_balance = cur.fetchone()[0]
            new_balance = int(current_balance) - new_course_data[2]
            cur.execute('''UPDATE Student
                           SET Credit = ?
                           WHERE SSNstu = ?''', (new_balance,login_user_ID))
            sg.popup("Registration successful!")
            window.close()
            window = window_my_courses()
        elif event == 'No':
            new_window.close()

def button_participate_quizzes():
    quizzes_done =[]
    all_quizzes = []
    quiz_info = {}
    quiz_found = False

    for row in cur.execute('''SELECT Session.quiz_number, Session.SSNteacher, Session.SSNstudent, Session.course_name
                   FROM Session
                   WHERE Session.SSNstudent = ?''', (login_user_ID, )):
        all_quizzes.append(row[0])
        quiz_info[row[0]] = [row[1], row[2], row[3]]


    for row in cur.execute('''SELECT Give.Quiz_Number
                   FROM Give
                   WHERE Give.SSNStu = ?''', (login_user_ID, )):
        quizzes_done.append(row[0])

    for quiz in all_quizzes:
         if quiz not in quizzes_done:
             found_quiz_num = quiz
             quiz_found = True

    if not quiz_found:
        sg.popup("You do not have any quizzes assigned...")
    else:
        new_window = window_participate_quiz(found_quiz_num)
        event, vals = new_window.read()
        if event == "Start the Quiz":
            sg.popup("Quiz done. Your teacher will grade it soon")

            cur.execute('''INSERT INTO Give(Quiz_Number, Quiz_Grade, SSNTea, SSNStu)
                           VALUES(?, null, ?, ?)
                           ''',(found_quiz_num, quiz_info[found_quiz_num][0], quiz_info[found_quiz_num][1]))
            cur.execute('''INSERT INTO Quiz(quiz_number, Subject, difficulty_level)
                           VALUES(?, ?, null)
                           ''', (found_quiz_num, quiz_info[found_quiz_num][2]))
            new_window.close()
        elif event == 'Cancel':
            new_window.close()

def button_search_by_subject(values):
    global window
    subject = values['searched_subject']

    if window_my_courses(None, subject) == None:
        window.close()
        window = window_my_courses()
    else:
        window.close()
        window = window_my_courses(None, subject)


def button_login(values):
    global login_user_ID
    global login_user_name
    global login_user_type
    global window

    user_id = values['id']
    user_surname = values['user_surname']
    if user_id == '':
        sg.popup('ID cannot be empty')
    elif user_surname == '':
        sg.popup('Surname cannot be empty')
    else:
        cur.execute('SELECT SSNstu, Surname FROM Student WHERE SSNstu = ? AND Surname = ?', (user_id, user_surname))
        ssn_s = cur.fetchone()

        if ssn_s is None:
            cur.execute('SELECT SSNtea, Surname FROM Teacher WHERE SSNtea = ? AND Surname = ?', (user_id, user_surname))
            ssn_t = cur.fetchone()
            if ssn_t is None:
                cur.execute('SELECT SSNman, Surname FROM Manager WHERE SSNman = ? AND Surname = ?',
                            (user_id, user_surname))
                ssn_m = cur.fetchone()
                if ssn_m is None:
                    sg.popup('ID or Surname is wrong!')
                else:
                    login_user_type = 'Manager'
                    login_user_ID = ssn_m[0]
                    login_user_name = ssn_m[1]
                    window.close()
                    window = window_manager()
            else:
                login_user_type = 'Teacher'
                login_user_ID = ssn_t[0]
                login_user_name = ssn_t[1]
                window.close()

                ratings = []

                for val in cur.execute('''SELECT teacher_rating
                               FROM Teacher, Session
                               WHERE Teacher.SSNtea = Session.SSNteacher
                               AND Teacher.SSNtea = ?''', (login_user_ID,)):
                    ratings.append(val[0])

                if len(ratings) > 0:
                    new_window = window_teacher_bonus('100')
                    new_window.read()
                    new_window.close()

                window = window_teacher()

        else:
            login_user_ID = ssn_s[0]
            login_user_name = ssn_s[1]
            login_user_type = 'Student'
            window.close()
            window = window_student()
                
def button_logout():
    global ratings
    global login_user_ID
    global login_user_name
    global login_user_type
    global window

    login_user_ID = -1
    login_user_name = -1
    login_user_type = -1
    ratings = []

    window.close()
    window = window_login()

# main program
if __name__ == '__main__':

    window = window_login()

    while True:
        event, values = window.read()
        if event == 'Login':
            button_login(values)
        elif event == 'Logout':
            button_logout()
        elif event == 'Filter':
            button_filter(values)
        elif event == 'Discount':
            window.close()
            window = window_discount()

        elif event == 'Add New Course':
            button_teacher_add_new_courses()
        elif event == 'Search by Subject':
            button_search_by_subject(values)
        elif event == 'Enter New Grade':
            button_enter_new_grade(values)

        elif event == 'Courses':
            window.close()
            if login_user_type == 'Teacher':
                window = window_teacher_my_courses()
            elif login_user_type == 'Student':
                window = window_my_courses()
            else:
                window = window_manager_courses()
        elif event == 'Assign Evaluator':
            window.close()
            window = window_manager_evaluate()

        elif event == 'Evaluate Sessions':
            window.close()
            window = window_manager_assigned_sessions()
        elif event == 'Discounts':
            window.close()
            window = window_manager_discount()
        elif event == 'Change Discount Rate':
            button_manager_change_discount_rate(values)

        elif event == 'Assign as Evaluator':
            button_manager_assign_as_evaluator(values)

        elif event == 'Change Rating':
            if values['update_rating_table'] != []:
                button_manager_change_rating(manager_sessions[values['update_rating_table'][0]])
            else:
                sg.popup('Select a session to update its rating!!!')



        elif event == 'Quizzes':
            window.close()
            if login_user_type == 'Student':
                window = window_quizzes()
            elif login_user_type == 'Teacher':
                window = window_teacher_quizzes()
        elif event == 'Main Menu':
            window.close()
            if login_user_type == 'Student':
                window = window_student()
            elif login_user_type == 'Teacher':
                window = window_teacher()
            else:
                window = window_manager()
        elif event == 'Register to Selected Course':
            button_register_course(values)
        elif event == 'Participate quizzes':
            button_participate_quizzes()
        elif event == sg.WIN_CLOSED:
            con.commit()
            con.close()
            break