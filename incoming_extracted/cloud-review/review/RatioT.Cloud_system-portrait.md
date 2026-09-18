# RatioT.Cloud — системный портрет



Дата актуализации: 2026-09-13 v019  
Статус: **BASELINE — содержательный портрет закрыт после финального аудита исходников**

> Этот файл собирает принятые решения в одном месте, чтобы продолжение работы не зависело от контекста чата. Он не заменяет журнал `decisions.md`, а даёт цельный портрет будущего ФТТ.

## 1. Назначение проекта и документа

- RatioT.Cloud — мультиарендная Cloud Mini-SCADA / IIoT-платформа на backend Tibbo AggreGate Server.
- ФТТ сначала передаётся владельцу продукта для заполнения недостающих исходных данных, затем подрядчику для **бюджетной оценки полного проекта**.
- После бюджетной оценки Заказчик и подрядчик совместно разрабатывают детальное ТЗ, включая UX/UI.
- Backend строится на AggreGate. Frontend — отдельный адаптивный web-клиент; конкретный стек выбирает подрядчик.
- На этапе ТЗ обязателен формальный frontend/backend contract, пригодный для независимой frontend-разработки на mock backend.
- Web frontend и внешние пользовательские приложения используют документированный Application/REST API поверх той же backend-бизнес-логики и общего RBAC/entitlement.
- Исходное требование «REST-API на работу с дашбордами» закрывается этим общим Application API: Dashboard/configuration operations должны быть доступны программно с той же authentication/RBAC/business logic; отдельная параллельная подсистема Dashboard API не требуется.
- Нативные Android/iOS-приложения в текущий проект не входят.

## 2. Обязательные исходные данные от владельца продукта до бюджетной оценки

Перед передачей ФТТ подрядчику владелец продукта должен заполнить отдельный начальный раздел. Детальный шаблон вынесен в `product-inputs_v003.md`.

Минимально требуется:

1. **Перечень конкретных SKU первой очереди.** Не классы «контроллер Mitra» или «счётчик Modbus», а точные модели. Для каждого SKU: протокол, роль в MVP, необходимость System Device Template, Visual Template, предоставление реального образца и документации.
2. **MQTT-профиль стороннего оборудования.** Указать конкретное устройство/SKU и документацию его MQTT-протокола, по которому подрядчик реализует пользовательский MQTT-профиль первой версии. Внутренний MQTT транспорт Gateway↔Cloud к этому профилю не относится.
3. **Gateway scope.** Подтвердить, что в текущий проект входит PC Gateway PoC, а Store-and-Forward, embedded-agent для ПЛК/панелей и аппаратные Gateway либо входят отдельно, либо относятся к LATER. Текущая рекомендуемая граница: PC PoC — IN; остальное — LATER.

Количество и состав SKU после согласования бюджетной оценки считаются базой scope; добавление новых SKU — изменение объёма работ.

## 3. Базовая информационная модель

### 3.1 Space и Asset

- `Space` — tenant и основная граница пользовательских данных, прав и эксплуатационного состояния.
- Space одновременно является безусловно существующим корневым `Asset`.
- Asset — универсальный вспомогательный узел произвольной иерархии для размещения, инвентаризации, поиска, фильтрации и наследования ACL. Типы «цех/этаж/комната» в модель не зашиваются. Иерархия должна без специальных ограничений поддерживать как минимум 10 уровней вложенности.
- Device может принадлежать любому Asset либо непосредственно корневому Space.
- Параметры принадлежат Device и отдельно к Asset не прикрепляются.
- На Asset и Device поддерживаются простые произвольные пользовательские метки/теги (`#Отопление`, `#Критично` и т.п.) для поиска и фильтрации. Сложный классификатор/таксономия не требуется.
- Asset и Device могут иметь необязательные координаты `latitude/longitude` и текстовое описание/адрес места установки. Геокодинг и сложная адресная модель в первую версию не входят.
- Dashboard принадлежит Space, но не является дочерним Asset и может использовать разрешённые данные любых Devices Space.

### 3.2 Пользователь

- Одна обычная учётная запись может состоять в нескольких Space, включая Space, размещённые на разных физических узлах одной логической инсталляции.
- Owner — специальное свойство Space, а не обычная группа.

## 4. Библиотеки, Device Templates и профили сопряжения

### 4.1 Библиотеки первого релиза

Отдельные библиотечные сущности первого релиза:

- **Заготовки устройств / Device Templates** — System Library, Space Library, User Library.
- **Visual Templates** — System Library, Space Library, User Library.

System Library поставляется платформой/DKC. Space Library принадлежит Space независимо от конкретного сотрудника. User Library принадлежит account и доступна ему в разных Spaces.
Отдельные библиотеки Dashboard и Automation в первой версии не вводятся. Dashboard и Automation являются сущностями конкретного Space. Jasper-шаблоны отчётов являются частью поставки, а не пользовательской библиотекой.

### 4.2 Заготовка устройства

- Отдельная видимая пользователю сущность «Функциональная модель устройства» не вводится.
- Пользователь работает с `Заготовкой устройства` и конкретным `Device`.
- Заготовка содержит смысловые параметры/команды, значения по умолчанию, профиль сопряжения и профильные настройки; может содержать типовые Alarm Rules.
- Метаданные параметра включают тип данных, единицу измерения, read/write, необязательные инженерные границы `min/max` и расширяемые атрибуты. Инженерные границы не являются Alarm limits.
- Настройки могут быть фиксированными, иметь default с возможностью изменения либо быть обязательными к вводу при создании экземпляра.
- Стабильные внутренние semantic ID позволяют менять display name без разрушения ссылок.
- Версии Заготовок неизменяемы; изменение создаёт новую версию. Старые экземпляры автоматически не мигрируют.
- Удаление Заготовки из библиотеки не должно ломать существующие Devices: версии, на которые есть ссылки, физически не уничтожаются, а переводятся в скрытое/архивное состояние.
- Совместимые изменения сохраняют смысловые привязки; несовместимые требуют ручного разрешения.
- Один экземпляр Device может сменить профиль сопряжения при сохранении смысловых ID, если пользователь заново задаст необходимый mapping/настройки.
- Поддерживается массовое создание/настройка однотипных Devices из Заготовки.
- Создание Device выполняется через универсальный Wizard, формируемый метаданными выбранной Заготовки и Профиля сопряжения; добавление нового SKU не должно требовать разработки отдельного мастера frontend.
- Импорт/экспорт Заготовок: обязательны документированный JSON и CSV. XML отдельно не требуется.
- Эксплуатационный Device напрямую между Spaces не переносится. Для тиражирования его конфигурацию сохраняют как Заготовку в подходящую библиотеку и создают новый Device в целевом Space; operational history старого Device не переезжает.
### 4.3 Профили сопряжения

