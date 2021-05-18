from django.views import View
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from collections import deque


class WelcomeView(View):
    def get(self, request, *args, **kwargs):
        data = "<h2>Welcome to the Hypercar Service!</h2>"
        return HttpResponse(data)

class MenuView(View):
    template_name = "tickets/menu.html"
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, self.template_name)



cars_queue = deque()
token_count = {"change_oil": [],
               "inflate_tires": [],
               "diagnostic": []}
minutes = 0
token_number = 1

def get_estimate_time(service, ticket):
    if service == "change_oil":
        minutes = len(token_count["change_oil"]) * 2
    elif service == "inflate_tires":
        minutes = len(token_count["change_oil"]) * 2 + \
              len(token_count["inflate_tires"]) * 5
    elif service == "diagnostic":
        minutes = len(token_count["change_oil"]) * 2 + \
                  len(token_count["inflate_tires"]) * 5 + \
                  len(token_count["diagnostic"]) * 30
    token_count[service].append(ticket)
    return minutes

class ChangeOilTicketsView(View):
    def get(self, request, *args, **kwargs):
        global token_number, cars_queue
        cars_queue.append("change_oil")
        context = {}
        context["ticket_number"] = token_number
        context["minutes_to_wait"] = get_estimate_time("change_oil", token_number)
        token_number += 1
        return render(request, "tickets/token_details.html", context)

class InflateTiresTicketsView(View):
    def get(self, request, *args, **kwargs):
        global token_number, cars_queue
        cars_queue.append("inflate_tires")
        context = {}
        context["ticket_number"] = token_number
        context["minutes_to_wait"] = get_estimate_time("inflate_tires", token_number)
        token_number += 1
        return render(request, "tickets/token_details.html", context)

class DiagnosticTicketsView(View):
    def get(self, request, *args, **kwargs):
        global token_number, cars_queue
        cars_queue.append("diagnostic")
        context = {}
        context["ticket_number"] = token_number
        context["minutes_to_wait"] = get_estimate_time("diagnostic", token_number)
        token_number += 1
        return render(request, "tickets/token_details.html", context)

class ProcessingView(View):
    global token_count
    context = {}
    def get(self, request, *args, **kwargs):
        self.context["data"] = token_count
        return render(request, "tickets/processing.html", self.context)
    def post(self, request, *args, **kwargs):
        return redirect("/next")

class NextView(View):
    global token_count
    context = {}
    def get(self, request, *args, **kwargs):
        for service in token_count:
            if token_count[service]:
                token_count[service].pop(0)
                self.context["data"] = token_count["change_oil"] + token_count["inflate_tires"] \
                                       + token_count["diagnostic"]
                if self.context["data"]:
                    self.context["ticket"] = self.context["data"][0]
                else:
                    self.context["ticket"] = "waiting"
                break
            self.context["ticket"] = "waiting"
        return render(request, "tickets/next.html", self.context)



