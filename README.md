# ZEMI Component

Все действия ниже выполняйте в VS Code, открытом для workspace текущего
ZEMI Instance.

## 1. Создайте компонент

Откройте встроенный терминал VS Code и выполните:

```powershell
zemi component create my_component
```

Команда создаст новый ZEMI Component из этого шаблона и добавит его в текущий
workspace. Если VS Code запросит доверие к добавленному каталогу, подтвердите
его. Затем откройте встроенный терминал для созданного компонента или перейдите
в его каталог:

```powershell
cd my_component
```

## 2. Инициализируйте Python venv

Откройте `00_init.py` и нажмите **Run Python File** в правом верхнем углу
редактора. Тот же скрипт можно запустить во встроенном терминале VS Code:

```powershell
python 00_init.py
```

`00_init.toml` декларативно описывает C-bundle компонента, а `00_init.py`
создаёт или актуализирует Python venv, устанавливает Z-bundle и C-bundle,
фиксирует их состояние, проверяет окружение и настраивает интерпретатор VS Code.

Чтобы подключить собственные Python-библиотеки:

1. Укажите версию C-bundle в `REQUIRED_C_BUNDLE_VERSION` в `00_init.toml`.
2. Добавьте пакеты компонента в список `C_BUNDLE_PACKAGES`, например:

   ```toml
   REQUIRED_C_BUNDLE_VERSION = "mycomp260816"
   C_BUNDLE_PACKAGES = [
       "requests==2.32.4",
       "openpyxl==3.1.5",
   ]
   ```

3. Из корня компонента запустите `python 00_init.py`.
4. Убедитесь, что инициализация завершилась успешно, включая итоговую проверку
   Python venv и штампов Z-bundle и C-bundle.

`00_init.py` предназначен не только для установки библиотек. При необходимости
он может выполнять другие операции первоначальной подготовки компонента:
запускать установочные скрипты через `venv.run_script("@comp/install.py")`,
генерировать конфигурацию, подготавливать каталоги и ресурсы, проверять
окружение и выполнять другие необходимые компоненту операции. Дополнительные
операции размещайте до `venv.finalize_install()` и итогового `venv.verify()`.

## 3. Проверьте playbook

Откройте `playbook.ipynb` в VS Code и выполните все ячейки. Если VS Code
предложит выбрать kernel, выберите Python-интерпретатор, настроенный на
предыдущем шаге. Убедитесь, что notebook выполняется без ошибок.

## 4. Начинайте разработку

Добавляйте код, notebooks, данные и настройки своего компонента. При изменении
пакетов или установочного кода измените RunID в `REQUIRED_C_BUNDLE_VERSION`.

Сам импорт `zemi` не проверяет окружение. Любой пользовательский код после
импорта обязан получить среду через `PythonVenv.from_config()` и вызвать
`verify()`. Использовать функциональность ZEMI можно только после успешной
проверки.

## Библиотечные интеграции Arsenal

Каждый ассистент предоставляет десять ленивых интеграций. Последнее имя пути
явно обозначает возвращаемую сущность:

```python
assistant.clients.openai.client
assistant.clients.litellm.router
assistant.clients.dspy.model
assistant.clients.instructor.client
assistant.clients.pydantic_ai.model
assistant.clients.smolagents.model
assistant.clients.llama_index.model
assistant.clients.httpx.client
assistant.clients.outlines.model
assistant.clients.guidance.model
```

Объект создаётся при первом обращении и затем кэшируется. Низкоуровневые
`openai.client` и `httpx.client` передают параметры llama.cpp, включая
`grammar` и `json_schema`, без фильтрации библиотекой Arsenal.
