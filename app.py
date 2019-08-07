from flask import Flask, render_template, request, jsonify, session, json
from db import connection
from flask_mail import Mail, Message
import random
import string
from flask_cors import CORS, cross_origin
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
import os
from datetime import datetime

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

app = Flask(__name__)

api = Api(app)

CORS(app)

app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME="",
    MAIL_PASSWORD="",
)
mail = Mail(app)

app.secret_key = "hi"


@app.route("/")
def ac():
 #   session["login"] = ""
    return render_template("login.html")


@app.route("/index")
def ind():
    return render_template("index.html")


@app.route("/user")
def us():
    return render_template("userhome.html")


@app.route("/document.html")
def docu():
    return render_template("document.html")
    

@app.route("/branch.html")
def brac():
    return render_template("branch.html")


@app.route("/employee.html")
def eploe():
    return render_template("employee.html")


@app.route("/task.html")
def tskk():
    return render_template("task.html")


@app.route("/login")
def log():
    cm, con = connection()
    username = request.args.get("user")
    password = request.args.get("password")
    r = (
            "select * from login where username='"
            + username
            + "' and password='"
            + password
            + "'"
    )
    cm.execute(r)
    ab = cm.fetchone()
    if ab is not None:
        if password == ab[2]:
            session["login"] = "in"
            session["uid"] = ab[0]
            print("haii")
            print(session["uid"])
            return jsonify(
                status="ok", id=ab[0], username=ab[1], password=ab[2], user_type=ab[3]
            )
        else:
            return jsonify(status="Incorrect Password")
    else:
        return jsonify(status="Incorrect UserName")


@app.route("/document_reg")
def doc():
    print("hello")
    a = 1
    document = request.args.get("doc")

    d = (
            "insert into document(document_name,creator_id,created_date,last_updated)VALUES ('"
            + document
            + "','"
            + str(a)
            #       + str(session["uid"])
            + "',NOW(),NOW())"
    )
    cm, con = connection()
    cm.execute(d)
    print(d)
    con.commit()
    return jsonify(status="ok")


@app.route("/view_document")
def viewdoc():
    vdoc = "select * from document"
    cm, con = connection()
    cm.execute(vdoc)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/delete_document")
def deldoc():
    did = request.args.get("docid")
    d = "delete from document where document_id='" + did + "'"
    cm, con = connection()
    cm.execute(d)
    con.commit()
    return jsonify(status="ok")


@app.route("/edit_document")
def editdoc():
    did = request.args.get("docid")
    edtdoc = "select * from document where document_id='" + did + "'"
    cm, con = connection()
    cm.execute(edtdoc)
    ab = cm.fetchone()
    return jsonify(status="ok", document_id=ab[0], document_name=ab[1])


@app.route("/update_document")
def updatedoc():
    did = request.args.get("docid")
    docname = request.args.get("docname")
    print(did, docname)
    a = 1
    upd = (
            "update document set document_name='"
            + docname
            + "', created_date=NOW(), creator_id='"
            + str(a)
            + "',last_updated=NOW() where document_id='"
            + did
            + "'"
    )
    cm, con = connection()
    cm.execute(upd)
    con.commit()
    return jsonify(status="ok")


@app.route("/taskregdoc")
def tskregdoc():
    tdc = "select * from document"
    cm, con = connection()
    cm.execute(tdc)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/taskregistration")
def tskreg():
    tname = request.args.get("task")
    tcost = request.args.get("cost")
    tday = request.args.get("days")
    cm, con = connection()
    tsk = (
            "insert into task_registration(task,processdays,cost)VALUES ('"
            + tname
            + "','"
            + tday
            + "','"
            + tcost
            + "')"
    )
    cm.execute(tsk)
    con.commit()
    tskid = cm.lastrowid
    did = request.args.get("docid")
    val = did.split(",")
    for i in val:
        res = (
                "insert into task_document(task_id,document_id)VALUES ('"
                + str(tskid)
                + "','"
                + (i)
                + "')"
        )
        cm.execute(res)
        con.commit()
    return jsonify(status="ok")


@app.route("/viewtask")
def tskview():
    cm, con = connection()
    abc = "select * from task_registration"
    cm.execute(abc)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/viewtaskdocuments")
def viewtskdoc():
    cm, con = connection()
    tskid = request.args.get("tid")
    res = (
            "select task_document.*,task_registration.*,document.* from task_document inner join task_registration on task_document.task_id=task_registration.task_id inner join document on task_document.document_id=document.document_id where task_document.task_id='"
            + tskid
            + "'"
    )
    cm.execute(res)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/deletetask")
