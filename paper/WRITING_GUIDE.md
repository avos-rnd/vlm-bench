# Гид по оформлению и написанию статьи (TAE @ NeurIPS 2026) — полная версия

Собрано 28–29.08.2026 по первоисточникам: CFP обоих воркшопов, OpenReview
API (живые invitation-формы), официальный шаблон/инструкции NeurIPS 2026,
блоги NeurIPS, гайды Peyton Jones / Widom / Foerster / Farquhar / Karpathy /
Rush, исследования LLM-маркеров (Liang 2403.07183, Kobak 2406.07016),
техотчёт Pangram, разбор 6 принятых и нескольких отклонённых статей жанра.
Каждый раздел содержит дословные цитаты правил и ссылки на источник —
этот файл используется как единственный справочник при написании статьи.

**Внутренний документ — в сабмишен-артефакт не включать** (как и
HANDOFF/WorkPlan/Readiness).

Содержание: §1 куда подаём · §2 формат-контракт · §3 автопроверки и
LLM-текст · §4 посекционный гид · §5 стиль принятых статей · §6 чек-лист.

---

## 1. Куда подаём

### 1.1 Основная цель: TAE (Trust-AI-Eval), Сидней — соответствие теме дословное

Источник: https://tai-eval.github.io/cfp/ и OpenReview API
(`NeurIPS.cc/2026/Workshop/TAE/-/Submission`).

- Тематика CFP: «We invite submissions that study evaluation protocols
  themselves, not only the models being evaluated»; в списке топиков —
  «Benchmark and leaderboard auditing» и «Stress tests and judge
  reliability». Наша работа попадает в оба пункта буквально.
- CFP описывает, что демонстрирует сильный сабмишен: работа «treats
  evaluation itself as an object of study: what is measured, which
  assumptions connect a protocol to a claim, how uncertainty and failure
  modes are reported, and when the resulting evidence is strong enough to
  guide deployment». **Это язык, который надо зеркалить**: для каждого
  детектора называть, какое допущение измерения он проверяет (visual
  dependency, корректность gold-меток, стабильность судьи, инвариантность
  к позиции) и что триггер флага означает для доверия к дельте лидерборда.
- Объём: «Full papers: up to 8 pages, excluding references and appendices».
  «Appendices: allowed, with no page limit, but reviewers are not required
  to read appendices». Short-track нет — только full papers.
- Формат: «Submissions should be anonymized and prepared using the official
  NeurIPS 2026 LaTeX template. Please use
  `\usepackage[dblblindworkshop]{neurips_2026}` for submission. For accepted
  camera-ready versions, please use
  `\usepackage[dblblindworkshop, final]{neurips_2026}`. The NeurIPS 2026
  workshop template requires both `\title{}` and `\workshoptitle{}`; please
  set `\workshoptitle{TAE (Trust-AI-Eval): Can We Trust AI Evaluation?}`».
- Процедура: «All submissions must be submitted as a single PDF through
  OpenReview. The review process is double-blind». «Each submission will
  receive up to three reviews from the program committee. Final decisions
  will be made by the organizing team». Опубликованной рубрики
  (novelty/soundness) нет.
- Статус: «All accepted papers will be presented in an in-person poster
  session. Accepted papers are to be considered non-archival». Правил о
  dual submission на сайте TAE нет вовсе; общеворкшопное правило NeurIPS:
  «All NeurIPS workshop papers are non-archival and therefore do not appear
  in proceedings» — работу можно потом подать на архивную конференцию.
  Main-track handbook явно разрешает встречное: «dual submissions to
  nonarchival workshops are permitted».
- Дедлайны (CFP помечает их «Indicative», но OpenReview-форма подтверждает):
  submission deadline **Aug 29, 2026 AoE**; в API duedate = 2026-08-30
  11:59 UTC (≈15:00 МСК 30-го) c expdate на 30 минут позже (grace 12:29
  UTC). Review deadline Sep 14; **нотификация Sep 22**; программа Sep 27;
  воркшоп 11 или 12 декабря 2026, Сидней. Контакт: aiteval2026@gmail.com.
- OpenReview-форма TAE: обязательные поля title / authors / keywords
  (через запятую) / abstract; опциональные TLDR и pdf (API помечает pdf
  optional, но CFP требует единый PDF — грузить обязательно; ≤ 50 МБ).
  Два обязательных чекбокса: email_sharing («We authorize the sharing of
  all author emails with Program Chairs») и data_release («We authorize the
  release of our submission and author names to the public in the event of
  acceptance»). Сабмишены непубличны (public_submissions=false).
- **Профили OpenReview**: «All authors must have an OpenReview profile
  prior to submitting a paper». CFP отдельно предупреждает: «new profile
  creation can take up to two weeks in some cases». Заводить немедленно,
  институциональная почта ускоряет активацию.

### 1.2 Запасной: JUDGe (Can We Trust the Judge?), Атланта

Источник: https://judge2026.github.io/ и OpenReview API
(`NeurIPS.cc/2026/Workshop/JUDGe/-/Submission`).

- Полное имя венью: «First Workshop on Reliable Evaluation for Language
  Models (JUDGe)», Атланта, 12–13 декабря 2026.
- Треки: «Full Papers — 6 pages + references · Oral presentation»; «Short
  Papers — 4 pages + references · Poster»; «Junior Spotlight — 2 pages +
  references · Oral · Students & early-career only» (≤3 лет после PhD).
  **Наша 8-страничная версия не влезает в full** — держать секции
  модульными: ~2 страницы (related work + деталь одного детектора + одна
  таблица) должны сбрасываться в приложение без переписывания.
- Правила: «All submissions via OpenReview, double-blind, ≥3 reviews per
  paper. All accepted work is non-archival and posted on the workshop
  website (authors may opt out). Previously published work at a major ML
  venue is not eligible». Приветствуются: «Works in progress, negative
  results, practitioner case studies».
- Дедлайны: «All deadlines are 11:59 PM AoE»; сабмишен 29.08.2026 (в API
  тот же duedate 30.08 11:59 UTC + 30 мин grace); нотификация 29.09;
  camera-ready 15.10. Контакт: judge-neurips-2026@googlegroups.com.
- `\workshoptitle` для JUDGe сайт не задаёт — разумный выбор: строка
  venue из OpenReview («First Workshop on Reliable Evaluation for Language
  Models (JUDGe)»).
- **Ловушка формы, которой нет на сайте: reciprocal reviewer.** В
  invitation два дополнительных поля: `reciprocal_reviewer_name` — «If
  nominating an author as a reciprocal reviewer, enter their full name and
  OpenReview username/email here. Leave blank only if declaring exemption
  below» — и `reciprocal_reviewer_exemption` с единственным чекбоксом
  «I confirm no author qualifies for reciprocal reviewing» и оговоркой
  «...understanding that the submission may be desk-rejected if this is
  found to be incorrect». То есть при сабмите надо либо номинировать
  одного автора ревьюером, либо формально декларировать exemption (риск
  desk-reject, если декларация ложная). PDF в JUDGe-форме REQUIRED, ≤ 50 МБ;
  те же чекбоксы email_sharing / data_release.

### 1.3 Стратегические следствия

