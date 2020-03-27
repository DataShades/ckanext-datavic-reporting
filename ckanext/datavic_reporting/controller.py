import ckan.lib.base as base
import ckan.model as model
import ckan.plugins.toolkit as toolkit
from ckan.controllers.api import ApiController
from ckanext.datavic_reporting.report_models import ReportSchedule
from pylons import response
from datetime import datetime
import json
import helpers
import authorisation

c = toolkit.c
h = base.h
request = base.request


class ReportingController(base.BaseController):
    @classmethod
    def check_user_access(cls):
        user_dashboard_reports = authorisation.user_dashboard_reports(helpers.get_context())
        if not user_dashboard_reports or not user_dashboard_reports.get('success'):
            toolkit.NotAuthorized(403, toolkit._('You are not Authorized'))

    @classmethod
    def general_report(cls, start_date, end_date, organisation):
        # Generate a CSV report
        filename = 'general_report_{0}.csv'.format(datetime.now().isoformat())
        helpers.generate_general_report(filename, start_date, end_date, organisation)

        return cls.download_csv(filename)

    @classmethod
    def download_csv(cls, filename):
        fh = open('/tmp/' + filename)

        response.headers[b'Content-Type'] = b'text/csv; charset=utf-8'
        response.headers[b'Content-Disposition'] = b"attachment;filename=%s" % filename

        return fh.read()

    def reports(self):
        self.check_user_access()
        vars = {}

        return base.render('user/reports.html',
                           extra_vars=vars)

    def reports_general_year_month(self):
        self.check_user_access()

        year, month = helpers.get_year_month(
            toolkit.request.GET.get('report_date_year', None),
            toolkit.request.GET.get('report_date_month', None)
        )

        start_date, end_date = helpers.get_report_date_range(year, month)
        organisation = toolkit.request.GET.get('organisation', None)
        sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

        return self.general_report(start_date, end_date, organisation if sub_organisation == 'all-sub-organisations' else sub_organisation)

    def reports_general_date_range(self):
        self.check_user_access()

        start_date = toolkit.request.GET.get('report_date_from', None)
        end_date = toolkit.request.GET.get('report_date_to', None)
        organisation = toolkit.request.GET.get('organisation', None)
        sub_organisation = toolkit.request.GET.get('sub_organisation', 'all-sub-organisations')

        return self.general_report(start_date, end_date, organisation if sub_organisation == 'all-sub-organisations' else sub_organisation)

    def reports_sub_organisations(self):
        self.check_user_access()

        organisation_id = toolkit.request.GET.get('organisation_id', None)

        return json.dumps(helpers.get_organisation_node_tree(organisation_id))


class ReportScheduleController(base.BaseController):
    def _get_context(self):
        return {'model': model, 'session': model.Session,
                'user': c.user, 'auth_user_obj': c.userobj}

    def schedules(self):
        # TODO: Check user access
        #self.check_user_access()
        vars = {}

        return base.render('user/report_schedules.html',
                           extra_vars=vars)

    def create(self):
        vars = {}
        if request.method == 'POST':
            params = helpers.clean_params(request.POST)
            result = toolkit.get_action('report_schedule_create')(self._get_context(), params)
            from pprint import pprint
            pprint(result)
            # handle success
            if result is True:
                h.flash_success('Report schedule created')
                h.redirect_to('/dashboard/report-schedules')
            # handle errors
            elif result and result.get('errors', None):
                vars['data'] = params
                errors = result.get('errors', None)
                vars['errors'] = errors
                h.flash_error(str(errors))

        return base.render('user/report_schedules.html',
                           extra_vars=vars)

    def update(self, id):
        vars = {}
        if request.method == 'GET':
            if id and model.is_id(id):
                schedule = ReportSchedule.get(id)
                if schedule:
                    vars['data'] = schedule.as_dict()
        elif request.method == 'POST':
            params = helpers.clean_params(request.POST)
            params['id'] = id
            result = toolkit.get_action('report_schedule_update')(self._get_context(), params)
            if result is True:
                h.flash_success('Report schedule updated')
                h.redirect_to('/dashboard/report-schedules')

        return base.render('user/report_schedules.html',
                           extra_vars=vars)

    def delete(self, id=None):
        result = toolkit.get_action('report_schedule_delete')(self._get_context(), {'id': id})
        if result:
            h.flash_success('Report schedule deleted')
        else:
            h.flash_error('Error')
        h.redirect_to('/dashboard/report-schedules')
        # vars = {}
        # return base.render('user/report_schedules.html',
        #                    extra_vars=vars)

    def jobs(self, report_schedule_id=None):
        vars = {}

        schedule = ReportSchedule.get(report_schedule_id)
        if schedule:
            vars['schedule'] = schedule.as_dict()
            vars['jobs'] = toolkit.get_action('report_jobs')(self._get_context(), {'report_schedule_id': report_schedule_id})

        return base.render('user/report_jobs.html', extra_vars=vars)