def deltsk():
    cm, con = connection()
    dlt = request.args.get("tskid")
    ddlt = "delete from task_document where task_id='" + dlt + "'"
    cm.execute(ddlt)
    con.commit()
    ddlt1 = "delete from task_registration where task_id='" + dlt + "'"
    cm.execute(ddlt1)
    con.commit()
    return jsonify(status="ok")


@app.route("/edittaskdocument")
def edittskdoc():
    cm, con = connection()
    updoc = request.args.get("tskid")
    up = "select * from task_document where task_id='" + updoc + "'"
    cm.execute(up)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/edittask")
def edittsk():
    cm, con = connection()
    uppt = request.args.get("tid")
    utt = "select * from task_registration where task_id='" + uppt + "'"
    cm.execute(utt)
    ab = cm.fetchone()
    return jsonify(status="ok", id=ab[0], task=ab[1], processdays=ab[2], cost=ab[3])


@app.route("/taskdeletdoc")
def tskdeldoc():
    cm, con = connection()
    kkd = request.args.get("docid")
    ddlt2 = "delete from task_document where task_id='" + kkd + "'"
    cm.execute(ddlt2)
    con.commit()
    return jsonify(status="ok")


@app.route("/updatetask")
def updtsk():
    cm, con = connection()
    kk = request.args.get("docid")
    qq = request.args.get("task")
    rr = request.args.get("processday")
    yy = request.args.get("cost")
    ii = (
            "update task_reg set task='"
            + qq
            + "',processdays='"
            + rr
            + "',cost='"
            + yy
            + "' where task_id='"
            + kk
            + "'"
    )
    cm.execute(ii)
    con.commit()
    xx = request.args.get("docid")
    val = xx.split(",")
    for i in val:
        njk = (
                "insert into task_document(task_id,document_id)VALUES ('"
                + kk
                + "','"
                + (i)
                + "')"
        )
        cm.execute(njk)
        con.commit()
    return jsonify(status="ok")


@app.route("/branch")
def brnch():
    if session["login"] == "":
        return render_template("login.html")
    else:
        return render_template("branch.html")


@app.route("/branchregistration")
def addbranch():
    name = request.args.get("branch_name")
    district = request.args.get("branch_district")
    place = request.args.get("branch_place")
    city = request.args.get("branch_city")
    post = request.args.get("branch_post")
    pin = request.args.get("branch_pincode")
    landmark = request.args.get("branch_landmark")
    email = request.args.get("branch_email")
    building = request.args.get("branch_building")
    phone = request.args.get("branch_phone")

    breg = (
            "insert into branch VALUES (NULL, '"
            + name
            + "','"
            + district
            + "','"
            + place
            + "','"
            + city
            + "','"
            + post
            + "','"
            + landmark
            + "','"
            + building
            + "','"
            + pin
            + "','"
            + email
            + "','"
            + phone
            + "',NOW(),NOW())"
    )
    cm, con = connection()
    cm.execute(breg)
    con.commit()
    return jsonify(status="ok")


@app.route("/viewbranch")
def vbr():
    cm, con = connection()
    vb = "select * from branch"
    cm.execute(vb)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/deletebranch")
def dbr():
    print("ddd")

    bid = request.args.get("branchid")
    cm, con = connection()
    dd = "delete from branch where branch_id='" + bid + "'"
    cm.execute(dd)
    con.commit()
    return jsonify(status="ok")


@app.route("/editbranch")
def ebr():
    dbv = request.args.get("branchid")
    cd = "select * from branch where branch_id='" + dbv + "'"
    cm, con = connection()
    cm.execute(cd)
    ab = cm.fetchone()
    return jsonify(
        status="ok",
        id=ab[0],
        name=ab[1],
        district=ab[2],
        place=ab[3],
        city=ab[4],
        post=ab[5],
        pin=ab[8],
        building=ab[7],
        landmark=ab[6],
        email=ab[9],
        phone=ab[10],
    )


