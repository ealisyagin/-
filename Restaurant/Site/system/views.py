from django.shortcuts import render
from django.http import HttpResponse
from .models import Unit
from .forms import UnitForm

import pickle
import numpy as np
import pandas as pd 
import os
import seaborn as sns
from surprise import Dataset
from surprise import Reader
from surprise import SVD
import difflib
import random

user_rating_file_path = "media/rating_final.csv"
geolocation_file_path = 'media/geoplaces2.csv'
data = pd.read_csv(user_rating_file_path)
location_data = pd.read_csv(geolocation_file_path)
data = pd.merge(data, location_data[['placeID', 'name']], on='placeID')
data = data[['userID', 'placeID' ,'name', 'rating', 'food_rating', 'service_rating']]
reader = Reader(rating_scale=(0,2))
rating_data = Dataset.load_from_df(data[['userID', 'placeID', 'rating']], reader)
svd = pickle.load(open('media/Model_Restorants.sav', 'rb'))


def get_rest_id(rest_name, data):
	rest_names = list(data['name'].values)
	closest_names = difflib.get_close_matches(rest_name, rest_names)
	rest_id = data[data['name'] == closest_names[0]]['placeID'].iloc[0]
	return rest_id

def predict_rating(user_id, rest_name, data, model=SVD):
	rest_id = get_rest_id(rest_name, data)
	estimated_ratings = model.predict(uid = user_id, iid = rest_id)
	return estimated_ratings.est

def ten_users():
	users = []
	for i in range(10):
		random_user_id = np.random.choice(list(np.unique(data['userID'].values)))
		users.append( str(random_user_id + " : " + pd.Series(data.loc[np.where(data.userID==random_user_id)]['name'].values)))
	return users

def recommend_restaurants(user_id, data=data, model=svd, threshold=1.7):
	recommended_restaurants = {}
	unique_rest_names = list(np.unique(data['name'].values))
	random.shuffle(unique_rest_names)
	for rest_name in unique_rest_names:
		rating = predict_rating(user_id=user_id, rest_name=rest_name, data=data, model=svd)
		if rating > threshold:
			recommended_restaurants[rest_name] = np.round(rating,2)
	print("Генерация рекомендаций ресторана для идентификатора пользователя {} : ".format(user_id))
	restaurant_names = np.array(list(recommended_restaurants.keys())).reshape(-1,1)
	restaurant_ratings = np.array(list(recommended_restaurants.values())).reshape(-1,1)
	results = np.concatenate((restaurant_names, restaurant_ratings), axis=1)
	results_df = pd.DataFrame(results, columns=['Restaurants', 'Rating (0-2)']).sort_values(by='Rating (0-2)', ascending=False)
	res = results_df.reset_index().drop('index', axis=1)
	return res


def index(request):
	return render(request, 'system/index.html')
	

def recom(request):
	work = Unit.objects.order_by('-user_id')
	if work:
		for n in work:
			if n.recomendations=="NULL":
				n.recomendations = recommend_restaurants(user_id = n.user_id)
				n.save()
	return render(request, 'system/recom.html', {'work':work})
	

def post(request):
	ex = ten_users()
	error = ''
	if request.method == 'POST':
		form = UnitForm(request.POST)

		if form.is_valid():
			form.save()
		else:
			error = 'Ошибка заполнения'
			
	form = UnitForm()
	data = {
		'form': form,
		'error': error,
		'ex': ex
	}
	return render(request, 'system/post.html', data)
