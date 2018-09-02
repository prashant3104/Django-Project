from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib import auth
from django.db import connection, IntegrityError, transaction
from django.core.urlresolvers import reverse
import re
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect

# Create your views here.

def default(request):
	if request.user.is_authenticated():				# Check if user is already logged in

		if request.user.first_name == 'admin':
			return HttpResponseRedirect(reverse('admin_dashboard'))
		else:
			return HttpResponseRedirect(reverse('dashboard'))

	return render(request, 'index.html')

#@csrf_protect
def login(request):
	if request.user.is_authenticated():				# Check if user is already logged in

		if request.user.first_name == 'admin':
			return HttpResponseRedirect(reverse('admin_dashboard'))
		else:
			return HttpResponseRedirect(reverse('dashboard'))

	if request.POST:								# POST Method
		email = request.POST['email']
		password = request.POST['password']
		if email == '':
			return render(request, 'login.html')

		cursor = connection.cursor()				# Establish connection with MySQL database
		cursor.execute("SELECT * from auth_user where username='"+email+"';")
		data = cursor.fetchone()
		connection.close()

		if data is not None:				# Check if user is registered
			username = data[4]
			user = auth.authenticate(username=username, password=password)			# Authenticates the username and password
			if user is not None:
				auth.login(request, user)											# Logs in
				if request.user.first_name == 'admin':
					return HttpResponseRedirect(reverse('admin_dashboard'))
				else:
					return HttpResponseRedirect(reverse('dashboard'))
			else:																	# User exists but password is incorrect
				messages.error(request, 'The username and password combination is incorrect.')
		else:
			messages.error(request, 'ID not registered.')							# User does not exist
	return render(request, 'login.html')

def register(request):

	if request.POST:
		email = request.POST['email']							# Fetch the values entered in the registration form
		first_name = request.POST['first_name']
		middle_name = request.POST['middle_name']
		last_name = request.POST['last_name']
		mobile = request.POST['mobile']
		address = request.POST['address']
		role = request.POST['role']
		pass1 = request.POST['pass1']
		pass2 = request.POST['pass2']

		match = re.search(r'[\w.-]+@[\w-]+\.[\w.-]+', email)
		cursor = connection.cursor()
		cursor.execute("SELECT * from "+ role +" WHERE email='"+email+"';")			# Check if member with email ID already exists
		data = cursor.fetchone()
		connection.close()

		if data is not None:												# Check if proper values are entered by the admin
			messages.error(request, 'Email ID already registered')
		elif pass1 != pass2:
			messages.error(request, 'Passwords do not match.')
		elif not match:
			messages.error(request, 'Invalid Email ID.')
		elif email == '':
			messages.error(request, 'Email ID cannot be left blank.')
		elif first_name == '':
			messages.error(request, 'First name cannot be left blank.')
		elif pass1 == '':
			messages.error(request, 'Password cannot be left blank.')
		else:
			cursor = connection.cursor()
			try:
				# If all constraints are satisfied, insert the record into the "+ role +" table
				cursor.execute("INSERT into "+role+" VALUES('"+email+"','"+first_name+"','"+middle_name
					+"','"+last_name+"','"+mobile+"','"+address+"');")

				# Create a new auth_user for the faculty member
				user = User.objects.create_user(email, None, pass1, first_name=role)	#workaround to store user type/role

				connection.commit()
				messages.success(request, 'Successfully registered. Please login using your credentials')
			except Exception as e:
				print(e)
				connection.rollback()
			connection.close()
			return HttpResponseRedirect(reverse('login'))

	return render(request, 'register.html')

# View to display the dashboard for the logged-in faculty member
def dashboard(request):
	if not request.user.is_authenticated():								# Directs to login page if user is not logged in
		return HttpResponseRedirect(reverse('login'))
	if request.user.first_name == 'pkg':
		return HttpResponseRedirect(reverse('admin_dashboard'))			# Directs to admin dashboard if user is admin

	role = request.user.first_name											#workaround to store user type/role

	cursor = connection.cursor()
	cursor.execute("SELECT * from "+ role +" where email='"+request.user.username+"';")
	data = cursor.fetchone()
	connection.close()

	# Sends details of user to be displayed
	details = {'email':data[0], 'name':data[1]+' '+data[2]+' '+data[3], 'mobile':data[4], 'address':data[5]}
	return render(request, 'dashboard.html', details)

# View to display warehouse
def warehouse(request):
	cursor = connection.cursor()
	
	# Fetches details of coal types
	cursor.execute("SELECT * from warehouse")
	data = cursor.fetchall()

	connection.close()
	return render(request, 'warehouse.html', {'data': data, 'role': request.user.first_name})

