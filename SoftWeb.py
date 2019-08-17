from flask import Flask,render_template,request
import psycopg2
import json


conn = psycopg2.connect("dbname=company user=postgres")

app = Flask(__name__)

@app.route("/")
def homePage():
	curr = conn.cursor()
	curr.execute('SELECT * FROM route')
	rows = curr.fetchall()
	conn.commit()
	return  render_template("mainpage.html",routes=rows)
	
	

@app.route("/loadTravels")
def loadTravels():
	route_id = request.args.get("route_id")
	curr = conn.cursor()
	curr.execute('SELECT * FROM travels WHERE id = ' + route_id ) 
	rows = curr.fetchall()
	conn.commit()
	result = []
	for element in rows:
		dic = {}	
		dic['travel_date'] = element[1]
		dic['travel_id'] = element[0]
		result.append(dic)
	
	
	return json.dumps(result)
	#javascritten cekmek ayni sayfada tutmak icin
	

@app.route("/loadSeats")
def loadSeats():
	travel_id = request.args.get("travel_id")
	curr = conn.cursor()
	curr.execute('SELECT * FROM seats WHERE travel_id = ' + travel_id + "and state LIKE 'free%' ORDER BY seat_no" ) 
	rows = curr.fetchall()
	conn.commit()
	result = []
	for element in rows:
		dic = {}
		dic['seat_no'] = element[0]
		result.append(dic)
		
	return json.dumps(result)


@app.route("/makeReservation")
def makeReservation():
		travel_id = request.args.get("travel_id")
		route_id = request.args.get("route_id")
		seat_no = request.args.get("seat_no")
		curr = conn.cursor()
		curr.execute('SELECT departure,arrival FROM route WHERE id = ' + route_id ) 
		rows = curr.fetchall()
		conn.commit()

		curr.execute('SELECT travel_date FROM travels WHERE id = ' + route_id + 'and travel_id=' + travel_id)
		rows2 =curr.fetchall()
		conn.commit()
		print rows2
		return render_template("reservation.html",
		route=rows[0][0] +" to " + rows[0][1],
		travel=rows2[0][0],
		seat=seat_no,
		travel_id=travel_id
		)
	


@app.route("/insertReservation")
def submitReservation():
	route = request.args.get("route")
	travel_id = request.args.get("travel_id")
	route.replace("'"," ")
	travel = request.args.get("travel")
	route.replace("'", " ")
	name = request.args.get("name")
	surname = request.args.get("surname")
	seat_no = request.args.get("seat")
	phone_no = request.args.get("phone_no")
	
	control_sql = "SELECT * FROM reservation WHERE travel_id=" + travel_id +" and seat_no="+ seat_no 
	curr =conn.cursor()
	curr.execute(control_sql)
	rows=curr.fetchall()
	print rows
	if rows == []:
		sql_part1 = "INSERT INTO reservation(route , travel , name , surname , seat_no , phone_no,travel_id)VALUES("
		sql_part2 = "'"+ route + "','" + travel + "','" + name + "','" + surname + "'," + seat_no + ",'" + phone_no + "','" + str(travel_id) + "');" 
		print sql_part1+sql_part2
		curr = conn.cursor()
		curr.execute(sql_part1 + sql_part2) 
		conn.commit()
		curr.execute("UPDATE seats SET state='reserved' WHERE seat_no=" + seat_no + "and travel_id=" + travel_id )
		conn.commit()
		curr.execute("SELECT reservation_id,name,surname,route,travel,seat_no FROM reservation ORDER BY reservation_id DESC LIMIT 1")
		result=curr.fetchall()
		return render_template("reservationInfo.html",resId=str(result[0][0]),
												  name=result[0][1],surname=result[0][2],
												  route=result[0][3],date=result[0][4],
												  seatNo=str(result[0][5]))
	else:
		return "yapili zaten"
			
	 	 
	 	
	 		


@app.route("/resCheck")
def reservationCheck():
	resNo = request.args.get("resNo")
	curr = conn.cursor()
	curr.execute("SELECT * FROM reservation WHERE reservation_id=" + resNo)
	rows=curr.fetchall()
	if len(rows)>0:
		return render_template("resCheck.html",id=rows[0][0],route=rows[0][1],travel=rows[0][2],seat=rows[0][5],name=rows[0][3],surname=rows[0][4])
	else: 
		return "<h3> There is no reservation made by this number </h3>"

@app.route("/deleteReservation")
def deleteReservation():
	resNo = request.args.get("resNo")
	curr =conn.cursor()
	curr.execute("SELECT seat_no FROM reservation WHERE reservation_id=" + resNo) 
	id=curr.fetchall()
	print "id",id[0][0]
	conn.commit()


	curr.execute("DELETE FROM reservation WHERE reservation_id=" + resNo)
	conn.commit()

	
	curr.execute("UPDATE seats SET state='free' WHERE seat_no=" + str(id[0][0]))

	conn.commit()


	
	conn.commit()
	return "<h3> Reservation Deleted  </h3>"
	


if __name__ == "__main__":
	app.run()
	