1. Дедлайны обоих воркшопов идентичны (29.08 AoE, grace 30 мин) —
   одновременный fallback-сабмит технически возможен; ни один сайт не
   запрещает параллельную подачу на два non-archival воркшопа, но подача
   идентичного текста на два воркшопа NeurIPS — вопрос норм, не правил.
2. Бюджеты страниц расходятся резко (8 vs 6) — модульность секций
   закладывать при написании, не после.
3. Профили OpenReview у ВСЕХ авторов — до сабмита, на обоих венью.
4. Чеклист NeurIPS (checklist.tex) — требование main-track; ни TAE, ни
   JUDGe его не упоминают. Страницы на него не тратить.
5. Нотификации (22.09 TAE / 29.09 JUDGe) раньше «mandatory NeurIPS
   deadline of September 29, 2026» — совместимо с любыми дальнейшими
   планами.

---

## 2. Технический контракт формата (нарушение = desk reject)

Источники: официальные formatting instructions NeurIPS 2026
(neurips_2026.tex/pdf), neurips_2026.sty, CFP NeurIPS 2026.
Локальные проверенные копии шаблона лежали в
`/private/tmp/claude-501/-Users-denisda-code-vlm-bench/0aa4de9b-.../scratchpad/`
(neurips_2026.sty, neurips_2026.tex, neurips2026.zip); Overleaf-зеркало:
https://www.overleaf.com/latex/templates/formatting-instructions-for-neurips-2026/bjdwqfdkyftc.

### 2.1 Стилевой файл

- «The only supported style file for NeurIPS 2026 is neurips_2026.sty».
  «Tweaking the style files may be grounds for desk rejection».
- «Do not change any aspects of the formatting parameters in the style
  files. In particular, do not modify the width or length of the rectangle
  the text should fit into, and do not change font sizes». Значит: никакого
  `geometry`, никаких `\vspace`-хаков, влияющих на текстовый прямоугольник,
  никаких игр с кеглем.
- Полный список опций .sty: `final` (camera-ready, деанонимизирует),
  `preprint` (arXiv-версия, футер «Preprint. Work in progress.», для
  сабмита запрещена), `nonatbib` (отключить natbib при конфликте пакетов),
  трековые: `main` (default), `position`, `eandd`, `creativeai`,
  `education`, `sglblindworkshop`, `dblblindworkshop`. «At submission time,
  please omit the final and preprint options. This will anonymize your
  submission and add line numbers to aid review».
- `dblblindworkshop` без `final` сам анонимизирует блок авторов и включает
  нумерацию строк; **на эти номера строк в тексте не ссылаться**.
- Преамбула сабмита (уже стоит в main.tex):
  ```tex
  \usepackage[dblblindworkshop]{neurips_2026}
  \workshoptitle{TAE (Trust-AI-Eval): Can We Trust AI Evaluation?}
  ```
  Camera-ready: `[dblblindworkshop, final]`. `\title{}` и `\workshoptitle{}`
  нужны оба (второй печатает имя воркшопа в футноте первой страницы).

### 2.2 Шрифты и геометрия

- «Times New Roman is the preferred typeface throughout, and will be
  selected for you by default» — внутри .sty это
  `\renewcommand{\rmdefault}{ptm}` + `\renewcommand{\sfdefault}{phv}`.
  **Не** подключать `times`/`mathptmx` руками.
- ℝ-символы: `amsfonts`, не `bbold` («The \bbold package almost always
  uses bitmap fonts. You should use the equivalent AMS Fonts»).
- Геометрия (задаёт стиль, не трогать): текст 5.5″×9″ (33×54 пика), левое
  поле 1.5″, старт 1″ от верха; 10pt / leading 11pt; «Paragraphs are
  separated by 1/2 line space (5.5 points), with no indentation».
- Бумага: «Please prepare submission files with paper size 'US Letter,'
  and not, for example, 'A4.'»
- PDF: «Your PDF file must only contain Type 1 or Embedded TrueType
  fonts» — собирать pdflatex, проверять `pdffonts main.pdf`. Страницы
  нумеруются (стиль делает сам).

### 2.3 Заголовки, абстракт, футноты

- Title: 17pt, «initial caps/lower case, bold, centered between two
  horizontal rules» (не ALL CAPS).
- Заголовки секций: «All headings should be lower case (except for first
  word and proper nouns), flush left, and bold». 1-й уровень 12pt, 2–3-й
  10pt. Для экономии места легален `\paragraph{}` — жирный run-in
  заголовок + 1 em пробела.
- Abstract: «must be limited to one paragraph»; отступ 1/2″ с обеих
  сторон, слово Abstract 12pt bold по центру — всё это делает
  `\begin{abstract}`; наше дело — ровно один абзац.
- Футноты: «use sparingly», номерные, внизу страницы, «properly typeset
  AFTER punctuation marks».

### 2.4 Фигуры, таблицы, цитирование

- Captions: «The figure number and caption always appear AFTER the
  figure»; «The table number and title always appear BEFORE the table».
  То есть **фигуры — подпись снизу, таблицы — сверху**. Обе — lower case
  (кроме первого слова и имён собственных). Шаблон добавляет: «Explain
  what the figure shows and add a key take-away message to the caption».
- «Publication-quality tables do not contain vertical rules. We strongly
  suggest the use of the booktabs package». Таблицы центрировать.
- Фигуры: `\includegraphics[width=0.8\linewidth]{...}` — ширина всегда в
  долях `\linewidth` (это же официальный фикс от вылезания за поля).
  Цвет разрешён, но «it is best... legible if the paper is printed in
  either black/white or in color».
- Цитирование: natbib загружен стилем. «Citations may be author/year or
  numeric, as long as you maintain internal consistency». Опции natbib —
  через `\PassOptionsToPackage{numbers,compress}{natbib}` ДО загрузки
  neurips_2026. Анонимность: «refer to your own published work in the
  third person. That is, use 'In the previous work of Jones et al. [4],'
  not 'In our previous work [4]'». Свою неопубликованную работу — как
  «A. Anonymous» + анонимизированный текст в supplementary.
- References: «the Reference section does not count towards the page
  limit»; «It is permissible to reduce the font size to small (9 point)».
- Display-математика: «Please use LaTeX (or AMSTeX) commands for
  unnumbered display math» — `\[...\]`/`equation`, **не** `$$...$$`
  (ломает нумерацию строк ревью-версии).

### 2.5 Лимит, appendix, чеклист

- Что считается: все фигуры и таблицы — В лимите; «Additional pages
  containing acknowledgments, references, checklist, and optional technical
  appendices do not count as content pages». TAE меняет число на 8, схему
  исключений сохраняет. Перелимит — «will not be reviewed».
- Appendix: «There is no page limit for the technical appendices», но
  «Think of the appendix as 'optional reading'... adding critical
  experiments that support the main claims to an appendix is
  inappropriate»; TAE вторит: «reviewers are not required to read
  appendices». В appendix: полный алгоритм пермутационного теста, детали
  каппы, judge-промпты, порог near-dup, полная таблица 134 кандидатов,
  протокол разметки, доп. HallusionBench-результаты. В основных 8
  страницах: все заголовочные числа и минимум одна сводная
  таблица/фигура на семейство детекторов.