- Профиль сопряжения — системное расширение, создаваемое разработчиками платформы; пользователь не программирует произвольный транспорт.
- Первый пользовательский конструктор ориентирован на Modbus и позволяет no-code описывать карту регистров/катушек, функции, типы, endian/word-swap/byte-swap, масштабирование, инженерные единицы и первичные преобразования Raw→Eng.
- Протокольные преобразования физического Device остаются в профиле/Заготовке и не должны переноситься в Automation.

### 4.4 Internal Space Store и вычисляемые параметры

- `Internal Space Store` — штатный профиль без внешнего транспорта; значения параметров постоянно хранятся в Space и переживают restart.
- При создании Space автоматически появляется видимый новичку Device типа «Переменные пространства» с примерно 10–15 примерными параметрами разных типов. Архив для них по умолчанию выключен.
- Параметр может иметь initial/default value и `Read Only`; это позволяет хранить понятные постоянные/конфигурационные значения Space.
- Отдельный тип/движок «вычисляемый параметр» **не создаётся**. Вычисляемые параметры реализуются связкой `Automation scenario + parameter of Virtual/Internal Device`.
- Пример: Automation читает `Meter1.P`, `Meter2.P`, `Meter3.P`, вычисляет `P_total` и пишет результат в `Переменные пространства.P_total`. После записи это обычный параметр: Dashboard, Archive, Alarm, API и другие Automation используют его без специальных связок.

## 5. Протоколы первой версии

### 5.1 Modbus

- В первую версию входят универсальные профили сопряжения **Modbus RTU** и **Modbus TCP**, которые реализуются один раз и применяются к множеству различных моделей оборудования.
- Конкретный SKU задаётся Заготовкой устройства: карта регистров/катушек, типы, семантика, scaling и команды; конкретный Device задаёт экземплярные настройки, например Slave/Unit ID, адрес/порт и доступные для изменения параметры.
- Обязательный protocol minimum: функции `01, 02, 03, 04, 05, 06, 15, 16`, типы данных, `Big-endian/Little-endian`, `word-swap/byte-swap`, масштабирование и преобразование Raw→Engineering value.
- Параметры одного Device могут иметь разные интервалы сбора/обновления, если профиль это допускает; для Modbus профиль должен позволять организовать разные polling groups/cycles, а не принуждать весь Device к одному периоду.
- Один физический Modbus-канал/Gateway может обслуживать несколько Devices с разными Slave ID и разными Заготовками.
- Пользователь работает именно с Modbus-профилем даже если физически RTU-устройство подключено через будущий Gateway; внутренний транспорт Gateway↔Cloud пользователю не показывается.

### 5.2 MQTT для стороннего устройства

- Пользовательский MQTT-профиль первой версии проектируется не абстрактно «для любого MQTT», а по конкретному SKU/протоколу, указанному владельцем продукта в начальном разделе ФТТ.
- Он является отдельной функцией от служебного MQTT-протокола Gateway↔Cloud.
- Поддержка Protobuf в пользовательском MQTT-профиле не является безусловным требованием: она включается в первую очередь только если протокол выбранного владельцем продукта MQTT-устройства этого требует. Внутренний Gateway-протокол первой версии остаётся человекочитаемым JSON.

### 5.3 OPC UA

Первая версия включает **OPC UA Client и OPC UA Server**.

Минимально обязательный Data Access scope:

- browse/address space;
- чтение;
- запись writable nodes;
- subscriptions / monitored items;
- согласованные типы данных;
- timestamps;
- quality/status;
- reconnect/recovery;
- согласованные на ТЗ security modes.

Не требуется в первой версии: OPC UA Methods, Historical Access, Alarms & Conditions; архив и аварии остаются собственными подсистемами RatioT.Cloud.

Разработка и приёмка проводятся на независимых программных эталонных OPC UA Client/Server, например на базе **open62541, UaExpert или эквивалентных инструментов**. OPC UA Client RatioT.Cloud проверяется независимым Server, OPC UA Server RatioT.Cloud — независимым Client. Проверка только «наш Client ↔ наш Server» недостаточна. Программный стенд и автоматические проверки должны войти в backend regression suite.

## 6. Gateway PoC и будущее Edge

### 6.1 Текущий проект

В текущий проект **не входят** производство аппаратных Gateway, заводской provisioning, factory reset, аппаратные изделия и embedded-agent в ПЛК/панель, если владелец продукта отдельно не расширит scope.

Подрядчик реализует `Cloud Gateway Agent` как PoC-программу для ПК/стандартной ОС:

- Modbus RTU Master через serial port;
- соединение с RatioT.Cloud по собственному MQTT-протоколу;
- получение эксплуатационной конфигурации из Cloud;
- постоянное и надёжное локальное хранение последней применённой конфигурации;
- периодическая проверка Cloud на наличие новой версии конфигурации;
- атомарное применение валидной конфигурации;
- передача телеметрии;
- получение команд из Cloud и передача их Modbus-устройству;
- результат/ошибка команды с correlation ID.

Для PoC допустим локальный bootstrap-конфиг только с адресом Cloud/broker, Gateway ID и credentials. Это способ запуска PoC, а не модель будущего серийного Gateway. Настройки serial/Modbus, polling, mapping регистров/катушек и иная эксплуатационная конфигурация должны приходить из Cloud.

### 6.2 Внутренний MQTT-протокол Gateway↔Cloud

- Это служебный транспорт платформы и обычному пользователю как профиль сопряжения не показывается.
- Первая версия ориентируется на MQTT over TLS и человекочитаемый формат, предпочтительно JSON.
- Протокол должен быть документированным, версионируемым, расширяемым и не ограничивать архитектуру одним Device на Gateway.
- Предусматриваются идентификаторы Gateway/Device/Parameter, source timestamp, quality, команды, ответы/ошибки, correlation ID и versioning.
- Каждый Gateway имеет индивидуальную аутентификацию и topic ACL. Общая учётная запись для всех шлюзов недопустима.
- Конкретный broker выбирает подрядчик. Желательно использовать возможности свободно распространяемых broker, например Dynamic Security/ACL Eclipse Mosquitto или эквивалент, не создавая отдельную самописную auth-подсистему.
- mTLS может быть развитием, но не является обязательным первым способом, если иное не определено ТЗ.

### 6.3 Будущее Edge

- CAN/CANopen/J1939 и иные CAN-протоколы в текущий Gateway PoC не входят; упоминание CAN в исходной концепции рассматривается как пример будущего локального адаптера.

Полноценный multi-device Edge Gateway, Store-and-Forward телеметрии, автономная логика, embedded-agent и производство аппаратных Gateway — LATER, если продукт не вернёт их в первую очередь. Архитектура Cloud и внутреннего протокола не должна мешать их добавлению.

Для будущих серийных Gateway допускается модель служебного Space «Склад» и последующей штатной передачи online Gateway клиентскому Space, но производственный provisioning в текущий контракт не входит.

## 7. Телеметрия, архив и экспорт

