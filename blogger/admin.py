
from django.contrib import admin
from django.contrib.admin import helpers
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext as _

from blogger.models import BloggerPost, HubbubSubscription

csrf_protect_m = method_decorator(csrf_protect)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published',)
    list_filter = ('published', 'author',)

class HubbubSubscriptionAdmin(admin.ModelAdmin):
    fields = ['topic_url']

    @csrf_protect_m
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        model_class = self.model
        opts = model_class._meta

        if not self.has_add_permission(request):
            raise PermissionDenied

        form_class = self.get_form(request)
        form = form_class(request.POST or None)
        if form.is_valid():
            model = form.save()
            model.send_subscription_request(url_prefix=get_url_prefix(request))
            return self.response_add(request, model)

        adminForm = helpers.AdminForm(form, list(self.get_fieldsets(request)),
            self.prepopulated_fields, self.get_readonly_fields(request),
            model_admin=self)
        media = self.media + adminForm.media

        return self.render_change_form(request, {
            'adminform': adminForm,
            'title': _('Add %s') % force_unicode(opts.verbose_name),
            'opts': opts,
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
            'is_popup': "_popup" in request.REQUEST,
            'show_delete': False,
            'media': media,
        })



def get_url_prefix(request):
    protocol = "%s://" % ("https" if request.is_secure() else "http")
    host = request.get_host()
    return protocol + host


admin.site.register(BloggerPost, PostAdmin)
admin.site.register(HubbubSubscription, HubbubSubscriptionAdmin)