- Чеклист NeurIPS обязателен только в main track («Papers not including
  the checklist will be desk rejected» — про main). TAE его не требует —
  не включать; но его нормы (error bars, воспроизводимость) ревьюеры
  применяют как дефолт — см. §4.7.

### 2.6 Полный desk-reject-список (проверять перед сабмитом)

1. >8 страниц контента (TAE) — не ревьюится.
2. Модифицированный .sty / geometry / кегли — «grounds for desk rejection».
3. Опция `final` или `preprint` при сабмите — деанонимизация.
4. Имена/аффилиации/благодарности/ссылки на наш GitHub — нарушение
   double-blind; артефакт через anonymous.4open.science.
5. A4 вместо US Letter.
6. Type 3 / незашитые шрифты (проверка `pdffonts`).
7. `$$...$$` — ломает line numbering.
8. Отдельный PDF для appendix — нужен единый файл.
9. Ссылки на авто-номера строк в тексте.
10. Футноты до знаков препинания / без номеров.
11. Авторы без профилей OpenReview.

---

## 3. Автопроверки NeurIPS и LLM-текст

### 3.1 Официальная политика (2025, перенесена в 2026)

Источник: https://neurips.cc/Conferences/2025/LLM + Main Track Handbook 2026.

- Разрешено: «We welcome authors to use any tool that is suitable for
  preparing high-quality papers and research» — полировка/копи-эдитинг ок.
  «The use of spell checkers and grammar suggestions, programming aid for
  editing purposes does not need to be documented».
- Обязательно: «Only humans are eligible to be authors». LLM-использование
  описывается «in the experimental setup section (or equivalent) if it is
  an important, original, or non-standard component» метода. **У нас
  LLM-судья — компонент метода: он и так описан в experimental setup, это
  закрывает требование.**
- Ответственность: авторы «are responsible for the entire content of the
  paper», включая «All content is correct (e.g., no citations of
  non-existent material) and original».
- Enforcement: «NeurIPS reserves the right to investigate at any time
  whether the Code of Conduct was adhered to, including after paper
  acceptance, publication, or the conference» вплоть до «revoke the
  paper's publication status».
- «Attempts at prompt injections as well as other attempts to manipulate
  reviewing is strictly prohibited» (скрытый белый текст = санкции).
- Ревьюерам: «Do not share, discuss, or disclose any information related
  to submissions with anyone or any LLMs»; E&D-track 2026 вообще запрещает
  ревьюерам LLM. Ревьюеры эпохи position-track-скандала настроены искать
  LLM-следы и гоняют детекторы неформально.

### 3.2 Pangram — главный факт enforcement 2026

Источник: блог NeurIPS 02.06.2026 «AI-Generated Papers in the NeurIPS 2026
Position Paper Track»; техотчёт Pangram arXiv:2402.14873.

- Политика position-track: «the final paper must itself be substantially
  written by human authors, meaning that AI is used only for copy-editing
  or similar peripheral changes to the main text».
- NeurIPS прогнал **все 971 сабмишенов** через Pangram v3.3.2. Скоринг —
  окнами по 250–350 слов; итоговый скор = % флагнутых окон («A Pangram AI
  score of 100% should not be interpreted as 100% of the text is
  AI-generated, rather that there is substantive use of AI in many parts
  of the text»).
- Результаты: 28.2% (273/971) — идеальный скор 100; **178 сабмишенов
  (18.4%) desk-reject без права апелляции**; ещё 123 (12.7%) должны были
  до 15.06.2026 предоставить доказательства соответствия. Апелляции
  требовали **историю версий**, доказывающую, что содержание существовало
  до участия ИИ.
- Сравнения: FAccT 2025 ≈ 1%; E&D-track NeurIPS 2026 тоже сканировали
  (43.7% для сравнения). NeurIPS отметил: Pangram «missed minor AI
  assistance under 20% completion» — лёгкий копи-эдитинг не триггерит.
- Как работает Pangram: transformer-классификатор, обученный через «hard
  negative mining with synthetic mirrors» — для каждого человеческого
  документа LLM генерирует зеркало, совпадающее «on as many axes as
  possible» по стилю/тону/семантике; active learning по false positives
  давит FPR почти в ноль. Он холистический, не словарный — **замена
  «delve» на «examine» его не обманывает**; честно написанный человеком
  текст почти не триггерит.
- Скрининг воркшоп-сабмишенов не анонсирован (подтверждено только для
  position и E&D) — считать возможным, но неподтверждённым; отдельные
  ревьюеры гоняют детекторы сами. Безопасная позиция одинакова в любом
  случае — см. 3.5.

### 3.3 Галлюцинированные цитаты — новая поверхность скрининга

Источник: https://gptzero.me/news/neurips/ + arXiv:2602.05930.

- GPTZero просканировал 4841 из 5290 принятых статей NeurIPS 2025 своим
  Hallucination Check: 100+ подтверждённых фейковых ссылок в ~53 статьях;
  оценка — **примерно каждая четвёртая принятая статья содержит хотя бы
  одну вероятно галлюцинированную ссылку** («vibe citations»).
- Метод: ссылка флагается, если не находится через web search / Google
  Scholar / PubMed / arXiv / CrossRef + валидация DOI/URL; флаги
  проверяются человеком.
- Таксономия фейков (2602.05930): полная фабрикация 66%, порча атрибутов
  (авторы/год/venue) 27%, угон идентификатора 4%, placeholder 2%,
  семантическая 1%.
- GPTZero «coordinating with the ICLR team to review future paper
  submissions» — проверка существования ссылок теперь дешёвая и внедряется.
- Для нас: `references.bib` уже верифицирован по первоисточникам
  (RelatedWork_Gap_Analysis); перед сабмитом — финальный проход: каждый
  ключ открывается по DOI/arXiv, авторы-год-название совпадают. Одна
  фейковая ссылка = свидетельство незадекларированного LLM + прямое
  нарушение «no citations of non-existent material».

### 3.4 Лексические и структурные маркеры LLM

Опасна плотность, не единичное вхождение. Не пересанитизировать до
деревянного текста — детекторы холистические.

**Слова-маркеры** (Liang et al. arXiv:2403.07183 — кратности роста
частоты: meticulous ×34.7, intricate ×11.2, commendable ×9.8; Kobak et
al. arXiv:2406.07016 / Science Advances 2025 — excess-ratio: delves
r=28.0, underscores r=13.8, showcasing r=10.7):

> delve/delves/delving, showcase/showcasing, underscore/underscores,
> pivotal, intricate/intricacies, commendable, meticulous/meticulously,
> notably, crucial, comprehensive, insights/valuable insights, robust
> (как филлер-похвала), leverage, landscape, tapestry, testament, boasts,
> fostering, garner, interplay, seamless, transformative, multifaceted,
> groundbreaking, unparalleled, holistic, noteworthy, align with,
> highlight/highlighting, emphasizing, enhance/enhancing, versatile,
> innovative, notable, exhibited; across/within/particularly как филлеры;
> цепочки sentence-initial Additionally/Moreover/Furthermore.

Компактный десятисловный набор Кобака (самый частый в LLM-абстрактах):
across, additionally, comprehensive, crucial, enhancing, exhibited,
insights, notably, particularly, within.