- Канонический контракт параметра RatioT.Cloud включает как минимум `value + data type + source timestamp + quality/status`; при необходимости для диагностики отдельно хранится `server/receive timestamp`.
- Нормализованный quality верхнего уровня должен различать как минимум `Good / Uncertain / Bad`, сохраняя возможность передать более подробный протокольный статус.
- Эта модель едина поверх Modbus, MQTT, OPC UA и будущих профилей сопряжения.
- Внутренние timestamps хранятся/передаются в UTC. Пользовательские журналы, тренды, события, отчёты и расписания отображаются и интерпретируются в timezone Space; UTC остаётся доступен в API/диагностике.
- Периодический сбор поддерживает интервалы примерно от 1 секунды до часов; конкретный профиль нагрузки определяется ТЗ.
- Поддерживаются event/on-change и deadband там, где это позволяет профиль.
- Для отдельного параметра архивирование должно поддерживать дискретность до **1 секунды**. Это не означает обязанность архивировать все параметры всех устройств с частотой 1 Hz одновременно.
- На один Space закладывается не менее **5000 параметров** как минимальная целевая ёмкость модели/обработки.
- Исторические агрегаты должны поддерживать минимум `Avg / Min / Max / Last` по типовым интервалам времени; способ предрасчёта/грануляции выбирается подрядчиком, желательно с использованием штатных механизмов AggreGate.
- Формулировка исходной концепции «сжатие и агрегация» не означает разработку собственного алгоритма compression. Эффективное хранение/сжатие обеспечивается штатными средствами AggreGate/выбранной СУБД; обязательная прикладная функция — агрегаты `Avg / Min / Max / Last`.
- Тренды используют архив/агрегаты, но Automation в первой версии прямого доступа к архиву не имеет.

### 7.1 Экспорт телеметрии

- CSV — прямой экспорт заголовков и данных без Jasper-шаблона.
- XLSX и PDF — через базовые JasperReports templates, подготовленные подрядчиком.
- Пользователь выбирает параметры и период; для больших объёмов допустима асинхронная подготовка файла.
- Отдельный proprietary «архивный dump RatioT.Cloud» для телеметрии не требуется.

## 8. Events, Alarms и Notifications

### 8.1 Events / Alarms

- Event — неизменяемый общесистемный факт; журнал append-only.
- Базовый Alarm lifecycle: `RAISED`, `CLEARED`, `ACKNOWLEDGED`; физическое состояние и acknowledgement независимы.
- Alarm Rule имеет настраиваемый признак `Acknowledgement required`. Если он включён, снятие физического аварийного условия не завершает операторский цикл до квитирования уполномоченным пользователем.
- Alarm и Automation используют единый Rule Engine внутри, но имеют разные UX.
- Alarm Rules поддерживают минимум TON, TOFF, hysteresis/deadband, debounce/anti-flapping/anti-flood.
- Severity: `Info / Warning / Alarm`.
- Alarm Rule может входить в Device Template; локальные overrides экземпляра не должны затираться обновлением template.
- `AcknowledgeAlarm` — отдельное RBAC permission.

### 8.2 Уведомления

Базовые каналы первой версии:

- Web/in-app Notification Center;
- Web Push;
- E-mail;
- Telegram;
- SMS.

MAX в первую версию не входит, но архитектура каналов должна позволять позже добавить новый adapter, **например уведомления через MAX**, без изменения Event/Alarm logic и routing.
Базовые каналы Web/in-app, Web Push, E-mail и Telegram не включаются/выключаются тарифом. SMS является отдельно лимитируемым ресурсом тарифа.

- Получатели задаются группами Space и/или настраиваемыми адресатами канала.
- Telegram должен поддерживать как персональную доставку, так и Telegram group chats для диспетчерских групп.
- Пользователь имеет личную матрицу `тип сообщения × канал` и может отключить внешние каналы.
- Notification Center хранит read/unread и ссылки на связанные alarms; ACK из него использует обычный механизм ACK.
- Каждая попытка доставки получает статус (`QUEUED/SENT/DELIVERED`, если транспорт позволяет, `FAILED`), retry и техническую диагностику.
- Автоматический cross-channel fallback не обязателен.
- При повторных отказах канала создаётся системное предупреждение/Event/Alarm.

## 9. Automation

- Automation — лёгкая SCADA-подобная No-Code автоматизация, не SoftPLC и не durable workflow engine.
- Alarm и Automation используют общее ядро Rule Engine, но разные UI.
- Внутри — общий интерпретируемый runtime на стандартном scripting/general-purpose языке уровня Lua/JavaScript/Python/Groovy; язык не фиксируется.
- No-Code — source of truth. Сгенерированный текст доступен platform developer/support только read-only в диагностическом режиме. Текстовое редактирование и reverse text→builder в MVP отсутствуют.
- Поддерживаются вложенные AND/OR/NOT, сравнения, арифметика, безопасные стандартные функции, IF/THEN/ELSE, последовательность, WAIT, Device write/command, create Event, START/CALL, RETURN.
- Циклы могут существовать в runtime, но не выставляются в No-Code MVP.
- Persistent state и named CONST внутри сценария отсутствуют; shared/persistent state хранится в Virtual/Internal Device.
- Local variables живут только в одном execution instance.
- Triggers: parameter change, Event, schedule/calendar, manual. Один сценарий может иметь несколько triggers.
- Автоматический trigger получает read-only `TriggerContext`; пользовательские input parameters используются для manual/START/CALL.
- `START` — async; `CALL` — wait + one returned value supported type, включая structured table/JSON-like object.
- По умолчанию ошибка действия останавливает instance; для действия можно разрешить continue-on-error.
- Deployment: явный `Deploy`; editing не влияет на running production. Хранятся active + предыдущие 3 deployed versions. Уже запущенный instance продолжает старую версию.
- Concurrency modes: Parallel / Single / Restart. Restart завершает предыдущий instance как normal `RESTARTED`, а не error.
- Max wall-clock может быть finite или ∞, но runtime защищается от non-yielding code стандартным watchdog/resource control.
- Instance не переживает restart runtime/server; missed schedules не догоняются.
- Scheduler: periodic минимум около 1 s без real-time guarantees; calendar schedule использует timezone Space, внутренние timestamps UTC.
- Нет гарантии ordering почти одновременных triggers.
- Space имеет пользовательский limit live Automation instances ≤ tariff max. При превышении trigger skipped/dropped без очереди; пишется log/counter и system Event/Alarm. Alarm/Event Engine этот quota не расходует.
- Есть минимальный monitor live instances и команда Stop. Для всей инсталляции в maintenance mode есть единая команда принудительно остановить все Automation instances.
- Runtime не имеет произвольного HTTP/MQTT/socket, shell, filesystem, OS, admin API и direct archive access.
- Сценарий принадлежит Space и после Deploy работает независимо от автора.

### 9.1 Явное толкование требования «проверка канала перед командой»

Исходное продуктовое требование «проверить доступность канала связи перед выдачей управляющего воздействия» **реализуется через единый Device/Profile execution mechanism**, а не отдельной командой `check connection` внутри каждого Automation scenario.

