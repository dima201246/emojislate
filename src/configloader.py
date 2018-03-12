import os
import configparser

## @defgroup configparser Управление конфигурациями
#  @{
# @brief Модуль с базовыми классами, которые умеют работать с конфигурациями
# 
# Принцип работы класса INIConfigLoader
# 1. Поиск файла конфигурации по имени без расширения
# 2. Ищем сперва кастомную конфигурацию (<filename>.<ext>
# 3. Если её нет - обращаемся к default (<filename>.default.<ext>)
# 4. Если нет default - ошибка поиска значения по ключу
#
# Принцип: кастомная конфигурация только переопределяет
# стандартную (только те ключи которые совпадают)
#
# Обязательное требование: 
# - бот **обязательно** должен 
# работать в default конфигурации
#
# Дополнительные требования: 
# - пока это модуль для работы с INI
# - без лишних сложностей
"""
              ------------------------------------      
              | Расширение под конкретный проект |
              ------------------------------------      
                                |
                                v
 ---------------------------------------------------------------------
 |Общее для всех ядро подгрузки конфигурации - класс INIConfigLoader |
 ---------------------------------------------------------------------
"""


## @brief Класс работы с INI конфигурациями
#
# На данном классе могут основываться различные расширения
# для остальных проектов. 
class INIConfigLoader(object):

    def __init__(self, configs_path: str, 
                 config_ext='.ini', default_ext='.default'):

        assert(configs_path[-1] != os.path.sep)

        self.__configs_path = configs_path
        self.__parsers = {}

        self.config_ext = config_ext
        self.default_ext = default_ext


    def _get_parser(self, config_path):
        parser = self.__parsers.get(config_path)

        if not parser:
            parser = configparser.ConfigParser()
            parser.read(config_path, encoding="utf-8")
            self.__parsers[config_path] = parser

        return parser

    
    ## Поиск пользовательской конфигурации по имени без расширения
    #  @param config_file_name имя файла конфигурации 
    #                            без расширении
    def _find_ini_custom(self, config_file_name): 

        file_name_base = self.__configs_path + os.path.sep + \
                config_file_name

        custom_path = file_name_base + self.config_ext

        if os.path.isfile(custom_path):
            return custom_path

        else:
            # Файл конфигурации не найден
            return None


    ## Поиск стандартной конфигурации по имени без расширения
    #  @param config_file_name имя файла конфигурации 
    #                            без расширении
    def _find_ini_default(self, config_file_name):

        file_name_base = self.__configs_path + os.path.sep + \
                config_file_name

        default_path = file_name_base + self.default_ext + self.config_ext

        if os.path.isfile(default_path):
            return default_path

        else:
            # Файл конфигурации не найден
            return None


    ## @param config_path путь до файла конфигурации
    #  @param section секция в ini конфигурации
    #  @param key ключе в секции ini конфигурации
    def _find_ini_value(self, config_path, section, key):

        parser = self._get_parser(config_path)

        try:
            return parser.get(section, key)

        except (configparser.NoOptionError, configparser.NoSectionError):
            return None

    ## @brief Данный метод возвращает словарь ключ-значение
    # секции из файла конфигурации
    #
    # @param config_path путь до фоайла конфигурации
    # @param section секция в ini конфигурации
    # @return словарь ключ-значение для данной секции или пустой словарь
    def _get_ini_section(self, config_path, section):

        parser = self._get_parser(config_path)

        if parser.has_section(section):
            return dict(parser[section].items())

        return dict()


    ## @param config_file_name название файла конфигурации без расширения
    #  @param section название секции в ini файле
    #  @param key ключ в section
    #  @return значение ключа в файле конфигурации
    def get_value(self, config_file_name, section, key):
        assert(isinstance(config_file_name, str))
        assert(isinstance(section, str))
        assert(isinstance(key, str))

        default_conf = self._find_ini_default(config_file_name)
        custom_conf = self._find_ini_custom(config_file_name)

        if custom_conf:
            value = self._find_ini_value(custom_conf, section, key)
            if not value and default_conf:
                value = self._find_ini_value(default_conf, section, key)

        elif default_conf:
            value = self._find_ini_value(default_conf, section, key)

        else:
            value = None

        if not value:
            if not default_conf:
                raise ConfigError(
                        'Default ini configuration file "{}" not found!'\
                            .format(config_file_name))

            raise ConfigError(
                    'Value for key "{}" in section "{}" not found'
                    ' in ini configuration "{}"!'\
                        .format(key, section, config_file_name))

        return value


    ## @brief Получение секции в конфигурационном файле в виде
    #         словаря ключ-значение
    #
    #  @param config_file_name - название файла конфигурации без расширения
    #  @param section название секции в ini файле
    #  @return словарь ключ-значение для заданной секции
    def get_section_values(self, config_file_name, section):
        assert(isinstance(config_file_name, str))
        assert(isinstance(section, str))

        default_conf = self._find_ini_default(config_file_name)
        custom_conf = self._find_ini_custom(config_file_name)

        result = {}

        if default_conf:
            result.update(self._get_ini_section(default_conf, section))

        if custom_conf:
            result.update(self._get_ini_section(custom_conf, section))

        if not result:
            if not default_conf:
                raise ConfigError(
                        'Default ini configuration file "{}" not found!'\
                            .format(config_file_name))

            raise ConfigError(
                    'Section "{}" not found'
                    ' in ini configuration "{}"!'\
                        .format(section, config_file_name))

        return result


class ConfigError(Exception):
    pass

## @}

if __name__ == '__main__':
    import IPython

    IPython.embed()