Дрейф словаря по эпохам моделей (Wikipedia: Signs of AI writing):
2023–сер.2024 (GPT-4): delve, intricate, tapestry, testament;
сер.2024–сер.2025 (GPT-4o): align with, enhance, fostering, highlighting;
с сер.2025 (GPT-5): emphasizing, enhance, highlighting, showcasing.
«delve» уже выцвел (перепубличен), выросли highlighting/showcasing/
emphasizing/align with/enhance — на них сейчас смотрят в первую очередь.

**Фразы и конструкции**:

- «In conclusion»; «stands as a testament to»; «plays a crucial/pivotal
  role in»; «It is important to note that».
- Negative parallelism: «not just X, but Y», «It's not X, it's Y».
- Rule-of-three в каждом предложении («cheap, fast, and reliable...
  simple, scalable, and effective»).
- Хвосты-причастия: «..., highlighting the importance of...»,
  «..., underscoring the need for...».
- Хеджи-обе-стороны: «While X offers advantages, it also presents
  challenges».
- Copula avoidance: «serves as», «represents», «functions as» вместо «is».
- Significance inflation: «setting the stage for», «key turning point»,
  «reflects broader trends».
- Vague attribution: «Experts argue», «Some critics argue», «Industry
  reports».
- Сигнпостинг-филлер: «In this section, we will...».

**Форматирование**: болды и em-dash в каждом абзаце; буллеты вида
«**Термин:** пояснение» как основной способ изложения; Title Case Везде;
шаблонные секции «Challenges and Future Prospects»; одинаковая длина
абзацев и предложений; артефакты копипаста (oaicite, contentReference,
[cite: 1], utm_source в URL, фигурные кавычки).

**Метрики детекторов старого типа** (GPTZero-эпоха): perplexity (низкая =
предсказуемые формулировки = ИИ) и burstiness (дисперсия perplexity по
предложениям; у людей короткие рубленые фразы перемешаны с длинными,
LLM-текст «tends to be fairly uniform»). Защита, которая работает и
против них, и просто улучшает текст: агрессивно варьировать длину
предложений; конкретика (числа, имена датасетов, примеры ошибок) сама по
себе высокоперплексийна — держать её в прозе.

### 3.5 Процессные правила (наша защита)

1. **Прозу пишем сами.** LLM — только вычитка/грамматика (политика
   разрешает без декларации). Не вставлять целиком LLM-черновики секций —
   именно они создают флагнутые 250–350-словные окна.
2. **Хранить историю версий** (git-коммиты LaTeX / Overleaf history) —
   это ровно тот формат доказательств, который NeurIPS принимал в
   апелляциях position-track.
3. Финальная верификация каждой bib-ссылки по DOI/arXiv/CrossRef.
4. Роль LLM-судьи в методе описана в experimental setup (см. 3.1).
5. Прогон avoid-листа по тексту — смотреть на кластеры, не на единичные
   слова; не ломать стиль ради нуля вхождений.

---

## 4. Посекционный гид

Источники: Simon Peyton Jones «How to write a great research paper»
(слайды MSR); Jennifer Widom (Stanford, «Tips for Writing Technical
Papers»); Jakob Foerster «How to ML Paper»; Sebastian Farquhar «How to
Write ML Papers» (11.2024); Karpathy «A Survival Guide to a PhD»; Sasha
Rush «How to write an okay research paper»; NeurIPS Reviewer Guidelines
2025/26; NeurIPS Paper Checklist; E&D Reviewer Guidelines 2026; TAE CFP.

### 4.0 Мастер-правило и матрица клеймов

SPJ: «Write the list of contributions first. The list of contributions
drives the entire paper: the paper substantiates the claims you have
made». И правило Evidence: «Your introduction makes claims. The body of
the paper provides evidence to support each claim. Check each claim in
the introduction, identify the evidence, and forward-reference it from
the claim». Никакого «The rest of this paper is organized as follows» —
вместо этого forward-references из нарратива интро.

Приватная матрица «клейм → evidence» (наши числа, проверенные по
significance_report):

| Клейм (число) | Evidence (таблица/фигура) |
|---|---|
| text_only 20.2% (Wilson CI), избыток над пермутационным нулём +3.2 п.п., p=0.001 (999 пермутаций, one-sided, поправка (ge+1)/(N+1)) | таблица пулов + описание процедуры |
| LOMO: разброс пулов 14.2 → 4.6 п.п. после нормировки нулём | таблица LOMO |
| Страты MMStar: math +6.6, sci&tech +7.5, coarse perception −1.7 | таблица/диаграмма страт |
| 134 unanimous-кандидата (8.9%); precision — **после человеческой разметки** (CSV пока пусты!) | таблица валидации |
| Unanimous-CE пик в перцепции (11.6–14.4%), минимум в math/reasoning (4.4–6.8%), sci&tech промежуточно (10.4%) | таблица страт CE |
| Judge-флипы 8.1% (122/1500), все от gpt-5-nano; без неё 0 — две модели полностью судье-стабильны | judge-таблица |
| Exact-only ≈ judged: 20.5/53.6/19.8/6.1 | main table |
| κ 0.495 (strict 0.544) | agreement-таблица |
| HallusionBench вне калибровки: design-label AUC 0.49 ≈ шанс; VS-избыток 2.2× VD (+7.6 vs +3.4) | HB-таблица (framing: negative result) |

⚠️ В ранних черновиках встречалась формулировка «7.9% human-verified
label-error rate» — это НЕ наше число: 7.9% — внешний уровень ошибок
аннотации из 2503.10079, с которым наши 8.9% unanimous сопоставимы.
Нашей человеческой precision пока нет (разметка 150 айтемов не сделана).
Не смешивать.

### 4.1 Title

- Widom: либо «long and descriptive», либо «short and sweet», опционально
  «a cute name that sticks in people's minds». SPJ: title читают ~1000
  человек против ~100 у абстракта — он должен нести идею в одиночку.
- Для нас: объект (аудит бенчмарков из сохранённых артефактов) +
  неожиданность (пост-хок, без новых прогонов). Текущий «Auditing VLM
  Benchmarks for Free» — правильный паттерн.
- Не: «A Study of VLM Benchmark Quality», нагромождение подзаголовков,
  клеймы, которые текст не тянет. Karpathy: ревьюеры судят по «gestalt» —
  title+abstract+Fig.1 задают якорь всего ревью.
- Бонус жанра: заголовок, обещающий эпистемическую аккуратность
  («A Careful Examination...» GSM1k), — и текст, её демонстрирующий.

### 4.2 Abstract (один абзац, ~5 предложений, 150–230 слов)

Сходящийся рецепт трёх источников:

- SPJ: 4 предложения — проблема / почему интересно-трудно / подход /
  результат.
- Foerster X-Y-Z-1: релевантность проблемы, почему трудно, решение,
  верификация экспериментами.
- Farquhar: ~5 предложений — «We introduce...», важность/трудность,
  методологический тизер с searchable keywords, потом «theorems or
  remarkable empirical numbers».
- Widom: «Include little if any background and motivation»; «material in
  the abstract should not be repeated later word for word».

