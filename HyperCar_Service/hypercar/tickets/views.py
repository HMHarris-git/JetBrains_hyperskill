from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from collections import deque

class HomeView(View):
    template_name = "tickets/home.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
class WelcomeView(View):
    template_name = "tickets/welcome.html"
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class MenuView(View):
    template_name = "tickets/menu.html"
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name)



# cars_queue = deque()  # In case you want to save the actual sequence of customers on based on priority for keeping logs.
token_count = {"change_oil": [],
               "inflate_tyres": [],
               "diagnostic": []}
minutes = 0
token_number = 1


class ServiceHandlerView(View):
    service_data = { 
                    "change_oil": {"name": "change_oil",
                                    "estimate_time": 2
                                    },

                    "inflate_tyres": {"name": "inflate_tyres",
                                        "estimate_time": 5
                                    },

                    "diagnostic": {"name": "diagnostic",
                                    "estimate_time": 30
                                    },                                
    }

    def get_estimate_time(self, service, ticket):
        global token_count
        minutes = 0
        for service_token in token_count:
            minutes += len(token_count.get(service_token)) * self.service_data.get(service_token).get("estimate_time")
            if service_token == service:
                break
        token_count[service].append(ticket)
        return minutes

    def get(self, request, *args, **kwargs):
        global token_number#, cars_queue
        service = kwargs.get("service_name")
        # cars_queue.append((token_number ,service))
        context = {}
        context["ticket_number"] = token_number
        context["minutes_to_wait"] = self.get_estimate_time(service, token_number)
        token_number += 1
        return render(request, "tickets/token_details.html", context)

class ProcessingView(View):
    global token_count
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["data"] = token_count
        return render(request, "tickets/processing.html", self.context)
        
    def post(self, request, *args, **kwargs):
        self.context["data"] = []
        for service in token_count:
            if token_count[service]:
                token_count[service].pop(0)
                for service_token in token_count:
                    self.context["data"].extend(token_count.get(service_token)) 
                if self.context["data"]:
                    request.session["ticket"] = self.context.get("data")[0]
                    self.context["data"] = []
                else:
                    request.session["ticket"] = "waiting"
                break
            request.session["ticket"] = "waiting"
        return redirect("/next")

class NextView(View):
    context = {}
    def get(self, request, *args, **kwargs):
        self.context["ticket"] = request.session.get("ticket")
        return render(request, "tickets/next.html", self.context)
