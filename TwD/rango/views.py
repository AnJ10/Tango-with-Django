from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core import serializers 	 	

from rango.models import Category, Page, UserProfile, LikeRelation
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.serpwow_search import run_query
from rango.templatetags.rango_template_tags import get_category_list
from datetime import datetime

def get_server_side_cookie(request, cookie, default_val = None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val	

def visitor_cookie_handler(request):
	visits_cookie = int(get_server_side_cookie(request,'visits', '1'))
	last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

	if ( datetime.now() - last_visit_time).days > 0:
		visits = visits_cookie + 1
		request.session['last_visit'] = str(datetime.now())
		request.session['visits'] = visits
	else :
		request.session['last_visit'] =  last_visit_cookie
		request.session['visits'] = visits_cookie

#	print('Last Visit : {0}'.format(request.session['last_visit']))

			


def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	page_list = Page.objects.order_by('-views')[:5]
	context_dict = { 'categories' : category_list, 'pages' : page_list }
	
	visitor_cookie_handler(request)
	context_dict['visits'] = request.session['visits']

	response = render(request, 'rango/index.html', context=context_dict)
	return response


def about(request):
	visits = get_server_side_cookie(request, 'visits', '1')
	context_dict = {'author' : "Aniket Jain", 'visits' : visits}
	return render(request, 'rango/about.html', context=context_dict)	


def show_category(request, category_name_slug):
	context_dict = {}
	result_list = []


	try:
		category = Category.objects.get(slug=category_name_slug)
		pages = Page.objects.filter(category=category).order_by('-views')
		context_dict['pages'] = pages
		context_dict['category'] = category

	except Category.DoesNotExist:
		context_dict['pages'] = None
		context_dict['category'] = None

	like_check = False		

	user = request.user

	if not request.user.is_authenticated():
		user = None


	if user and category:
		try :
			like = LikeRelation.objects.get(category=category, user=user)
		except LikeRelation.DoesNotExist: 
			like_check = True
			

	context_dict['like_display'] = like_check		
		
	if request.method == 'POST':
		query = request.POST['query']

		if query:
			result_list = run_query(query, size = 50)	
			context_dict['result_list'] = result_list
			context_dict['query'] = query
		
	return render(request, 'rango/category.html', context=context_dict)	

@login_required
def add_category(request):
	form = CategoryForm()
	#print(form)

	if request.method == 'POST':
		form = CategoryForm(request.POST)	

		if form.is_valid():
			name = form.cleaned_data.get('name')
			print("Category Name is {0}".format(name))
			form.save(commit=True)
			category = Category.objects.get(name=name)	
			return redirect('rango:show_category', category.slug)
		
		else:
			print(form.errors)

#	print("Rendering......")
#	print(form)
	return render(request, 'rango/add_category.html', context={'form' : form })	

@login_required
def add_page(request, category_name_slug):

	try:
		category = Category.objects.get(slug=category_name_slug)

	except Category.DoesNotExist :
		category = None

	form = PageForm()
	
	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			if category:
				page = form.save(commit = False)
				page.category = category
				page.views = 0
				page.save()
				return show_category(request, category_name_slug)

		else : 
			print(form.errors)

	context_dict = {'form' : form, 'category' : category}
	return render(request, 'rango/add_page.html', context=context_dict)		

"""
def register(request):

	registered = False

	if request.method == 'POST':
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)	
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			profile.save()
			registered = True

		else:
			print(user_form.errors)
			print(profile_form.errors)	
				
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	context_dict = {'user_form' : user_form, 'profile_form' : profile_form, 'registered' : registered}

	return render(request, 'rango/register.html', context = context_dict )


def user_login(request):

	context_dict = {}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(username=username, password=password)

		if user:
			if user.is_active:
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
				return HttpResponse("Your rango account is disabled. ")	

		else:
			print("Invalid login details: {0}, {1}".format(username, password))
			context_dict = {'error' : "Invalid username/password."}

	#else:
	
	return render(request, 'rango/login.html', context=context_dict )		


@login_required
def user_logout(request):
	logout(request)
	return HttpResponseRedirect(reverse('index'))

"""


@login_required
def restricted(request):
	return HttpResponse("Since you're logged in, you can see this text!")



def search(request):
	result_list = []

	if request.method == 'POST':
		query = request.POST['query'].strip()

		if query:
			result_list = run_query(query)
			return render(request, 'rango/search.html', {'result_list' : result_list, 'query' : query})


	return render(request, 'rango/search.html', {'result_list' : result_list})		


def track_url(request, category_name_slug):

	if request.method == 'GET':
		if 'page_id' in request.GET:
			page_id = request.GET['page_id']

			try:
				page = Page.objects.get(id = page_id)

			except Page.DoesNotExist:
				page = None

			if page :
				page.views = page.views + 1
				page.save() 
				print("{0} - {1} views".format(page.title, page.views))
				return HttpResponseRedirect(page.url)

			
			else :
				return show_category(request, category_name_slug)

		
	return HttpResponseRedirect(reverse('index'))
			
				
@login_required
def register_profile(request):

	
	form = UserProfileForm()
	context_dict = {'form' : form}
	if request.method == 'POST':
		form = UserProfileForm(request.POST, request.FILES)
	
		if form.is_valid() :
			userprofile = form.save(commit=False)
			userprofile.user = request.user
			userprofile.save() 
			#context_dict = {'form' : userprofile}
			return redirect('rango:profile', userprofile.user.username	)

	
	return render(request, 'rango/profile_registration.html', context=context_dict)		


@login_required
def profile(request, username):
	
	try:
		user = User.objects.get(username=username)

	except User.DoesNotExist:
		return redirect('rango:index')


	profile = UserProfile.objects.get_or_create(user=user)[0]	
	form = UserProfileForm({'website':profile.website, 'picture':profile.picture })

	if request.method == 'POST':
		form = UserProfileForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			form.save(commit=True)
			return redirect('rango:profile', user.username)
		else:
			print(form.errors)

	return render(request, 'rango/profile.html', {'profile':profile, 'selected_user':user, 'form':form })

@login_required
def list_profiles(request):
	userprofile_list = UserProfile.objects.all()
	return render(request, 'rango/list_profiles.html', {'userprofile_list':userprofile_list})


@login_required
def like_category(request):
	cat_id = None
	if request.method == 'GET' :

		if request.GET['like_id'] == "like" :
			cat_id = request.GET['category_id']
			likes = 0
			if cat_id :			
				category = Category.objects.get(id = int(cat_id))
				if category :
					like_query = LikeRelation.objects.get_or_create(category=category, user=request.user)
					liked_by = like_query[0]
					liked_by.save()
					if like_query[1]:
						category.likes = category.likes + 1
						category.save()
					
					
					likes = category.likes

			return JsonResponse({ "likes" : likes, "button_update" : "Unlike", "like_id_update" : "unlike" })

		elif request.GET['like_id'] == "unlike" :
			cat_id = request.GET['category_id']
			likes = 0
			if cat_id :
				category = Category.objects.get(id = int(cat_id))
				if category :
					try:
						liked_by = LikeRelation.objects.get(category=category, user=request.user)
					except LikeRelation.DoesNotExist:
						liked_by = None

					if liked_by:	
						liked_by.delete()
						category.likes = category.likes - 1
						if category.likes <= 0 :
							category.likes = 0

						category.save()
				
					likes = category.likes
				
			return JsonResponse({ "likes" : likes, "button_update" : "Like", "like_id_update" : "like" })	


def suggest_categories(request):
	category_list = []
	if request.method == 'GET':
		starts_with = request.GET['suggestion']
		category_list = get_category_list(starts_with)

	return render(request, 'rango/cats.html', {'cats' : category_list})	

@login_required
def button_add_page(request):

	if request.method == 'GET':
		url = request.GET["url"]
		title = request.GET["title"]
		category_id = request.GET['category_id']
		context_dict = {}
	
		if category_id :
			try:
				category = Category.objects.get(id=category_id)
			except Category.DoesNotExist :
				category = None

			context_dict['category'] = category

			if category:			
				if request.GET['add_id'] == 'add' :
					page_object = Page.objects.get_or_create(title=title, url=url, category=category)
					page = page_object[0]
					page.views = 0
					page.save()
					context_dict['pages'] = Page.objects.filter(category=category).order_by('-views')
					return render(request, 'rango/page_list.html', context_dict)

				elif request.GET['add_id'] == 'remove' :
					print("Here")
					try:
						page = Page.objects.get(title=title, url=url, category=category)
					except Page.DoesNotExist : 
						page = None

					if page:	
						print("here2")	
						page.delete()

					context_dict['pages'] = Page.objects.filter(category=category).order_by('-views')
					return render(request, 'rango/page_list.html', context_dict)

	return redirect('rango:index')			