При выполнении управляющего действия профиль сопряжения знает текущее состояние соединения/сессии и либо выполняет команду, либо возвращает нормализованный результат `unavailable / timeout / failed / confirmed` и т.п. Automation ждёт результат до timeout. Это считается функциональным замещением прямого pre-check, потому что отдельная последовательность `check → command` создаёт race condition и дублирует логику профиля.

Этот тезис должен быть явно сохранён в ФТТ/source-map, чтобы к нему не возвращаться как к «потерянному требованию».

## 10. Dashboard и визуализация

- После самостоятельной регистрации создаются первый Space и первый Dashboard; пользователь начинает работу с Dashboard, а не с архитектурных экранов.
- Главная навигация разделяет рабочие области: Dashboards, Libraries, Events, Automation, Users/Access, Settings и дополнительные entitlement-функции.
- Готовое оборудование System Library ищется по SKU либо через категории. После выбора конкретного Device Template данные экземпляра вводятся в одной форме; если Asset не выбран, Device можно создать в root Space.
- Dashboard принадлежит одному Space; Device существует независимо от Dashboard.
- View/Edit — два состояния одного Dashboard.
- Drag&Drop: можно перенести целый Device или отдельный semantic parameter. Для одиночного параметра создаётся простое представление по умолчанию.
- Copy/paste dashboard element копирует визуальное представление и bindings, но не создаёт второй Device. Один Device может иметь несколько разных визуальных представлений.
- Смена представления открывает semantic-filtered catalog визуализаций.
- Built-in dashboard hierarchy/drill-down не требуется; Dashboard связываются обычными ссылками/действиями и имеют стабильные URL.
- Один responsive web frontend работает на desktop/tablet/mobile.
- Один Dashboard может иметь отдельный mobile layout для тех же элементов; если он не настроен, используется auto-responsive layout.
- Kiosk/fullscreen, grid/lock и стандартные базовые widgets входят в первую версию.
- Dashboard трактуется как **целое автоматизированное рабочее место для конкретной группы/роли**, а не как набор кнопок с разными правами для разных пользователей. В первой версии не требуется per-widget RBAC, при котором на одном Dashboard у разных пользователей работают разные элементы.
- При предоставлении группе доступа к Dashboard конфигурация должна обеспечивать соответствующие backend-права `Read/Control` на используемые Devices; backend всё равно проверяет права при API/command, чтобы Dashboard не мог повысить полномочия.
- Kiosk/fullscreen использует стабильный URL, но не создаёт anonymous/public dashboard: действуют обычные authentication и RBAC.
- Минимальный набор базовых widgets включает: сигнальные лампы/светофоры/бейджи; числовой вывод; стрелочные и секторные шкалы; progress/level bars; импульсные и фиксируемые кнопки; тумблеры/слайдеры; селекторы/Enum; поля ввода аналоговых уставок. Для изменяющих/опасных операций должна поддерживаться настраиваемая confirmation перед отправкой команды/значения.
- Frontend первой версии поставляется на русском и английском языках. Все системные строки вынесены во внешние документированные словари/resource files, чтобы новый язык добавлялся без изменения программной логики и переработки экранов.
- Пользовательские названия Asset/Device/Dashboard не переводятся автоматически. Отсутствующий перевод не должен ломать UI.
- Поддерживаются актуальные распространённые Chrome/Edge/Firefox.
- При потере связи с backend UI явно показывает недоступность и не имитирует успешное выполнение команд/изменений. После восстановления соединения актуальное состояние перечитывается, а пользователь по возможности остаётся в том же рабочем контексте; полноценный offline-mode не требуется.

### 10.1 Visual Templates

- Visual Template — отдельная library entity с input contract по семантике/типу parameter/command.
- Одна Visual Template может связывать несколько Devices одного Space.
- Она может представлять как один прибор, так и технологический фрагмент (мини-котельная, насосная, электрощит).
- Physical topology оборудования не входит в её contract. Например, Visual Template с пятью входами `Voltage` остаётся одной и той же при пяти одноканальных Devices, комбинации `2+2+1` или одном пятиканальном Device.
- Optional recommended SKU/Device Templates — advisory metadata, не BOM и не ограничение совместимости.
- Visual Template никогда не создаёт Device неявно. Recommended SKU может только открыть обычный Create Device wizard.

### 10.2 GIS

- Базовый map widget на Leaflet или эквивалентной открытой библиотеке.
- Tile source конфигурируемый, стандартный XYZ; допускается OSM-compatible source и собственный tile proxy Заказчика для платных Yandex tiles.
- Специальная интеграция с Yandex Maps API не требуется.
- Минимум: Device/Asset markers по сохранённым coordinates, popup/link to Asset/Device/Dashboard. На карте должны независимо различаться как минимум состояние связи/доступности и наличие/тяжесть активных Alarm; конкретное визуальное совмещение этих признаков прорабатывается в UX.
- Геозоны, маршруты, сложное редактирование геометрий — вне текущего объёма.

### 10.3 SVG HMI

- SVG рисуется внешним редактором, например Inkscape.
- В SVG используются стабильные element `id`.
- RatioT.Cloud загружает SVG и позволяет привязывать отдельные IDs к parameters/commands: text/value, color/state, opacity, visibility, простые состояния animation и click/control behavior.
- Собственный full SVG editor внутри Cloud не требуется.
- Простая анимация управляет свойствами/состояниями уже существующих SVG-элементов; отдельный animation editor внутри RatioT.Cloud не требуется.

### 10.4 Тренды

- Несколько параметров на одном trend;
- выбор периода, pan/zoom, legend;
- значения/statistics по видимому диапазону;
- multiple Y axes;
- overlay Alarm/Warning thresholds;
- export visible range;
- работа с raw archive и aggregates.

Специализированный engineering historian analytics package не требуется.

### 10.5 Оперативная таблица Device

Для каждого Device должен быть стандартный диагностический экран текущих параметров до создания Dashboard: display name/semantic ID, current value, engineering unit, quality, timestamp, при необходимости raw value; для writable parameters — штатная запись с учётом RBAC.

## 11. Пользователи, RBAC, Integrator и SuperAdmin

### 11.1 RBAC

- User↔Group many-to-many.
- ACL: Group→resource permissions; allow-only; права суммируются.
- Asset ACL наследуется вниз.
- Dashboard: View/Edit.
- Asset/Device: Read/Control/Manage.
- Space administrative permissions отдельно.
- Исходное требование `Группа × Ресурс → Панель настроек` не реализуется отдельным ACL-ресурсом «Панель настроек»: его назначение закрывают функциональные административные права Space, а UI показывает только доступные пользователю разделы настроек.
- Исходное требование `Группа × Ресурс → Группа устройств` не создаёт отдельную параллельную сущность: его назначение выполняет Asset и его поддерево с наследуемым ACL.
- Preset editable groups: Masters / Operators / Observers.
- Entitlement и RBAC независимы: effective capability = owner tariff entitlement AND user RBAC.
- Все изменения RBAC и административных полномочий журналируются.

