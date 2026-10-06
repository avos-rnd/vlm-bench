# Передача проекта: что осталось сделать (TAE @ NeurIPS 2026, Sydney)

Дата: 28.08.2026. Все ссылки — относительно корня репозитория.
Английский ранбук с полной матрицей экспериментов: [docs/en/WorkPlan_TAI-Eval.md](../en/WorkPlan_TAI-Eval.md).

## ⚠️ Главное: дедлайн

CFP проверен 28.08: воркшоп называется **TAE — "Can We Trust AI Evaluation?"**
(https://tai-eval.github.io/), дедлайн подачи — **29 августа 2026, AoE**
(это ~15:00 МСК 30 августа). OpenReview:
`https://openreview.net/group?id=NeurIPS.cc/2026/Workshop/TAE`.
В топиках прямо заявлены *benchmark and leaderboard auditing* и *judge
reliability* — наша тема попадает в цель дословно. Нотификация 22.09,
формат — постер, Сидней 11–12.12.

**Лимит страниц и режим анонимности на сайте НЕ указаны** — первым делом
открой страницу OpenReview и проверь (обычно 4–9 стр. без референсов,
double-blind).

Поэтому два сценария. Реалистичный на ближайшие 48 часов — Сценарий A.

---

## Что УЖЕ сделано (не переделывай)

1. **Код починен и протестирован** (36 тестов, из них 11 наших — все зелёные;
   2 падающих `test_inference_api` падают и на чистом апстриме, это среда):
   - `--blind` — штатный флаг `run.py` (единый механизм для локальных и
     API-моделей; файлы получают суффикс `_blind`); хаки в обёртках моделей
     откатаны;
   - детекторы выровнены по dataset `index`, подмена ответа на ground truth
     удалена, «Z»-абстенции исключены из голосований;
   - параметры генерации/commit/argv пишутся в манифесты прогонов;
   - NumPy-докстринги по всему audit-слою.
2. **Литература проверена по базам**: [docs/en/RelatedWork_Gap_Analysis.md](../en/RelatedWork_Gap_Analysis.md)
   (вердикт: gap реальный, но узкий; concurrent: DatBench, Fantastic Bugs,
   BenchMarker — позиционирование уже вшито в текст статьи). 20 проверенных
   ссылок: [paper/references.bib](../../paper/references.bib).
3. **Манускрипт**: [paper/main.tex](../../paper/main.tex) — полный каркас,
   компилируется (0 ошибок), все недостающие числа помечены красным `\ph{...}`.
4. **Предварительные числа уже посчитаны** исправленным кодом на артефактах
   3 моделей из ветки `origin/results`: см.
   [audit_preliminary/README.md](../../audit_preliminary/README.md).
   Ключевое: text_only **20.2%** (CI [18.2, 22.2]), consensus-error **23.9%**
   (unanimous **134** вопроса = 8.9%; в старом коде было 12 — подмена GT
   маскировала), Fleiss' κ **0.495**, смена судьи меняет категорию у **8.1%**
   вопросов (Jaccard text_only 0.79).
5. **Пакет ручной разметки готов**: `audit_preliminary/annotation_mmstar/`
   (150 вопросов, 3 страты по 50). Протокол:
   [docs/en/AnnotationProtocol.md](../en/AnnotationProtocol.md).
6. Превью-фигуры: `paper/figures/` (scatter по свежему прогону, каркасы таблиц).

---

## Сценарий A: подача 29.08 AoE (≈48 часов)

Статья честно позиционируется как «audit layer + 3-модельный кейс + judge
sensitivity»; 6-модельный пул уходит в camera-ready/поster-версию (после
нотификации 22.09 будет ~2.5 месяца до воркшопа).

### День 1 (сегодня)

- [ ] **(30 мин)** OpenReview: лимит страниц, анонимность, шаблон. Скачай
      официальный `neurips_2026.sty` в `paper/` (см. [paper/README.md](../../paper/README.md)).
- [ ] **(3–4 ч, параллельно вдвоём)** Ручная разметка: вы оба независимо
      заполняете `audit_preliminary/annotation_mmstar/annotator_A.csv` и
      `annotator_B.csv` (`verdict` = yes/no/ambiguous). **key.json не
      открывать до конца.** Картинки MMStar смотри по `index` через
      `scripts/data_browser.py` или HF-viewer датасета Lin-Chen/MMStar.
- [ ] **(10 мин)** Подсчёт:
      ```bash
      python scripts/sample_for_annotation.py score \
        --a audit_preliminary/annotation_mmstar/annotator_A_filled.csv \
        --b audit_preliminary/annotation_mmstar/annotator_B_filled.csv \
        --key audit_preliminary/annotation_mmstar/key.json \
        --out audit_preliminary/annotation_mmstar
      python scripts/audit_paper_assets.py \
        --validation audit_preliminary/annotation_mmstar/validation_report.json \
        --out paper/figures
      ```
      Разногласия из `adjudication_worklist.csv` обсудите и зафиксируйте.
- [ ] **(вечер)** Заполнение `\ph{}` в `paper/main.tex` числами из
      [audit_preliminary/README.md](../../audit_preliminary/README.md) +
      precision/κ из validation_report. Карта соответствий:
      - абстракт: `N=6` → **3** (и переписать под «case study»), text_only →
        20.2%, consensus → 23.9% / 134 unanimous, judge-сдвиг → 8.1% флипов /
        Jaccard 0.79, precision/κ — из разметки;
      - Table `tab:main`: строка MMStar готова в `paper/figures/tab_main.tex`;
        HallusionBench — см. чекбокс ниже, иначе убрать строку и сузить
        клейм до MMStar;
      - LOMO-диапазоны и bootstrap-CI: `audit_preliminary/.../stability_report.json`
        (и честно: «with 3 models LOMO ranges span up to ~13pp — motivating
        larger pools»);
      - Fig scatter: `paper/figures/fig_scatter_mmstar.pdf` уже сгенерирован —
        замени `\fbox`-заглушку на `\includegraphics`.
- [ ] **(если успеваешь, +1–2 ч)** HallusionBench тем же способом: xlsx лежат в
      `origin/results:outputs/reports_hallusion/`; повтори локальный прогон
      (см. «Как я считал preliminary» ниже).

### День 2 (29.08)

- [ ] Пройтись по тексту: убрать `\ph{`-остатки
      (`grep -n 'ph{' paper/main.tex` — только определение макроса);
      Limitations дополнить наблюдёнными false-positive модами из разметки.
- [ ] Анонимизация: в PDF нет имён/ссылки на репо; артефакт — через
      anonymous.4open.science (без `docs/ru/HANDOFF.md`,
      `docs/en/WorkPlan_TAI-Eval.md`, `NeurIPS2026_Workshop_Readiness.md`).
- [ ] Компиляция: `pdflatex → bibtex → pdflatex ×2`, проверить лимит страниц.
- [ ] Внутреннее ревью по чек-листу: (а) «враждебный автор MMStar» — в тексте
      должен быть абзац про то, что MMStar сам строился blind-фильтрацией, и
      наша находка — рефлексивная; (б) «скептик воспроизводимости» — команды
      воспроизведения в приложении.
- [ ] Сабмит на OpenReview до 23:59 AoE. Сохрани id сабмишена.

### Чего НЕ делать в Сценарии A

- Не запускать новые инференсы (не успеют и не нужны для подачи).
- Не добавлять HallusionBench, если к вечеру дня 1 он не готов.
- Не включать композитный «Benchmark Score» и `question_image_relevance`.

---

## Сценарий B: после подачи (или если дедлайн пропущен)

Это полный [WorkPlan_TAI-Eval.md](../en/WorkPlan_TAI-Eval.md), фазы 1–6:
6 моделей × MMStar/HallusionBench × full/blind на Colab A100 + API,
3 судьи, variance-study, повторная разметка на новой выборке. Если подача
состоялась — это материал для camera-ready и постера. Если нет — цели:
**Can We Trust the Judge?** (Atlanta) и **AI for Meta-Science** (Paris) —
дедлайны проверить на OpenReview немедленно.

Краткая шпаргалка команд на Colab:

```bash
git clone <repo> && cd vlm-bench && pip install -e .
export OPENAI_API_KEY=...
python -m pytest tests/ -q          # 2 падения в test_inference_api - норма среды
# полный/blind прогон (пример)
python run.py --data MMStar --model Qwen2.5-VL-7B-Instruct --mode all --reuse --judge gpt-4o-mini
python run.py --data MMStar --model Qwen2.5-VL-7B-Instruct --mode all --reuse --blind --judge gpt-4o-mini
# аудит
python run.py --mode bench_eval --data MMStar --model <все 6 имён> --detectors all --work-dir outputs
# стабильность / судьи / фигуры
python scripts/audit_stability.py --all-stat outputs/reports/visual_dependency/all_stat.json --out outputs/reports/visual_dependency
python scripts/rejudge_exact.py --src outputs --dst outputs_exact   # + bench_eval на outputs_exact
python scripts/audit_paper_assets.py --run MMStar=outputs --judge-run gpt=outputs --judge-run exact=outputs_exact --out paper/figures
```

## Как считались preliminary-числа (для воспроизведения)

Артефакты 3 моделей взяты из `origin/results` (eval id `T20260611-093811`),
разложены в стандартную структуру `outputs/<model>/<eval_id>/` и прогнаны
текущим кодом. На машине без полного окружения (нет decord и т.п.) это
делается через тестовый харнесс: см.
`tests/test_bench_eval_pipeline.py::load_pipeline` — он подставляет лёгкие
стабы вместо тяжёлых импортов, но исполняет **настоящий** пайплайн
(`vlmeval/bench_eval.py`) и настоящие детекторы. На Colab с полным
окружением используй просто `run.py --mode bench_eval`.

## Открытые вопросы (реши сам, они не блокируют подачу)

1. Пересечение нашего text_only-множества со списком отбраковки авторов
   MMStar — если найдёшь их списки (repo MMStar), добавь один абзац в
   результаты; это сильно укрепляет статью.
2. Судья `gpt-4.1-mini` как третья точка judge-sensitivity — только для
   camera-ready.
3. Что делать со старой веткой `origin/feature/report` — рекомендую закрыть:
   её скоринг («Benchmark Score», ключ-опечатка `"0ю"`) в статью не идёт.

## Git-состояние

Всё лежит **незакоммиченными правками** в рабочей копии на `main`
(так решил Лев). Перед началом работы: `git status`, создай ветку
(например `feature/tai-eval-submission`), закоммить блоками: код / тесты /
доки / paper / audit_preliminary. Ничего не пушить в публичный remote до
решения об анонимизации.