Правила из принятых статей жанра (§5): первое число — во 2–3-м
предложении; счётчик детектора и человеческую верификацию сшивать в одно
предложение (образец Northcutt: «51% of the algorithmically-flagged
candidates are indeed erroneously labeled»); хеджи — численные («at
least», «up to», «we estimate»), не модальные («might suggest»);
нумеровать проблемы, каждой — своё число (образец MMStar); артефакт
(код + списки флагов) — прямо в абстракте с URL (анонимным). 2–3 наших
числа: text_only 20.2% (+3.2 п.п. над нулём, p=0.001), 134 кандидата,
8.1% флипов от одной модели; замыкать следствием: дельта лидерборда
меньше уровня артефактов — неинтерпретируема.

### 4.3 Introduction (~1–1.25 стр.)

- SPJ: «The introduction (1 page): 1. Describe the problem 2. State your
  contributions ...and that is all. ONE PAGE!»
- Открытие — конкретный кейс, не throat-clearing. Анти-пример SPJ:
  «Computer programs often have bugs. It is very important to eliminate
  these bugs [1,2]» против «Consider this program, which has an
  interesting bug». Для нас: один реальный вопрос MMStar, который все
  модели решают одинаково с картинкой и без, или сразу 20.2%.
- Схема Widom (5 вопросов одной страницей): что за проблема → почему
  важно → почему трудно → почему не решено раньше → ключевые компоненты
  подхода и результатов. Farquhar сжимает в 3 абзаца + буллеты.
- Karpathy: «each paragraph should be organized around a single concrete
  point stated on the first sentence».
- Не: «our field is huge»-зачины; пересказ prior work в интро; laundry
  list «first we do X, then Y, then Z»; «личное путешествие открытия»
  (SPJ: «choose the most direct route to the idea»).
- Явно разделить: «патологии известны [цит.]; наш вклад — они ловятся
  бесплатно из уже сохранённых артефактов + два новых результата».
  Foerster: «Never blur the lines between what had been done before and
  what you did».
- **Фигура 1 на первой странице** (Foerster: «Extra points for having
  Figure 1 on the first page»). Жанровое уточнение из §5: у всех шести
  образцов Fig.1 показывает ЯВЛЕНИЕ (реальные флагнутые айтемы, примеры
  blind-ответов), а не пайплайн; пайплайн-диаграмма — вторая фигура.

**Contributions**: SPJ-таблица NO/YES — NO «We describe the WizWoz
system. It is really cool» / YES «We give the syntax and semantics of a
language that supports concurrent processes (Section 3)». Каждый буллет —
опровержимый клейм с числом и ссылкой на секцию. Farquhar: 2–4 буллета по
1–2 строки. Karpathy: одна «single core contribution» — «contributions in
a paper are additive: two contributions are better than one. Unfortunately,
this is very wrong». Наш единственный «пинг»: дешёвый пост-хок аудит-слой
над сохранёнными артефактами VLMEvalKit; 6 детекторов и находки MMStar —
evidence, не шесть вкладов. Лесенка буллетов: (1) аудит-слой + детекторы
(секции), (2) кейс-стади MMStar с фальсифицируемыми числами, (3)
код/артефакты.

### 4.4 Related work (~0.5 стр.)

- SPJ: «Related work: later» — после технического контента. «Problem 1:
  the reader knows nothing about the problem yet... absolutely
  incomprehensible»; «Problem 2: describing alternative approaches gets
  between the reader and your idea». Widom: рано — только если «absolutely
  necessary to defend novelty», иначе перед Conclusions. В воркшоп-статье
  допустим компромисс: короткий позиционирующий абзац в интро + сжатая
  секция.
- Позиционирование, не перечисление. Farquhar: «methodological, not
  paper-by-paper» — «One line of previous research used X assumption
  whereas we make Y assumption instead». Rush: related work читают, чтобы
  разместить статью на ментальной карте — размещай, не перечисляй.
- Наши кластеры (по одному `\paragraph`): курируемые-заново бенчмарки
  (MMStar/DatBench/MMGist); аудит-тулкиты (BenchMarker/ABA/Inspect Scout);
  протокольная чувствительность (Rosenthal/xFinder). В каждом — одна фраза
  отличия (единый пост-хок слой над сохранёнными артефактами,
  пермутационная значимость, ноль новых прогонов).
- Щедрость: SPJ «Fallacy: To make my work look good, I have to make other
  people's work look bad»; «Giving credit to others does not diminish the
  credit you get from your paper»; «Be generous to the competition».
- Обязательные цитаты: список RelatedWork_Gap_Analysis + 2503.10079
  (13.5% ошибок MMStar) + 2506.07962 (correlated errors) — их отсутствие
  заметит ревьюер.

### 4.5 Method (~2 стр.)

- SPJ: «Explain it as if you were speaking to someone using a whiteboard»;
  «Conveying the intuition is primary, not secondary»; «Introduce the
  problem, and your idea, using EXAMPLES and only then present the general
  case». Анти-пример: «Consider a bifurcated semi-lattice...» — «Sends
  readers to sleep, and/or makes them feel stupid».
- Farquhar: «If your methods section starts after page 3 try to rearrange
  things» (information-momentum). Widom: «A clear new important technical
  contribution should have been articulated by the time the reader
  finishes page 3». Адаптация: к концу 2-й страницы читатель видел весь
  пайплайн и хотя бы одно заголовочное число.
- Одна общая нотация (айтемы, модели, ответы, gold) — задать один раз,
  переиспользовать (Foerster).
- **Несущий элемент секции — таблица «детектор × сигнал × артефакт ×
  статистика × цена»**, по строке на детектор; затем абзац + формула на
  детектор, каждый заканчивается «flags X when Y». Один worked example
  для наименее знакомого (пермутационный нуль blind-избытка).
- Блок «протокольная гигиена» (index-alignment, no back-fill, Z-сентинель)
  — коротко, со ссылкой на то, что back-fill менял результат в 11 раз
  (довод, что гигиена — часть вклада).
- В appendix: алгоритмы, промпты, пороги.
- Планка ясности NeurIPS: «a superbly written paper provides enough
  information for an expert reader to reproduce its results».

### 4.6 Results (~2.5–3 стр.)

- Подсекция = одно заголовочное число + его таблица. Матрица §4.0:
  каждое число абстракта/интро → ровно одна таблица; каждая строка
  таблицы подпирает какой-то клейм; таблицы-сироты вырезаются.
- Farquhar, на каждый эксперимент: «high-level signpost of main insight;
  clear claim statement; experimental setting (appendix for detail);
  specific guidance on what to observe in figures/tables». Проза говорит,
  куда смотреть («все 8.1% флипов — одна модель, Table 3, row 2»), не
  пересказывает ячейки. Его предупреждение: неверные словесные описания
  таблиц — самый частый ловимый баг; «triple-check all claims against
  visualizations».
- Widom-осторожность (глазами ревьюера): «It's easy to craft experiments
  to show your work in its best light» — негативные контроли
  (пермутационный нуль, согласие детекторов, будущая человеческая
  верификация) — на видном месте, не в приложении.
- Foerster: «statistics, confidence intervals, hyperparameter discussion,
  ablations, and limitations». Наши абляции: чувствительность к числу
  моделей (LOMO), к выбору судьи (exact vs judged), к числу пермутаций,
  VD threshold sweep (22.5→54.8% — хрупкость порога показана честно).
