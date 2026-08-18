# RatioT SCADA

База знаний / выжимка

## Содержание

- [Введение](#intro)
- [Архитектура](#architecture)
- [Технологический стек](#stack)
- [Порты и протоколы](#ports)
- [Установка и развёртывание](#install)
- [Управление сервером](#run)
- [Основные сущности системы](#entities)
- [Подключение устройств по протоколам](#protocols)
- [Создание и настройка тегов / переменных](#tags)
- [Построение дашборда в Web UI Builder](#dashboards)
- [Историк и архивы](#historian)
- [Аварии и события](#alarms)
- [Пользователи, роли и права доступа](#users)
- [Резервное копирование и обновление](#backup)
- [API и интеграции](#api)
- [HMI / Web UI](#hmi)
- [Скрипты, SQL и выражения](#scripts)
- [Источники](#sources)
- [Пользовательский опыт](./ux) — отдельная страница

---

<a id="intro"></a>
## Введение

**RatioT SCADA** — серверная SCADA/HMI-платформа для сбора данных, визуализации и управления промышленными объектами.

Этот документ — краткая выжимка по официальным руководствам. Она поможет быстро понять, из чего состоит система, как её развернуть и куда копать дальше.

[Пользовательский опыт](./ux) — отдельная выжимка про вход, дашборды, binding, права доступа, аварии и типовые сценарии.

---

<a id="architecture"></a>
## Архитектура

### Компоненты системы

- **RatioT SCADA Server**
  Ядро системы. Работает как служба/демон, собирает данные, выполняет скрипты, хранит историю, отдаёт API и Web UI.

- **Web UI**
  Клиентская часть на React. Открывается в браузере Chrome/Firefox по HTTPS `8443` или HTTP `8080`.

- **Net Admin**
  Административный интерфейс на порту `6440`. Нужен для лицензирования, конфигурации, активации.

- **Historian / NoSQL**
  Встроенное хранилище на Apache Cassandra. Опционально можно подключить классические СУБД.

### Схема взаимодействия

```
[ PLC / RTU / Датчики ]
         │
         ▼
[ RatioT SCADA Server ] ◄──── API (6460) / Net Admin (6440)
   │ JVM Java 17       │      Web UI (8080/8443)
   │ Cassandra (NoSQL) │
   │ RDBMS (опц.)      │
         │
         ▼
[ Web UI / Dashboards / HMI ]
```

---

<a id="stack"></a>
## Технологический стек

| Компонент | Технология |
|-----------|------------|
| Сервер | Java 17 (JVM) |
| NoSQL-хранилище | Apache Cassandra (встроенная) |
| Реляционные БД (опц.) | MySQL, PostgreSQL, Oracle, MS SQL Server, Firebird |
| Встроенные БД | H2 / Cassandra |
| Web UI | React |
| HMI-редактор | Web UI Builder, SVG, CSS, bindings |
| Скриптование | Java, R, Python, встроенные выражения |
| ОС сервера | Windows 7/10/11, Windows Server 2016/2019, Linux |

---

<a id="ports"></a>
## Порты и протоколы

| Порт | Назначение |
|------|------------|
| 6460 | Собственный API сервера |
| 6440 | Net Admin |
| 8080 | Web UI — HTTP |
| 8443 | Web UI — HTTPS |
| 162/UDP | SNMP-ловушки |
| 2055 | NetFlow |
| 6343 | sFlow |
| 514 | Syslog |
| 9042 | NoSQL (Cassandra) |
| 47808 | BACnet |
| 7800 | Heartbeat |
| 21 / 22 / 69 | FTP / SSH / TFTP |
| 389 | LDAP / Active Directory |
| 25 / 110 / 143 | SMTP / POP3 / IMAP |
| 1812 | RADIUS |
| 50000–60000 | Диапазон для вспомогательных соединений |

---

<a id="install"></a>
## Установка и развёртывание

### Требования

- Java 17 (JRE/JDK).
- 64-разрядная ОС Windows или Linux.
- Для NoSQL-историка желательны SSD и 12–16 ГБ RAM.
- На Linux установку и запуск рекомендуется выполнять под root или через sudoers.

### Дистрибутивы

- Windows: `RatioT_SCADA_full_6.34.07_windows-x64.exe`
- Linux: `RatioT_SCADA_full_6.34.07_unix-x64.sh`

### Варианты установки

1. **GUI:** запустить инсталлятор и пройти мастер.
2. **Тихая:**
   ```bash
   # Linux
   ./installer.sh -q -varfile response.varfile

   # Windows
   installer.exe -q -varfile response.varfile
   ```
3. **Вручную через response.varfile:** файл находится в `RatioT SCADA/.install4j/response.varfile`. После правки перезапустить установку.
4. **Docker:** собрать образ и запустить:
   ```bash
   docker build -t RatioT_SCADA .
   docker run RatioT_SCADA
   ```
   Внутри контейнера сервер стартует через `xvfb-run --auto-servernum ./ag_server -r`.

### Пути по умолчанию

| ОС | Путь |
|----|------|
| Linux | `/opt/RatioT SCADA` |
| Windows | `C:\Program Files\RatioT SCADA` |

### Лицензирование

1. Сгенерировать `activation.txt` через Net Admin.
2. Получить файл `server.license`.
3. Положить `server.license` в каталог сервера и перезапустить.

---

<a id="run"></a>
## Управление сервером

### Linux

```bash
# systemd
systemctl enable RatioT_SCADA.service
systemctl restart RatioT_SCADA.service
systemctl status RatioT_SCADA.service -l

# init-скрипт
service RatioT_SCADA_service start|stop|restart|status

# консоль
RatioT_SCADA_console
```

### Windows

- Служба запускается через `Services.msc`.
- Консоль: `RatioT_SCADA_console.exe`.

### Полезные флаги

| Флаг | Назначение |
|------|------------|
| `-a` | Режим администратора |
| `-e <file>` | Выполнить SQL-скрипт |
| `-s <file>` | Сохранить SQL-скрипт |
| `-c` | Консольный режим |
| `-u` | GUI-установщик |
| `-p <user> <pass>` | Авторизация |

---

<a id="entities"></a>
## Основные сущности системы

- **Проект (.prs)**
  Главный файл конфигурации SCADA. В него входят модели, устройства, теги, dashboards, скрипты.

- **Модель (Model)**
  Логическое описание объекта или устройства. Может включать параметры, состояния, подмодели.

- **Устройство (Device)**
  Источник данных: PLC, RTU, контроллер, виртуальный источник. Связывается с моделью.

- **Тег / переменная**
  Значение, приходящее с устройства или вычисляемое. Имеет тип, контекст, историю.

- **Historian**
  Подсистема хранения временных рядов. По умолчанию на Cassandra; можно использовать RRD.

- **Dashboard / HMI**
  Визуализация: формы, SVG-элементы, таблицы, диаграммы, динамические панели.

- **События и аварии**
  Журнал событий, SLA, уведомления по e-mail/SMS. Поддерживаются фильтры и подписки.

- **Пользователи и роли**
  Аутентификация и права доступа. Интеграция с LDAP/AD и RADIUS.

---

<a id="protocols"></a>
## Подключение устройств по протоколам

### Modbus

RatioT SCADA Server поддерживает Modbus TCP, Modbus UDP и Modbus Serial (RTU, ASCII, BIN). Драйвер расположен в `com.dkc.linkserver.plugin.device.modbus`.

1. Создайте устройство и выберите тип подключения: TCP/UDP или Serial.
2. Для TCP/UDP укажите IP-адрес сервера и порт (по умолчанию 502).
3. Для Serial задайте параметры COM-порта: Baud Rate, Data Bits, Stop Bits, Parity, RTS/CTS или XON/XOFF.
4. Укажите **Modbus Unit ID**. Для линии RS-485 один Unit ID используется на шине.
5. Добавьте переменные (теги) с типами регистров: Coil, Discrete Input, Input Register, Holding Register.
6. Для числовых регистров выберите формат данных: 2-Int/Unsigned, 4-Int/Unsigned/Swapped, 4-Float, 8-Int/Float, BCD и др.

> **Примечание:** для Modbus TCP используется IP-соединение; для Modbus Serial можно использовать serial-over-IP (преобразователь Ethernet/Serial).

### OPC UA

Драйвер OPC UA: `com.dkc.linkserver.plugin.device.opcua`. Поддерживается режим клиента и встроенный OPC UA Server.

1. В настройках устройства задайте URL сервера:
   ```
   connectionType://serverAddress:serverPort[/serverPath]
   ```
   где `connectionType` — `tcp` или `https`.
2. Выберите политику безопасности (Security Policy): Basic128Rsa15, Basic256, Basic256Rsa15, Basic256Sha256, Aes128_Sha256_RsaOaep, Aes256_Sha256_RsaOaep или None.
3. Выберите режим (Security Mode): Sign, SignAndEncrypt или None.
4. При необходимости включите SSL/TLS и укажите сертификаты.
5. Для импорта переменных используйте маску, например `*`, или задайте конкретный NodeId. Пример пути после импорта: `users/admin/devices/virtual/Waves/Random`.

> **Примечание:** RatioT SCADA также может выступать OPC UA Server (плагин `com.dkc.linkserver.plugin.device.opcua-server`). Настройте IP-интерфейс, TCP-порт и URL-адрес.

### MQTT

Драйвер MQTT: `com.dkc.linkserver.plugin.device.mqtt`. Работает по TCP/IP, поддерживает топики с разделителем `/`.

1. Создайте MQTT-устройство и выберите транспорт:
   - TCP — обычное TCP-соединение;
   - SSL/TLS — защищённое соединение;
   - WebSocket / Secure WebSocket — через WebSocket.
2. Укажите IP-адрес и порт брокера MQTT.
3. Настройте параметры сессии: **Client ID**, **Clean Session**, **Keep Alive** (по умолчанию 60 с).
4. Задайте QoS для публикации/подписки: 0 (at most once), 1 (at least once) или 2 (exactly once).
5. Добавьте элементы публикации (Publisher) и подписки (Subscriber): Topic, QoS, Retained, Message.
6. Сообщение может передаваться как строка (`message`) или как Data Block (`messageData`).

---

<a id="tags"></a>
## Создание и настройка тегов / переменных

### Структура переменной в модели устройства

Переменные (Variables) описываются в контексте устройства и имеют следующие основные поля:

- `name` — имя переменной;
- `format` — формат данных (String, Integer, Double, Data Table и др.);
- `description` — описание;
- `readable` — доступно для чтения;
- `writable` — доступно для записи;
- `group` — группа переменных;
- `iconId`, `helpId` — иконка и справка.

### Путь к переменной

Переменные адресуются через путь контекста. Примеры:

```
users.admin.devices.virtual:random
users.admin.devices.dev1:voltage
form/label1:text
events:get("users.admin.devices.virtual", "event1")
```

### Работа с переменными из выражений и скриптов

- Чтение: `{users.admin.devices.virtual:random}`
- Преобразование: `round(10 * {users.admin.devices.virtual:random})`
- Функции API: `getVariable(context, variable)`, `setVariable(...)`.

> **Примечание:** подробная пошаговая инструкция по созданию тегов через UI в исходных файлах не представлена явно; часть настроек выполняется автоматически при импорте устройства.

---

<a id="dashboards"></a>
## Построение дашборда в Web UI Builder

### Быстрый старт

1. Откройте Web UI Builder в Net Admin или по URL `https://<host>:8443/web`.
2. Создайте новую форму (Form). По умолчанию она получает имя, например `form`.
3. Перетащите на форму компоненты: Label, Button, LineChart, Data Table, SVG и др.
4. Для каждого компонента настройте свойства (Property) и привязку (Binding).

### Binding (привязка данных)

Свяжите свойство компонента с переменной сервера:

```xml
<!-- Пример: Label отображает переменную -->
{users.admin.devices.virtual:random}

<!-- Пример: преобразование значения -->
round(10 * {users.admin.devices.virtual:random})

<!-- Пример: привязка к свойству формы -->
form/label1:text

<!-- Пример: событие нажатия кнопки -->
form/button0:mouseClicked@
```

### Работа с CSS

Для компонента можно задать CSS-класс и стили:

```css
.my-label {
  font-size: 1.5em;
  margin-left: 20%;
}
.my-button {
  font-size: 1.5em;
}
```

### SVG-графика

1. Загрузите SVG-изображение, например `images>scada>control>fan.svg`.
2. Включите поддержку манипуляций SVG: свойство `svgManipulation` / "SVG Manipulation".
3. Привяжите SVG-элемент (например, `Fan`) к переменной: `form/Fan:state`.
4. Используйте условные выражения для визуализации состояния:
   ```
   {form/Fan:state} == "on" ? "off" : "on"
   {color} = {form/fan:state} == 'on' ? color(255,0,0) : color(0,255,0)
   ```

### Виджеты: LineChart и Data Table

Для построения графика:

1. Добавьте компонент **LineChart**.
2. Настройте Series: укажите имя поля строки (`string`) и значения (`int`).
3. Привяжите источник данных: `{users.admin.devices.virtual:table}`.

Для таблицы событий используйте функцию `events:get`:

```
subtable(
  {events:get("users.admin.devices.virtual", "event1")},
  "eCreationtime",
  "eLevel"
)
```

### Динамическое содержимое и шаблоны

Компонент Panel может формировать содержимое динамически:

```
table(
  "<<text><S><D=Text><F=N><M=1>>>",
  "First",
  "Second",
  "Third",
  "Button Clicked"
)
```

Пример привязки динамического источника:

```
form/panel0:dynamicContentsSource
```

Для повторяющихся элементов используйте `_clone_{#row}` и привязку к Data Table.

---

<a id="historian"></a>
## Историк и архивы

### Хранилище данных

RatioT SCADA использует два типа хранилища:

- **NoSQL (Apache Cassandra)** — основное хранилище истории, событий, данных.
- **RDBMS** — для конфигурации и внешних SQL-запросов: MySQL, PostgreSQL, Oracle, Microsoft SQL Server, Firebird.

### Ключевые таблицы в Cassandra

| Таблица | Назначение |
|---------|------------|
| ag_properties | Конфигурация и свойства |
| ag_events | События, аварии, журналы |
| ag_data | Данные, бинарные массивы |
| ag_alert | Информация об авариях |

### Настройка Cassandra

1. Установите Java 8 JDK 8.
2. Настройте `config/cassandra.yaml`: пути commitlog, seeds, listen_address, rpc_address.
3. Укажите IP Cassandra в `server.xml`:
   ```xml
   <databaseCassandraHost>your_cassandra_ip_address</databaseCassandraHost>
   ```
4. Задайте переменные окружения `JAVA_HOME` и `CASSANDRA_HOME`.
5. Запустите Cassandra: `bin/cassandra`.

### Работа с историей в выражениях

Пример получения статистики по энергопотреблению:

```sql
SELECT
  stats.statistics$context as "Device Context",
  stats.statistics$end as "Period",
  stats.statistics$average * 60 as "Average kW per hour"
FROM
  utilities:statistics("users.admin.devices.virtual", "energy_consumption", null, "hour") as stats
```

Пример запроса к истории переменной:

```
{utilities:variableHistory("users.admin.devices.meter", "temperature", "2012-05-03", ...)}
```

---

<a id="alarms"></a>
## Аварии и события

### Контекст аварий

Алармы располагаются в контексте пользователя. Примеры путей:

```
users.USER_NAME.alerts
users.*.alerts
users.admin.alerts
```

### Создание аварии (структура)

Основные поля определения аварии:

- `name`, `description`, `enabled`;
- `eventTriggers` — список триггеров по событиям (mask, event, filter, level, message);
- `variableTriggers` — триггеры по переменным (variable, filter, period, delay, level, deactivator, message);
- `notifications` — уведомления:
  - `notifyOwner` — уведомить владельца;
  - `ackRequired` — требуется квитирование;
  - `sound` — звуковое оповещение;
  - `mailToOwner`, `mailRecipients` — email;
  - `smsRecipients` — SMS.
- `escalation` — эскалация (pending, numberEscalation, numberThreshold, timeEscalation, timeThreshold);
- `alertActions` — действия при срабатывании.

### Фильтрация событий

Пример получения событий из раздела дашбордов:

```
{events:get("users.admin.devices.virtual", "event1")}
```

Пример фильтра по пользователю:

```
{events:get("users", "login", "{username} == 'john'")}
```

> **Примечание:** пошаговая инструкция по созданию аварий через Web UI Builder в исходных файлах присутствует частично (событие `event1`, `errorReport`). [нужно уточнить в мануале]

---

<a id="users"></a>
## Пользователи, роли и права доступа

### LDAP / Active Directory

RatioT SCADA поддерживает интеграцию с Microsoft Active Directory через LDAP (порт 389, LDAPs — 636).

1. В настройках аутентификации включите LDAP/Active Directory.
2. Укажите IP-адрес и порт LDAP-сервера.
3. Выберите режим привязки:
   - **Use RDN Prefix** — используется RDN (например, `DC=Lookup Domain`);
   - **Use Authentication User** — используется служебная учётная запись для поиска.
4. Настройте соответствие атрибута `primaryGroupID` ролям RatioT SCADA.
5. При необходимости включите SSL/TLS (LDAPs).

### RADIUS

Поддерживается аутентификация по протоколу RADIUS (RFC 2138, порт 1812).

1. Создайте профиль RADIUS (`radiusSettings`).
2. Укажите сервер RADIUS, порт и общий секрет.
3. RatioT SCADA отправляет `Access-Request`; при получении `Access-Accept` аутентификация считается успешной.
4. Для авторизации RADIUS можно комбинировать с LDAP.

### OAuth / SSO

Поддерживается OAuth 2.0 / OpenID Connect для Web UI. Провайдеры: Google Cloud, Microsoft Azure AD.

1. Зарегистрируйте приложение в провайдере и получите Client ID / Secret.
2. Настройте URL авторизации, токена и callback.
3. В RatioT SCADA укажите провайдера и перенаправление:
   ```
   /web?provider=provider_id
   ```

### Права доступа

Права задаются через поле `permissions` в определениях переменных, функций, событий, аварий и контекстов. Примеры контекстов:

```
users.*.alerts.*
users.admin.devices.*
users.admin.models.*
```

> **Примечание:** [нужно уточнить в мануале] детальное ролевое разграничение (создание ролей, назначение прав на UI-экраны) в исходных файлах описано фрагментарно.

---

<a id="backup"></a>
## Резервное копирование и обновление

### Резервное копирование

Перед обновлением и для архивирования рекомендуется сохранить:

- файл лицензии `server.license`;
- конфигурационный файл `server.xml`;
- каталоги `/statistics` и `/db`;
- резервную копию внешней RDBMS.

### Резервное копирование RDBMS

Примеры команд:

```bash
# PostgreSQL
pg_dump -U USER -W PASSWORD DATABASE > database.sql

# Восстановление PostgreSQL
psql -U USER -W PASSWORD DATABASE < database.sql

# MySQL
mysqldump -u USER -p PASSWORD --skip-lock-tables DATABASE > database.sql

# Копирование только таблиц RatioT SCADA
mysqldump -u USER -p PASSWORD --skip-lock-tables DATABASE \
  ag_properties ag_events ag_data ag_alert > MySQL.sql
```

### Обновление RatioT SCADA Server

1. Сохраните лицензию и конфигурацию.
2. Остановите RatioT SCADA Server.
3. Сделайте резервную копию каталогов `/db` и `/statistics`.
4. Удалите старую версию (для Linux — запустить `uninstall`).
5. Установите новую версию RatioT SCADA Server.
6. Восстановите конфигурацию и лицензию.
7. Запустите сервер и проверьте работу.

---

<a id="api"></a>
## API и интеграции

### REST API

REST API работает по HTTP/HTTPS и использует JSON.

- Базовый URL HTTPS: `https://localhost:8443/rest/{request}`
- Базовый URL HTTP: `http://localhost:8080/rest/{request}`
- Поддерживаются методы: GET, POST, PUT, PATCH.
- Авторизация по токену: `Authorization: Bearer <token>`

Пример запроса контекста:

```
GET https://localhost:8443/rest/v1/contexts/users.admin.devices.virtual
```

### Java API

Java API позволяет подключаться к RatioT SCADA Server по TCP-порту 6460.

```java
RemoteLinkServer rls =
  new RemoteLinkServer("localhost", RemoteLinkServer.DEFAULT_PORT, "admin", "admin");
RemoteLinkServerController rlc = new RemoteLinkServerController(rls, true);
rlc.connect();
rlc.login();
ContextManager cm = rlc.getContextManager();
```

Основные операции: `getVariable()`, `setVariable()`, `callFunction()`, `addEventListener()`.

### SQL-запросы

В выражениях Web UI и скриптах можно выполнять SQL через функцию `executeQuery`:

```
{users.admin.devices.linkserver_database:executeQuery(
  "SELECT * FROM logins WHERE username = 'john'")}
```

Использование источника событий как таблицы:

```
{:executeQuery("SELECT * FROM events:get('users', 'login') as logins
  WHERE logins.get$username = 'john'")}
```

### Скрипты Python

Python-скрипты выполняются через JEP (Java Embedded Python). Поддерживаются Python 3.5 / 3.6 и выше.

1. Установите Python, Visual C++ Redistributable (Windows), Pip, Pandas, JEP:
   ```bash
   pip install pandas
   pip install jep
   ```
2. Настройте переменные окружения `PYTHONHOME` и пути к библиотекам JEP.
3. Для обмена данными используйте `dataSetDataFrameInput` и `dataSetDataFrameOutput` (тип `pandas.DataFrame`).

```python
import pandas
dataSetDataFrameInput  # pandas.DataFrame на входе
df = pandas.DataFrame(...)
dataSetDataFrameOutput = df
```

### Скрипты R

R-скрипты выполняются через JRI. Используются переменные `dataSetMatrixInput` и `dataSetMatrixOutput`.

```r
dataSetMatrixInput  # Matrix на входе
dp = double(5)
dp[1] = 1
dp[2] = 2
strs = c("str1", "str2", "str3")
rMatrix = matrix(list(), nrow = 1, ncol = 2)
rMatrix[[1,1]] = dp
rMatrix[[1,2]] = strs
colnames(rMatrix) = c("numericField", "characterField")
dataSetMatrixOutput = rMatrix
```

---

<a id="hmi"></a>
## HMI / Web UI

### Как открыть

- Стартовый URL по умолчанию: `https://<host>:8443/web` или `http://<host>:8080/web`.
- Поддерживаемые браузеры: Google Chrome, Mozilla Firefox.
- Учётная запись по умолчанию: `admin/admin`.

### Web UI Builder

Редактор мнемосхем работает в браузере. Основные инструменты:

- **Формы и виджеты** — label, button, chart, table, panel.
- **SVG-графика** — встроенная библиотека `svgManipulation`; можно вставлять свои SVG.
- **Binding** — связывание свойств виджетов с тегами через выражения вида `{users.admin.devices.virtual:random}`.
- **CSS** — стилизация элементов через обычный CSS.
- **Динамические панели** — генерация содержимого из таблиц/списков.

### Пример binding

```
// Отображение значения
{users.admin.devices.virtual:random}

// Масштабирование и округление
round(10 * {users.admin.devices.virtual:random})

// Условие для цвета
{form/fan:state} == 'on' ? color(255,0,0) : color(0,255,0)
```

---

<a id="scripts"></a>
## Скрипты, SQL и выражения

- **Встроенные выражения** — используются в binding и событиях виджетов.
- **Java** — можно писать сложную логику и расширения.
- **R** и **Python** — поддерживаются для аналитики и обработки данных.
- **SQL** — встроенные запросы к данным системы и внешним БД.

### Пример SQL-запроса к событиям

```sql
SELECT *
FROM events:get('users', 'login') as logins
WHERE logins.get$username = 'john'
```

### Пример executeQuery во внешней БД

```
{users.admin.devices.linkserver_database:executeQuery(
  "SELECT * FROM logins WHERE username = 'john'"
)}
```

---

<a id="sources"></a>
## Источники

- PDF: Руководство по развёртыванию RatioT SCADA (98 стр.)
- PDF: Руководство по эксплуатации RatioT SCADA (2849 стр.)

---

Собрано из официальной документации RatioT SCADA. Последнее обновление: август 2026.
