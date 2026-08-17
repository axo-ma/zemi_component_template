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

Скрипт создаст или проверит Python venv для работы с компонентом, установит
необходимые библиотеки ZEMI и обновит `python.defaultInterpreterPath` и
`python.terminal.activateEnvironment` в настройках проекта так, чтобы VS Code
использовал созданную среду.

Если компоненту нужны собственные пакеты, настройте C-bundle в `00_init.toml`.
Для редкого дополнительного установочного кода используйте закомментированный
вызов `venv.run_script()` в `00_init.py`.

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
