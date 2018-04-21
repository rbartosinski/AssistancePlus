"""asssystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from assistance.views import OrderSearchView, OrderSimpleAddView, \
    OrderEditView, OrderCheckView, CheckInsuranceView, PolicyDetailsView, TaskAddView, \
    TaskListView, GenerateTaskReceipt, LoginView, LogoutView, \
    TaskEditView, SaveTaskReceipt, DocListView, DocAddView, ShowDocView, HelpView, ContactView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^order_search/$', OrderSearchView.as_view(), name='order_search'),
    url(r'^order_add/$', OrderSimpleAddView.as_view(), name='order_add'),
    url(r'^order_edit/(?P<order_id>\d+)/$', OrderEditView.as_view(), name='order_edit'),
    url(r'^order_check/(?P<order_id>\d+)/$', OrderCheckView.as_view(), name='order_check'),
    url(r'^doc_list/(?P<order_id>\d+)/$', DocListView.as_view(), name='doc_list'),
    url(r'^doc_add/(?P<order_id>\d+)/$', DocAddView.as_view(), name='doc_add'),
    url(r'^doc_show/(?P<order_id>\d+)/(?P<doc_id>\d+)/$', ShowDocView.as_view(), name='doc_show'),
    url(r'^check_insurance/(?P<order_id>\d+)/$', CheckInsuranceView.as_view(), name='check_insurance'),
    url(r'^policy_details/(?P<order_id>\d+)/(?P<policy_id>\d+)/$', PolicyDetailsView.as_view(), name='policy_details'),
    url(r'^task_list/(?P<order_id>\d+)/$', TaskListView.as_view(), name='task_list'),
    url(r'^task_add/(?P<order_id>\d+)/$', TaskAddView.as_view(), name='task_add'),
    url(r'^task_edit/(?P<order_id>\d+)/(?P<task_id>\d+)$', TaskEditView.as_view(), name='task_edit'),
    url(r'^generate_receipt/(?P<order_id>\d+)/(?P<task_id>\d+)$', GenerateTaskReceipt.as_view(), name='generate_doc'),
    url(r'^save/(?P<order_id>\d+)/(?P<task_id>\d+)$', SaveTaskReceipt.as_view(), name='save_task'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^help/$', HelpView.as_view(), name='help'),
    url(r'^contact/$', ContactView.as_view(), name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

