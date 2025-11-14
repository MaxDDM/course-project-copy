<table>
<thead>
<tr>
<th>RiskID</th>
<th>Описание</th>
<th>Связь (F/NFR)</th>
<th>L</th>
<th>I</th>
<th>Risk</th>
<th>Стратегия</th>
<th>Владелец</th>
<th>Срок</th>
<th>Критерий закрытия</th>
</tr>
</thead>
<tbody><tr>
<td>R1</td>
<td>Брутфорс входа к API</td>
<td>F1, NFR-04</td>
<td>3</td>
<td>4</td>
<td>12</td>
<td>Снизить</td>
<td>@MaxDDM</td>
<td>2025-11-15</td>
<td>CI: rate-limit на /workouts и /workouts/{id} пройден; тесты нагрузки</td>
</tr>
<tr>
<td>R2</td>
<td>Утечка данных тренировок</td>
<td>F2, F3, NFR-06</td>
<td>2</td>
<td>5</td>
<td>10</td>
<td>Снизить</td>
<td>@MaxDDM</td>
<td>2025-11-20</td>
<td>Профили доступа и маскирование полей; журналирование без PII</td>
</tr>
<tr>
<td>R3</td>
<td>Несоответствие payload payload.workout_id URL workout_id</td>
<td>F4, NFR-04</td>
<td>2</td>
<td>5</td>
<td>10</td>
<td>Снизить</td>
<td>@MaxDDM</td>
<td>2025-11-22</td>
<td>Контрактные тесты: 100% соответствует условиям; негативные сценарии</td>
</tr>
<tr>
<td>R4</td>
<td>Ошибки в обработке ошибок</td>
<td>F2, F3, NFR-06</td>
<td>1</td>
<td>4</td>
<td>4</td>
<td>Избежать</td>
<td>@MaxDDM</td>
<td>2025-11-25</td>
<td>Валидация формата ошибок</td>
</tr>
<tr>
<td>R5</td>
<td>Неправильная авторизация на чтение наборов</td>
<td>F5, NFR-04</td>
<td>2</td>
<td>3</td>
<td>6</td>
<td>Снизить</td>
<td>@MaxDDM</td>
<td>2025-11-28</td>
<td>Тесты на доступность данных и отсутствие лишних полей</td>
</tr>
<tr>
<td>R6</td>
<td>Время отклика GET /workouts &gt; порог</td>
<td>NFR-08</td>
<td>3</td>
<td>4</td>
<td>12</td>
<td>Снизить</td>
<td>@MaxDDM</td>
<td>2025-12-05</td>
<td>Нагрузочное тестирование (p95 ≤ 300 ms при 1000+ тренировках)</td>
</tr>
<tr>
<td>R7</td>
<td>Уязвимости зависимостей (зависимости Python)</td>
<td>NFR-07</td>
<td>2</td>
<td>3</td>
<td>6</td>
<td>Перенести/Снизить</td>
<td>@MaxDDM</td>
<td>2025-12-10</td>
<td>Сканирование зависимостей; обновления SCA/SBOM в CI; порог реагирования ≤ 7 дней</td>
</tr>
<tr>
<td>R8</td>
<td>Неприемлемый риск дублирования подходов</td>
<td>F4</td>
<td>2</td>
<td>4</td>
<td>8</td>
<td>Снизить</td>
<td>@MaxDDM</td>
<td>2025-12-12</td>
<td>Контроль уникальности ID; тесты на дубликаты</td>
</tr>
<tr>
<td>R9</td>
<td>Ошибки в возврате пустых наборов после удаления тренировки</td>
<td>F6, F5</td>
<td>1</td>
<td>3</td>
<td>3</td>
<td>Избежать</td>
<td>@MaxDDM</td>
<td>2025-12-15</td>
<td>Тесты на состояние после удаления тренировки; сценарии</td>
</tr>
<tr>
<td>R10</td>
<td>Отсутствие мониторинга и алертинга сервисов</td>
<td>NFR-05</td>
<td>2</td>
<td>4</td>
<td>8</td>
<td>Снизить</td>
<td>@MaxDDM</td>
<td>2025-12-20</td>
<td>Мониторинг/алертинг в CI; система оповещений</td>
</tr>
</tbody></table>
