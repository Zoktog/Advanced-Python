Log Analyzer
============

Запуск скрипта:
---------------

* конфигурация по умолчанию

    :code:`python log_analyzer.py`

* использование конфигурации из файла config_file.py

    :code:`python log_analyzer.py --config config_file.py`

* использование конфигурации из директории ./CONFIG_DIR/, с именем config.py по умолчанию

    :code:`python log_analyzer.py --config ./CONFIG_DIR/`

* использование конфигурации config-second.py из директории ./CONFIG_DIR/

     :code:`python log_analyzer.py --config ./CONFIG_DIR/config-second.py`

Конфигурация по умолчанию
-------------------------

.. code:: Python

    config = {
        "REPORT_SIZE": 1000, # В отчет попадает REPORT_SIZE URL'ов с наибольшим суммарным временем обработки (time_sum)
        "REPORT_DIR": "./reports",  # Расположение отчетов
        "REPORT_NAME": "report-{}.html", # Шаблон имени, результирующего отчета
        "REPORT_TEMPLATE": "report.html", # Шаблон отчета
        "MAX_PERCENT_ERRORS": 30, # Допустимое кол-во ошибок (пропуска строк)
        "LOG_DIR": "./logs", # Расположение логов на обработку
        "ROUND_NUMBER": 3, # Число округления чисел
        "LOGGING_FORMAT": "[%(asctime)s] %(levelname).1s %(message)s", # Формать  вывода логов
        "LOGGING_LEVEL": "INFO", # Уровень логирования
        "LOG_FILE": None,   # Файл для логирования, по умолчанию в stdout
        "LOGGING_DATA_FORMAT": "%Y.%m.%d %H:%M:%S" # Формат времени logging
    }




Файл конфигурации может содержать частичную информацию, т.е хранить изменения только необходимых параметров.

Например: *config_file.py*

.. code:: Python

  config = { "LOG_DIR": "./log" }
..

Внесет изменения только касательно LOG_DIR, все остальные параметры останутся по умолчанию.

Тестирование
------------

    :code:`python test_log_analyzer.py -v`