@app.route("/updatebranch")
def ub():
    branch_id = request.args.get("bid")
    name = request.args.get("name")
    district = request.args.get("district")
    place = request.args.get("place")
    city = request.args.get("city")
    post = request.args.get("post")
    building = request.args.get("building")
    pin = request.args.get("pin")
    landmark = request.args.get("landmark")
    email = request.args.get("email")
    phone = request.args.get("phone")

    upbranc = (
            "update branch set name='"
            + name
            + "',district='"
            + district
            + "',place='"
            + place
            + "',city='"
            + city
            + "',post='"
            + post
            + "',building='"
            + building
            + "',pincode='"
            + pin
            + "',landmark='"
            + landmark
            + "',email='"
            + email
            + "',phone='"
            + phone
            + "',last_updated= NOW() where branch_id='"
            + str(branch_id)
            + "'"
    )
    cm, con = connection()
    cm.execute(upbranc)
    con.commit()
    return jsonify(status="ok")


@app.route("/employee_registration", methods=["POST"])
def empreg():
    cm, con = connection()
    type = request.form["jpos"]
    branch_id = request.form["branch"]
    work_email = request.form["wmail"]
    work_mobile = request.form["wmob"]
    fname = request.form["firstnm"]
    lname = request.form["lastnm"]
    gender = request.form["gender"]
    dob = request.form["dob"]
    district = request.form["dist"]
    address = request.form["address"]
    place = request.form["place"]
    pin = request.form["pin"]
    status = request.form["mstatus"]
    mobile = request.form["mobile"]
    email = request.form["email"]
    username = request.form["uname"]
    password = request.form["pword"]

    # photo = ""

    if not "image" in request.files:
        if gender == "Male":
            photo = "male.png"
        elif gender == "Female":
            photo = "female.png"
    else:
        file = request.files["image"]
        timestr = datetime.now().strftime("%Y%m%d-%H%M%S")
        photo = timestr + file.filename
        if file and allowed_file(photo):
            file.save(os.path.join(app.root_path, "static/uploads/" + photo))
        else:
            return (
                """<script>alert("Only JPEG, JPG & PNG Files Allowed..!!");</script>"""
            )

    inlo = (
            "insert into login(username,password,user_type)VALUES ('"
            + username
            + "','"
            + password
            + "','"
            + type
            + "')"
    )
    cm.execute(inlo)
    con.commit()
    id = cm.lastrowid
    ademp = (
            "insert into employee VALUES ('"
            + str(id)
            + "','"
            + fname
            + "','"
            + lname
            + "','"
            + gender
            + "','"
            + dob
            + "','"
            + address
            + "','"
            + place
            + "','"
            + district
            + "','"
            + pin
            + "','"
            + status
            + "','"
            + email
            + "','"
            + work_email
            + "','"
            + mobile
            + "','"
            + work_mobile
            + "','"
            + photo
            + "','"
            + branch_id
            + "',NOW(),NOW())"
    )
    cm.execute(ademp)
    con.commit()
    return jsonify(status="ok")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/view_employee")
def view_employee():
    cm, con = connection()
    viem = "SELECT `employee`.*,`branch`.`name`,`login`.`user_type` FROM  `branch`  INNER JOIN  `employee` ON `employee`.`branch_id` = `branch`.`branch_id` INNER JOIN `login` ON `employee`.`employee_id` = `login`.`id`"
    cm.execute(viem)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/delete_employee")
def delete_employee():
    dem = request.args.get("employee_id")
    cm, con = connection()
    cm.execute("delete from employee where employee_id='" + dem + "'")
    cm.execute("delete from  login where id='" + dem + "'")
    con.commit()
    return jsonify(status="ok")


@app.route("/edit_employee")
def edit_employee():
    emp_id = request.args.get("empid")
    vmm = (
            "SELECT `employee`.*,`branch`.`name`,`login`.`user_type`,`login`.`username`,`login`.`password`  FROM  `branch`  INNER JOIN  `employee` ON `employee`.`branch_id` = `branch`.`branch_id` INNER JOIN `login` ON `employee`.`employee_id` = `login`.`id` AND `login`.`id` = '"
            + emp_id
            + "'"
    )
    cm, con = connection()
    cm.execute(vmm)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/update_employee", methods=["POST"])
