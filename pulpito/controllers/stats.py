from collections import OrderedDict
from pecan import conf, expose, redirect
from pulpito.controllers import error
import requests

base_url = conf.paddles_address


class NodeStatsController(object):
    @expose('node_stats_jobs.html')
    def jobs(self, machine_type=None, since_days=14):
        uri = '{base}/nodes/job_stats?since_days={days}'.format(
            base=base_url,
            days=since_days)
        if machine_type:
            uri += '&machine_type=%s' % machine_type

        resp = requests.get(uri, timeout=60)
        if resp.status_code == 502:
            redirect('/errors?status_code={status}&message={msg}'.format(
                status=200, msg='502 gateway error :('),
                internal=True)
        elif resp.status_code == 400:
            error('/errors/invalid/', msg=resp.text)

        nodes = resp.json()
        statuses = ['pass', 'fail', 'dead', 'unknown', 'running']
        for name in nodes.keys():
            node = nodes[name]
            total = sum(node.values())
            node['total'] = total
            for status in statuses:
                if node.get(status) is None:
                    node[status] = 0
        nodes = OrderedDict(
            sorted(nodes.items(), key=lambda t: t[1]['total'], reverse=True))
        title_templ = "{days}-day stats for {mtype} nodes"
        title = title_templ.format(days=since_days,
                                   mtype=(machine_type or 'all'))
        return dict(
            title=title,
            nodes=nodes,
            count=len(nodes),
        )


class StatsController(object):
    nodes = NodeStatsController()