### 11.2 Owner и transfer

- Owner — специальный статус Space.
- Transfer может указать любого существующего пользователя RatioT.Cloud; если он ещё не member Space, добавление и transfer выполняются одной atomic operation.
- Перед transfer выполняется жёсткий pre-check тарифа/лимитов нового Owner.
- Если новый Owner не может владеть ещё одним Space либо его quota ниже фактического состояния Space, transfer блокируется до гармонизации Space или тарифа. Restricted mode из-за transfer не создаётся автоматически.
- Account нельзя удалить, пока он владеет хотя бы одним Space; сначала ownership передаётся либо Space удаляются.

### 11.3 Integrator Workspace

- Клиент делегирует/отзывает доступ **организации-интегратору как стабильному субъекту**, а не управляет каждым её сотрудником.
- Интегратор сам управляет своим персоналом и назначением людей клиентским Space; конкретный механизм через native AggreGate IAM или минимальное расширение определяется ТЗ/prototype.
- Audit фиксирует фактического human actor.
- Integrator Workspace показывает все делегированные client Spaces, поиск/фильтры, базовое состояние, active alarms/problems и переход внутрь Space.
- Есть единый cross-space список active Alarm/Event с фильтрацией и переходом к источнику.
- Обычный Dashboard по-прежнему принадлежит одному Space; универсальный cross-space Dashboard Builder не нужен.

### 11.4 SuperAdmin

- SuperAdmin — отзывная платформенная привилегия обычного аккаунта; системный `admin` с SuperAdmin неудаляем.
- SuperAdmin управляет users, Spaces, tariffs, On-Premise license, состоянием программного контура, maintenance и другими platform-level функциями.
- SuperAdmin имеет сервисный доступ внутрь любого клиентского Space без приглашения, но всегда действует от своего имени. Вход и все его действия должны попадать в Security Audit. Скрытая impersonation под клиента не нужна.
- В SuperAdmin показывается operational state критических software components/nodes. Полноценные CPU/RAM/disk/network dashboards и history остаются внешним Zabbix/Grafana ДИТ.

### 11.5 Регистрация и контакты SaaS

Модель берётся из уже работающего Charge:

- обязательный телефон является первичным контактом регистрации;
- номер подтверждается SMS-code;
- e-mail можно указать дополнительно, он также валидируется test message/code/link;
- после успешной регистрации назначается Default tariff и создаётся первый Space;
- SMS безопасности — регистрация, смена телефона, восстановление доступа и аналогичные security operations — **не расходуют коммерческую SMS quota уведомлений**.

## 12. Тарифы SaaS и On-Premise licensing

### 12.1 SaaS

- Billing/payments в текущий scope не входят.
- Исходное «управление биллингом» Owner не реализуется в первой версии: коммерческие платежи, самостоятельная покупка/смена тарифа и пользовательский конфигуратор пакетов опций относятся к LATER. Тарифы создаёт/назначает SuperAdmin, Owner видит действующий тариф, limits и usage.
- SuperAdmin создаёт tariffs и вручную назначает их accounts.
- Account видит свой tariff/limits в профиле. Администратор Space видит effective limits и usage своего Space, не обязательно раскрывая все персональные данные/детали тарифа Owner.
- Ровно один tariff помечен `Default`; он назначается при регистрации до auto-create первого Space.
- Tariff mutable in-place и влияет на все assigned accounts; перед уменьшением quotas/features требуется impact/preflight + explicit confirmation.
- Tariff нельзя удалить пока он назначен accounts.
- Не создаётся universal arbitrary entitlement key-value builder; есть фиксированные product fields, архитектура расширяема.
- Нет индивидуальных overrides; custom client = отдельный tariff.
- Quantitative quota может быть finite или semantic `Unlimited`; representation — ТЗ.
- Значения `100 / 500 / 2000 / 5000+`, приведённые в исходной продуктовой концепции для количества тегов, трактуются как иллюстративный пример возможной тарифной сетки, а не как обязательный набор предустановленных тарифов первой версии.
- Подрядчик реализует общий механизм тарифов с фиксированным набором продуктовых полей, включая `Max Parameters per Space`; SuperAdmin может создавать произвольные тарифы и задавать значения лимитов. Конкретная коммерческая тарифная сетка является эксплуатационными данными продукта и не входит в объём разработки как жёстко заданный набор.

Обязательные SaaS tariff fields:

- Max owned Spaces;
- Max Devices per Space;
- Max Parameters per Space (все physical + virtual params);
- Max users per Space включая Owner;
- Max simultaneous interactive UI users per Space; REST API не входит в этот лимит, механизм учёта — ТЗ;
- Max telemetry/archive retention days per Space;
- Max Event/Alarm journal retention days per Space;
- Max parallel user Automation instances per Space;
- monthly SMS quota owner-wide across all owned Spaces;
- Device Template Builder enabled;
- White-label/customization enabled;
- Integrator Workspace enabled;
- Max client Spaces in Integrator Workspace.

Integrator tariff не ограничивает число сотрудников/seat интегратора; управление персоналом относится к IAM/RBAC, а не billing.
Не тарифицируются: Gateway count, Dashboard count, Reports, REST API, poll/update frequency, число Automation scenarios, число Alarm rules, backup/export, базовая Automation как функция.
Исходное пожелание «доступные каналы оповещений» как tariff field в первой версии реализуется иначе: Web/in-app, Web Push, E-mail и Telegram являются базовыми каналами, а SMS ограничивается количественной quota.

### 12.2 Boolean entitlement downgrade

Принцип: **disable the tool, keep what it produced**.

- White-label off: текущая custom appearance остаётся, но её нельзя редактировать.
- Template Builder off: уже созданные custom templates/devices продолжают работать, но нельзя создавать/редактировать templates.
- Boolean feature removal сам по себе не удаляет results.

### 12.3 Restricted mode при quota downgrade

- SuperAdmin может назначить tariff ниже текущего usage.
- Никакие «лишние» сущности автоматически не удаляются.
- Account/Space переходит в `Restricted`: Owner/Masters могут войти, увидеть violations, читать current/history, export, менять config и удалить/уменьшить excess.
- Normal operation, control commands и Automation блокируются до устранения нарушений.
- Restricted снимается автоматически после соответствия лимитам.

### 12.4 SMS

- Коммерческая SMS quota — общий monthly pool Owner на все его Spaces.
- Формулировка исходной концепции «лимит баланса SMS» в первой версии означает количественную quota, а не денежный баланс: расчёт стоимости, пополнение и списание средств не реализуются.
- Дополнительно есть non-reserving protective limit per Space и protective limit per recipient.
- Отправка разрешена только если не превышены owner total + Space protection + recipient protection.
- Dedup/cooldown/anti-flapping — первая защита.
- При protective block SMS branch останавливается, создаётся system warning; остальные channels продолжают работу.
- Actual commercial consumption не сбрасывается Space users; owner/master может re-arm protective block после исправления причины, history не стирается.
- Security/service SMS account operations не входят в commercial pool.