# View for member to submit offer
@csrf_protect
def offer(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if request.user.first_name == 'admin':
		return HttpResponseRedirect(reverse('warehouse'))


	if request.POST:
		
		cursor = connection.cursor()					
		

		sql = "','".join([request.user.username, request.POST['item'], request.POST['quantity'], request.POST['offered_price']])
		


		try:										# Tries to insert input values into  table
			cursor.execute("INSERT into " + request.user.first_name + "_transactions(email, coal_type, quantity, offered_price) VALUES ('" + sql + "');");
			connection.commit()						# Commits the insertion
		except Exception as e:
			print(e)
			connection.rollback()
		connection.close()

		cursor = connection.cursor()
		
		cursor.execute("SELECT quantity FROM warehouse WHERE coal_type='"+request.POST['item']+"';")
		
		stock = cursor.fetchone()[0]
		
		if int(request.POST['quantity']) > stock:
			messages.success(request, 'NOTE: Given quantity exceeds available stock. Request will be processed once stock arrives')
		else:
			messages.success(request, 'Request submitted')			# Displays success error message
		return HttpResponseRedirect(reverse('dashboard'))

	item = request.GET['item']
	print (item)
	
	if item == '':
		return HttpResponseRedirect(reverse('warehouse'))

	cursor = connection.cursor()
	cursor.execute("SELECT * from warehouse WHERE coal_type = '" + item +"';")				# Passes all to form if method is not POST
	data = cursor.fetchone()
	connection.close()
	return render(request, 'offer.html', {'data': data})

@csrf_protect
def edit(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.first_name == 'admin':
		messages.error(request, 'You do not have rights to edit warehouse')
		return HttpResponseRedirect(reverse('dashboard'))


	if request.POST:
		
		cursor = connection.cursor()					
		item = request.POST['item']
		print (item)


		try:										# Tries to insert input values into  table
			cursor.execute("UPDATE warehouse SET price="+request.POST['price']+" WHERE coal_type='"+item+"';")
			cursor.execute("UPDATE warehouse SET quantity="+request.POST['quantity']+" WHERE coal_type='"+item+"';")
			connection.commit()						# Commits the insertion
		except Exception as e:
			print (e)
			connection.rollback()
		connection.close()
		messages.success(request, 'Values updated')			# Displays success message
		return HttpResponseRedirect(reverse('warehouse'))

	item = request.GET['item']
	print (item)
	
	if item == '':
		return HttpResponseRedirect(reverse('warehouse'))

	cursor = connection.cursor()
	cursor.execute("SELECT * from warehouse WHERE coal_type = '" + item +"';")				# Passes all to form if method is not POST
	data = cursor.fetchone()
	connection.close()
	return render(request, 'edit.html', {'data': data})


# View to display the past requests made by the member
def history(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	
	cursor = connection.cursor()

	if request.user.first_name == 'admin':
		# Fetch columns
		cursor.execute("SHOW COLUMNS from vendors_transactions;")
		columns = cursor.fetchall()
		columns = [row[0] for row in columns]

		# Fetch reviewed requests made by vendors
		cursor.execute("SELECT * from vendors_transactions where status is not NULL;")
		v_pending = cursor.fetchall()
		

		# Fetch reviewed requests made by customers
		cursor.execute("SELECT * from customers_transactions where status is not NULL;")
		c_pending = cursor.fetchall()

		connection.close()
		return render(request, 'admin_history.html', {'vendors':v_pending, 'customers':c_pending, 'columns':columns})
		

	else:
		# Fetch columns
		cursor.execute("SHOW COLUMNS from " + request.user.first_name + "_transactions;")
		columns = cursor.fetchall()
		columns = [row[0] for row in columns]

		# Fetch unreviewed requests made by the user
		cursor.execute("SELECT * from " + request.user.first_name + "_transactions where email='"+request.user.username+"' AND status is NULL;")
		pending = cursor.fetchall()
		

		# Fetch reviewed leave requests made by the user
		cursor.execute("SELECT * from " + request.user.first_name + "_transactions where email='"+request.user.username+"' AND status is not NULL;")
		checked = cursor.fetchall()
		connection.close()
		return render(request, 'history.html', {'checked':checked, 'pending':pending, 'columns':columns})

def admin_dashboard(request):
	if not request.user.is_authenticated():							# Checks if user is logged in or not
		return HttpResponseRedirect(reverse('login'))
	if not request.user.first_name == 'admin':									# Checks if the logged-in user has adminn status or not
		return HttpResponseRedirect(reverse('dashboard'))
	cursor = connection.cursor()


	# Fetch columns
	cursor.execute("SHOW COLUMNS from vendors_transactions;")
	columns = cursor.fetchall()
	columns = [row[0] for row in columns]

	# Fetch unreviewed requests made by vendors
	cursor.execute("SELECT * from vendors_transactions where status is NULL;")
	v_pending = cursor.fetchall()
	

	# Fetch unreviewed requests made by customers
	cursor.execute("SELECT * from customers_transactions where status is NULL;")
	c_pending = cursor.fetchall()

	connection.close()
	return render(request, 'admin_dashboard.html', {'vendors':v_pending, 'customers':c_pending, 'columns':columns})

# View for the admin to approve/decline requests made by members
def update(request):
	if not request.user.is_authenticated():							# Checks if user is logged in or not
		return HttpResponseRedirect(reverse('login'))
	if not request.user.first_name == 'admin':									# Checks if the logged-in user has admin status or not
		return HttpResponseRedirect(reverse('dashboard'))

	if request.GET:
		if not request.GET.has_key('tid'):
			messages.error(request, 'Please select a transaction and try again')
			return HttpResponseRedirect(reverse('admin_dashboard'))

		t_id = request.GET['tid']
		action = request.GET['action']
		role = request.GET['role']


		cursor = connection.cursor()
		cursor.execute("SELECT * from " + role + "_transactions where t_id='"+t_id+"';")			# Fetches details of request to be reviewed
		data = cursor.fetchone()
		print ('1.', data)
		connection.close()
		if data is None:						# Checks if request identified by tid exists or not
			messages.error(request, 'Transaction with given ID does not exist.')
			return HttpResponseRedirect(reverse('admin_dashboard'))

	
		cursor = connection.cursor()
		cursor.execute("SELECT quantity from warehouse where coal_type='"+data[2]+"';")			# Fetches details of request to be reviewed
		quantity = int(cursor.fetchone()[0])
		print ('1.', data)
		connection.close()

		if role == 'customers' and quantity < int(data[3]):
			messages.error(request, 'Requested quantity exceeds available stock')
			return HttpResponseRedirect(reverse('admin_dashboard'))

			
		print ('2.',t_id, action, role)
		try:
			print ("UPDATE " + role + "_transactions SET status="+action+" WHERE t_id="+str(t_id)+";")
			cursor = connection.cursor()
			cursor.execute("UPDATE " + role + "_transactions SET status="+str(action)+" WHERE t_id="+str(t_id)+";")
			
			connection.commit()
			cursor.execute("SELECT * from " + role + "_transactions where t_id='"+str(t_id)+"';")			# Fetches details of request to be reviewed
			data = cursor.fetchone()
			print ('3.', data)
			if role == 'customers':
				cursor = connection.cursor()
				print ("UPDATE warehouse SET quantity=quantity-"+str(data[3])+" WHERE coal_type="+data[2]+";")
				cursor.execute("UPDATE warehouse SET quantity=quantity-"+str(data[3])+" WHERE coal_type='"+data[2]+"';")
			
			connection.commit()

		except Exception as e:
			print (e)
			print ("exception!!!!!!!!!")
			connection.rollback()

		connection.close()
		messages.success(request, 'Action successfull.')

		return HttpResponseRedirect(reverse('admin_dashboard'))

	messages.error(request, 'Incomplete data. Please try again')
	return HttpResponseRedirect(reverse('admin_dashboard'))
	
# View for the admin to display details of the member identified by email
def profile(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect(reverse('login'))
	if not request.user.first_name == 'admin':
		return HttpResponseRedirect(reverse('dashboard'))

	if not request.GET:
		return HttpResponseRedirect(reverse('admin_dashboard'))

	role = request.GET['role']
	email = request.GET['email']

	cursor = connection.cursor()

	cursor = connection.cursor()
	cursor.execute("SELECT * from "+ role +" where email='"+email+"';")
	data = cursor.fetchone()
	connection.close()

	# Sends details of user to be displayed
	details = {'email':data[0], 'name':data[1]+' '+data[2]+' '+data[3], 'mobile':data[4], 'address':data[5]}
	return render(request, 'profile.html', details)


# View for the logged-in user to log out
def logout(request):
	if request.user.is_authenticated():
		auth.logout(request)
		messages.success(request, 'Successfully logged out.')
	return HttpResponseRedirect(reverse('home'))