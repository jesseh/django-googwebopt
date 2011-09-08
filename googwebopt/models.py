import re

from django.contrib import admin
from django.db import models
from django.template import Template
from django.conf import settings
from django.template import Context, loader
from django.utils.safestring import mark_safe

class GwoExperiment(models.Model):
    """
    Simple mechansim to implement Google Website Optimizer tests

    Requires
    ========
    1. Add the setting GOOGWEBOPT_ACCOUNT which should be the account id for the tests. Like 'UA-10082613-4'

    2. Install the {{ GWO_HEAD_SCRIPT }} at the very top of the head section. You can do this in the base template since it is blank except for pages that are inluded in a test.

    Creating an Experiment
    ======================
    1. Set up the test in the Google website optmizer site.

    2. In the admin area add a new test.
      - The test id is found in the tracking codes. 
      - The url matches indicates for what pages the template tags should be generated. A test can span multiple pages (and must in the case of an A/B expirement). The match should start with '/'. Only one test can be run at a time on a given url match. Earlier created tests take priority. Make sure to inlclude all the pages that are relevant to the test, which is all control, alternative and conversion pages.
      - You can set the test to active at any point. It simply makes the tags show up or be blank. An inactive test is as good as paused on the GWO site.

    3. If the test is multivariate test, then load the tag set 'googwebopt_tags' and define the sections using {% gwo_start_section "name" %} and {% gwo_end_section %}. These generate <script>  tags so they must not be embedded into other tags. The sections can be on any template, but each page must be included in the url match  list to participate in the test. Multiple sections can share a name, in which case they will get the same variant.

    4. Load the tag set 'googwebopt_tags' and set the conversion moment using one of these mechisms
        * if the conversion is simply the page view, put {{ GWO_PAGE_CONVERSION }} in the head.
        * if the conversion is a link click then put {{ GWO_IN_HREF_CONVERSION }} within the <a> tag. For example::

    <a href="page.html" {{ GWO_IN_HREF_CONVERSION }} >

        * if the conversion is within a function use {{ GWO_IN_SCRIPT_CONVERSION }} within the script. For example::

       <script>
        function yay() {
            {{ GWO_IN_SCRIPT_CONVERSION }}
            alert "converted";
        }
        </script>

    If the test is multivariate then go back to the Google website optimizer site and enter the section names and variants.

    4. Mark the test as active and check that all the tags are showing up in the right places. There should be a script at the top of each relevant page, sections if it is a multivariate test, and a conversion mechanism.

    5. Start the test on the Google web optmizer site and learn lots!

    6. When the test is over change it to inactive in the admin pages. The makes the template tags all be blank. As a result you can leave all the tags in place so that the next test is easy.
    """

    title = models.CharField(max_length=100, help_text="A short name for this test.")
    exp_num = models.CharField(max_length=50, help_text="The expirement number for the Google Website Optmizer site. It's in the event tag: /XXXXXX/test")
    active = models.BooleanField(help_text="Insert the tags or not. Non-active is as good as paused on the GWO site.")
    description = models.TextField(blank=True, help_text="What are we testing?")
    conclusion = models.TextField(blank=True, help_text="What did we learned from the test?")
    
    def __unicode__(self):
        return "%s (%s)" % (self.title, self.exp_num)

    class Meta:
        verbose_name = "Google website optimizer control"
    def matches(self):
        """
        List the match strings
        """
        matches = self.urlmatch_set.order_by("role", "url_match").all()
        res = []
        for m in matches:
            res.append("%s: '%s'" % (m.get_role_display(), m.url_match))
        return mark_safe(("<br />").join(res))

    matches.allow_tags=True

    def context(self, role):
        """
        Return a dictionary with the template tags set up for this expirement
        """
        to_render = {
            "GWO_PAGE_CONVERSION" : "googwebopt/page_conversion.html",
            "GWO_IN_SCRIPT_CONVERSION": "googwebopt/in_script_conversion.html",
            "GWO_IN_HREF_CONVERSION" : "googwebopt/in_href_conversion.html",
        }
        # The head script depends on the page's role
        if role == "3cnvr":
            to_render["GWO_HEAD_SCRIPT"] = "googwebopt/conversion_only_script.html"
        elif role == "2alt":
            to_render["GWO_HEAD_SCRIPT"] = "googwebopt/alternate_and_conversion_script.html"
        else: #"1ctrl-ab" or "1ctrl-mv"
            to_render["GWO_HEAD_SCRIPT"] = "googwebopt/control_and_conversion_script.html"
        is_ab_type = role == "1ctrl-ab"
        c = Context({
                    "exp_num" : self.exp_num,
                    "gwo_account" : settings.GOOGWEBOPT_ACCOUNT,
                    "is_ab_type" : is_ab_type,
                    })
        rv = { "GWO_ACTIVE" : True }
        for tag, tplt in to_render.items():
            rv[tag] = loader.get_template(tplt).render(c)
        return rv


class UrlMatch(models.Model):
    ROLE_CHOICES = (
        ("1ctrl-ab", "A/B test control page"),
        ("1ctrl-mv", "Multivariate test page"),
        ("2alt", "A/B test alternate page (for AB test"),
        ("3cnvr", "Non-tested conversion page"),
    )
    gwoexpirement = models.ForeignKey(GwoExperiment)
    url_match = models.CharField(max_length=100, help_text="What urls should get tagged. Should start with '/'")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, help_text="The type of page defines what tags are set. Any type of page can include a conversion. The non-tested conversion page type is for a conversion on a page that is not otherwise part of the test.")
    
    class Meta:
        verbose_name_plural = "matches"
        
    def __unicode__(self):
        return self.url_match

class UrlMatchInline(admin.TabularInline):
    model = UrlMatch
    extra = 3

class ExperimentAdmin(admin.ModelAdmin):
    inlines = [UrlMatchInline]
    list_display = ("title", "active",  "exp_num", "matches", "description", "conclusion" )
    list_editable = ("active",)

admin.site.register(GwoExperiment, ExperimentAdmin)

def set_experiment(request):
    """
    A context processor that sets tags for the experiment applicable to the url.
    """
    path = request.path_info
    experiments = GwoExperiment.objects.select_related().filter(active=True)
    for exp in experiments:
        patterns = exp.urlmatch_set.all()
        for p in patterns:
            if re.match(p.url_match, path):
                rv = exp.context(p.role)
                return rv
    # if no match return empty values so that at they show up in a debug list
    return { 
           "GWO_ACTIVE" : False,
           "GWO_HEAD_SCRIPT" : "",
           "GWO_PAGE_CONVERSION" : "",
           "GWO_IN_SCRIPT_CONVERSION": "",
           "GWO_IN_HREF_CONVERSION" : "",
           }