### 12.5 White-label

- Один owner-level boolean entitlement разрешает custom appearance/FQDN для всех owned Spaces в пределах Max Spaces.
- White-label config Space включает как минимум colors/theme, logo, индивидуальное отображаемое название проекта/Space и custom FQDN.
- Настройки per Space: colors/theme, logo, custom FQDN.
- DNS, domain ownership, VPN/network и предоставление certificates — зона Заказчика/ДИТ.
- Подрядчик реализует применение custom FQDN за nginx/reverse proxy и должен на этапе ТЗ проработать, как Space определяется по входному FQDN.
- White-label должен применяться уже на login page до authentication. Если AggreGate штатно это не умеет, подрядчик предлагает минимальное расширение/обходной механизм без изменения UX.

### 12.6 On-Premise

Текущее требование — полноценная crypto licensing architecture, но простой first-version Installation ID:

- единый `Entitlement Manager` + pluggable `License Provider`;
- signed license содержит Installation ID, validity и limits;
- vendor signing private key отсутствует у клиента; runtime имеет public verification key;
- `InstallationIdProvider` — extension point;
- first version ID читается из fixed local file, например `/var/lib/ratiot/installation-id`, а не hardware fingerprint;
- позже provider можно заменить на TPM/hardware/VM UUID/dongle/license server без изменения entitlement consumers;
- invalid/missing/expired license оставляет admin UI для diagnostics/license replacement, но блокирует normal licensed runtime;
- license может быть perpetual либо иметь expiration date;
- installation-wide limits только три: total Spaces, total Devices, total Parameters;
- остальные функции On-Premise доступны полностью;
- incompatible lower license → Restricted analog, no deletion;
- On-Premise SMS использует provider/contract клиента и не расходует SaaS commercial quota.

## 13. Backup, Space portability, update и maintenance

### 13.1 Full installation backup/restore

Подрядчик должен реализовать весь operational lifecycle:

- initial deployment;
- automatic backup не реже одного раза в сутки;
- manual admin backup;
- restore на clean installation;
- update приложения на эксплуатируемом экземпляре;
- rollback/recovery через backup;
- scripts/configs/instructions для всех процедур.

Не требуется ежедневный full dump всей telemetry: full/incremental/DB-native strategy выбирает подрядчик. Процедура не должна зависеть от ручного восстановления «по памяти разработчика».

### 13.2 Space export/restore

- Space config export/backup должен быть self-contained и включать **всю активную конфигурацию** и зависимости: Assets, Devices, parameters, profiles/mapping, Dashboard, Visual Templates Space, Automation, Alarm/Event rules/config, groups, ACL, user assignments, notification config, white-label и т.п.
- Telemetry/history в этот config package не входит; её export — отдельная функция.
- Import wizard анализирует user references: если user существует — mapping; если нет — мастер спрашивает, что делать. Допустимые действия (create/map/leave unresolved и т.п.) фиксируются ТЗ.
- Целевые сценарии: restore, migration SaaS→compatible On-Premise, migration между инсталляциями, передача другому operator/owner Cloud.
- Owner может одной операцией сформировать backup/export всех принадлежащих ему Spaces; приглашённые чужие Spaces в такой пакет не входят. Логически это набор тех же self-contained Space packages с последующим wizard-import.

### 13.3 Удаление Space

- Удаление требует explicit confirmation.
- На той же странице доступны config backup и, при необходимости, отдельный export history.
- После подтверждения удаляются active configuration, telemetry, Event/Alarm journals и прочие Space operational/history data.
- Security Audit платформы живёт отдельно и не уничтожается автоматически вместе со Space.

### 13.4 Maintenance mode

- Maintenance существует **только на уровне всей инсталляции**, не per Space.
- В maintenance новые Automation executions не запускаются, существующим по умолчанию дают штатно завершиться.
- Telemetry/archive/Event/Alarm/notifications продолжаются до фактической остановки системы, насколько это возможно.
- Администратор видит остаточную активность и имеет одну команду `Stop all Automation`, принудительно завершающую живые instances с корректным technical status/audit.
- Выход из maintenance восстанавливает прежние trigger enabled states; maintenance не переписывает конфигурацию каждого scenario.

### 13.5 Update

Реалистичная обязательная схема:

`backup → update → smoke/regression checks → OK`, либо `FAIL → rollback/restore backup`.

Отдельный сложный predictive pre-check совместимости profiles не требуется.

Порядок поддержки/обновления Tibbo AggreGate, baseline-version, новые releases и возможность vendor patches старой версии **обязательно согласуются на этапе ТЗ**. Выход новой версии AggreGate не должен автоматически блокировать release fixes RatioT.Cloud на текущем baseline.

## 14. Backend autotests и health checks

### 14.1 Backend regression suite

- Backend RatioT.Cloud должен быть покрыт automated regression tests.
- Цель: после обновления AggreGate или приложения автоматически развернуть/обновить test/stage и быстро увидеть regression.
- Покрываются критические end-to-end backend scenarios: auth/RBAC/entitlement, Space/Device, profiles, parameters, Automation, Events/Alarms, backup/restore/update, API и протокольные integration tests.
- Frontend autotest не является обязательным требованием текущего scope.

### 14.2 Постоянные health checks

Полный regression suite не заменяет постоянно работающие проверки.

Обязательны machine-readable уровни:

- liveness — process/node жив;
- readiness — node реально способен обслуживать traffic;
- system health — critical components/dependencies всей инсталляции с причиной unhealthy.

HTTP 200 от nginx или login page AggreGate не считается достаточным health signal. Если application/backend component умер, overall health должен отражать failure, например HTTP 503/readiness false.

Health/readiness могут использоваться штатной кластеризацией/load balancer. Интеграция с конкретным Zabbix/Grafana не требуется; ДИТ выбирает monitoring сам.

## 15. Архитектура, HA, масштабирование и NFR

### 15.1 AggreGate cluster и HA

- Промышленная конфигурация должна использовать штатные механизмы отказоустойчивого кластера Tibbo AggreGate Server.
- Подрядчик конфигурирует cluster, адаптирует и проверяет RatioT.Cloud в cluster mode, включая failure отдельного node.
- Собственные механизмы failover для AggreGate не разрабатываются, если штатные возможности достаточны.
- Архитектура должна поддерживать horizontal scaling обработки устройств/telemetry и распределение Spaces по processing nodes при сохранении одной логической RatioT.Cloud.
- Один account может работать со Spaces на разных physical nodes.
- Исходная формулировка «каждый клиент закреплён за конкретным узлом» трактуется на уровне **Space**, а не пользовательской учётной записи. Space является единицей tenant isolation/load placement; он может обслуживаться назначенным узлом или группой узлов средствами AggreGate. Строгое правило «один Space = один server» не навязывается.
- Конкретное mapping/scheduling tenant resources и topology согласуются в ТЗ/prototype на native AggreGate cluster/distributed mechanisms.