- **Экскульпаторные результаты — с той же выпуклостью, что обвинительные**
  (паттерн GSM1k, §5): blind-точности ≈ random согласуются с курированием
  MMStar; две из трёх моделей полностью судье-стабильны; перцептивные
  страты утечки не имеют. Это укрепляет статью, а не ослабляет.
- Rush: убедительность = предвосхищённые альтернативные объяснения.
  Наши два обязательных: «blind-избыток — это просто угадывание по
  приорам ответов» → закрывается пермутационным нулём (он ровно это и
  моделирует); «consensus-ошибки — это общий байес моделей, а не ошибки
  gold» → закрывается человеческой верификацией + цитатой 2506.07962.

### 4.7 Error bars и статистическая отчётность (нормы чеклиста NeurIPS)

Дословно из Paper Checklist (для воркшопа формально не нужен, но это
дефолтная планка ревьюеров, а для eval-methodology аудитории статистика —
сам вклад):

- «Results are accompanied by error bars, confidence intervals, or
  statistical significance tests, at least for the experiments that
  support the main claims».
- «Factors of variability that the error bars are capturing should be
  clearly stated» — у нас: Wilson CI ловит варьирование айтемов;
  LOMO — варьирование пула моделей; пермутационный нуль — случайность
  приор-угадывания. Проговорить каждое.
- «Method for calculating the error bars should be explained (closed form
  formula, call to a library function, bootstrap, etc.)» — описать: 999
  пермутаций, one-sided, поправка (ge+1)/(N+1); Wilson — закрытая формула.
- «It is OK to report 1-sigma error bars, but one should state it».

### 4.8 Limitations (именованная секция, ~0.4 стр.)

- Ревью-форма спрашивает напрямую: «Have the authors adequately addressed
  the limitations and potential negative societal impact of their work?»
  И инструктирует: ревьюеры «will not penalize honesty concerning
  limitations».
- Чеклист-определение содержательной секции: «Strong assumptions and how
  robust the results are to violations»; как допущения «might be violated
  in practice and what the implications would be»; «Scope of the claims».
- Каждое ограничение — конкретное, с механизмом и следствием:
  1. 3 модели → ошибки моделей коррелированы (одинаковый неправильный
     ответ в 61–74% случаев против 11–33% при независимости; цит.
     2506.07962) → консенсус даёт кандидатов, не вердикты.
  2. Отказы/безответы моделей вшивают политику модели в метку вопроса.
  3. Бинарные форматы вне калибровки детекторов (HallusionBench: blind
     угадывание 50%, унанимность тривиальна, design-label AUC 0.49).
  4. Контаминация и приоры мира не разделены — text_only-избыток это
     lower bound визуальной независимости, а не мера утечки.
  5. Один бенчмарк как кейс-стади; базовые уровни детекторов могут не
     переноситься.
- Анти-паттерн: перфункторное «more models/benchmarks needed», «compute
  limited our experiments», пересказ скоупа без следствий.
- Образцы: Northcutt называет три конфаунда поимённо; MMLU-Redux считает
  непокрытое точно («remaining 8,342 questions»).

### 4.9 Conclusion (~0.2 стр.)

- Widom: выводы «should not simply repeat material from the Abstract or
  Introduction» — что СЛЕДУЕТ из находок, а не что статья сделала.
  Следствие: аудит-отчёт должен идти в комплекте с лидербордом; дельта
  моделей меньше уровня артефактов бенчмарка — шум.
- Future work = застолбить территорию (Widom: «If you're actively engaged
  in follow-up work, say so»): 6-модельный пул, полный свип бенчмарков
  VLMEvalKit.
- Foerster: «avoid grandiose language or overly broad claims».

### 4.10 Reproducibility / артефакт

- Чеклист: «Papers cannot be rejected simply for not including code,
  unless this is central to the contribution» — у тулкит-статьи код
  ЦЕНТРАЛЕН, значит релиз фактически обязателен.
- Планка E&D-ревьюеров: код «accessible, executable, properly anonymized,
  and sufficiently documented»; тест ясности — «Could another team re-run
  the benchmark from this paper?»
- Конкретно: анонимный репозиторий (anonymous.4open.science) с
  детекторами, сохранённые артефакты MMStar внутри, **одна команда**
  воспроизведения; выложить список 134 кандидатов (после разметки — с
  вердиктами) как самостоятельный артефакт; зафиксировать версии моделей
  и судьи и даты прогонов; короткий Reproducibility-абзац.

### 4.11 Критерии ревьюеров (писать так, чтобы на каждый был ответ в одну фразу)

Ревью-форма NeurIPS, дословно: Quality — «Is the submission technically
sound? Are claims well supported?»; Clarity — «Is the submission clearly
written? Does it adequately inform the reader?»; Significance — «Are
others (researchers or practitioners) likely to use the ideas or build on
them?»; Originality — «Does the work provide new insights, deepen
understanding, or highlight important properties of existing methods?» —
originality явно покрывает insight-про-существующие-методы, ровно наш
жанр; «novel combinations of well-known techniques» ценны, когда «it is
clear how the work differs from previous contributions».

E&D-guidelines (ближайший прокси TAE-ревьюера): «Evaluate the rigor of
task design, item selection, and evaluation setup»; «Assess the
statistical soundness, rigor, and validity of proposed evaluation
protocols or metrics»; significance-тест: «Does it shift conclusions if
applied to existing benchmarks?»; для нашего жанра: «If a negative
result: is it deep and carefully controlled?»; трек-блог: сабмишен «need
not "beat a baseline"; its primary contribution should be to deepen and
refine our understanding of evaluation practices».

Заготовленные ответы: significance = аудит любого сохранённого прогона
VLMEvalKit за копейки; originality = унификация + кейс-стади, не шесть
новых алгоритмов; «shift conclusions» = состав text_only и judge-флипы
меняют интерпретацию дельт на MMStar.

### 4.12 Бюджет 8 страниц и процесс

Бюджет (синтез SPJ-раскладки под 8 стр.): title/abstract ~0.4;
Introduction 1.0–1.25 (contributions + Fig.1); Related work 0.5 (или
0.25 + поинтер); Method: аудит-слой + 6 детекторов 2.0–2.5 (сводная
таблица детекторов); Case study MMStar 2.5–3.0 (2–3 таблицы + ≤1 фигура,
booktabs); Limitations 0.4 (именованная); Conclusion 0.2. Эмпирика жанра:
≤25–30% площади под floats; Fig.1 (явление) на стр. 1–2; без float на
стр. 8; references `\small`.

Процесс под дедлайн:

- SPJ #1: «Don't wait: write» — «Writing papers is a primary mechanism
  for doing research». Сначала список contributions, он ведёт всё.
- Farquhar (метод для сжатых сроков): рекурсивный буллет-поинтинг —
  outline → поинты уровня абзацев → предложения, фидбек на каждом уровне.
- SPJ #7: свежие читатели — «Each reader can only read your paper for the
  first time once! So use them carefully»; просить «I got lost here», а
  не охоту на опечатки. «Experts are good. Non-experts are also very good».
- Финальный проход: SPJ evidence-аудит (каждый клейм интро → его таблица)
  + Farquhar triple-check каждой прозаической фразы против фактических
  значений в таблицах.