def update_employee():
    cm, con = connection()

    emp_id = request.form["empid"]
    branch_id = request.form["branch_id"]
    type = request.form["jpos"]
    work_email = request.form["work_email"]
    work_mobile = request.form["work_mobile"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    gender = request.form["genderedit"]
    dob = request.form["dob"]
    district = request.form["district"]
    address = request.form["address"]
    place = request.form["place"]
    pin = request.form["pin"]
    status = request.form["statusedit"]
    mobile = request.form["mobile"]
    email = request.form["email"]
    password = request.form["password"]
    username = request.form["username"]

    print(type)
    print(emp_id)

    cm.execute(
        "UPDATE login SET `username`='"
        + username
        + "',`password` = '"
        + password
        + "',`user_type` = '"
        + type
        + "'  WHERE `id` = '"
        + emp_id
        + "'"
    )

    cm.execute(
        "UPDATE employee SET `first_name` = '"
        + fname
        + "',`last_name`= '"
        + lname
        + "',`gender`= '"
        + gender
        + "',`dob`= '"
        + dob
        + "',`postal_address`= '"
        + address
        + "',`place`= '"
        + place
        + "',`district`= '"
        + district
        + "',`pincode`= '"
        + pin
        + "',`maritalstatus`= '"
        + status
        + "',`email`= '"
        + email
        + "',`work_email`= '"
        + work_email
        + "',`mobile`= '"
        + mobile
        + "',`work_mobile`= '"
        + work_mobile
        + "',`branch_id`= '"
        + branch_id
        + "',`last_updated`= NOW()  WHERE `employee_id` =  '"
        + emp_id
        + "'"
    )

    con.commit()
    return jsonify(status="ok")


@app.route("/expense_reg")
def expense_reg():
    expense_category = request.args.get("expense_category")
    cm, con = connection()
    cm.execute(
        "insert into `expense_category` values(NULL,'"
        + expense_category
        + "',NOW(),NOW())"
    )
    con.commit()
    return jsonify(status="ok")


@app.route("/view_expense")
def view_expense():
    i = "select * from expense_category"
    cm, con = connection()
    cm.execute(i)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/delete_expense")
def delete_expense():
    p = request.args.get("dex")
    y = "delete from expense_category where(id='" + p + "')"
    cm, con = connection()
    n = cm.execute(y)
    con.commit()
    if (n) == 0:
        return jsonify(status="no")
    else:
        return jsonify(status="deleted")


@app.route("/edit_expense")
def edit_expense():
    expense_category_id = request.args.get("expid")
    udt = (
            "select * from expense_category where(id='"
            + expense_category_id
            + "')"
    )
    cm, con = connection()
    cm.execute(udt)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/update_expense")
def update_expense():
    upid = request.args.get("expid")
    upt = request.args.get("name")

    updc = (
            "update expense_category set name='"
            + upt
            + "',last_updated=NOW() where (id='"
            + upid
            + "')"
    )

    cm, con = connection()
    cm.execute(updc)
    con.commit()
    return jsonify(status="ok")


@app.route("/task_reg")
def task_reg():
    task_name = request.args.get("task")
    expected_cost = request.args.get("cost")
    pro_day = request.args.get("pday")

    print(task_name)
    print(pro_day)
    print(expected_cost)

    cm, con = connection()
    cm.execute(
        "insert into task VALUES (NULL,'"
        + task_name
        + "','"
        + expected_cost
        + "','"
        + pro_day
        + "',NOW(),NOW())"
    )
    con.commit()
    x = cm.lastrowid

    doct = request.args.get("docs_ids")
    print(doct)

    val = doct.split(",")

    for i in val:
        cm.execute(
            "insert into task_document VALUES (NULL,'"
            + str(x)
            + "','"
            + (i)
            + "',NOW(),NOW())"
        )
        con.commit()

    return jsonify(status="ok")


@app.route("/delete_task")
def delete_task():
    cm, con = connection()
    task_id = request.args.get("task_id")
    cm.execute("delete from task_document where task_id='" + task_id + "'")
    cm.execute("delete from task where task_id='" + task_id + "'")
    con.commit()
    return jsonify(status="ok")


@app.route("/view_task")
def view_task():
    cm, con = connection()
    abc = "select * from task"
    cm.execute(abc)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/view_task_doc")
def view_task_doc():
    cm, con = connection()
    task_id = request.args.get("task_id")
    cm.execute(
        "SELECT  `task_document`.`document_id`,`document_name`,`task_document`.`task_id`,`task` FROM `task` INNER JOIN `task_document` ON `task`.`task_id` = `task_document`.`task_id` INNER JOIN `document` ON `task_document`.`document_id` = `document`.`document_id`  AND `task_document`.`task_id` = '"
        + task_id
        + "'"
    )
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/edit_task")
def edit_task():
    cm, con = connection()
    task_id = request.args.get("task_id")
    utt = "select * from task where task_id='" + task_id + "'"
    cm.execute(utt)
    ab = cm.fetchone()
    return jsonify(
        status="ok",
        task_id=ab[0],
        task=ab[1],
        processdays=ab[2],
        expected_cost=ab[3],
        created_date=ab[4],
        last_updated=ab[5],
    )


@app.route('/update_task')
def update_task():
    cm, con = connection()
    task_id = request.args.get('task_id')
    task_name = request.args.get('task')
    expected_cost = request.args.get('cost')
    pro_day = request.args.get('pday')
    cm.execute(
        "UPDATE task SET `task`='" + task_name + "',`processdays`='" + pro_day + "',`cost`='" + expected_cost + "',`last_updated`=NOW()  WHERE `task_id` = '" + task_id + "'")

    doct = request.args.get('docs_ids')
    val = doct.split(',')

    for i in val:

        cm.execute(
            "SELECT * FROM `task_document` WHERE `task_id` = '" + task_id + "' AND `document_id` = '" + str(i) + "'")
        res = cm.fetchone()
        if res is None:
            cm.execute("insert into task_document VALUES (NULL,'" + task_id + "','" + str(i) + "',NOW(),NOW())")
            con.commit()
        else:
            cm.execute("")
    return jsonify(status="ok")


@app.route("/exp_reg")
def exp():
    expense = request.args.get("exp")
    d = (
            "insert into expense_category(name,created_date,last_updated)VALUES ('"
            + expense
            + "','"
            + "',NOW(),NOW())"
    )
    cm, con = connection()
    cm.execute(d)
    print(d)
    con.commit()
    return jsonify(status="ok")


@app.route("/view_exp")
def viewexp():
    vexp = "select * from expense_category"
    cm, con = connection()
    cm.execute(vexp)
    ab = cm.fetchall()
    if ab is not None:
        row_header = [x[0] for x in cm.description]
        json_data = []
        for result in ab:
            json_data.append(dict(zip(row_header, result)))
        return jsonify(json_data)
    else:
        return jsonify(status="no")


@app.route("/delete_exp")
def delexp():
    did = request.args.get("expid")
    d = "delete from expense_category where id='" + did + "'"
    cm, con = connection()
    cm.execute(d)
    con.commit()
    return jsonify(status="ok")


@app.route("/edit_exp")
def editexp():
    did = request.args.get("expid")
    edtexp = "select * from expense_category where id='" + did + "'"
    cm, con = connection()
    cm.execute(edtexp)
    ab = cm.fetchone()
    return jsonify(status="ok", document_id=ab[0], document_name=ab[1])


@app.route("/update_exp")
def updateexp():
    eid = request.args.get("expid")
    ename = request.args.get("expname")
    upd = (
            "update expense_category set name='"
            + ename
            + "', created_date=NOW(), '"
            + "',last_updated=NOW() where document_id='"
            + eid
            + "'"
    )
    cm, con = connection()
    cm.execute(upd)
    con.commit()
    return jsonify(status="ok")


@app.route("/org_reg", methods=["POST"])
def orgreg():
    cm, con = connection()
    oname = request.form["orgnm"]
    place = request.form["plc"]
    post = request.form["post"]
    pin = request.form["zcode"]
    email = request.form["email"]
    wbst = request.form["wsite"]
    contact = request.form["wmob"]
    registry = request.form["creg"]
    gstin = request.form["gstin"]
    #photo = ""
    file = request.files["image"]
    if file is None:
        photo = "male.png"
    else:
        file = request.files["image"]
        timestr = datetime.now().strftime("%Y%m%d-%H%M%S")
        photo = timestr + file.filename
        if file and allowed_file(photo):
            file.save(os.path.join(app.root_path, "static/uploads/" + photo))
        else:
            return (
                """<script>alert("Only JPEG, JPG & PNG Files Allowed..!!");</script>"""
            )

    print(oname)
    print(place)
    print(post)
    print(pin)
    print(email)
    print(wbst)
    print(contact)
    print(registry)
    print(gstin)
    ademp =(
            "insert  into `organisation`(`org_name`,`place`,`post`,`pin`,`email`,`website`,`contact`,`registry`,`gstin`,`image`) values('"
            + oname
            + "','"
            + place
            + "','"
            + post
            + "','"
            + pin
            + "','"
            + email
            + "','"
            + wbst
            + "','"
            + contact
            + "','"
            + registry
            + "','"
            + gstin
            + "','"
            + photo
            + "')")
    cm.execute(ademp)
    con.commit()
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(debug=True, port=4700, host="localhost")