### 15.2 HA data storage

- СУБД/хранилище не должно оставаться очевидной single point of failure в промышленной схеме.
- Подрядчик сам выбирает СУБД и общедоступный механизм clustering/replication/failover с учётом реальной совместимости и производительности используемой версии AggreGate.
- Galera — возможный пример, но **не главный ориентир и не обязательная технология**.
- Выбранная topology, recovery и backup должны быть спроектированы/реализованы как часть целой системы.

### 15.3 Логическое разделение приложения и пользовательских данных

Исходная продуктовая пометка «разделение баз данных для пользовательских данных и приложения» трактуется как **обязательное логическое разделение** прикладных компонентов RatioT.Cloud и эксплуатационных пользовательских данных. Физическое размещение в двух отдельных БД/СУБД не предписывается и определяется архитектурой AggreGate и решением подрядчика на этапе ТЗ.

Разделение должно позволять обновлять/развёртывать приложение и выполнять backup/restore эксплуатационного состояния без ручного переноса прикладных компонентов.

### 15.4 Target NFR

- Формулировка исходной концепции «телеметрия и управление в реальном времени» означает оперативную сетевую IIoT/SCADA-работу, а не hard real-time. RatioT.Cloud не является SoftPLC или контуром противоаварийной автоматики; детерминированные миллисекундные времена реакции не требуются.
- Typical interactive UI operations при normal load: целевой response до ~1.5 s. Heavy reports/export/large historical ranges могут быть asynchronous/progress-based.
- Не менее **500 simultaneous interactive UI users** на installation как target. Load profile определяется ТЗ.
- Архитектура horizontal scale — **50 000+ Devices** на logical installation. Это не означает 1 Hz для всех параметров всех Devices одновременно.
- Архитектура должна допускать географически распределённое размещение processing nodes/контуров в рамках возможностей выбранной AggreGate topology; конкретное deployment placement — ТЗ.
- Не менее **5000 Parameters per Space** как ёмкость модели/обработки.
- Individual archive interval down to **1 s**.
- Space fault isolation: runaway automation/noisy device/bad config/profile failure одного Space не должны materially degrade другие Spaces в пределах designed load. Это не означает отдельный process/DB/container per Space.
- Нагрузочные испытания обязательны для agreed load profile; перечисленные maxima не обязаны складываться в один экстремальный test.
- Формальный SLA вида `99.9%/99.99%` и фиксированный RTO в текущем ФТТ не задаются. При этом HA architecture, backup/restore и fault isolation являются обязательными.
- Zero-downtime update не является обязательным: допускается плановое maintenance window после корректного drain/остановки активности.
- На этапе ТЗ подрядчик выполняет sizing и обосновывает CPU/RAM/storage/network/processing nodes, подход к horizontal growth и желательно reference configurations small/medium/target.

## 16. Граница поставки и ответственность подрядчика

### 16.1 Заказчик/ДИТ предоставляет

- ОС на VM/physical servers;
- compute/storage resources;
- network/routing;
- VPN;
- DNS;
- domain/certificate provisioning по корпоративным правилам;
- базовую infrastructure security.

### 16.2 Подрядчик отвечает за всё выше ОС

Включая:

- AggreGate application;
- frontend;
- СУБД;
- MQTT broker;
- nginx reverse proxy/load balancer;
- clustering/replication components;
- runtime/middleware/auxiliary services;
- JasperReports templates;
- configurations и versions;
- deployment/update/backup/restore scripts;
- health checks;
- backend autotests;
- documentation;
- диагностические логи всех существенных программных компонентов, пригодные для стандартного сбора/выгрузки и не содержащие passwords, tokens, private keys, device credentials и другие secrets.

Отдельную централизованную log-platform (ELK/Loki и т.п.) подрядчик создавать не обязан; способ интеграции с эксплуатационными средствами Заказчика определяется ТЗ.

Результат проекта — законченная software system + reproducible deployment package, а не «AggreGate application плюс список настроек для админов Заказчика».

### 16.3 Российское ПО и third-party components

- Подрядчик самостоятельно контролирует состав всех software components/dependencies с точки зрения действующих требований Минцифры РФ и переданных Заказчиком ограничений, влияющих на статус российского ПО.
- Нельзя без согласования включать компонент, который препятствует сохранению/получению требуемого статуса либо запрещён применимыми ограничениями.
- При изменении требований/обнаружении проблемной зависимости подрядчик уведомляет Заказчика и предлагает замену.
- Ведётся актуальный реестр сторонних компонентов и зависимостей с versions, назначением и licenses; обновляется вместе с releases.
- Это касается backend/frontend libraries, DB, broker, nginx, base images, middleware и прочего software supply chain.

## 17. Security

- 2FA входит в первую версию, преимущественно штатными средствами AggreGate. Конкретные factors и recovery flows — ТЗ.
- Поддерживается trusted device/browser, чтобы не вводить второй фактор при каждом login; срок trust, revoke и security triggers — ТЗ.
- Brute-force protection обязателен; Captcha — допустимый механизм, но не самостоятельное обязательное требование.
- Web/API используют HTTPS и актуальные защищённые TLS versions/cipher suites; конкретика — ТЗ и corporate requirements. TLS 1.3 желателен, но не искусственный blocker при необходимости совместимости.
- Для protocols со штатной security используется protected mode: MQTT over TLS, OPC UA security и т.п.
- Для Modbus RTU/TCP собственная crypto wrapper не разрабатывается; защита обеспечивается trusted LAN/VPN/Gateway/network perimeter.
- External AD/LDAP/OIDC/SSO в first release не входят; architecture не должна мешать будущему использованию external identity providers, поддерживаемых AggreGate.
- Security Audit неизменяемый, отделён от Event/Alarm retention; Owner/User не может его очистить. Retention/archiving — ТЗ.
- Стандартные secure-development требования (XSS/SQLi/CSRF и т.п.) обязательны без отдельной продуктовой логики.
- DDoS-защита, геоблокировки, фильтрация VPN и иные функции сетевого периметра из образца Charge не переносятся как функции RatioT.Cloud; это зона инфраструктуры Заказчика/ДИТ. Принудительная периодическая смена пароля также не является отдельным обязательным продуктовым требованием, если иное не будет согласовано в ТЗ.

## 18. Reports

- Не создаётся собственный BI/report designer.
- Подрядчик готовит в JasperReports базовые templates для табличных параметров/данных.
- PDF и XLSX формируются через Jasper templates.
- CSV — прямой экспорт table headers + data без template.
- Поддерживаются manual и scheduled reports.
- Scheduled report может формироваться автоматически и отправляться по e-mail указанным recipients.
- В базовую поставку входят как минимум Jasper-шаблоны отчёта по потреблению ресурсов за период и отчёта по журналу аварий и действий персонала.
- В отчёте «журнал аварий и действий персонала» под действиями персонала понимается технологически значимая выборка: квитирование, управляющие команды, изменение уставок и аналогичные действия с actor/time. Полный Security Audit остаётся отдельным системным журналом и целиком в этот отчёт не выгружается.
- Необходимость отдельного типового отчёта по наработке моточасов должна быть подтверждена владельцем продукта до бюджетной оценки.

