from django.conf import settings
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import RequestContext, loader
from django.views.generic import TemplateView, DetailView
from django.contrib.auth import authenticate, login, logout, get_user_model
from .forms import form_user_login
from reversion.models import Version
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from vocabs.models import *
from .metadata import PROJECT_METADATA as PM
from copy import deepcopy



class GenericWebpageView(TemplateView):
    template_name = 'webpage/index.html'

    def get_context_data(self, **kwargs):
        context = super(GenericWebpageView, self).get_context_data(**kwargs)
        context['apps'] = settings.INSTALLED_APPS
        return context

    def get_template_names(self):
        template_name = "webpage/{}.html".format(self.kwargs.get("template", 'index'))
        try:
            loader.select_template([template_name])
            template_name = "webpage/{}.html".format(self.kwargs.get("template", 'index'))
        except:
            template_name = "webpage/index.html"
        return [template_name]


#################################################################
#               User detail view                                #
#################################################################

class UserDetailView(DetailView):
    model = get_user_model()
    template_name = 'webpage/user_detail.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data()
        current_user = self.kwargs['pk']
        versions = Version.objects.filter(revision__user__id=current_user)[:500]
        context['versions'] = versions
        context['created_cs'] = SkosConceptScheme.objects.filter(created_by=current_user)
        context['curated_cs'] = SkosConceptScheme.objects.filter(curator=current_user)
        context['created_collections'] = SkosCollection.objects.filter(created_by=current_user)
        context['created_concepts'] = SkosConcept.objects.filter(created_by=current_user)
        context['created_labels'] = SkosLabel.objects.filter(created_by=current_user)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UserDetailView, self).dispatch(*args, **kwargs)

#################################################################
#               views for login/logout                          #
#################################################################

def user_login(request):
    if request.method == 'POST':
        form = form_user_login(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'], password=cd['password'])
            if user and user.is_active:
                login(request, user)
                return HttpResponseRedirect(request.GET.get('next', '/'))
            return HttpResponse('user does not exist')
    else:
        form = form_user_login()
        return render(request, 'webpage/user_login.html', {'form': form})


def user_logout(request):
    logout(request)
    return render_to_response('webpage/user_logout.html')


def handler404(request, exception):
    return render(request, 'webpage/404-error.html', locals())


#################################################################
#                    project info view                          #
#################################################################


def project_info(request):

    """
    returns a dict providing metadata about the current project
    """

    info_dict = deepcopy(PM)

    if request.user.is_authenticated:
        pass
    else:
        del info_dict['matomo_id']
        del info_dict['matomo_url']
    info_dict['base_tech'] = 'django'
    info_dict['framework'] = 'djangobaseproject'
    return JsonResponse(info_dict)