from django.views.generic.edit import CreateView, DeleteView
from django.views.generic.detail import DetailView
from graphs.models import Scenario, Activity, Student
from django import forms
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from graphs.forms import StudentRegistrationForm
from django.http import HttpResponseRedirect, HttpResponse
from activities.views import user_activity
import random
import json
import csv


class ScenarioCreateView(CreateView):
    model = Scenario
    fields = ['name', 'group', 'json']
    template_name = 'graph-editor.html'
    success_url = reverse_lazy("scenario-list")

    def get_form(self, form_class):
        form = super(ScenarioCreateView, self).get_form(form_class)
        form.fields['json'].widget = forms.HiddenInput()
        return form


class ScenarioDeleteView(DeleteView):
    model = Scenario
    success_url = reverse_lazy("scenario-list")


class ScenarioDetailView(DetailView):
    """DetailView subclass used to use multiple models in the template"""
    model = Scenario

    def get_context_data(self, **kwargs):
        context = super(ScenarioDetailView, self).get_context_data(**kwargs)
        context["activities"] = Activity.objects.all()
        return context


def student_registration(request):
    form = StudentRegistrationForm(request.POST)
    if form.is_valid():
        form.save()
        student = Student.objects.get(email=form.cleaned_data['email'])
        random_id = random.randint(0, Scenario.objects.count() - 1)
        student.scenario = Scenario.objects.all()[random_id]
        json_data = json.loads(student.scenario.json)
        edges = json_data['edges']
        act = json_data['start']
        path = [act]

        while True:
            next_act = []
            for e in edges:
                if e['a1'] == path[-1]:
                    next_act.append(e['a2'])

            if next_act:
                path.append(random.choice(next_act))
            else:
                break

        student.path = json.dumps(path)
        student.save()
        request.session['user_id'] = student.pk

        return HttpResponseRedirect('/student/')
    else:
        return render(request, 'registration/student-registration.html', {'form': form})


def student_learning(request):
    if 'user_id' in request.session:
        return user_activity(request)
    else:
        return HttpResponseRedirect('/student/register/')


def stats_view(request, pk):
    scenario = Scenario.objects.get(pk=pk)
    paths = Student.objects.filter(scenario=scenario).order_by('path').values_list('path', flat=True).distinct()
    data = []
    for path in paths:
        data.append([('Path', path),
                     ('Number of students', scenario.num_students(path)),
                     ('Average time', scenario.avg_time(path)),
                     ('Average learning gain', scenario.avg_learning(path)),
                     ('Standard deviation', scenario.learning_stdev(path)),
                     ('Variance', scenario.learning_variance(path))])

    return render(request, 'scenario-stats.html', context={'scenario': scenario, 'data': data})


def get_csv(request, pk):
    """Export scenario data as a CSV file$

    :param pk: Scenario primary key
    """
    # TODO export useful data
    scenario = Scenario.objects.get(pk=pk)
    students = Student.objects.filter(scenario=scenario).order_by('path')
    filename = 'scenario_' + str(scenario.pk) + '.csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    writer = csv.writer(response)
    for student in students:
        writer.writerow([student.path, student.email, student.start_date, student.completion_date])
    return response
