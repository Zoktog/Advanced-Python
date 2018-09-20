import sys
import os
import re
import json
import gzip

import logging
import argparse

from statistics import median


def get_config(path):
    config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "./reports",
        "REPORT_NAME": "report-{}.html",
        "REPORT_TEMPLATE": "report.html",
        "MAX_ERRORS": 30,
        "LOG_DIR": "./logs",
        "ROUND_NUMBER": 3,
        "LOGGING_FORMAT": "[%(asctime)s] %(levelname).1s %(message)s",
        "LOGGING_LEVEL": "INFO",
        "LOG_FILE": None,
        "LOGGING_DATA_FORMAT": "%Y.%m.%d %H:%M:%S"
    }
    if path:
        custom_config = import_config_file(path)
        config.update(custom_config)
    return config


def import_config_file(config_path):  # /path/to/file
    default_cfg_filename = 'default.py'
    config_path = config_path.config
    if config_path:
        if os.path.isfile(config_path):
            path = config_path
        elif os.path.isdir(config_path):
            path = os.path.join(config_path, default_cfg_filename)
        else:
            logging.error(f'File not found: {config_path}')
            sys.exit(0)

        with open(path, 'r') as custom_config:
            try:
                cfg = json.load(custom_config)
                logging.info(f'Import custom env : {cfg}')
                return cfg
            except:
                logging.error(f"Can't use config file: {paht}")
                sys.exit(0)
    else:
        return {}


def parse_arg():
    description = "parse Nginx log and create report html."
    parser = argparse.ArgumentParser(description=description)
    help_description = 'path to config. (by default name "config.py")'
    parser.add_argument('-c', '--config', help=help_description)
    return parser.parse_args()


def find_log_in_dir(cfg):
    try:
        files = [f for f in os.listdir(cfg['LOG_DIR']) if re.match(r'nginx-access-ui.log-\d{8}.(gz|log)', f)]

        v = sorted(files, key=lambda x: re.findall('\d{8}', x), reverse=True)
        if len(v) is not len(set(v)):
            logging.warning('ERORR: several files names of the same')
        abs_file_path = os.path.join(cfg['LOG_DIR'], v[0])
        return abs_file_path
    except:
        logging.exception("Can't find the last log file in the dir")
        sys.exit(0)


def parse_line(line):
    re_obj = re.compile(r'\s+'.join([
        r'(?P<remote_addr>\S+)',  # $remote_addr
        r'(?P<remote_user>\S+)',  # $remote_user
        r'(?P<http_x_real_ip>\S+)',  # $http_x_real_ip
        r'(?P<time_local>\[.+\])',  # [$time_local]
        r'"\S+\s(?P<request_url>\S+)\s\S+"',  # "$request"
        r'(?P<status>\S+)',  # $status
        r'(?P<body_bytes_sent>\S+)',  # $body_bytes_sent
        r'"(?P<http_referer>.+)"',  # "$http_referer"
        r'"(?P<http_user_agent>.+)"',  # "$http_user_agent"
        r'"(?P<http_x_forwarded_for>.+)"',  # "$http_x_forwarded_for"
        r'"(?P<http_x_request_id>.+)"',  # "$http_X_REQUEST_ID"
        r'"(?P<http_x_rb_user>.+)"',  # "$http_X_RB_USER"
        r'(?P<request_time>\S+)',  # $request_time
    ]))

    return re_obj.match(line)


def read_line(log_path, cfg):
    report = {
        'count_all': 0,
        'time_sum_all': 0}

    with gzip.open(log_path, 'r') if log_path.endswith(".gz") else open(log_path) as file:
        line_number = 0
        errors_line = 0
        for line in file:
            line_object = parse_line(line)
            if line_object:
                r_url = line_object.group('request_url')
                line_number += 1
                logging.debug(f' line_number: {line_number} url: {r_url}')
                if report.get(r_url):
                    report[r_url], report['count_all'], report['time_sum_all'] = \
                        calculate_report(report[r_url], report['count_all'], report['time_sum_all'], line_object, cfg)

                else:
                    r_url_params = {
                        'count': 0,
                        'count_perc': 0,
                        'time_perc': 0,
                        'time_avg': 0,
                        'time_max': 0,
                        'time_med': 0,
                        'time_sum': 0,
                        'time_list': []}
                    report[r_url], report['count_all'], report['time_sum_all'] = \
                        calculate_report(r_url_params, report['count_all'], report['time_sum_all'], line_object, cfg)
            else:
                errors_line += 1
                logging.warning(f'ERORR: {errors_line}\t LINE: {line}')
                if errors_line > cfg['MAX_ERRORS']:
                    logging.error('The Errors > MAX_ERRORS')
                    sys.exit(0)
        del report['count_all']
        del report['time_sum_all']

        report_sort = sorted(report.items(), key=lambda x: x[1]['time_sum'], reverse=True)
        report = dict(report_sort[:cfg['REPORT_SIZE']])

        # dirty
        res = []
        for key, value in report.items():
            _d = {}
            _d['url'] = key
            del value['time_list']
            for k, v in value.items():
                _d[k] = v
            res.append(_d)

        return res


def calculate_report(r_url_params, r_count, r_time, line_object, cfg):
    r_count += 1
    r_time += round(float(line_object.group('request_time')), cfg['ROUND_NUMBER'])

    r_url_params['count'] += 1
    r_url_params['time_list'].append(float(line_object.group('request_time')))
    r_url_params['count_perc'] = round((float(r_url_params['count'])) * 100 / float(r_count), cfg['ROUND_NUMBER'])
    r_url_params['time_perc'] = round((float(line_object.group('request_time'))) * 100 / float(r_time),
                                      cfg['ROUND_NUMBER'])
    r_url_params['time_sum'] = round(sum(r_url_params['time_list']), cfg['ROUND_NUMBER'])
    r_url_params['time_avg'] = round(r_url_params['time_sum'] / r_url_params['count'], cfg['ROUND_NUMBER'])
    r_url_params['time_max'] = round(max(r_url_params['time_list']), cfg['ROUND_NUMBER'])
    r_url_params['time_med'] = round(median(r_url_params['time_list']), cfg['ROUND_NUMBER'])
    return r_url_params, r_count, r_time


def export_report_to_html(report, cfg, date_report):
    template_html = os.path.join(cfg['REPORT_DIR'], cfg['REPORT_TEMPLATE'])
    report_name = cfg['REPORT_NAME'].replace('{}', date_report)
    report_html = os.path.join(cfg['REPORT_DIR'], report_name)
    with open(template_html, "rt") as template_html:
        with open(report_html, "wt") as report_html:
            for line in template_html:
                report_html.write(line.replace('$table_json', json.dumps(report)))


def main():
    path_config = parse_arg()
    config = get_config(path_config)
    try:
        logging.basicConfig(filename=config["LOG_FILE"],
                            format=config["LOGGING_FORMAT"],
                            datefmt=config["LOGGING_DATA_FORMAT"],
                            level=config['LOGGING_LEVEL'])

        log_path = find_log_in_dir(config)
        date_report = re.search('\d{8}', log_path).group(0)
        logging.info(f'Start analysis log {log_path}')
        json_report = read_line(log_path, config)
        logging.info('End analysis and export report')
        export_report_to_html(json_report, config, date_report)

    except:
        logging.exception("We have a problem")
        sys.exit(0)


if __name__ == "__main__":
    main()
