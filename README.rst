==================
django-googwebopt
==================


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

  - if the conversion is simply the page view, put {{ GWO_PAGE_CONVERSION }} in the head.
  - if the conversion is a link click then put {{ GWO_IN_HREF_CONVERSION }} within the <a> tag. For example::

        <a href="page.html" {{ GWO_IN_HREF_CONVERSION }} >

  - if the conversion is within a function use {{ GWO_IN_SCRIPT_CONVERSION }} within the script. For example::

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

For Help
========
GoogWebOpt is very much in development and the documentation could
use some work.  If you want help using this code please contact me at
jesseh@i-iterate.com.