## 19. White-label / custom FQDN

- Custom FQDN + colors/logo + индивидуальное отображаемое название проекта/Space — per Space config при наличии owner entitlement.
- DNS/certificate lifecycle — responsibility Заказчика/ДИТ.
- nginx/deployment должен принимать настроенный FQDN без ручной переделки application.
- На этапе ТЗ подрядчик прорабатывает trusted propagation исходного host/FQDN за reverse proxy и определение Space до authentication.
- Не следует считать arbitrary frontend-provided Space ID источником истины; mechanism должен опираться на trusted ingress information.
- White-label appearance применяется уже на login page.

## 20. Проект, этапы, испытания и комплект поставки

### 20.1 Бюджетная оценка

Подрядчик обязан разбить оценку минимум на:

1. **Backend и общая архитектура** — AggreGate application, backend business logic, API, protocols, profiles, data/storage, middleware, HA, deployment, backup/update, autotests, health, опытная эксплуатация и т.п.
2. **Frontend** — adaptive web frontend.
3. **Разработка ТЗ + UX/UI** — детальная проработка requirements/user scenarios и полный Figma album desktop + mobile, достаточный для frontend development без самостоятельного додумывания UI.

Отдельно показываются:

- необходимые Tibbo AggreGate licenses для development/test/experience/prod и cluster topology;
- прочие commercial third-party licenses, если подрядчик их предлагает;
- assumptions, exclusions, трудоёмкость/стоимость каждого блока.

### 20.2 AggreGate licenses

В бюджетной оценке подрядчик определяет types/count/purpose всех AggreGate Server licenses, необходимых предлагаемой architecture, включая dev/test/experience/prod и HA/cluster. Known license constraints, влияющие на solution, должны быть явно указаны.

### 20.3 ТЗ и UX/UI

Разработка ТЗ — отдельный оплачиваемый этап. В него входит полная UX проработка и Figma album desktop/mobile.

### 20.4 ПМИ и ПСИ

- Подрядчик разрабатывает ПМИ и согласует её до испытаний.
- Проводит ПСИ №1, оформляет protocol. Успешный ПСИ №1 = готовность к запуску production и старту опытной эксплуатации.
- ПМИ должна включать functional/backend scenarios, RBAC/security, protocols, backup/restore/update, HA, health и agreed load/NFR tests.
- После 12 месяцев опытной эксплуатации выполняется **ПСИ №2 как регрессионная проверка**, а не полный повтор ПСИ №1. Scope второго ПСИ покрывает critical end-to-end, всё изменённое за период и отсутствие regression по критичным NFR.

### 20.5 Опытная эксплуатация — 12 месяцев

Это отдельный активный этап проекта, **не «гарантия»**.

- Production запускается сразу после ПСИ №1.
- 12 месяцев подрядчик исправляет defects, устраняет agreed technical debt, выпускает fixes и сопровождает releases на production.
- Исправления RatioT.Cloud не должны месяцами ждать следующего AggreGate release; текущий stable baseline используется для normal release train.
- Стратегия baseline AggreGate, vendor patches и перехода на новые releases согласуется в ТЗ.
- Новые product features/change of agreed behavior не считаются defects и оформляются change request.
- Конкретные SLA severity/reaction/fix определяются ТЗ; critical production defects имеют priority над плановым technical debt.

### 20.6 Technical debt

В ходе development/experience ведётся согласованный technical-debt register с priority. До ПСИ №2 подрядчик закрывает все items, совместно помеченные как обязательные к завершению проекта. Остальные могут перейти в future backlog только с явным согласованием Заказчика.

### 20.7 Комплект поставки

У Заказчика остаётся полный воспроизводимый комплект:

- backend source;
- frontend source;
- AggreGate application/low-code components;
- Gateway PoC source;
- backend autotests;
- deployment/update/backup/restore scripts;
- nginx/DB/MQTT/middleware configs;
- migrations;
- Jasper templates;
- API/protocol documentation;
- architecture/admin/user documentation;
- health/diagnostic documentation;
- PМИ и protocols ПСИ;
- Figma UX/UI sources;
- third-party dependency registry.

Все artefacts хранятся в repositories/resources Заказчика либо регулярно синхронизируются туда. Сборка, deployment и support не должны зависеть от private GitLab/CI/CD/internal systems подрядчика.

## 21. Удаление и отчуждение данных

- Space deletion удаляет config + telemetry + Event/Alarm operational journals.
- Перед удалением предлагается config backup и отдельный history export.
- Security Audit не уничтожается автоматически вместе со Space.
- Account deletion запрещено при owned Spaces.

## 22. Что сознательно LATER / вне текущего объёма

- Native Android/iOS apps;
- AD/LDAP/OIDC/SSO integration;
- full hardware Gateway product и manufacturing provisioning;
- embedded agent для PLC/HMI;
- Store-and-Forward, если продукт не вернёт его в MVP;
- durable Automation workflow / SoftPLC / real-time control;
- direct archive access from Automation;
- full SVG editor;
- complex GIS;
- cross-space Dashboard Builder;
- MAX adapter (архитектура должна позволять добавить его позже);
- OPC UA Methods/Historical Access/Alarms&Conditions;
- user text editing/debugger of generated Automation code;
- пользовательский конфигуратор тарифных пакетов / самостоятельная покупка и смена тарифа;
- CAN/CANopen/J1939 adapters Gateway.

Отдельно **NOT REQUIRED**, а не LATER: специальная архитектура «ядро + отраслевые модули» / plugin framework из образца Charge. Этот пункт был просмотрен при аудите, но для RatioT.Cloud сознательно не переносится.

## 23. Статус после финального аудита

Содержательный системный портрет закрыт. Архитектурных blocker-вопросов для перехода к написанию ФТТ не осталось.

Перед бюджетной оценкой остаются только **входные данные владельца продукта** из `product-inputs_v003.md`: конкретные SKU первой очереди, конкретный MQTT device/protocol, подтверждение Gateway scope и решение по типовому отчёту моточасов.

На этапе ТЗ остаются implementation choices: AggreGate baseline/update policy, cluster topology, sizing/load profile, конкретные 2FA/trusted-device flows, FQDN mechanics, detailed OPC UA security/test matrix, конкретные значения retention/SMS protections и иные технические параметры, которые сознательно не фиксируются на уровне ФТТ.

Финальный аудит исходной Cloud-заготовки и образца Charge завершён. Для требований, которые реализуются иным принятым механизмом либо сознательно не переносятся, явные соответствия должны сохраняться в `source-map_v012.md`, чтобы они не воспринимались как случайно потерянные.
