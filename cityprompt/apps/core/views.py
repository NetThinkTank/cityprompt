from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib import messages

from models import Asset, Automaton, BasketballAutomaton

import logging, re

def index(request):
	return HttpResponse('INDEX')



def asset(request, client, automaton, slug):
	assets = Asset.objects.filter(client__slug=client, automaton__slug=automaton, slug=slug)
	
	if len(assets):
		asset = assets[0]
	else:
		return HttpResponse('ASSET NOT FOUND')
	
	return HttpResponse(asset.automaton.output(asset.value))



def cron(request):
	automata = Automaton.objects.all()
		
	for automaton in automata:
		automaton.run_check()

	return HttpResponse('DONE')