- Стиль Foerster: без пассива где можно; удалить ~1/3 слов первого
  черновика; единое время (без будущего); «avoid subjective claims —
  usually adjectives are red flags» (писать «+3.2pp excess, p=0.001»,
  не «substantial contamination»); «Never copy-paste from other papers,
  unless verbatim quoting».

---

## 5. Стиль принятых статей жанра

### 5.1 Разбор шести образцов (что именно у них работает)

**Northcutt «Pervasive Label Errors» (NeurIPS 2021 D&B, 1000+ цит.,
arXiv:2103.14749)** — родитель нашего consensus-детектора.
Абстракт открывается плоским декларативом без прелюдий: «We identify
label errors in the test sets of 10 of the most commonly-used...
datasets». Первое число — во 2-м предложении через двоеточие: «Errors in
test sets are numerous and widespread: we estimate an average of at least
3.3% errors». Ключевое предложение жанра — детектор+верификация+precision
в ОДНОЙ фразе: «Putative label errors are identified using confident
learning algorithms and then human-validated via crowdsourcing (51% of
the algorithmically-flagged candidates are indeed erroneously labeled)».
Хеджи консервативными границами («at least»), сюрприз помечен явно
(«Surprisingly, we find...»), два живых артефакта прямо в абстракте
(labelerrors.com, github). Лимитация хирургически конкретна: названы три
неразличимых конфаунда оверфиттинга. Тон конструктивный — советы
практикам, не обвинения.

**MMStar «Are We on the Right Way...» (NeurIPS 2024, arXiv:2403.20330)**
— прямой предок нашего blind-детектора; цитировать и зеркалить framing.
Одно контекстное предложение, затем pivot: «we dig into current
evaluation works and identify two primary issues: 1) Visual content is
unnecessary for many samples... 2) Unintentional data leakage exists...».
У каждой пронумерованной проблемы — своё шок-число немедленно:
«GeminiPro achieves 42.9% on the MMMU benchmark without any visual
input»; «Sphinx-X-MoE gets 43.6% on MMMU without accessing images».
Проблема → следствие («misjudgments of actual multi-modal gains») →
артефакт-решение → масштаб валидации (16 LVLM, 7 бенчмарков). Fig.1 —
примеры проблемных айтемов (качественные), не пайплайн. Тон
расследовательский, не обвинительный.

**MMLU-Redux «Are We Done with MMLU?» (NAACL 2025, arXiv:2406.04127)**.
Единственный образец с вопросом-заголовком — работает, потому что ответ
двумя словами сразу: «Maybe not. We identify and analyse errors...».
Паттерн shock-then-calibrate: сначала крайняя страта («57% of the
analysed questions in the Virology subset contain errors»), затем трезвый
глобал («We estimate that 6.49% of MMLU questions contain errors»). Наша
версия: sci&tech +7.5 → глобальные +3.2. Лесенка вкладов: находка →
протокол аннотации → артефакт (5,700 переразмеченных вопросов) →
следствие («significant discrepancies with the model performance metrics
that were originally reported»). Закрытие конструктивное: «advocate for
revising... to enhance its future utility». Лимитации считают непокрытое
точно: «remaining 8,342 questions».

**BetterBench (NeurIPS 2024 D&B, arXiv:2411.12990)**. Открытие со ставок
деплоя; первые числа — масштаб фреймворка («46 best practices... 24 AI
benchmarks»), находки смягчены намеренно. Их эмпирика — наш козырь: «most
benchmarks do not report statistical significance of their results nor
allow for their results to be easily replicated» — мы делаем ровно то,
чего не делает большинство (p=0.001 + one-command repro), сказать это.
Вклады — стопка деливераблов глаголами: «we develop... we evaluate... we
find... we provide a checklist... a living repository».

**Platinum benchmarks «Do LLM Benchmarks Test Reliability?» (MadryLab,
arXiv:2502.03461)**. Открытие именованием пробела простым языком: «Many
benchmarks have been created to track LLMs' growing capabilities, however
there has been no similar focus on measuring their reliability». Находка
с механизмом: «pervasive label errors can compromise these evaluations,
obscuring lingering model failures». Чеканка переиспользуемого концепта
инлайн («platinum benchmarks, i.e., benchmarks carefully curated to...»).
Скромность скоупа внутри вклада: «As a first attempt at constructing such
benchmarks...». Тон «measured and academic... direct without being
sensational».

**GSM1k «A Careful Examination...» (NeurIPS 2024 D&B oral,
arXiv:2405.00332)** — мастер-класс калиброванного хеджирования. Каждый
клейм дозирован: «accuracy drops of up to 8%, with several families of
models showing evidence of systematic overfitting»; корреляция измерена,
не заявлена («Spearman's r² = 0.36... suggesting that some models may
have partially memorized»). Фирменный ход — экскульпаторная находка с
равной выпуклостью: «Nevertheless, many models, especially those on the
frontier, show minimal signs of overfitting». Прямое применение к нашему
judge-результату: все 8.1% флипов от одной модели → сказать плоско, что
две другие стабильны. Даже заголовок рекламирует аккуратность.

Ритм и плотность образцов: абстракты 150–230 слов с высокой дисперсией
длины предложений — где-то фраза в 2–4 слова («Maybe not.») против
40+-словных предложений с evidence; числа почти в каждом предложении
средней трети. Полные статьи: 5–12 фигур / 2–8 таблиц; в масштабе
воркшопа: Fig.1 (явление) + 1 пайплайн-фигура + 2 results-таблицы с CI.

### 5.2 Одиннадцать правил «имитировать»

R1. Открыть плоским декларативом о ставке или самой находке; без
    литобзорной прелюдии. Вопрос-зачин — только если ответ ≤3 слов сразу.
R2. Первое число — во 2–3-м предложении абстракта: «text-only answerable
    20.2% (+3.2pp over a permutation null, p=0.001)».
R3. Детектор + человеческая верификация + precision — одним предложением
    в стиле Northcutt; алгоритмический счётчик никогда не стоит один
    (после разметки 150 айтемов вставить точную формулу фразы).
R4. Хеджи-границы на числах («at least», «up to», «we estimate»), не
    размытые модальности на клеймах.
R5. Экскульпаторная находка — с равной выпуклостью (GSM1k
    «Nevertheless...»): две модели судье-стабильны; перцепция чиста.
R6. Арка абстракта: проблема → измерение → следствие → артефакт; артефакт
    с (анонимным) URL прямо в абстракте.
R7. Нумеровать проблемы/детекторы в абстракте, каждой — своё число-пример
    (образец MMStar «1)... 42.9%... 2)... 43.6%»).
R8. Fig.1 показывает явление (реальные флагнутые айтемы MMStar, примеры
    blind-ответов), не пайплайн; ссылка на неё в 1–2-м абзаце интро.
R9. Конструктивная позиция к авторам бенчмарков: «делаем бенчмарки
    аудируемыми», никогда «бенчмарк X сломан». Наша рамка: «даже отлично
    курированный MMStar сохраняет резидуальные N% — значит, аудит нужен
    как процесс, а не разовое усилие» (авторы MMStar могут оказаться
    ревьюерами).
R10. Вклады — нумерованный список с числами масштаба внутри, замкнутый
    следствием для практики.
