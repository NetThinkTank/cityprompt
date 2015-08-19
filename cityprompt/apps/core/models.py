from django.contrib.auth.models import User
from django.db import models, transaction
from django_fsm import ConcurrentTransitionMixin, FSMField, transition, TransitionNotAllowed

from polymorphic import PolymorphicModel

import mptt, re

class BaseModel(PolymorphicModel):
	class Meta:
		abstract = True
		# managed = True
	
	created = models.DateTimeField(editable=False, auto_now_add=True)
	
	creator = models.ForeignKey(
		User, related_name='%(app_label)s_%(class)s_creator',
		blank=True, null=True, editable=False
	)

	modified = models.DateTimeField(editable=False, auto_now=True)
	
	modifier = models.ForeignKey(
		User, related_name='%(app_label)s_%(class)s_modifier',
		blank=True, null=True, editable=False
	)



class Category(BaseModel):
	class Meta:
		verbose_name_plural = 'Categories'

	name = models.CharField(max_length=250)

	slug = models.CharField(max_length=250)
	parent = models.ForeignKey('self', blank=True, null=True, related_name='children')

	def __unicode__(self):
		return u'%s' % (self.name)



class Automaton(ConcurrentTransitionMixin, BaseModel):
	class Meta:
		verbose_name_plural = 'Automata'

	name = models.CharField(max_length=250)
	slug = models.CharField(max_length=250)
	
	date = models.DateTimeField()
	category = models.ForeignKey(Category)

	def __unicode__(self):
		return u'%s' % (self.slug)

	def output(self, template):
		matches = re.finditer('\{.*\}', template)
		
		for match in matches:
			attr_slot = match.group(0)
			attr_name = attr_slot[1:len(attr_slot)-1]
			
			attr = None
		
			try:
				attr = getattr(self, attr_name)
			except:
				pass
			
			if not attr:
				continue
			
			template = template.replace(attr_slot, attr)

		return template



class BasketballAutomaton(Automaton):
	class Meta:
		verbose_name_plural = 'BasketballAutomata'

	state = FSMField(default='NEW')

	away_team = models.CharField(max_length=50)
	home_team = models.CharField(max_length=50)
	
	away_score = models.IntegerField(default=0)
	home_score = models.IntegerField(default=0)
	
	quarters_completed = models.IntegerField(default=0)
	
	check_list = [
		'q1a', 'q1h', 'q1t',
		'q2a', 'q2h', 'q2t',
		'q3a', 'q3h', 'q3t',
		'q4a', 'q4h', 'q4t',
		'ota', 'oth', 'ott'
	]

	def __unicode__(self):
		return u'%s' % (self.name)

	def quarter1(self):
		return self.quarters_completed == 1
	
	def quarter2(self):
		return self.quarters_completed == 2
	
	def quarter3(self):
		return self.quarters_completed == 3
	
	def quarter4(self):
		return self.quarters_completed == 4
	
	def overtime(self):
		return self.quarters_completed == 5
	
	def away_winning(self):
		return self.away_score > self.home_score
	
	def home_winning(self):
		return self.away_score < self.home_score
	
	def tie(self):
		return self.away_score == self.home_score

	@transition(field=state, source='NEW', target='Q1A', conditions=[quarter1, away_winning])
	def q1a(self):
		pass
	
	@transition(field=state, source='NEW', target='Q1H', conditions=[quarter1, home_winning])
	def q1h(self):
		pass
	
	@transition(field=state, source='NEW', target='Q1T', conditions=[quarter1, tie])
	def q1t(self):
		pass
	
	@transition(field=state, source=['Q1A', 'Q1H', 'Q1T'], target='Q2A', conditions=[quarter2, away_winning])
	def q2a(self):
		pass
	
	@transition(field=state, source=['Q1A', 'Q1H', 'Q1T'], target='Q2H', conditions=[quarter2, home_winning])
	def q2h(self):
		pass
	
	@transition(field=state, source=['Q1A', 'Q1H', 'Q1T'], target='Q2T', conditions=[quarter2, tie])
	def q2t(self):
		pass
	
	@transition(field=state, source=['Q2A', 'Q2H', 'Q2T'], target='Q3A', conditions=[quarter3, away_winning])
	def q3a(self):
		pass
	
	@transition(field=state, source=['Q2A', 'Q2H', 'Q2T'], target='Q3H', conditions=[quarter3, home_winning])
	def q3h(self):
		pass
	
	@transition(field=state, source=['Q2A', 'Q2H', 'Q2T'], target='Q3T', conditions=[quarter3, tie])
	def q3t(self):
		pass
	
	@transition(field=state, source=['Q3A', 'Q3H', 'Q3T'], target='Q4A', conditions=[quarter4, away_winning])
	def q4a(self):
		pass
	
	@transition(field=state, source=['Q3A', 'Q3H', 'Q3T'], target='Q4H', conditions=[quarter4, home_winning])
	def q4h(self):
		pass
	
	@transition(field=state, source=['Q3A', 'Q3H', 'Q3T'], target='Q4T', conditions=[quarter4, tie])
	def q4t(self):
		pass
	
	@transition(field=state, source=['Q4A', 'Q4H', 'Q4T'], target='OTA', conditions=[overtime, away_winning])
	def ota(self):
		pass
	
	@transition(field=state, source=['Q4A', 'Q4H', 'Q4T'], target='OTH', conditions=[overtime, home_winning])
	def oth(self):
		pass
	
	@transition(field=state, source=['Q4A', 'Q4H', 'Q4T'], target='OTT', conditions=[overtime, tie])
	def ott(self):
		pass

	def run_check(self):
		for method in self.check_list:
			try:
				eval('self.' + method + '()')
			except TransitionNotAllowed:
				pass

		try:
			with transaction.atomic():
				self.save()
		except IntegrityError:
			pass



class Client(BaseModel):
	name = models.CharField(max_length=250)
	slug = models.CharField(max_length=250)	

	def __unicode__(self):
		return u'%s' % (self.name)



class Asset(BaseModel):
	client = models.ForeignKey(Client)
	automaton = models.ForeignKey(Automaton)
	slug = models.CharField(max_length=250)

	state = FSMField()
	value = models.TextField()

	def __unicode__(self):
		return u'%s' % (self.slug)

	def output(self):
		pass



mptt.register(Category, order_insertion_by=['name'])
