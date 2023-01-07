from django.db import models

class Unit(models.Model):
	user_id = models.TextField('user_id', default = 0)
	recomendations = models.TextField('Рекомендация', default = "NULL")
	
	def __str__(self):
		return self.title
		
	class Meta:
		verbose_name = 'Объект'
		verbose_name_plural = 'Объекты'