R11. Одна сквозная мысль (Karpathy: single core contribution): «дешёвый
    пост-хок аудит из готовых артефактов» — все 6 детекторов подчинены
    ей; статья — не шесть мини-отчётов.

### 5.3 Восемь правил «никогда» (по реальным ревью и отклонённым статьям)

Источники: ClaimCheck (arXiv:2503.21717 — таксономия слабостей из
реальных ревью NeurIPS 2023/24), E&D guidelines, блоги чейров D&B,
подтверждённые реджекты жанра.

N1. Критика без переиспользуемого артефакта/протокола. Показательная
    пара: «Detecting Label Errors in Token Classification Data»
    (Cleanlab-линия, arXiv:2210.03920) отклонена TMLR 21.06.2023 — 
    компетентный последователь Northcutt, но: одна задача, нет
    consequence-клейма (ранкинги не дестабилизированы), нет заголовочного
    артефакта. Детектор-без-следствия — проигрышная форма.
N2. Счётчик детектора без человеческой precision на выборке. Топ-слабость
    ClaimCheck — Insufficient Evidence: «The paper provides insufficient
    evidence for some claim(s)—e.g. due to lack of statistical
    significance testing, missing experiments, weak baselines...».
N3. Числа без significance/CI. Дословная фраза из реального ревью: «The
    paper should include statistical significance testing to determine if
    the models' underperformance is truly indicative of sandbagging
    rather than random variation». Второй реальный паттерн: «I would like
    to see the performance of other correction methods (e.g.,
    GPT3.5/4/4o) for a more comprehensive comparison» — нам предъявят
    один судья gpt-4o-mini → предвосхитить exact-армом и явной
    scoping-фразой.
N4. Обвинения (моделей, лабораторий, авторов бенчмарков) в
    контаминации/читерстве. GSM1k даже сильнейшую улику формулирует «may
    have partially memorized».
N5. Скрытые механики пайплайна, способные сфабриковать заголовочное
    число: «conclusions can be silently manufactured by implementation
    details that readers cannot see in the reported numbers» («Auditing
    the Audit»). Документировать no-op-проверки — см. 5.4.
N6. Неадресованный масштаб 3 моделей (MMStar — 16 моделей, BetterBench —
    24 бенчмарка): либо расширять, либо явно скоупить («case study,
    валидирующий детекторы, не лидерборд»).
N7. Ответ «нет» на вопрос ревьюера «Could another team re-run the
    benchmark from this paper?» — версии зафиксированы, списки флагов
    выложены, одна команда воспроизведения.
N8. Похороненное следствие: каждый принятый образец говорит, что меняется
    downstream (ранкинги дестабилизируются, метрики были неверно
    отрепортованы); «Does it shift conclusions if applied to existing
    benchmarks?» — буквальный критерий ревью.

### 5.4 Самопроверка «Auditing the Audit» (ICML 2026 TAIGR, arXiv:2607.02586)

Тезис статьи: аудиты «are themselves fragile: their conclusions can be
silently manufactured by implementation details that readers cannot see
in the reported numbers». Пять failure modes аудит-статей и наши ответы
(достойно короткого абзаца/таблицы «audit of the audit» — это теперь
table stakes жанра; их рекомендация — публиковать self-audit chronology,
потому что «repair silently absorbed into a clean narrative is
indistinguishable from a pipeline where the bugs were never caught»):

- F1 Silent no-op perturbation («the scorer-consumed prompt is
  bit-identical to the unperturbed input») → наш blind реально вырезает
  картинку центрально (`strip_visual_content`); показать пример отказа
  модели, доказывающий, что изображения не было.
- F2 Regex-extraction artefacts («Δfmt tracks regex coverage, not model
  behaviour») → у нас арм judge-vs-exact — прямой ответ; расхождение
  задокументировано (флипы 8.1%, все от одной модели).
- F3 Non-faithful scoring (не тот протокол измерения) → используем родной
  судейский протокол VLMEvalKit без модификаций.
- F4 Broken pairing in uncertainty («Bootstrap that independently
  resamples originals and perturbations breaks per-item coupling») → наш
  пермутационный нуль item-paired по построению — сказать это явно.
- F5 Metric-archetype mismatch (один скаляр на два прочтения) → мы
  дизагрегируем: категории детектора, страты MMStar, состав text_only
  (164/303 — обе стороны неверны).

---

## 6. Чек-лист перед сабмитом

Формат:
- [ ] `\usepackage[dblblindworkshop]{neurips_2026}` +
  `\workshoptitle{TAE (Trust-AI-Eval): Can We Trust AI Evaluation?}`;
  НЕ `preprint`/`final`
- [ ] официальный `neurips_2026.sty` рядом, не модифицирован; никакого
  geometry/кеглей/\vspace-хаков
- [ ] ≤ 8 стр. контента (фигуры/таблицы включены); references (`\small`
  ок) и appendix вне лимита; единый PDF ≤ 50 МБ
- [ ] US Letter; pdflatex; `pdffonts main.pdf` → только Type 1/embedded
- [ ] captions: таблицы сверху, фигуры снизу, sentence case, с
  take-away; booktabs без вертикальных линий; ширины в `\linewidth`
- [ ] нет `$$...$$`; футноты после пунктуации; на номера строк не
  ссылаемся

Содержание:
- [ ] `grep -n 'ph{' main.tex` → только определение макроса
- [ ] evidence-аудит: каждый клейм интро → forward-ref на его таблицу
  (матрица §4.0); таблиц-сирот нет
- [ ] triple-check: каждая прозаическая фраза о числах сверена с
  фактическими значениями таблиц
- [ ] экскульпаторные находки на месте (R5); тон к MMStar конструктивный
  (R9); скоуп 3 моделей заявлен явно (N6)
- [ ] абзац «audit of the audit» / ответы на F1–F5 (§5.4)
- [ ] статистика проговорена: 999 пермутаций, one-sided, (ge+1)/(N+1);
  Wilson; что ловит каждый интервал (§4.7)
- [ ] limitations — именованная секция, каждая с механизмом и следствием
- [ ] «7.9%» НЕ выдаётся за нашу human precision (см. предупреждение §4.0)

Анонимность и ссылки:
- [ ] нет имён, аффилиаций, благодарностей, ссылок на наш GitHub;
  self-citations в третьем лице; артефакт на anonymous.4open.science
- [ ] из артефакта исключены HANDOFF.md, WorkPlan, Readiness-doc, этот
  файл
- [ ] каждая bib-ссылка открывается по DOI/arXiv, авторы-год-название
  совпадают (анти-«vibe citations»)

LLM-гигиена:
- [ ] прогон avoid-листа §3.4 (плотность, не единичные вхождения);
  дисперсия длины предложений; конкретика в прозе
- [ ] история git-коммитов текста сохранена (доказательство авторства)

Сабмит:
- [ ] профили OpenReview у ВСЕХ авторов; keywords; чекбоксы
  email_sharing + data_release
- [ ] загрузка ≥ часа до 23:59 AoE (grace 30 мин — страховка, не план)
- [ ] (если JUDGe) версия ужата до 6 стр.; поле reciprocal reviewer:
  номинант выбран заранее или exemption обоснован
